import matplotlib.pyplot as plt
import numpy as np
import time

from data_sources.zmq_data_source import ZMQDataSource

class RealTimeScatterPlot:
    def __init__(self, fetch_data_fns, buffer_size=1000, vline_buffer_size=10, fps_sample_size=1000, fps_report_rate=100, xlim=[-1000, 10], ylim=[-1, 1]):
        self.fetch_data_fns = fetch_data_fns
        self.num_series = len(fetch_data_fns)
        self.buffer_size = buffer_size
        self.fps_sample_size = fps_sample_size
        self.fps_report_rate = fps_report_rate

        # Initialize series arrays
        self.x_series = [np.zeros(buffer_size) for _ in range(self.num_series)]
        self.y_series = [np.zeros(buffer_size) for _ in range(self.num_series)]
        self.last_horizontal_ticks = [0] * self.num_series

        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

        # Create scatter plots for each series
        self.scatters = [self.ax.scatter([], [], animated=True, s=1) for _ in range(self.num_series)]

        plt.title("Realtime Scatter Plot")
        plt.show(block=False)
        plt.pause(0.1)

        self.bg = self.fig.canvas.copy_from_bbox(self.ax.get_figure().bbox)
        for sc in self.scatters:
            self.ax.draw_artist(sc)
        self.fig.canvas.blit(self.fig.clipbox)
        self.old_fig_size = self.fig.get_size_inches()

        # fps calculation
        self.t_start = 0
        self.fps_sample_start_frame = 0

    def calculate_fps(self, i):
        if i % self.fps_sample_size == 0:
            self.t_start = time.time()
            self.fps_sample_start_frame = i
        if i % self.fps_report_rate == 0:
            elapsed_time = time.time() - self.t_start
            if elapsed_time:
                fps = (i - self.fps_sample_start_frame) / elapsed_time
                print("fps: {}".format(fps))

    def update_plot(self, data_points, i, update_xlim=False, new_xlim=None):
        if (self.old_fig_size != self.fig.get_size_inches()).any():
            self.bg = self.fig.canvas.copy_from_bbox(self.fig.bbox)
            self.old_fig_size = self.fig.get_size_inches()
        self.fig.canvas.restore_region(self.bg)

        # Update scatter plots
        for series_index, (data_point_x, data_point_y) in enumerate(data_points):
            # recalculate shifted horizontal value
            if not self.last_horizontal_ticks[series_index]:
                new_x_delta = 0
            else:
                new_x_delta = (data_point_x - self.last_horizontal_ticks[series_index])
            self.last_horizontal_ticks[series_index] = data_point_x

            new_y_data = data_point_y

            # left shift the buffer
            self.x_series[series_index] -= self.x_series[series_index][1]
            self.x_series[series_index] = np.roll(self.x_series[series_index], -1)
            self.x_series[series_index][-1] = self.x_series[series_index][-2] + new_x_delta
            self.x_series[series_index] -= self.x_series[series_index][-1]  # make the last item to be 0, and all rest to be negative
            self.y_series[series_index] = np.roll(self.y_series[series_index], -1)
            self.y_series[series_index][-1] = new_y_data

            # Update scatter plots for each series
            self.scatters[series_index].set_offsets(np.column_stack((self.x_series[series_index], self.y_series[series_index])))

            self.ax.draw_artist(self.scatters[series_index])

            # Update xlim if requested
            if update_xlim and new_xlim:
                self.ax.set_xlim(new_xlim)

        self.fig.canvas.blit(self.fig.clipbox)
        self.fig.canvas.flush_events()

        self.calculate_fps(i)

    def run(self):
        i = 0
        while True:
            # Fetch data for each series
            data_points = [fetch_data_fn() for fetch_data_fn in self.fetch_data_fns]
            
            # every 100 data we adjust the xlim
            if i % 100 == 0:
                new_xlim = [self.x_series[0][0], 100]
                print(new_xlim)
                self.update_plot(data_points, i, update_xlim=True, new_xlim=new_xlim)
            else:
                self.update_plot(data_points, i)

            i += 1

# Usage
if __name__ == "__main__":
    # Example: Create an array of data sources
    data_sources = [ZMQDataSource(7002)]
    real_time_plot = RealTimeScatterPlot([ds.get_data for ds in data_sources], ylim=[-180, 180])
    real_time_plot.run()

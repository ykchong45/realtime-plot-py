import matplotlib.pyplot as plt
import numpy as np
import time
import math

## uncomment the following import when you are subscribing to zmq endpoint
# import zmq
# import stream_data_pb2 as stream_data

## EXAMPLE DATA SOURCES

class DataGenerator:
    def __init__(self):
        self.x = 0

    def get_data(self):
        self.x += 1
        y = math.sin(self.x * 2 * math.pi / 1000)
        return self.x, y
    
# class ZMQDataReceiver:
#     def __init__(self, endpoint=7000):
#         self.endpoint = endpoint
#         self.context = zmq.Context()
#         self.socket = self.initialize_socket()

#     def initialize_socket(self):
#         socket = self.context.socket(zmq.SUB)
#         socket.connect('tcp://localhost:{}'.format(self.endpoint))
#         socket.subscribe(b'')
#         socket.RCVTIMEO = 1000
#         return socket

#     def get_data(self):
#         data = self.socket.recv()
#         message = stream_data.StreamData()
#         message.ParseFromString(data)

#         # edit the following line when using
#         newDataTime = message.optical_data.recorded_time / 6000000
#         data_point_y = message.optical_data.position.x  # edit this when using
#         return newDataTime, data_point_y
    

## REALTIME SCATTER PLOT DEFINITION

class RealTimeScatterPlot:
    def __init__(self, fetch_data_fn, buffer_size=1000, fps_sample_size=1000, fps_report_rate=100, xlim=[-1000, 10], ylim=[-1, 1]):
        self.fetch_data_fn = fetch_data_fn
        self.buffer_size = buffer_size
        self.fps_sample_size = fps_sample_size
        self.fps_report_rate = fps_report_rate

        self.x = np.zeros(buffer_size)
        self.y = np.zeros(buffer_size)
        self.last_horizontal_tick = 0

        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.sc = self.ax.scatter(self.x, self.y, animated=True, s=1)

        plt.title("Realtime Scatter Plot")
        plt.show(block=False)
        plt.pause(0.1)

        self.bg = self.fig.canvas.copy_from_bbox(self.ax.get_figure().bbox)
        self.ax.draw_artist(self.sc)
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
        
    def update_plot(self, data_point_x, data_point_y, i):
        if (self.old_fig_size != self.fig.get_size_inches()).any():
            self.bg = self.fig.canvas.copy_from_bbox(self.fig.bbox)
            self.old_fig_size = self.fig.get_size_inches()
        self.fig.canvas.restore_region(self.bg)

        # recalculate shifted horizontal value
        if not self.last_horizontal_tick:
            new_x_delta = 0
        else:
            new_x_delta = (data_point_x - self.last_horizontal_tick)
        self.last_horizontal_tick = data_point_x

        new_y_data = data_point_y

        # left shift the buffer
        self.x -= self.x[1]
        self.x = np.roll(self.x, -1)
        self.x[-1] = self.x[-2] + new_x_delta
        self.x -= self.x[-1]    # make the last item to be 0, and all rest to be negative
        self.y = np.roll(self.y, -1)
        self.y[-1] = new_y_data

        self.sc.set_offsets(np.column_stack((self.x, self.y)))
        self.ax.draw_artist(self.sc)
        self.fig.canvas.blit(self.fig.clipbox)
        self.fig.canvas.flush_events()

        self.calculate_fps(i)

    def run(self, max_iterations=10000):
        for i in range(max_iterations):
            newDataTime, data_point_y = self.fetch_data_fn()
            self.update_plot(newDataTime, data_point_y, i)

## Usage
if __name__ == "__main__":
    data_generator = DataGenerator()
    # data_generator = ZMQDataReceiver()
    real_time_plot = RealTimeScatterPlot(data_generator.get_data)
    real_time_plot.run()

import matplotlib.pyplot as plt
import numpy as np
import time
import random

# configurables
buffer_size= 2000    # number of data in across the horizontal axis 
fpsTestSize = 1000  # every `fpsTestSize` of frames we re-evaluate the fps
fpsReportRate = 100 # every `fpsReportRate` count of frames, the program report the fps once

# START
x = np.zeros(buffer_size)
y = np.zeros(buffer_size)
fig, ax = plt.subplots()
ax.set_xlim([0, buffer_size])
ax.set_ylim([-1, 1])
sc = ax.scatter(x, y, animated=True)

plt.title("Sine Wave Scatter Plot")
plt.show(block=False)
plt.pause(0.1)

bg = fig.canvas.copy_from_bbox(ax.get_figure().bbox)

ax.draw_artist(sc)

fig.canvas.blit(fig.clipbox)
old_fig_size = fig.get_size_inches()

tStart = 0
fpsTestStartFrame = 0

for j in range(10000):
    ## RESPONSE TO RESIZING THE WINDOW
    if (old_fig_size != fig.get_size_inches()).any():
        bg = fig.canvas.copy_from_bbox(fig.bbox)   
        old_fig_size = fig.get_size_inches()
    fig.canvas.restore_region(bg)


    # generate data and shift
    newXDelta = random.uniform(0, 2)
    newYData = np.sin(j * 2 * np.pi / buffer_size)

    if j < buffer_size:
        x[j] = x[j-1] + newXDelta
        y[j] = newYData
    else:
        x -= x[1]
        x = np.roll(x, -1)
        x[-1] = x[-2] + newXDelta
        y = np.roll(y, -1)
        y[-1] = newYData

    
    sc.set_offsets(np.column_stack((x, y)))
    ax.draw_artist(sc)
    fig.canvas.blit(fig.clipbox)
    fig.canvas.flush_events()
    
    # calculate fps with test range
    if j % fpsTestSize == 0:
        tStart = time.time()
        fpsTestStartFrame = j
    if j % fpsReportRate == 0:
        elapsedTime = time.time() - tStart
        if elapsedTime:
            fps = (j - fpsTestStartFrame) / elapsedTime
            print(fps)
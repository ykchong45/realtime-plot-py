import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import random
import time

# Initialize data
buffer_size = 100  # Number of data points to display
currentIdx = 0
x_buffer = np.empty(shape=(buffer_size))
y_buffer = np.empty(shape=(buffer_size))

fig, ax = plt.subplots()  # Use a single set of axes
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])

# Use scatter plot instead of line plot
sc = ax.scatter(x_buffer, y_buffer)
sc2 = ax.scatter(x_buffer, y_buffer)

nCount = 0
tStart = time.time()

def update_buffer():
    currentIdx = nCount % buffer_size
    x_buffer[currentIdx] = random.uniform(-1, 1)
    y_buffer[currentIdx] = random.uniform(-1, 1)
    currentIdx += 1
    

def animate(i):
    update_buffer()
    global nCount
    nCount += 1
    fps = nCount / (time.time() - tStart)
    print(fps)
    # Set the data for the scatter plot
    sc.set_offsets(np.column_stack((x_buffer, y_buffer)))
    sc2.set_offsets(np.column_stack((x_buffer + 0.01, y_buffer + 0.01)))

    return sc, sc2

# We'd normally specify a reasonable "interval" here...
ani = animation.FuncAnimation(fig, animate, interval=1, blit=True)
plt.show()

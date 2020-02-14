import matplotlib.pyplot as plt
import matplotlib.animation as animation
import linecache
from collections import deque

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

tar = deque([0 for i in range(1000)])
xar = deque([0 for i in range(1000)])
yar = deque([0 for i in range(1000)])
zar = deque([0 for i in range(1000)])

line_no = 1
def animate(i):
    global line_no
    while True:
        line = linecache.getline('data.txt', line_no).strip()
        if line == '':
            linecache.clearcache()
            break
        t, x, y, z = line.split(' ')
        tar.popleft(); tar.append(int(t))
        xar.popleft(); xar.append(int(x))
        yar.popleft(); yar.append(int(y))
        zar.popleft(); zar.append(int(z))
        line_no += 1
    ax1.clear()
    ax1.plot(tar,zar)

ani = animation.FuncAnimation(fig, animate, interval=10)
plt.show()

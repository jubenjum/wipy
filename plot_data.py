import matplotlib.pyplot as plt
import matplotlib.animation as animation
import linecache

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

tar = [0 for i in range(1000)]
xar = [0 for i in range(1000)]
yar = [0 for i in range(1000)]
zar = [0 for i in range(1000)]

line_no = 1
def animate(i):
    global line_no
    while True:
        line = linecache.getline('data.txt', line_no).strip()
        if line == '':
            linecache.clearcache()
            break
        t, x, y, z = line.split(' ')
        tar.reverse(); tar.pop(); tar.reverse(); tar.append(int(t))
        xar.reverse(); xar.pop(); xar.reverse(); xar.append(int(x))
        yar.reverse(); yar.pop(); yar.reverse(); yar.append(int(y))
        zar.reverse(); zar.pop(); zar.reverse(); zar.append(int(z))
        line_no += 1
    ax1.clear()
    ax1.plot(tar,zar)
ani = animation.FuncAnimation(fig, animate, interval=10)
plt.show()

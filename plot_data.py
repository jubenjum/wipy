import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

tar = [0 for i in range(1000)]
xar = [0 for i in range(1000)]
yar = [0 for i in range(1000)]
zar = [0 for i in range(1000)]

line_no = 0
def animate(i):
    global line_no
    fp = open("data.txt")
    for i, line in enumerate(fp):
        if i >= line_no:
            t, x, y, z = line.split(' ')
            tar.reverse(); tar.pop(); tar.reverse(); tar.append(int(t))
            xar.reverse(); xar.pop(); xar.reverse(); xar.append(int(x))
            yar.reverse(); yar.pop(); yar.reverse(); yar.append(int(y))
            zar.reverse(); zar.pop(); zar.reverse(); zar.append(int(z))
    line_no = i
    fp.close()
    ax1.clear()
    ax1.plot(tar,zar)
ani = animation.FuncAnimation(fig, animate, interval=10)
plt.show()

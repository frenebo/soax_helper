import tk
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import (
                                    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

root = tk.Tk()
root.wm_title("Embedding in Tk")

fig = Figure(figsize=(5, 4), dpi=100)

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()

ax = fig.add_subplot(111, projection="3d")
t = np.arange(0, 3, .01)
ax.plot(t, 2 * np.sin(2 * np.pi * t))

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
v = tk.StringVar(root, "1")
w = tk.RadioButton(root, from_=0, to=200, orient=tk.HORIZONTAL)
w.pack()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


tk.mainloop()
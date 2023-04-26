import math, random, os
import pandas as pd
import matplotlib.pyplot as plt
import tkinter.ttk as ttk
from tkinter import *
from tktooltip import ToolTip
from matplotlib import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

class PointsSet:
    def __init__(self, points, center, circ_no):
        self.points = points
        self.center = center if not math.isnan(circ_no) else None
        self.circ_no = circ_no if not math.isnan(circ_no) else None

    def add_point(self, point):
        self.points.append(point)

    def is_noise(self):
        return self.circ_no is None

    def __str__(self):
        if self.is_noise():
            return f"{len(self.points)} of Noise"
        else:
            return f"Circunference {self.circ_no} has {len(self.points)} points and center in {self.center}"

def extract_point_sets(df):
    data = []
    for index, row in df.iterrows():
        
        existing_ps = next(filter(lambda ps: ps.circ_no==row.circ_no if not math.isnan(row.circ_no) else ps.circ_no is None, data), None)
        if existing_ps is not None:
            existing_ps.add_point((row.point_x, row.point_y))
        else:
            data.append(PointsSet([(row.point_x, row.point_y)], (row.center_x, row.center_y), row.circ_no))
    return data

# Main function

def visualize():
    DATASET_LOCATION = dle.get()

    def plot_data(data):
        points = []
        c = []
        for points_set in data:
            points.extend(points_set.points)
            
            # We set the color for the set, making sure its different for each set
            set_color = random.uniform(0, 100)
            while(set_color in c):
                set_color = random.uniform(0, 100)
            c.extend([set_color for _ in points_set.points])

        fig = Figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot()
        ax.scatter(*zip(*points), s=10, c=c)
        ax.set(xlim=(0, 100), ylim=(0, 100))
        ax.set_aspect('equal')
        
        canvas = FigureCanvasTkAgg(fig, master=visualize_window)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas,
                                    visualize_window)
        toolbar.update()
    
        # placing the toolbar on the Tkinter window
        canvas.get_tk_widget().pack()

    main_window.destroy()
    use('TkAgg')

    for filename in os.listdir(DATASET_LOCATION):
        visualize_window = Tk()
        visualize_window.resizable(False, False)
        visualize_window.title(filename)

        if filename.endswith(".csv"): 
            df = pd.read_csv(f"{DATASET_LOCATION}/{filename}",header=0, sep=";")
            data = extract_point_sets(df)
            plot_data(data)
            Button(visualize_window, text="Next", command=visualize_window.destroy).pack(side=RIGHT, expand=True)
            Button(visualize_window, text="Finish", command=exit).pack(side=LEFT, expand=True)
            visualize_window.mainloop()


if __name__=="__main__":
    main_window = Tk()
    main_window.resizable(False, False)
    main_window.title('Dataset Visualizer')

    Label(main_window, text="Output").grid(row=6, column=0, sticky='w')
    dlh = Label(main_window, text="?", borderwidth=4)
    dlh.grid(row=6, column=2)
    ToolTip(dlh, msg="Dataset directory (relative path)")

    dle = Entry(main_window, width=20, selectborderwidth=5)
    dle.insert(0, "./dataset")
    dle.grid(row=6, column=1)

    Button(main_window, text="Visualize", command=visualize).grid(row=7, column=0, columnspan=3)

    main_window.mainloop()

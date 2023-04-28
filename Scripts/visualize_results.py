import math, random, os, json
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
    def __init__(self, points, center, radius, circ_no):
        self.points = points
        self.center = center if not math.isnan(circ_no) else None
        self.radius = radius if not math.isnan(circ_no) else None
        self.circ_no = int(circ_no) if not math.isnan(circ_no) else None

    def add_point(self, point):
        self.points.append(point)

    def is_noise(self):
        return self.circ_no is None

    def unpack(self):
        if self.is_noise():
            return [[p[0], p[1], None, None, None] for p in self.points]
        else:
            return [[p[0], p[1], self.center[0], self.center[1], self.radius, self.circ_no] for p in self.points]

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
            data.append(PointsSet([(row.point_x, row.point_y)], (row.center_x, row.center_y), row.radius, row.circ_no))
    return data

# Main function
class ResultsVis():
    def __init__(self, current_set_type):
        self.current_set_type = current_set_type

    def visualize(self, set_type):
        def plot_data(data):
            points = []
            c = []
            for key, circ in data["circunferences"].items():
                points.extend(circ["points"])
                
                # We set the color for the set, making sure its different for each set
                set_color = random.randint(0, 100)
                while(set_color in c):
                    set_color = random.randint(0, 100)
                c.extend([set_color for _ in circ["points"]])
            
            noise = list(*data["noise"])
            points.extend(noise)
            set_color = random.randint(0, 100)
            while(set_color in c):
                set_color = random.randint(0, 100)
            c.extend([set_color for _ in noise])

            rings = []
            for det_center_ind, _ in data["pairs"]:
                points.append(data["predicted_centers"][det_center_ind])
                rings.append(plt.Circle(data["predicted_centers"][det_center_ind], data["predicted_radii"][det_center_ind], fill=False))
                c.append(0.0)

            fig = Figure(figsize=(5, 5), dpi=100)
            ax = fig.add_subplot()
            ax.scatter(*zip(*points), s=10, c=c)
            for r in rings:
                ax.add_artist( r )
            ax.set(xlim=(0, 100), ylim=(0, 100))
            ax.set_aspect('equal')
            
            canvas = FigureCanvasTkAgg(fig, master=visualize_window)
            canvas.draw()
            toolbar = NavigationToolbar2Tk(canvas,
                                        visualize_window)
            toolbar.update()
        
            # placing the toolbar on the Tkinter window
            canvas.get_tk_widget().pack()

        def next_set_type():
            match set_type:
                case "clean": visualize_window.destroy(); self.current_set_type="extends"; self.visualize("extends")
                case "extends": visualize_window.destroy(); self.current_set_type="collides"; self.visualize("collides")
                case _ : visualize_window.destroy(); self.current_set_type = None
        
        def next(filename):
            if filename == list(RESULTS[set_type].keys())[-1]:
                next_set_type()
            else: 
                visualize_window.destroy()
        
        def finish():
            visualize_window.destroy()
            self.current_set_type = None

        for filename in RESULTS[set_type].keys():
            if(self.current_set_type==set_type):
                visualize_window = Tk()
                visualize_window.resizable(False, False)
                visualize_window.title(f"{set_type} - {filename}")

                plot_data(RESULTS[set_type][filename])

                Button(visualize_window, text="Next", command= lambda: next(filename)).pack(side=RIGHT, expand=True)
                Button(visualize_window, text="Next Type", command=next_set_type).pack(side=RIGHT, expand=True)
                Button(visualize_window, text="Finish", command=finish).pack(side=LEFT, expand=True)
                visualize_window.mainloop()

def init_res_vis(results_dir):
    global RESULTS
    f = open(f"{results_dir}/results.json")
    RESULTS = json.load(f)
    res_vis = ResultsVis("clean")
    res_vis.visualize("clean")
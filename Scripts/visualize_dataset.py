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
from Scripts.utils import PointsSet

def extract_point_sets(df):
    data = []
    for index, row in df.iterrows():
        
        existing_ps = next(filter(lambda ps: ps.circ_no==row.circ_no if not math.isnan(row.circ_no) else ps.circ_no is None, data), None)
        if existing_ps is not None:
            existing_ps.add_point((row.point_x, row.point_y))
        else:
            data.append(PointsSet.parse([(row.point_x, row.point_y)], (row.center_x, row.center_y), row.radius, row.circ_no))
    return data

# Main loop

class DataSetVis():
    def __init__(self, current_set_type):
        self.current_set_type = current_set_type

    def visualize(self, set_type):
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

        def next_set_type():
            match set_type:
                case "clean": visualize_window.destroy(); self.current_set_type="extends"; self.visualize("extends")
                case "extends": visualize_window.destroy(); self.current_set_type="collides"; self.visualize("collides")
                case _ : visualize_window.destroy(); self.current_set_type = None
        
        def next(i):
            if i == (len(os.listdir(DATASET_LOCATION+f"/{set_type}"))-1):
                next_set_type()
            else: 
                visualize_window.destroy()
        
        def finish():
            visualize_window.destroy()
            self.current_set_type = None

        if os.path.exists(DATASET_LOCATION+f"/{set_type}") or len(os.listdir(DATASET_LOCATION+f"/{set_type}")) > 0:
            for i in range(len(os.listdir(DATASET_LOCATION+f"/{set_type}"))):
                if(self.current_set_type==set_type):
                    filename = (os.listdir(DATASET_LOCATION+f"/{set_type}")[i])
                    visualize_window = Tk()
                    visualize_window.resizable(False, False)
                    visualize_window.title(f"{set_type} - {filename}")

                    if filename.endswith(".csv"): 
                        df = pd.read_csv(f"{DATASET_LOCATION}/{set_type}/{filename}",header=0, sep=";")
                        data = extract_point_sets(df)
                        plot_data(data)
                        Button(visualize_window, text="Next", command= lambda: next(i)).pack(side=RIGHT, expand=True)
                        Button(visualize_window, text="Next Type", command=next_set_type).pack(side=RIGHT, expand=True)
                        Button(visualize_window, text="Finish", command=finish).pack(side=LEFT, expand=True)
                        visualize_window.mainloop()
        else:
            next_set_type()

def init_vis(dataset_dir):
    global DATASET_LOCATION
    DATASET_LOCATION = dataset_dir
    if not os.path.exists(DATASET_LOCATION) or len(os.listdir(DATASET_LOCATION)) == 0:
        message = QMessageBox()
        message.setText(f"The provided dataset does not exist or its empty:\n{DATASET_LOCATION}")
        message.exec_()
        return None

    data_vis = DataSetVis("clean")
    data_vis.visualize("clean")
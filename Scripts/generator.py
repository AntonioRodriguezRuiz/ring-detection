import random, os
import pandas as pd
import tkinter.ttk as ttk
from tkinter import *
from tktooltip import ToolTip
from math import pi, cos, sin


# Class PointsSet

class PointsSet:
    def __init__(self, points, center, circ_no):
        self.points = points
        self.center = center
        self.circ_no = circ_no

    def add_point(self, point):
        self.points.append(point)

    def is_noise(self):
        return self.circ_no is None

    def unpack(self):
        if self.is_noise():
            return [[p[0], p[1], None, None] for p in self.points]
        else:
            return [[p[0], p[1], self.center[0], self.center[1], self.circ_no] for p in self.points]

    def __str__(self):
        if self.is_noise():
            return f"{len(self.points)} of Noise"
        else:
            return f"Circunference {self.circ_no} has {len(self.points)} points and center in {self.center}"


# Dataset generation

def get_circunference_points(n, center, rad):
    RANDOMNESS = float(rde.get())

    points = []
    for _ in range(n):
        theta = random.random() * 2 * pi
        x = center[0] + cos(theta)*rad*RANDOMNESS + (random.random()/10)*rad
        y = center[1] + sin(theta) * rad*RANDOMNESS + (random.random()/10)*rad
        points.append((x,y)) if 0<=x<=100 and 0<=y<=100 else _ # We only add those points inside the valid range
    return points
    
def get_data():
    NUM_CIRC = int(nce.get())
    RANGE_RADIUS = (float(rre.get().split(",")[0]), float(rre.get().split(",")[1]))
    RANGE_POINTS = (int(rpe.get().split(",")[0]), int(rpe.get().split(",")[1]))
    NOISE_RATIO = float(nre.get())

    data = []
    for i in range(NUM_CIRC):
        circ_no = i+1 # 0 will be used for noise
        center = (random.uniform(0.0, 100.0), random.uniform(0.0, 100.0))
        rad = random.uniform(*RANGE_RADIUS)
        n = random.randint(*RANGE_POINTS)
        points = get_circunference_points(n, center, rad)
        circunference = PointsSet(points, center, circ_no)
        data.append(circunference)
    
    # Add noise
    n = int(sum([len(c.points) for c in data]) * (NOISE_RATIO)) # Number of total points so far in the dataset * NOISE_RATIO. This gives us the ammount of noise to include in the dataset
    points = [(random.uniform(0.0, 100.0), random.uniform(0.0, 100.0)) for _ in range(n)]
    noise = PointsSet(points, None, None)

    data.append(noise)
    return data

# Main function

def generate():
    NUM_IMAGES = int(nie.get())
    
    OUTPUT = oe.get()

    if not os.path.exists(OUTPUT):
        os.mkdir(OUTPUT)
        counter = 1
    else:
        # Start counter from the last csv in the directory as to not overwrite previous data
        counter = sorted([int(x.split(".")[0]) for x in os.listdir(OUTPUT)])[-1]+1

    dataset_list = [get_data() for _ in range(NUM_IMAGES)]
    for data in dataset_list:
        data_frame_list = []
        for points_set in data:
            data_frame_list.extend(points_set.unpack())
        
        plane_pd = pd.DataFrame(data_frame_list,
                                columns=["point_x", "point_y", "center_x", "center_y", "circ_no"])

        # We save the data in a csv, in the output folder specified, continue to the next circle
        plane_pd.to_csv(OUTPUT+f"/{counter}.csv", sep=";", index=False)
        counter += 1
    
    main_window.destroy()

if __name__=="__main__":
    main_window = Tk()
    main_window.resizable(False, False)
    main_window.title('Dataset Generator')

    # Labels and tooltips

    Label(main_window, text="Nº images").grid(row=0, column=0, sticky='w')
    nih = Label(main_window, text="?", borderwidth=4)
    nih.grid(row=0, column=2)
    ToolTip(nih, msg="Size of the Dataset")

    Label(main_window, text="Nª circunferences").grid(row=1, column=0, sticky='w')
    nch = Label(main_window, text="?", borderwidth=4)
    nch.grid(row=1, column=2)
    ToolTip(nch, msg="Number of circunferences per image")

    Label(main_window, text="Randomness").grid(row=2, column=0, sticky='w')
    rdh = Label(main_window, text="?", borderwidth=4)
    rdh.grid(row=2, column=2)
    ToolTip(rdh, msg="Ammount of randomness in the points of a circunference. The more the randomness, the less defined the circunference. It is advised to not make it too large")

    Label(main_window, text="Range points").grid(row=3, column=0, sticky='w')
    rph = Label(main_window, text="?", borderwidth=4)
    rph.grid(row=3, column=2)
    ToolTip(rph, msg="Range for the ammount of points in a circunference of radius 1, the ammount of points for a circunference will be random inside this interval. For other radiuses it will be proportional")

    Label(main_window, text="Range radius").grid(row=4, column=0, sticky='w')
    rrh = Label(main_window, text="?", borderwidth=4)
    rrh.grid(row=4, column=2)
    ToolTip(rrh, msg="Range for the radius of the circunferences. Values must be float")

    Label(main_window, text="Noise ratio").grid(row=5, column=0, sticky='w')
    nrh = Label(main_window, text="?", borderwidth=4)
    nrh.grid(row=5, column=2)
    ToolTip(nrh, msg="Number of random points generated in the Dataset per circunference point. These will be added at the end of the process")

    Label(main_window, text="Output").grid(row=6, column=0, sticky='w')
    oh = Label(main_window, text="?", borderwidth=4)
    oh.grid(row=6, column=2)
    ToolTip(oh, msg="Dataset output (relative path)")

    # Text Input

    nie = Entry(main_window, width=20, selectborderwidth=5)
    nie.insert(0, "10")
    nie.grid(row=0, column=1)

    nce = Entry(main_window, width=20, selectborderwidth=5)
    nce.insert(0, "3")
    nce.grid(row=1, column=1)

    rde = Entry(main_window, width=20, selectborderwidth=5)
    rde.insert(0, "1.0")
    rde.grid(row=2, column=1)

    rpe = Entry(main_window, width=20, selectborderwidth=5)
    rpe.insert(0, "30,50")
    rpe.grid(row=3, column=1)

    rre = Entry(main_window, width=20, selectborderwidth=5)
    rre.insert(0, "5.0, 15.0")
    rre.grid(row=4, column=1)

    nre = Entry(main_window, width=20, selectborderwidth=5)
    nre.insert(0, "0.05")
    nre.grid(row=5, column=1)

    oe = Entry(main_window, width=20, selectborderwidth=5)
    oe.insert(0, "./dataset")
    oe.grid(row=6, column=1)

    # Main Button

    Button(main_window, text="Generate", command=generate).grid(row=7, column=0, columnspan=3)

    main_window.mainloop()
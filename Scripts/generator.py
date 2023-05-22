import random, os
import pandas as pd
import tkinter.ttk as ttk
import numpy as np
from math import pi, cos, sin, sqrt
from PyQt5.QtWidgets import *
from Scripts.utils import PointsSet


# Dataset generation

def get_circunference_points(n, center, rad):
    points = []
    for _ in range(n):
        theta = random.random() * 2 * pi
        x = center[0] + cos(theta)*rad + (random.random()/10)*rad*RANDOMNESS
        y = center[1] + sin(theta)*rad + (random.random()/10)*rad*RANDOMNESS
        points.append((x,y)) if 0<=x<=100 and 0<=y<=100 else _ # We only add those points inside the valid range
    return points
    
def get_circ_parameters():
    centers = [(random.uniform(0.0, 100.0), random.uniform(0.0, 100.0)) for _ in range(NUM_CIRC)]
    radii = [random.uniform(*RANGE_RADIUS) for _ in range(NUM_CIRC)]
    collides = any(any((centers[i][0]-centers[j][0])**2 + (centers[i][1]-centers[j][1])**2 <= (radii[i]+radii[j])**2 for i in range(j+1, NUM_CIRC)) for j in range(NUM_CIRC))
    extends = any(0>=centers[i][0]-radii[i] or radii[i]+centers[i][0]>=100 or 0>=centers[i][1]-radii[i] or radii[i]+centers[i][1]>=100 for i in range(NUM_CIRC))
    return centers, radii, collides, extends

def get_data(set_type):
    centers, radii, collides, extends = get_circ_parameters()

    match set_type:
        case "clean":
            while(collides or extends): 
                centers, radii, collides, extends = get_circ_parameters()
        case "extends":
            while(collides or not extends):
                centers, radii, collides, extends = get_circ_parameters()
        case "collission":
            while(not collides or extends):
                centers, radii, collides, extends = get_circ_parameters()

    data = [PointsSet(get_circunference_points(random.randint(*RANGE_POINTS), centers[i], radii[i]), centers[i], radii[i], i+1) for i in range(NUM_CIRC)]
    '''
    for i in range(NUM_CIRC):
        circ_no = i+1 # 0 will be used for noise
        center = centers[i]
        rad = radii[i]
        n = random.randint(*RANGE_POINTS)

        points = get_circunference_points(n, center, rad)
        circunference = PointsSet(points, center, circ_no)
        data.append(circunference)
    '''
    
    # Add noise
    n = int(sum([len(c.points) for c in data]) * (NOISE_RATIO)) # Number of total points so far in the dataset * NOISE_RATIO. This gives us the ammount of noise to include in the dataset
    points = [(random.uniform(0.0, 100.0), random.uniform(0.0, 100.0)) for _ in range(n)]
    noise = PointsSet(points, None, None, None)

    data.append(noise)
    return data


# Main function

def generate(num_circ, num_images, randomness, range_radius, range_points, noise_ratio, output):
    global NUM_CIRC, NUM_IMAGES, RANDOMNESS, RANGE_RADIUS, RANGE_POINTS, NOISE_RATIO, OUTPUT
    try:
        NUM_CIRC = int(num_circ)
        NUM_IMAGES = int(num_images)
        RANDOMNESS = float(randomness)
        RANGE_RADIUS = (float(range_radius.split(",")[0]), float(range_radius.split(",")[1]))
        RANGE_POINTS = (int(range_points.split(",")[0]), int(range_points.split(",")[1]))
        NOISE_RATIO = float(noise_ratio)
        OUTPUT = output
    except Exception as e:
        message = QMessageBox()
        message.setText(f"Some input was invalid:\n{e}")
        message.exec_()
        return None

    dataset_clean = [get_data(set_type="clean") for _ in range(NUM_IMAGES)]
    dataset_extend = [get_data(set_type="extends") for _ in range(NUM_IMAGES)]
    if(NUM_CIRC>1): dataset_collission = [get_data(set_type="collission") for _ in range(NUM_IMAGES)]

    def save_dataset(dataset, set_type):
        if not os.path.exists(OUTPUT+f"/{set_type}"):
            os.makedirs(OUTPUT+f"/{set_type}")
            counter = 1
        else:
            # Start counter from the last csv in the directory as to not overwrite previous data
            counter = sorted([int(x.split(".")[0]) for x in os.listdir(OUTPUT+f"/{set_type}")])[-1]+1
        for data in dataset:
            data_frame_list = []
            for points_set in data:
                data_frame_list.extend(points_set.unpack())
            
            plane_pd = pd.DataFrame(data_frame_list,
                                    columns=["point_x", "point_y", "center_x", "center_y", "radius", "circ_no"])

            # We save the data in a csv, in the output folder specified, continue to the next circle
            plane_pd.to_csv(OUTPUT+f"/{set_type}/{counter}.csv", sep=";", index=False)
            counter += 1

    save_dataset(dataset_clean, "clean")
    save_dataset(dataset_extend, "extends")
    if(NUM_CIRC>1): save_dataset(dataset_collission, "collides")

    message = QMessageBox()
    message.setText("Success!")
    message.exec_()


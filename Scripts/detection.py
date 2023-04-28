import math, random, os, datetime, json
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from tqdm import tqdm
from Scripts.utils import PointsSet
from PyQt5.QtWidgets import *

def extract_point_sets(df):
    data = []
    for index, row in df.iterrows():
        
        existing_ps = next(filter(lambda ps: ps.circ_no==row.circ_no if not math.isnan(row.circ_no) else ps.circ_no is None, data), None)
        if existing_ps is not None:
            existing_ps.add_point((row.point_x, row.point_y))
        else:
            data.append(PointsSet.parse([(row.point_x, row.point_y)], (row.center_x, row.center_y), row.radius, row.circ_no))

    points = []
    for points_set in data:
        points.extend(points_set.points)
    
    rings = sorted(list(filter(lambda x : not x.is_noise() , data)), key=lambda x: x.circ_no)
    noise = [ps.points for ps in list(filter(lambda x : x.is_noise() , data))]
    return (points, rings, noise)

## ALGORITHM

def alg_iteration(centers, points, m):
    # m is the fuzziness parameter, usually set to 2
    fuzziness = 2 / (m - 1)
    n_clusters = len(centers)
    n_points = len(points)
    membership_matrix = np.zeros((n_points, n_clusters))
    
    # compute the membership degree of each point to each cluster
    for i in range(n_points):
        for j in range(n_clusters):
            distance = np.sqrt((centers[j][0]-points[i][0])**2 + (centers[j][1]-points[i][1])**2)
            membership_matrix[i][j] = 1 / ((sum([(distance/np.sqrt((centers[k][0]-points[i][0])**2 + (centers[k][1]-points[i][1])**2))**(fuzziness) for k in range(n_clusters)])))
    
    # update the cluster centroids based on the membership degrees
    new_centers = [(0,0) for _ in range(n_clusters)]
    for j in range(n_clusters):
        new_centers[j] = tuple(np.average(points, axis=0, weights=membership_matrix[:, j]))
    return new_centers, membership_matrix

def alg_perform(k, points):
    old_centers = [(random.uniform(0.0, 100.0), random.uniform(0.0, 100.0)) for _ in range(k)]
    new_centers, membership_matrix = alg_iteration(old_centers, points, random.uniform(*FUZZINESS_RANGE))
    count = 1
    while(count<=MAX_ITERATIONS and old_centers!=new_centers):
        old_centers = new_centers
        new_centers, membership_matrix = alg_iteration(old_centers, points, random.uniform(*FUZZINESS_RANGE))
        count +=1
    return new_centers, membership_matrix

def estimate_radii(center, points, center_membership_matrix):
    member_weights = center_membership_matrix[center_membership_matrix >= MEMBERSHIP_THRESSHOLD]
    member_points = np.asarray(points)[center_membership_matrix >= MEMBERSHIP_THRESSHOLD]
    return np.average([np.sqrt((center[0]-p[0])**2 + (center[1]-p[1])**2) for p in member_points], weights=member_weights)

## ERROR

def find_pairs(centers, rings_centers):
    cost_matrix = np.zeros((len(centers), len(rings_centers)))
    
    for i in range(len(centers)):
        for j in range(len(rings_centers)):
            cost_matrix[i][j] = np.sqrt((centers[i][0] - rings_centers[j][0])**2 + (centers[i][1] - rings_centers[j][1])**2)
    center_ind, ring_ind = linear_sum_assignment(cost_matrix)

    return [[int(center_ind[i]), int(ring_ind[i])] for i in range(len(center_ind))]

def get_centers_error(pairs, centers, rings):
    avg_offset = np.mean([np.sqrt((centers[p[0]][0] - rings[p[1]].center[0])**2 + (centers[p[0]][1] - rings[p[1]].center[1])**2) for p in pairs])
    return avg_offset / np.sqrt(2000)

def get_radii_error(pairs, centers, rings, points, membership_matrix):
    return np.mean([abs(estimate_radii(centers[p[0]], points, membership_matrix[:, p[0]]) - rings[p[1]].radius)/rings[p[1]].radius for p in pairs])

def get_error(centers_error, radii_error):
    return centers_error * 0.9 + radii_error * 0.1

def get_total_error(centers, rings, points, membership_matrix):
    pairs = find_pairs(centers, [r.center for r in rings])
    return get_centers_error(pairs, centers, rings)*0.9 + get_radii_error(pairs, centers, rings, points, membership_matrix)*0.1

## MAIN LOOP

def detect(dataset_location, output_dir, fuzziness_range, attempts, max_iter, membeership_thress):
    global DATASESET_LOCATION, OUTPUT_DIRECTORY, FUZZINESS_RANGE, ATTEMPTS, MAX_ITERATIONS, MEMBERSHIP_THRESSHOLD
    DATASET_LOCATION = dataset_location
    OUTPUT_DIRECTORY = output_dir
    FUZZINESS_RANGE = (float(fuzziness_range.split(",")[0]), float(fuzziness_range.split(",")[1]))
    ATTEMPTS = int(attempts)
    MAX_ITERATIONS = int(max_iter)
    MEMBERSHIP_THRESSHOLD = float(membeership_thress)
    
    results = {}

    message = QMessageBox()
    message.setText("Progress can be seen in terminal output")
    message.exec_()

    for set_type in ["clean", "extends", "collides"]:
        
        results[set_type] = {}

        for filename in tqdm(os.listdir(f"{DATASET_LOCATION}/{set_type}"), desc=f"Predicting clouds of type {set_type}", leave=True):
            if filename.endswith(".csv"): 
                df = pd.read_csv(f"{DATASET_LOCATION}/{set_type}/{filename}",header=0, sep=";")
                points, rings, noise = extract_point_sets(df)
                predicted_centers, membership_matrix = min([alg_perform(len(rings), points) for _ in tqdm(range(ATTEMPTS), desc=f"Predicting {filename}", leave=False)], key=lambda c: get_total_error(c[0], rings, points, c[1]))

                pairs = find_pairs(predicted_centers, [r.center for r in rings])
                centers_error = get_centers_error(pairs, predicted_centers, rings)
                radii_error = get_radii_error(pairs, predicted_centers, rings, points, membership_matrix)
                results[set_type][filename] =   {
                                                "circs_num": len(rings),
                                                "circunferences":
                                                {
                                                    f"{r.circ_no}":
                                                    {
                                                        "points": r.points,
                                                        "center": r.center,
                                                        "radius": r.radius
                                                    }
                                                    for r in rings
                                                },
                                                "noise": noise,
                                                "pairs": pairs, 
                                                "predicted_centers": predicted_centers, 
                                                "predicted_radii": [estimate_radii(predicted_centers[p[0]], points, membership_matrix[:, p[0]]) for p in pairs],
                                                "membership_matrix" : membership_matrix.tolist(),
                                                "centers_error": centers_error,
                                                "radii_error": radii_error,
                                                "tot_error": get_error(centers_error, radii_error)
                                                }

            #pbar_set_type.setValue(np.round(((i+1)/len(os.listdir(f"{DATASET_LOCATION}/{set_type}"))*100)))



    current_moment = datetime.datetime.now()
    if not os.path.exists(f"{OUTPUT_DIRECTORY}"):
                os.makedirs(f"{OUTPUT_DIRECTORY}")
    with open(f"{OUTPUT_DIRECTORY}/results_{current_moment}.json", 'w') as outfile:
        json.dump(results, outfile)

    message.destroy()

    message = QMessageBox()
    message.setText(f"Success!\nResults saved in {OUTPUT_DIRECTORY}/results_{current_moment}.json")
    message.exec_()
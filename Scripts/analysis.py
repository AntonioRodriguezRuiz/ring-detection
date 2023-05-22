import json
import numpy as np
from tkinter import *
from tktooltip import ToolTip
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

# Calculate stats

def get_extension_perc_stats(results):
    extension_perc_stats = {"over": {}, "under": {}}

    avg_error_over_25_ls = []
    avg_center_error_over_25_ls = []
    avg_radius_error_over_25_ls = []

    avg_error_under_25_ls = []
    avg_center_error_under_25_ls = []
    avg_radius_error_under_25_ls = []

    for filename in results["extends"].keys():
        if any(results["extends"][filename]["circunferences"][str(circ_no+1)]["center"][0] < results["extends"][filename]["circunferences"][str(circ_no+1)]["radius"]/2 or
               100 - results["extends"][filename]["circunferences"][str(circ_no+1)]["center"][0] < results["extends"][filename]["circunferences"][str(circ_no+1)]["radius"]/2  or
               results["extends"][filename]["circunferences"][str(circ_no+1)]["center"][1] < results["extends"][filename]["circunferences"][str(circ_no+1)]["radius"]/2  or
               100 -results["extends"][filename]["circunferences"][str(circ_no+1)]["center"][1] < results["extends"][filename]["circunferences"][str(circ_no+1)]["radius"]/2 
                for circ_no in range(results["extends"][filename]["circs_num"])):
            avg_error_over_25_ls.append(results["extends"][filename]["tot_error"])
            avg_center_error_over_25_ls.append(results["extends"][filename]["centers_error"])
            avg_radius_error_over_25_ls.append(results["extends"][filename]["radii_error"])

        else:
            avg_error_under_25_ls.append(results["extends"][filename]["tot_error"])
            avg_center_error_under_25_ls.append(results["extends"][filename]["centers_error"])
            avg_radius_error_under_25_ls.append(results["extends"][filename]["radii_error"])
            
    extension_perc_stats["over"]["avg_error_over_25"] = np.mean(avg_error_over_25_ls)
    extension_perc_stats["over"]["avg_center_error_over_25"] = np.mean(avg_center_error_over_25_ls)
    extension_perc_stats["over"]["avg_radius_error_over_25"] = np.mean(avg_radius_error_over_25_ls)

    extension_perc_stats["under"]["avg_error_under_25"] = np.mean(avg_error_under_25_ls)
    extension_perc_stats["under"]["avg_center_error_under_25"] = np.mean(avg_center_error_under_25_ls)
    extension_perc_stats["under"]["avg_radius_error_under_25"] = np.mean(avg_radius_error_under_25_ls)

    return extension_perc_stats

def get_collission_type_stats(results):
    collission_type_stats = {"overlaps": {}, "contains": {}}

    avg_error_overlaps_ls = []
    avg_center_error_overlaps_ls = []
    avg_radius_error_overlaps_ls = []

    avg_error_contains_ls = []
    avg_center_error_contains_ls = []
    avg_radius_error_contains_ls = []

    for filename in results["collides"].keys():
        circunferences = results["collides"][filename]["circunferences"]
        if any(any(np.sqrt((circunferences[str(i+1)]["center"][0]-circunferences[str(j+1)]["center"][0])**2 + (circunferences[str(i+1)]["center"][1]-circunferences[str(j+1)]["center"][1])**2) < max(circunferences[str(i+1)]["radius"], circunferences[str(j+1)]["radius"]) 
                   for i in range(j+1, len(circunferences))) for j in range(len(circunferences))):
            avg_error_contains_ls.append(results["collides"][filename]["tot_error"])
            avg_center_error_contains_ls.append(results["collides"][filename]["centers_error"])
            avg_radius_error_contains_ls.append(results["collides"][filename]["radii_error"])

        else:
            avg_error_overlaps_ls.append(results["collides"][filename]["tot_error"])
            avg_center_error_overlaps_ls.append(results["collides"][filename]["centers_error"])
            avg_radius_error_overlaps_ls.append(results["collides"][filename]["radii_error"])
            
    collission_type_stats["overlaps"]["avg_error_overlaps"] = np.mean(avg_error_overlaps_ls)
    collission_type_stats["overlaps"]["avg_center_error_overlaps"] = np.mean(avg_center_error_overlaps_ls)
    collission_type_stats["overlaps"]["avg_radius_error_overlaps"] = np.mean(avg_radius_error_overlaps_ls)

    collission_type_stats["contains"]["avg_error_contains"] = np.mean(avg_error_contains_ls)
    collission_type_stats["contains"]["avg_center_error_contains"] = np.mean(avg_center_error_contains_ls)
    collission_type_stats["contains"]["avg_radius_error_contains"] = np.mean(avg_radius_error_contains_ls)

    return collission_type_stats

def extract_stats(results):
    stats = {}
    tot_avg_error_ls = []
    tot_avg_center_error_ls = []
    tot_avg_radius_error_ls = []

    for set_type in results.keys():
        stats[set_type] = {}
        avg_error_ls = []
        avg_center_error_ls = []
        avg_radius_error_ls = []

        match set_type:
            case "extends": stats[set_type]["25%"] = get_extension_perc_stats(results)
            case "collides": stats[set_type]["collission_type"] = get_collission_type_stats(results)

        for filename in results[set_type].keys():
            tot_avg_error_ls.append(results[set_type][filename]["tot_error"])
            tot_avg_center_error_ls.append(results[set_type][filename]["centers_error"])
            tot_avg_radius_error_ls.append(results[set_type][filename]["radii_error"])

            avg_error_ls.append(results[set_type][filename]["tot_error"])
            avg_center_error_ls.append(results[set_type][filename]["centers_error"])
            avg_radius_error_ls.append(results[set_type][filename]["radii_error"])

        stats[set_type]["avg_error"] = np.mean(avg_error_ls)
        stats[set_type]["avg_center_error"] = np.mean(avg_center_error_ls)
        stats[set_type]["avg_radii_error"] = np.mean(avg_radius_error_ls)

    stats["tot_avg_error"] = np.mean(tot_avg_error_ls)
    stats["tot_avg_center_error"] = np.mean(tot_avg_center_error_ls)
    stats["tot_avg_radii_error"] = np.mean(tot_avg_radius_error_ls)
    
    return stats

# Visualize Stats

def create_tables(stats):

    visualize_window = Tk()
    visualize_window.resizable(False, False)

    # General table
    fig = Figure(figsize=(9, 8), dpi=100)
    gs1 = fig.add_gridspec(nrows=13, ncols=1)

    ax1 = fig.add_subplot(gs1[0:4, 0:1])
    ax2 = fig.add_subplot(gs1[5:9, 0:1])
    ax3 = fig.add_subplot(gs1[10:13, 0:1])

    rows = 3   # Type of average
    cols = 5    # Type of set

    ax1.set_ylim(-0.1, .8 + .0)
    ax1.set_xlim(-0.25, cols + .9)

    data = [    
        {'title':"Total Accuracy", 'avg_clean_error': str(np.around((1-stats["clean"]["avg_error"])*100, decimals=2))+"%", 'avg_extends_error': str(np.around((1-stats["extends"]["avg_error"])*100, decimals=2))+"%", 'avg_collides_error': str(np.around((1-stats["collides"]["avg_error"])*100, decimals=2))+"%", 'tot_avg_error': str(np.around((1-stats["tot_avg_error"])*100, decimals=2))+"%"},
        {'title':"Radius Accuracy", 'avg_clean_error': str(np.around((1-stats["clean"]["avg_radii_error"])*100, decimals=2))+"%", 'avg_extends_error': str(np.around((1-stats["extends"]["avg_radii_error"])*100, decimals=2))+"%", 'avg_collides_error': str(np.around((1-stats["collides"]["avg_radii_error"])*100, decimals=2))+"%", 'tot_avg_error': str(np.around((1-stats["tot_avg_radii_error"])*100, decimals=2))+"%"},
        {'title':"Center Accuracy", 'avg_clean_error': str(np.around((1-stats["clean"]["avg_center_error"])*100, decimals=2))+"%", 'avg_extends_error': str(np.around((1-stats["extends"]["avg_center_error"])*100, decimals=2))+"%", 'avg_collides_error': str(np.around((1-stats["collides"]["avg_center_error"])*100, decimals=2))+"%", 'tot_avg_error': str(np.around((1-stats["tot_avg_center_error"])*100, decimals=2))+"%"}
    ]

    for row in range(rows):
        d = data[row]

        ax1.text(x=1.25, y=row/4, s=d['title'], va='center', ha='right', weight='bold')
        ax1.text(x=2.45, y=row/4, s=d['avg_clean_error'], va='center', ha='right')
        ax1.text(x=3.65, y=row/4, s=d['avg_extends_error'], va='center', ha='right')
        ax1.text(x=4.75, y=row/4, s=d['avg_collides_error'], va='center', ha='right')
        ax1.text(x=5.85, y=row/4, s=d['tot_avg_error'], va='center', ha='right')

        ax1.text(1.25, 0.7, 'Error Type', weight='bold', va='center', ha='right')
        ax1.text(2.45, 0.7, 'Clean Sets', weight='bold', va='center', ha='right')
        ax1.text(3.65, 0.7, 'Extend Sets', weight='bold', va='center', ha='right')
        ax1.text(4.75, 0.7, 'Collide Sets', weight='bold', va='center', ha='right')
        ax1.text(5.85, 0.7, 'Total', weight='bold', va='center', ha='right')
    for row in range(rows):
        ax1.plot(
            [cols/3 -.25, cols/3 - .25],
            [row/3 -.25, row/3 - .25]
        )
    ax1.plot([-1, cols + 1], [0.65, 0.65], lw='.5', c='black')
    ax1.axis('off')
    ax1.set_title(
        'General Accuracy',
        loc='left',
        fontsize=18,
        weight='bold'
    )

    #Extends table

    rows = 3   # Type of average
    cols = 4    # Type of set

    ax2.set_ylim(-0.1, .8 + .0)
    ax2.set_xlim(0.1, cols + .9)

    data = [    
        {'title':"Total Accuracy", 'avg_<25_error': str(np.around((1-stats["extends"]["25%"]["under"]["avg_error_under_25"])*100, decimals=2))+"%", 'avg_>25_error': str(np.around((1-stats["extends"]["25%"]["over"]["avg_error_over_25"])*100, decimals=2))+"%", 'tot_avg_error': str(np.around((1-stats["extends"]["avg_error"])*100, decimals=2))+"%"},
        {'title':"Radius Accuracy", 'avg_<25_error': str(np.around((1-stats["extends"]["25%"]["under"]["avg_radius_error_under_25"])*100, decimals=2))+"%", 'avg_>25_error': str(np.around((1-stats["extends"]["25%"]["over"]["avg_radius_error_over_25"])*100, decimals=2))+"%", 'tot_avg_error': str(np.around((1-stats["extends"]["avg_radii_error"])*100, decimals=2))+"%"},
        {'title':"Center Accuracy", 'avg_<25_error': str(np.around((1-stats["extends"]["25%"]["under"]["avg_center_error_under_25"])*100, decimals=2))+"%", 'avg_>25_error': str(np.around((1-stats["extends"]["25%"]["over"]["avg_center_error_over_25"])*100, decimals=2))+"%", 'tot_avg_error': str(np.around((1-stats["extends"]["avg_center_error"])*100, decimals=2))+"%"}
    ]

    for row in range(rows):
        d = data[row]

        ax2.text(x=1.25, y=row/4, s=d['title'], va='center', ha='right', weight='bold')
        ax2.text(x=2.45, y=row/4, s=d['avg_<25_error'], va='center', ha='right')
        ax2.text(x=3.65, y=row/4, s=d['avg_>25_error'], va='center', ha='right')
        ax2.text(x=4.75, y=row/4, s=d['tot_avg_error'], va='center', ha='right')

        ax2.text(1.25, 0.7, 'Error Type', weight='bold', va='center', ha='right')
        ax2.text(2.45, 0.7, "<25% out Sets", weight='bold', va='center', ha='right')
        ax2.text(3.65, 0.7, ">25% out Sets", weight='bold', va='center', ha='right')
        ax2.text(4.75, 0.7, 'Total', weight='bold', va='center', ha='right')
    for row in range(rows):
        ax2.plot(
            [cols/3 -.25, cols/3 - .25],
            [row/3 -.25, row/3 - .25]
        )
    ax2.plot([-1, cols + 1], [0.65, 0.65], lw='.5', c='black')
    ax2.axis('off')
    ax2.set_title(
        'Accuracy based on Clippling percentage',
        loc='left',
        fontsize=18,
        weight='bold'
    )

    # Collides table

    rows = 3   # Type of average
    cols = 4    # Type of set

    ax3.set_ylim(-0.1, .8 + .0)
    ax3.set_xlim(0.1, cols + .9)

    data = [    
        {'title':"Total Accuracy", 'avg_overlapping_error': str(np.around((1-stats["collides"]["collission_type"]["overlaps"]["avg_error_overlaps"])*100, decimals=2))+"%", 'avg_containing_error': str(np.around((1-stats["collides"]["collission_type"]["contains"]["avg_error_contains"])*100, decimals=2))+"%", 'tot_avg_error': str(np.around((1-stats["collides"]["avg_error"])*100, decimals=2))+"%"},
        {'title':"Radius Accuracy", 'avg_overlapping_error': str(np.around((1-stats["collides"]["collission_type"]["overlaps"]["avg_radius_error_overlaps"])*100, decimals=2))+"%", 'avg_containing_error': str(np.around((1-stats["collides"]["collission_type"]["contains"]["avg_radius_error_contains"])*100, decimals=2))+"%", 'tot_avg_error': str(np.around((1-stats["collides"]["avg_radii_error"])*100, decimals=2))+"%"},
        {'title':"Center Accuracy", 'avg_overlapping_error': str(np.around((1-stats["collides"]["collission_type"]["overlaps"]["avg_center_error_overlaps"])*100, decimals=2))+"%", 'avg_containing_error': str(np.around((1-stats["collides"]["collission_type"]["contains"]["avg_center_error_contains"])*100, decimals=2))+"%", 'tot_avg_error': str(np.around((1-stats["collides"]["avg_center_error"])*100, decimals=2))+"%"}
    ]

    for row in range(rows):
        d = data[row]

        ax3.text(x=1.25, y=row/4, s=d['title'], va='center', ha='right', weight='bold')
        ax3.text(x=2.45, y=row/4, s=d['avg_overlapping_error'], va='center', ha='right')
        ax3.text(x=3.65, y=row/4, s=d['avg_containing_error'], va='center', ha='right')
        ax3.text(x=4.75, y=row/4, s=d['tot_avg_error'], va='center', ha='right')

        ax3.text(1.25, 0.7, 'Error Type', weight='bold', va='center', ha='right')
        ax3.text(2.45, 0.7, "Overlapping", weight='bold', va='center', ha='right')
        ax3.text(3.65, 0.7, "Containing", weight='bold', va='center', ha='right')
        ax3.text(4.75, 0.7, 'Total', weight='bold', va='center', ha='right')
    for row in range(rows):
        ax3.plot(
            [cols/3 -.25, cols/3 - .25],
            [row/3 -.25, row/3 - .25]
        )
    ax3.plot([-1, cols + 1], [0.65, 0.65], lw='.5', c='black')
    ax3.axis('off')
    ax3.set_title(
        'Accuracy based on Collission type',
        loc='left',
        fontsize=18,
        weight='bold'
    )

    canvas = FigureCanvasTkAgg(fig, master=visualize_window)
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas,
                                visualize_window)
    toolbar.update()

    # placing the toolbar on the Tkinter window
    canvas.get_tk_widget().pack()
    visualize_window.mainloop()

    

# Main loop

def show_accuracy(results_path):
    if not os.path.isfile(f"{results_path}"):
        message = QMessageBox()
        message.setText(f"The provided file does not exist:\n{results_path}")
        message.exec_()
        return None
    f = open(f"{results_path}")
    results = json.load(f)
    stats = extract_stats(results)
    create_tables(stats)
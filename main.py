import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from Scripts.generator import * 
from Scripts.detection import *
from Scripts.visualize_dataset import *
from Scripts.visualize_results import *
from Scripts.analysis import *

class ClusteringRingsGUI(QMainWindow):
    def __init__(self):
        super(ClusteringRingsGUI, self).__init__()
        uic.loadUi("clustering_rings.ui", self)
        self.setFixedSize(self.size())

        self.generate_button.clicked.connect(lambda: generate(self.num_circs_input.text(), 
                                                              self.num_instances_input.text(),
                                                              self.randomness_input.text(),
                                                              self.range_radius_input.text(),
                                                              self.range_points_input.text(),
                                                              self.noise_ratio_input.text(),
                                                              self.dataset_input_generation.text()))

        self.detect_button.clicked.connect(lambda: detect(self.dataset_input_detection.text(), 
                                                            self.results_input_detection.text(),
                                                            self.fuzziness_input.text(),
                                                            self.attempts_input.text(),
                                                            self.max_iter_input.text(),
                                                            self.mem_thress_input.text()))
        
        self.vis_dataset_button.clicked.connect(lambda: init_vis(self.dataset_input_visuals.text()))
        self.vis_results_button.clicked.connect(lambda: init_res_vis(self.results_input_visuals.text()))
        self.stats_results_button.clicked.connect(lambda: show_accuracy(self.results_input_visuals.text()))

if __name__=="__main__":
    app = QApplication(sys.argv)
    main_window = ClusteringRingsGUI()
    main_window.show()
    app.exec_()
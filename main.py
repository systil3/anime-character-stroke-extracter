import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
import cv2
import numpy as np
import filters

form_class = uic.loadUiType("program.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.LoadImgButton.clicked.connect(self.open_file_from_path)
        self.inputPixmap = QPixmap()
        self.inputImg.setPixmap(self.inputPixmap)
        self.outputPixmap = QPixmap()
        self.outputImg.setPixmap(self.outputPixmap)
        self.file_loc = ""

        self.sobelRatioSlider.setRange(0,100)
        self.sobelRatioSlider.setSingleStep(1)
        self.lapRatioSlider.setRange(0,100)
        self.lapRatioSlider.setSingleStep(1)
        self.cannyRatioSlider.setRange(0,100)
        self.cannyRatioSlider.setSingleStep(1)
        self.gateSlider.setRange(0,255)
        self.gateSlider.setSingleStep(1)

        self.gateApplied = False
        self.gateCheckBox.stateChanged.connect(self.change_gate_apply_state)

        self.generateButton.clicked.connect(self.apply_filter)

    def open_file_from_path(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')
        self.file_loc = str(fname[0])
        input_img_matrix = cv2.imread(self.file_loc, 0)
        input_img_matrix = cv2.cvtColor(input_img_matrix, cv2.COLOR_BGR2RGB)
        input_img_matrix = cv2.resize(input_img_matrix, dsize=(400, 640))
        print(input_img_matrix.shape)
        qImg = QImage(input_img_matrix.data, input_img_matrix.shape[1],
                      input_img_matrix.shape[0], 3 * input_img_matrix.shape[1], QImage.Format_RGB888).rgbSwapped()
        self.inputImg.setPixmap(QPixmap(qImg))

        '''if self.file_loc:
            self.inputPixmap = self.inputPixmap.scaledToWidth(600)
            self.inputPixmap.load(fname)'''

    def change_gate_apply_state(self):
        self.gateApplied = not self.gateApplied

    def apply_filter(self):
        if self.file_loc != "":
            sobelw = self.sobelRatioSlider.value() / 100
            lapw = self.lapRatioSlider.value() / 100
            cannyw = self.cannyRatioSlider.value() / 100
            filtered = filters.apply_filter(self.file_loc, sobelw, lapw, cannyw)

            if self.gateApplied:
                thresh = self.gateSlider.value()
                filtered = filters.apply_gate(filtered, thresh)

            file_extension = self.file_loc.split(".")[1]
            print(filtered.shape)
            cv2.imwrite(self.file_loc + '_filtered.' + file_extension, filtered)

            filtered_to_show = cv2.resize(filtered, dsize=(400, 640))
            qImg = QImage(filtered_to_show.data, filtered_to_show.shape[1],
                          filtered_to_show.shape[0], 3 * filtered_to_show.shape[1])
            self.outputImg.setPixmap(QPixmap(qImg))

    def closeEvent(self, event):
        self.deleteLater()

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
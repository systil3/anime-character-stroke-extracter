import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
import cv2
import numpy as np
import filters
import qimage2ndarray

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
        self.denoiseSlider.setRange(0,30)
        self.denoiseSlider.setSingleStep(1)

        self.gateApplied = False
        self.gateCheckBox.stateChanged.connect(self.change_gate_apply_state)
        self.denoiseApplied = False
        self.denoiseCheckBox.stateChanged.connect(self.change_denoise_apply_state)

        self.generateButton.clicked.connect(self.apply_filter)
        self.saveImageButton.clicked.connect(self.save_image)

    def open_file_from_path(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')
        self.file_loc = str(fname[0])
        input_to_show = cv2.imread(self.file_loc)
        height, width, channel = map(int, input_to_show.shape)

        #normalize
        ratio1 = 331 / height
        ratio2 = 471 / width
        ratio = min(ratio1, ratio2)
        print(ratio)
        qImg = qimage2ndarray.array2qimage(cv2.resize(input_to_show,
            dsize=(471,331)), normalize=False).rgbSwapped()
        self.inputImg.setPixmap(QPixmap(qImg))

        '''if self.file_loc:
            self.inputPixmap = self.inputPixmap.scaledToWidth(600)
            self.inputPixmap.load(fname)'''

    def change_gate_apply_state(self):
        self.gateApplied = not self.gateApplied

    def change_denoise_apply_state(self):
        self.denoiseApplied= not self.denoiseApplied

    def apply_filter(self):
        if self.file_loc != "":
            sobelw = self.sobelRatioSlider.value() / 100
            lapw = self.lapRatioSlider.value() / 100
            cannyw = self.cannyRatioSlider.value() / 100
            filtered = filters.apply_filter(self.file_loc, sobelw, lapw, cannyw)

            if self.gateApplied:
                thresh = self.gateSlider.value()
                filtered = filters.apply_gate(filtered, thresh)
            if self.denoiseApplied:
                strength = self.denoiseSlider.value()
                print("---")
                filtered = filters.apply_denoise(filtered, strength)
            print(filtered.shape)

            filtered_to_show = cv2.resize(filtered, dsize=(511, 461))
            qImg = qimage2ndarray.array2qimage(filtered_to_show, normalize=False)
            self.outputImg.setPixmap(QPixmap(qImg))
            self.filtered = filtered
            del filtered

    def save_image(self):
        file_name, file_extension = self.file_loc.split(".")
        cv2.imwrite(file_name + '_filtered.' + file_extension, self.filtered)

    def closeEvent(self, event):
        self.deleteLater()

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
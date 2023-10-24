import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFrame, QColorDialog
from PyQt5.QtGui import QColor
from copy import deepcopy
import cv2
import numpy as np
import filters
import qimage2ndarray

form_class = uic.loadUiType("program.ui")[0]
def apply_filter(imgpath, sobelw, cannyw, lapw):
    img = cv2.imread(imgpath, 0).astype(np.uint8)


    dst1_sobel = cv2.Sobel(img, ddepth=-1,
                           dx=1, dy=1,
                           borderType=cv2.BORDER_DEFAULT)
    dst1_canny = cv2.Canny(img, threshold1=100, threshold2=255)
    dst1_lap = cv2.Laplacian(img, ksize=3, ddepth=-1, borderType=0)

    return dst1_sobel * sobelw + dst1_canny * cannyw + dst1_lap * lapw

def apply_gate(target, thresh):
    target[target<thresh] = 0
    return target

def apply_denoise(target, strength, thresh):

    res = cv2.fastNlMeansDenoising(target, target, strength, 5, 21)
    print("---")
    ker_sharpen = np.array([
        [1, -2, 1],
        [-2, 4, -2],
        [1, -2, 1]])
    #res = cv2.filter2D(target, -1, ker_sharpen)
    res[res<thresh] = 0
    return res

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
        self.denoiseSlider.setRange(0,60)
        self.denoiseSlider.setSingleStep(1)

        self.gateApplied = False
        self.gateCheckBox.stateChanged.connect(self.change_gate_apply_state)
        self.denoiseApplied = False
        self.denoiseCheckBox.stateChanged.connect(self.change_denoise_apply_state)

        self.generateButton.clicked.connect(self.apply_filter)
        self.strokeColorButton.clicked.connect(self.show_color_dialog)
        self.strokeColor = QColor(255, 255, 255)
        self.strokeColorFrame.setStyleSheet(
            'QWidget { background-color: %s }' % self.strokeColor.name())
        self.saveImageButton.clicked.connect(self.save_image)

    def open_file_from_path(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')
        self.file_loc = str(fname[0])
        input_to_show = cv2.imread(self.file_loc).astype(np.uint8)
        height1, width1, channel1 = map(int, input_to_show.shape)

        #normalize
        ratio1 = 341 / height1
        ratio2 = 471 / width1
        ratioi = min(ratio1, ratio2)

        qImg = qimage2ndarray.array2qimage(cv2.resize(input_to_show,
            dsize=(int(width1*ratioi),int(height1*ratioi)))).rgbSwapped()
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

            #file_name, file_extension = self.file_loc.split(".")
            #cv2.imwrite(file_name + '_filtered.' + file_extension, filtered)

            if self.denoiseApplied:
                thresh = self.gateSlider.value()
                strength = self.denoiseSlider.value()
                filtered = filters.apply_denoise(filtered.astype(np.uint8), strength, thresh)

            height2, width2 = filtered.shape

            # normalize
            ratio3 = 519 / height2
            ratio4 = 569 / width2
            ratioo = min(ratio3, ratio4)
            print(ratioo)

            qImg = qimage2ndarray.array2qimage(cv2.resize(filtered,
                dsize=(int(width2*ratioo), int(height2*ratioo))).astype(np.uint8), normalize=False)
            self.outputImg.setPixmap(QPixmap(qImg))
            self.filtered = filtered
            del filtered

    def show_color_dialog(self):
        self.strokeColor = QColorDialog.getColor()
        print(self.strokeColor.name())

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
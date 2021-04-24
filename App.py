from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QMessageBox
from pyqtgraph import PlotWidget, PlotItem
from PyQt5.QtCore import QSettings
from autologging import logged, TRACE, traced
from numpy.fft import fft2, ifft2, fftfreq
from numpy.lib.type_check import imag
import numpy as np
import math
import cv2 as cv
import sys
import pandas as pd
import pyqtgraph as pg
import os
import logging


# Create and configure logger
LOG_FORMAT = "%(levelname)s:%(filename)s,%(lineno)d:%(name)s.%(funcName)s:%(message)s"
logging.basicConfig(filename="FTMixer.log",
                    level=TRACE,
                    format=LOG_FORMAT,
                    filemode='w')
logger = logging.getLogger()


@ traced
@ logged
class ImagesMixer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('FTMixer.ui', self)
        self.__log.info("initialized")

        
        # connecting buttons
        self.loadImgs = [self.Open_Img1, self.Open_Img2]

        self.loadImgs[0].triggered.connect(lambda: self.Open(0))
        self.loadImgs[1].triggered.connect(lambda: self.Open(1))
        self.loadImgs[1].setDisabled(True)

        self.displays = [self.fixedDisplay_1, self.fixedDisplay_2, self.selectedDisplay_1,
                         self.selectedDisplay_2, self.output1_Display, self.output2_Display]

        for i in range(len(self.displays)):
            self.displays[i].ui.histogram.hide()
            self.displays[i].ui.roiBtn.hide()
            self.displays[i].ui.menuBtn.hide()
            self.displays[i].ui.roiPlot.hide()

    def Open(self, index):
        selected_image = QtGui.QFileDialog.getOpenFileName(
            self, 'Select image', os.getenv('HOME'), "Images (*.png *.xpm *.jpg)")

        self.path = selected_image[0]
        self.imgByte = cv.cvtColor(cv.imread(self.path), cv.COLOR_BGR2GRAY)
        # shape method return tuple of number of rows, columns, and channels (if the image is color)
        self.shape = self.imgByte.shape
        #self.image = self.imageModel(self.path)

        if index == 0:
            self.Img1_Size = self.shape
            self.loading(index)
            self.loadImgs[1].setDisabled(False)

        elif index != 0:
            if self.shape != self.Img1_Size:
                #print('Error the images are not the same size')
                self.msg.setWindowTitle("Error in Image Size")
                self.msg.setText("The 2 images must have the same size")
                self.msg.setIcon(QMessageBox.Warning)
                x = self.msg.exec_()
                return
            else:
                self.loading(index)

    def loading(self, index):
        self.displays[index].show()
        self.displays[index].setImage(self.imgByte.T)
        
        
        

    def get_fft(self, data_array):
        #Fourier transform of given data array
        self.fft_data = fft2(data_array)
        #separate the magnitude
        self.fft_data_mag = np.abs(self.fft_data)
        #separate the phase
        self.fft_data_phase = np.angle(self.fft_data)
        #separate the real components
        self.fft_data_real = np.real(self.fft_data)
        #separate the imaginary components
        self.fft_data_imag = np.imag(self.fft_data)
        # The Discrete Fourier Transform sample frequencies
        sample_freq = fftfreq(self.fft_data.size)
        #list of lists holds all calculated values
        FT_list = [self.fft_data_mag, self.fft_data_phase,
                self.fft_data_real, self.fft_data_imag, sample_freq]
        #return the list of lists
        return FT_list

    def get_ifft (self, data_array):
        return ifft2(data_array)

      
   
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName("CUFE")
    app.setOrganizationDomain("CUFEDomain")
    app.setApplicationName("Fourier Transform Mixer")
    application = ImagesMixer()
    application.show()
    app.exec_()


if __name__ == "__main__":
    main()

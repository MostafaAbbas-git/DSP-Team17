from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QMessageBox
from pyqtgraph import PlotWidget, PlotItem
from PyQt5.QtCore import QSettings
from autologging import logged, TRACE, traced
from numpy.fft import fft2, ifft2, fftfreq
import numpy as np
import cv2 as cv
import sys
import os
import logging


# Create and configure logger
LOG_FORMAT = "%(levelname)s:%(filename)s,%(lineno)d:%(name)s.%(funcName)s:%(message)s"
logging.basicConfig(filename="ImagesMixer.log",
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
        self.settings = QSettings("FT Images Mixer", 'App')

        try:
            # Saving the last position and size of the application window
            self.resize(self.settings.value('window size'))
            self.move(self.settings.value('window position'))
        except:
            pass

        # Creating warning msg for image-2 size
        self.size_warning_msg = QMessageBox()
        self.size_warning_msg.setWindowTitle("Error in Image Size")
        self.size_warning_msg.setText("The 2 images must have the same size!")
        self.size_warning_msg.setIcon(QMessageBox.Warning)

        self.number_warning_msg = QMessageBox()
        self.number_warning_msg.setWindowTitle("Error in selected Images ")
        self.number_warning_msg.setText("You must select two images at once!")
        self.number_warning_msg.setIcon(QMessageBox.Warning)

        self.loaded_imgs = [0, 0]
        self.displays = [self.fixedDisplay_1, self.fixedDisplay_2, self.selectedDisplay_1,
                         self.selectedDisplay_2, self.output1_Display, self.output2_Display]

        ## Connecting Buttons ##

        self.actionClear.triggered.connect(lambda: self.clearall())
        self.actionNewWindow.triggered.connect(lambda: self.make_new_window())
        self.actionOpenImgs.triggered.connect(lambda: self.browse_imgs())

        # Adjusting QtPlotWidgets to only show images
        for i in range(len(self.displays)):
            self.displays[i].ui.histogram.hide()
            self.displays[i].ui.roiBtn.hide()
            self.displays[i].ui.menuBtn.hide()
            self.displays[i].ui.roiPlot.hide()

    # Related to QSettings
    def closeEvent(self, event):
        self.settings.setValue('window size', self.size())
        self.settings.setValue('window position', self.pos())

    # Creating new window by calling the main class
    def make_new_window(self):
        self.new_win = ImagesMixer()
        self.new_win.show()
        print("self.arrays_list: ", self.arrays_list)

    def browse_imgs(self):
        selected_image = QtGui.QFileDialog.getOpenFileNames(
            self, 'Select image', os.getenv('HOME'), "Images (*.png *.xpm *.jpg)")
        if len(selected_image[0]) != 2:
            # Showing number of images warning msg and return
            self.number_warning_msg.exec_()
            return self.browse_imgs()
        # Ignore RGB values; converting to greyscale images
        self.img1_data = cv.cvtColor(
            cv.imread(selected_image[0][0]), cv.COLOR_BGR2GRAY)
        self.img2_data = cv.cvtColor(
            cv.imread(selected_image[0][1]), cv.COLOR_BGR2GRAY)
        self.loaded_imgs = [self.img1_data, self.img2_data]
        if self.img1_data.shape != self.img2_data.shape:
            # Showing size warning msg and return
            self.size_warning_msg.exec_()
            return self.browse_imgs()
        else:
            #Plotting loop
            for i in range(2):
                self.plotting(self.loaded_imgs[i], self.displays[i])

    def plotting(self, data, viewer):
        viewer.setImage(data.T)
        viewer.show()

    def get_fft(self, data_array):
        # Fourier transform of given data array
        self.fft_data = fft2(data_array)
        # separate the magnitude
        self.fft_data_mag = np.abs(self.fft_data)
        # separate the phase
        self.fft_data_phase = np.angle(self.fft_data)
        # separate the real components
        self.fft_data_real = np.real(self.fft_data)
        # separate the imaginary components
        self.fft_data_imag = np.imag(self.fft_data)
        # The Discrete Fourier Transform sample frequencies
        sample_freq = fftfreq(self.fft_data.size)
        # list of lists holds all calculated values
        FT_list = [self.fft_data_mag, self.fft_data_phase,
                   self.fft_data_real, self.fft_data_imag, sample_freq]
        # return the list of lists
        return FT_list

    def get_ifft(self, data_array):
        return ifft2(data_array)

# Fixed displays are excluded
    def clearall(self):
        for i in range(4):
            self.displays[i+2].clear()


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

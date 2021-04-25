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
import qimage2ndarray

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

        self.Comp1_Slider.valueChanged.connect(
            lambda: self.mixer_panel())  # Component #1 slider
        self.Comp2_Slider.valueChanged.connect(
            lambda: self.mixer_panel())  # Component #2 slider

        # Adjusting QtPlotWidgets to show images properly
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

    def browse_imgs(self):
        selected_image = QtGui.QFileDialog.getOpenFileNames(
            self, 'Select image', os.getenv('HOME'), "Images (*.png *.xpm *.jpg)")

        if len(selected_image[0]) != 2:
            # Showing number of images warning msg and return
            self.number_warning_msg.exec_()
            return self.browse_imgs()
        # Ignore RGB values; converting to greyscale images
        self.img1Byte = cv.cvtColor(
            cv.imread(selected_image[0][0]), cv.COLOR_BGR2GRAY)
        self.img2Byte = cv.cvtColor(
            cv.imread(selected_image[0][1]), cv.COLOR_BGR2GRAY)

        self.loaded_imgs = [self.img1Byte, self.img2Byte]
        if self.img1Byte.shape != self.img2Byte.shape:
            # Showing size warning msg and return
            self.size_warning_msg.exec_()
            return self.browse_imgs()
        else:
            ## Calculate and store all fourier components for each image at once to be used later##
            # self.image1_Allfft[0] -> fft Magnitude of img1
            # self.image1_Allfft[1] -> fft Phase of img1 .. and so on
            self.image1_Allfft = self.get_fft(self.loaded_imgs[0])
            self.image2_Allfft = self.get_fft(self.loaded_imgs[1])

            # Plotting loop
            for i in range(2):
                self.plotting(self.loaded_imgs[i], self.displays[i])

    def plotting(self, data, viewer):
        viewer.setImage(data.T)
        viewer.show()

    def mixer_panel(self):
        # index starts from 0 i.e.( 0 -> Output 1)
        if self.Output_menu.currentIndex() == 0:
            if self.Comp1_Menu.currentText() == 'Magnitude':
                # Set comboBox2Menu to Phase automatically
                self.Comp2_Menu.setCurrentText('Phase')
                self.slider1_value = (self.Comp1_Slider.value() / 100)
                self.slider2_value = (self.Comp2_Slider.value() / 100)

                self.magarr = self.slider_limiter(
                    self.image1_Allfft[0], self.slider1_value)
                self.phasearr = self.slider_limiter(
                    self.image1_Allfft[1], self.slider2_value)
                self.plotting(self.magarr, self.output1_Display)

    def slider_limiter(self, data, slidervalue):
        temparr = np.array(data)
        index = int((temparr.size/2) * slidervalue)
        temparr[0:2, index:temparr.size] = 0
        returned_array = ifft2(temparr)
        return returned_array

    def get_fft(self, data_array):
        # Fourier transform of given data array
        fft_data = fft2(data_array)
        # separate the magnitude
        fft_data_mag = np.abs(fft_data)
        # separate the phase
        fft_data_phase = np.angle(fft_data)
        # separate the real components
        fft_data_real = np.real(fft_data)
        # separate the imaginary components
        fft_data_imag = np.imag(fft_data)
        # The Discrete Fourier Transform sample frequencies
        sample_freq = fftfreq(fft_data.size)
        # list of lists holds all calculated values
        FFT_list = [fft_data_mag, fft_data_phase,
                    fft_data_real, fft_data_imag, sample_freq]
        # return the list of lists
        return FFT_list

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

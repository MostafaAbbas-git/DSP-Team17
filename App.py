from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSettings
from autologging import logged, TRACE, traced
from numpy.fft import fft2, ifft2, fftfreq, fftshift
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

        self.Comp1_Slider.setMinimum(0)
        self.Comp1_Slider.setMaximum(100)
        self.Comp2_Slider.setMinimum(0)
        self.Comp2_Slider.setMaximum(100)

        self.loaded_imgs = [0, 0]
        
        self.slider = [self.Comp1_Slider, self.Comp2_Slider]
        
        self.dropMenu = [self.displaySelection_Menu1, self.displaySelection_Menu2, self.Output_menu, 
                         self.Comp1_ImageMenu, self.Comp2_ImageMenu, self.Comp1_Menu, self.Comp2_Menu]
        
        self.displays = [self.fixedDisplay_1, self.fixedDisplay_2, self.selectedDisplay_1,
                         self.selectedDisplay_2, self.output1_Display, self.output2_Display]
        ## Connecting Buttons ##

        self.actionClear.triggered.connect(lambda: self.clearall())
        self.Close.triggered.connect(lambda: self.close())
        self.actionNewWindow.triggered.connect(lambda: self.make_new_window())
        self.actionOpenImgs.triggered.connect(lambda: self.browse_imgs())

        # connecting Combo boxes of the input displays
        self.displaySelection_Menu1.currentIndexChanged.connect(
            lambda: self.display_component(self.displaySelection_Menu1, self.displays[2], self.image1_Allfft[1]))
        self.displaySelection_Menu2.currentIndexChanged.connect(
            lambda: self.display_component(self.displaySelection_Menu2, self.displays[3], self.image2_Allfft))

        # connecting the Sliders
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
            self.image1_Allfft = self.get_fft(self.loaded_imgs[0])
            self.image2_Allfft = self.get_fft(self.loaded_imgs[1])


            # Plotting loop
            for i in range(2):
                self.plotting(self.loaded_imgs[i], self.displays[i])

    def plotting(self, data, viewer):
        viewer.clear()
    def display_component(self, menu, display, img_components):
        # get the index of the selected component from the combo box ,the comps start from index 1
        selected_option = menu.currentIndex()

        if selected_option == 0:
            display.clear()
        else:
            # get the required component from the fourier components list
            component = img_components[selected_option-1]
            self.plotting(component, display)

    def mixer_panel(self):
        # index starts from 0 i.e.( 0 -> Output 1)
        if self.Output_menu.currentIndex() == 0:
            if self.Comp1_Menu.currentText() == 'Magnitude':
                # Set comboBox2Menu to Phase automatically
                self.Comp2_Menu.setCurrentText('Phase')

                self.slider1_value = (self.Comp1_Slider.value() / 100)
                self.slider2_value = (self.Comp2_Slider.value() / 100)

                self.output_for_plot = self.phase_mag_slicer(
                    self.image1_Allfft[0], self.slider1_value, self.image2_Allfft[1], self.slider2_value)
                self.plotting(self.output_for_plot, self.output1_Display)

    ''' 
    Current issues:
    1- maybe slicing using 0 value isn't the correct method
    '''

    def phase_mag_slicer(self, mag_array, slider1value,  phase_array, slider2value):
        # mag_array is a list (of length 295) of lists (each of length 236)
        max_length = len(mag_array[0])  # = 236

        temp_mag_array = mag_array
        mag_index = int(max_length * slider1value)
        temp_mag_array[0:, mag_index:max_length] = 0

        temp_phase_array = phase_array
        phase_index = int(max_length * slider2value)
        temp_phase_array[0:, phase_index:max_length] = 0

        polar_multiply = np.multiply(
            temp_mag_array, np.exp(1j*temp_phase_array))

        returned_arr = np.real(ifft2(polar_multiply))
        returned_arr = np.abs(returned_arr)

        return returned_arr

    def get_fft(self, data_array):
        # Fourier transform of given data array
        fft_data = fft2(data_array)
        #shifting the array of data
        fft_data_shifted= np.fft.fftshift(fft_data)
        # separate the magnitude
        fft_data_mag = np.abs(fft_data)
        # get the magnitude spectrum
        fft_mag_spectrum = 20*np.log(np.abs(fft_data_shifted))
        # separate the phase
        fft_data_phase = np.angle(fft_data)
        # separate the real components
        fft_data_real = np.real(fft_data)
        # get the real spectrum 
        fft_real_spectrum = 20*np.log(np.real(fft_data_shifted))
        # separate the imaginary components
        fft_data_imag = np.imag(fft_data)
        # The Discrete Fourier Transform sample frequencies
        sample_freq = fftfreq(fft_data.size)
        
        FFT_mixinglist = [fft_data_mag, fft_data_phase,
                    fft_data_real, fft_data_imag, sample_freq]
        # list of lists holds all calculated values
        FFT_displayComponents = [fft_mag_spectrum, fft_data_phase,
                    fft_real_spectrum, fft_data_imag, sample_freq]
        FFT_list = [FFT_mixinglist,FFT_displayComponents]
        '''
        return a list that contains 2 lists
        FFT_list[0] is fourier components without any shift or multiplying by log
        FFT_list[1] contains the magnitude and real spectrum with the rest of components, 
        that are neaded in the component display.
        '''
        return FFT_list

    # Fixed displays are excluded
    def clearall(self):
        self.default()
        for i in range(4):
            self.displays[i+2].clear()
    
    # setting the default values        
    def default (self):
        for i in range(7):
            self.dropMenu[i].setCurrentIndex(0)
            
        for i in range(2):
            self.slider[i].setProperty("value", 50)


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

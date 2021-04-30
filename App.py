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

        self.loaded_imgs = [0, 0]
        self.ratios = [0, 0]
        self.mixing_sliders = [self.Comp1_Slider, self.Comp2_Slider]

        self.dropMenu = [self.displaySelection_Menu1, self.displaySelection_Menu2, self.Output_menu,
                         self.Comp1_ImageMenu, self.Comp2_ImageMenu, self.Comp1_Menu, self.Comp2_Menu]

        self.displays = [self.fixedDisplay_1, self.fixedDisplay_2, self.selectedDisplay_1,
                         self.selectedDisplay_2, self.output1_Display, self.output2_Display]

        ## Connecting Buttons ##
        self.actionClear.triggered.connect(lambda: self.clear_all_widgets())
        self.Close.triggered.connect(lambda: self.close())
        self.actionNewWindow.triggered.connect(lambda: self.make_new_window())
        self.actionOpenImgs.triggered.connect(lambda: self.browse_imgs())

        for i in range(2):  # connecting the Sliders
            self.mixing_sliders_counter(i)
            self.display_component_counter(i)

        # Update Component2-ComboBox when index of Component1-ComboBox change
        self.Comp1_Menu.currentIndexChanged.connect(
            lambda: self.comboBox_updater())

        # Adjusting QtPlotWidgets to show images properly
        for i in range(len(self.displays)):
            self.displays[i].ui.histogram.hide()
            self.displays[i].ui.roiBtn.hide()
            self.displays[i].ui.menuBtn.hide()
            self.displays[i].ui.roiPlot.hide()
            vbox = self.displays[i].getView()
            vbox.setBackgroundColor('#2d2d46')

    def mixing_sliders_counter(self, i: int):
        self.mixing_sliders[i].valueChanged.connect(lambda: self.mixer())

    # connecting Combo boxes of the input displays
    def display_component_counter(self, i: int):
        self.dropMenu[i].currentIndexChanged.connect(
            lambda: self.display_component(self.dropMenu[i], self.displays[i+2], self.image_Allfft[i][1]))

    def comboBox_updater(self):
        # updating component 1 comboBox will affect the available items of component 2 comboBox

        self.component1 = self.Comp1_Menu.currentText()

        # first, remove all items from the menu
        self.Comp2_Menu.clear()
        # start adding specific items according to the current choice of component 1 comboBox
        if self.component1 == "Magnitude" or self.component1 == "Uniform magnitude":
            self.Comp2_Menu.addItems(["Phase", "Uniform phase"])
        elif self.component1 == "Phase" or self.component1 == "Uniform phase":
            self.Comp2_Menu.addItems(["Magnitude", "Uniform magnitude"])
        elif self.component1 == "Select Component":
            self.Comp2_Menu.addItems(
                ["Select Component", "Magnitude", "Phase", "Real", "Imaginary", "Uniform magnitude", "Uniform phase"])
        else:
            if self.component1 == "Real":
                self.Comp2_Menu.addItems(["Imaginary"])
            else:
                self.Comp2_Menu.addItems(["Real"])

        # get the latest update of comp2_menu
        self.component2 = self.Comp2_Menu.currentText()

    def update_selected_img(self):
        # Get the current selected image from ImageMenucomboBox for each one
        self.image_of_component1 = self.Comp1_ImageMenu.currentText()
        self.image_of_component2 = self.Comp2_ImageMenu.currentText()

        # Assign the correct image components to different arrays according to selected images
        if self.image_of_component1 == "Image 1" and self.image_of_component2 == "Image 2":
            first_img_slot = self.image1_Allfft
            second_img_slot = self.image2_Allfft

        if self.image_of_component1 == "Image 2" and self.image_of_component2 == "Image 1":
            first_img_slot = self.image2_Allfft
            second_img_slot = self.image1_Allfft

        if self.image_of_component1 == "Image 1" and self.image_of_component2 == "Image 1":
            first_img_slot = self.image1_Allfft
            second_img_slot = self.image1_Allfft

        if self.image_of_component1 == "Image 2" and self.image_of_component2 == "Image 2":
            first_img_slot = self.image2_Allfft
            second_img_slot = self.image2_Allfft

        # Return all fft components of each image in separate arrays
        return [first_img_slot, second_img_slot]

    def mixer(self):

        self.image1, self.image2 = self.update_selected_img()

        # self.image1[0][0] -> Magnitude ,, self.image1[0][1] -> Phase
        # self.image1[0][2] -> Real ,, self.image1[0][3] -> Imaginary

        for i in range(2):
            # creating a list that holds the current slider values divided by 100 to be used later with mixing equations
            self.ratios[i] = (self.mixing_sliders[i].value() / 100)

        if self.component1 == "Magnitude" and self.component2 == "Phase":
            new_mag = np.add(
                self.image1[0][0] * self.ratios[0], self.image2[0][0] * (1 - self.ratios[0]))
            new_phase = np.add(
                self.image2[0][1] * (self.ratios[1]), self.image1[0][1] * (1 - self.ratios[1]))

        if self.component1 == "Magnitude" and self.component2 == "Uniform phase":
            new_mag = np.add(
                self.image1[0][0] * self.ratios[0], self.image2[0][0] * (1 - self.ratios[0]))
            new_phase = np.zeros(self.image2[0][1].shape)

        if self.component1 == "Phase" and self.component2 == "Magnitude":
            new_mag = np.add(
                self.image2[0][0] * self.ratios[1], self.image1[0][0] * (1 - self.ratios[1]))
            new_phase = np.add(
                self.image1[0][1] * (self.ratios[0]), self.image2[0][1] * (1 - self.ratios[0]))

        if self.component1 == "Phase" and self.component2 == "Uniform magnitude":
            new_mag = np.ones(self.image2[0][0].shape)
            new_phase = np.add(
                self.image1[0][1] * (self.ratios[0]), self.image2[0][1] * (1 - self.ratios[0]))

        if self.component1 == "Real" and self.component2 == "Imaginary":
            new_real = np.add(
                self.image1[0][2] * self.ratios[0], self.image2[0][2] * (1 - self.ratios[0]))
            new_imag = np.add(
                self.image2[0][3] * (self.ratios[1]), self.image1[0][3] * (1 - self.ratios[1]))

        if self.component1 == "Imaginary" and self.component2 == "Real":
            new_real = np.add(
                self.image2[0][2] * self.ratios[1], self.image1[0][2] * (1 - self.ratios[1]))
            new_imag = np.add(
                self.image1[0][3] * (self.ratios[0]), self.image2[0][3] * (1 - self.ratios[0]))

        if self.component1 == "Uniform magnitude" and self.component2 == "Phase":
            new_mag = np.ones(self.image1[0][0].shape)
            new_phase = np.add((self.image2[0][1] * self.ratios[1]),
                               (self.image1[0][1] * (1 - self.ratios[1])))

        if self.component1 == "Uniform magnitude" and self.component2 == "Uniform phase":
            new_mag = np.ones(self.image1[0][0].shape)
            new_phase = np.zeros(self.image2[0][1].shape)

        if self.component1 == "Uniform phase" and self.component2 == "Magnitude":
            new_mag = np.add(
                self.image2[0][0] * self.ratios[1], self.image1[0][0] * (1 - self.ratios[1]))
            new_phase = np.zeros(self.image1[0][1].shape)

        if self.component1 == "Uniform phase" and self.component2 == "Uniform magnitude":
            new_mag = np.ones(self.image2[0][0].shape)
            new_phase = np.zeros(self.image1[0][1].shape)

        if self.component1 == "Imaginary" or self.component2 == "Imaginary":
            new_imag = (1j * new_imag)
            new_array = np.add(new_real, new_imag)
        else:
            new_phase = np.exp(1j * new_phase)
            new_array = np.multiply(new_phase, new_mag)

        output = np.real(ifft2(new_array))

        if self.Output_menu.currentText() == "Output 1":
            return self.plotting(output, self.output1_Display)

        elif self.Output_menu.currentText() == "Output 2":
            return self.plotting(output, self.output2_Display)

        else:
            self.output1_Display.clear()
            self.output2_Display.clear()

    def closeEvent(self, event):  # Related to QSettings
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
            self.image_Allfft = [self.image1_Allfft,self.image2_Allfft]

            # Plotting loop
            for i in range(2):
                self.plotting(self.loaded_imgs[i], self.displays[i])

    def plotting(self, data, viewer):
        viewer.setImage(data.T)
        viewer.show()

    def display_component(self, menu, display, img_components):
        # menu represents which combo box is used
        # get the index of the selected component from the combo box ,the comps start from index 1
        selected_option = menu.currentIndex()

        if selected_option == 0:
            display.clear()
        else:
            # get the required component from the fourier components list
            component = img_components[selected_option-1]
            self.plotting(component, display)

    def get_fft(self, data_array: np.ndarray):
        # Fourier transform of given data array
        fft_data = fft2(data_array)
        # shifting the array of data
        fft_data_shifted = np.fft.fftshift(fft_data)
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

        FFT_list = [FFT_mixinglist, FFT_displayComponents]
        '''
        return a list that contains 2 lists
        FFT_list[0] is fourier components without any shift or multiplying by log
        FFT_list[1] contains the magnitude and real spectrum with the rest of components, 
        that are neaded in the component display.
        '''
        return FFT_list

    # Fixed displays are excluded
    def clear_all_widgets(self):
        self.default()
        for i in range(4):
            self.displays[i+2].clear()

    # setting the default values
    def default(self):
        for i in range(7):
            self.dropMenu[i].setCurrentIndex(0)

        value = 100 
        for i in range(2):
            self.mixing_sliders[i].setProperty("value", i*value)


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

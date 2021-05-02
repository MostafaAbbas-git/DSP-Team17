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
from ImageDisplay import imageDisplay
import ctypes
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

        self.image_Allfft = []
        self.images = ["Image 1", "Image 2"]
        self.outputs = ["Output 1", "Output 2"]

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

        for i in range(2):
            for j in range(2):
                if self.image_of_component1 == self.images[i] and self.image_of_component2 == self.images[j]:
                    first_img_slot = self.image_Allfft[i]
                    second_img_slot = self.image_Allfft[j]

        # Return all fft components of each image in separate arrays
        return [first_img_slot, second_img_slot]

    def mixer(self):

        self.image1, self.image2 = self.update_selected_img()

        # self.image1[0][0] -> Magnitude ,, self.image1[0][1] -> Phase
        # self.image1[0][2] -> Real ,, self.image1[0][3] -> Imaginary

        for i in range(2):
            # creating a list that holds the current slider values divided by 100 to be used later with mixing equations
            self.ratios[i] = (self.mixing_sliders[i].value() / 100)

        output = imageDisplay()
        output_Data = output.mixing(
            self.image1, self.image2, self.component1, self.component2, self.ratios)

        for i in range(2):
            if self.Output_menu.currentText() == self.outputs[i]:
                return self.plotting(output_Data, self.displays[i+4])
            else:
                self.displays[i+4].clear()

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
        for i in range(len(selected_image)):
            self.loaded_imgs[i] = imageDisplay()
            self.loaded_imgs[i].read(selected_image[0][i])

        if self.loaded_imgs[0].shape != self.loaded_imgs[1].shape:
            # Showing size warning msg and return
            self.size_warning_msg.exec_()
            return self.browse_imgs()
        else:
            ## Calculate and store all fourier components for each image at once to be used later##
            for i in range(2):
                self.fft_Access = imageDisplay()
                self.image_Allfft.append(
                    self.fft_Access.get_fft(self.loaded_imgs[i].imgByte))
                self.plotting(self.loaded_imgs[i].imgByte, self.displays[i])

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

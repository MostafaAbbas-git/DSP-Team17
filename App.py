from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSettings
from autologging import logged, TRACE, traced
import sys
import os
import logging
from ImageDisplay import imageDisplay
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

        self.loaded_imgs = [0, 0]
        self.ratios = [0, 0]
        self.image1 = []
        self.image2 = []
        self.mixing_sliders = [self.Comp1_Slider, self.Comp2_Slider]

        self.drop_menus = [self.displaySelection_Menu1, self.displaySelection_Menu2, self.Output_menu,
                           self.Comp1_ImageMenu, self.Comp2_ImageMenu, self.Comp1_Menu, self.Comp2_Menu]

        self.displays = [self.fixedDisplay_1, self.fixedDisplay_2, self.selectedDisplay_1,
                         self.selectedDisplay_2, self.output1_Display, self.output2_Display]

        self.imgs_fft_list = []
        self.imagesText = ["Image 1", "Image 2"]
        self.outputs = ["Output 1", "Output 2"]

        ## Connecting Buttons ##
        self.actionClear.triggered.connect(lambda: self.clear_all_widgets())
        self.Close.triggered.connect(lambda: self.close())
        self.actionNewWindow.triggered.connect(lambda: self.make_new_window())
        self.actionOpenImgs.triggered.connect(lambda: self.browse_imgs())

        for i in range(2):
            self.mixing_sliders_counter(i)  # connecting the Sliders
            # Trigger the components drop menus
            self.display_component_counter(i)

        # Update Component2-ComboBox on the change of Component1-ComboBox selection.
        self.Comp1_Menu.currentIndexChanged.connect(
            lambda: self.update_components_CB())

        # Adjusting QtPlotWidgets to show images properly
        for i in range(len(self.displays)):
            self.displays[i].ui.histogram.hide()
            self.displays[i].ui.roiBtn.hide()
            self.displays[i].ui.menuBtn.hide()
            self.displays[i].ui.roiPlot.hide()
            vbox = self.displays[i].getView()
            vbox.setBackgroundColor('#2d2d46')

    def mixing_sliders_counter(self, i: int):
        self.mixing_sliders[i].valueChanged.connect(lambda: self.mixer_panel())

    # Connecting ComboBoxes of input displays
    def display_component_counter(self, i: int):
        self.drop_menus[i].currentIndexChanged.connect(
            lambda: self.display_fft_component(self.drop_menus[i], self.displays[i+2], self.imgs_fft_list[i][1]))

    def browse_imgs(self):
        selected_image = QtGui.QFileDialog.getOpenFileNames(
            self, 'Select image', os.getenv('HOME'), "Images (*.png *.xpm *.jpg)")

        if len(selected_image[0]) != 2:
            # Showing number of images warning msg and return
            self.warning_msg_generator(
                "Error in selected Images ", "You must select two images at once!")
            logger.info("The user didn't select exactly 2 images")
            return self.browse_imgs()
        # Ignore RGB values; converting to greyscale images
        for i in range(2):
            self.loaded_imgs[i] = imageDisplay()
            self.loaded_imgs[i].read(selected_image[0][i])

        if self.loaded_imgs[0].shape != self.loaded_imgs[1].shape:
            # Showing size warning msg and return
            self.warning_msg_generator(
                "Error in Image Size", "The 2 images must have the same size!")
            logger.info("The user selected 2 images with different sizes")
            return self.browse_imgs()
        else:
            for i in range(2):
                # Calculate and store all fourier components for each image at once to be used later
                self.imgs_fft_list.append(
                    imageDisplay.get_fft(self, self.loaded_imgs[i].imgByte))
                # Plot original selected images on input displays
                imageDisplay.plotting_img(
                    self, self.loaded_imgs[i].imgByte, self.displays[i])
            logger.info(
                "selection, calculation of fft-components for the two images, and plotting are done successfully.")

    def display_fft_component(self, menu, viewer, img_components):
        # menu represents which comboBox is used
        # get the index of the selected component from the combo box ,the comps start from index 1
        selected_option = menu.currentIndex()

        if selected_option == 0:
            viewer.clear()
        else:
            # get the required component from the fourier components list
            component = img_components[selected_option-1]
            imageDisplay.plotting_img(self, component, viewer)

    def update_components_CB(self):
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

    def update_images_CB(self):
        # Get the current selected image from ImageMenucomboBox for each one
        self.image_of_component1 = self.Comp1_ImageMenu.currentText()
        self.image_of_component2 = self.Comp2_ImageMenu.currentText()
        for i in range(2):
            for j in range(2):
                if self.image_of_component1 == self.imagesText[i] and self.image_of_component2 == self.imagesText[j]:
                    first_img_slot = self.imgs_fft_list[i]
                    second_img_slot = self.imgs_fft_list[j]
        # Return all fft components of each image in separate arrays
        logger.info(
            f"Images-ComboBoxes are updated with {self.image_of_component1} and {self.image_of_component2} respectively.")
        return [first_img_slot, second_img_slot]

    def update_slider_values(self):
        for i in range(2):
            # creating a list that holds the current slider values divided by 100 to be used later with mixing equations.
            self.ratios[i] = float(self.mixing_sliders[i].value() / 100)
        return self.ratios

    def mixer_panel(self):
        # Get the current selection of Component2-comboBox.
        self.component2 = self.Comp2_Menu.currentText()
        # Get the current slider values.
        self.ratios = self.update_slider_values()
        logger.info(
            f"Components-ComboBoxes are updated with {self.component1} and {self.component2} respectively.")
        # Get the current selected images.
        self.image1, self.image2 = self.update_images_CB()
        output = imageDisplay()
        output_data = output.mixer(
            self.component1, self.component2, self.image1, self.image2, self.ratios)

        for i in range(2):
            if self.Output_menu.currentText() == self.outputs[i]:
                output.plotting_img(output_data, self.displays[i+4])
                logger.info(
                    f"A mixed image of {self.image_of_component1}.{self.component1} and {self.image_of_component2}.{self.component2} is plotted on {self.displays[i+4].objectName()}.")

    def warning_msg_generator(self, title, text):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Warning)
        return msg.exec_()

    def closeEvent(self, event):  # Related to QSettings
        self.settings.setValue('window size', self.size())
        self.settings.setValue('window position', self.pos())

    # Creating new window by calling the main class
    def make_new_window(self):
        self.new_win = ImagesMixer()
        self.new_win.show()
        logger.info("The user created new window")

    def clear_all_widgets(self):  # Fixed displays are excluded
        self.default()
        for i in range(4):
            self.displays[i+2].clear()
        logger.info("All widgets and comboBoxes are reset to default values.")

    # setting the default values
    def default(self):
        for i in range(7):
            self.drop_menus[i].setCurrentIndex(0)

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

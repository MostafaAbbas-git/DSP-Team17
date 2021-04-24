import sys
from PyQt5 import QtCore, QtWidgets, QtGui, uic
import logging
from autologging import logged, TRACE, traced
import numpy as np
from numpy.fft import fft2, ifft2, fftfreq
from numpy.lib.type_check import imag
# Create and configure logger
LOG_FORMAT = "%(levelname)s:%(filename)s,%(lineno)d:%(name)s.%(funcName)s:%(message)s"
logging.basicConfig(filename="FTMixer.log",
                    level=TRACE,
                    format=LOG_FORMAT,
                    filemode='w')
logger = logging.getLogger()


@ traced
@ logged
class FTMixer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('FTMixer.ui', self)
        self.__log.info("initialized")


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
    application = FTMixer()
    application.show()
    app.exec_()


if __name__ == "__main__":
    main()

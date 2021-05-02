from numpy.fft import fft2, ifft2, fftfreq, fftshift
import numpy as np
import cv2 as cv


class imageDisplay():

    def read(self, imgPath: str):

        self.imgByte = cv.cvtColor(
            cv.imread(imgPath), cv.COLOR_BGR2GRAY)

        self.shape = self.imgByte.shape

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

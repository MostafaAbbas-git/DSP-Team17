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


    def mixing(self, image1, image2, component1, component2, ratio):

        self.component1=component1
        self.component2=component2
        self.ratios=ratio
        self.image1=image1
        self.image2=image2

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

        return (output)
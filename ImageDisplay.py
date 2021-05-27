from numpy.fft import fft2, ifft2, fftfreq, fftshift
import numpy as np
import cv2 as cv
import enum


class Cases(enum.Enum):
    MagandPhase = "MagnitudeandPhase"
    RealandImag = "RealandImaginary"
    UniMagandPhase = "UniformMagnitudeandPhase"
    MagandUniPhase = "MagnitudeandUniformPhase"
    UniMagandUniPhase = "UniformMagnitudeandUniformPhase"


class imageDisplay():
    def __init__(self):
        self.imgByte = []
        self.shape = 0

    def read(self, imgPath: str):
        self.imgByte = cv.cvtColor(
            cv.imread(imgPath), cv.COLOR_BGR2GRAY)
        self.shape = self.imgByte.shape

        # return self.imgByte

    def plotting_img(self, data, viewer):
        viewer.setImage(data.T)
        viewer.show()

    def get_fft(self, data: np.ndarray):
        # Fourier transform of given data array
        fft_data = fft2(data)
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

        FFT_mixinglist = [fft_data_mag, fft_data_phase,
                          fft_data_real, fft_data_imag]
        # list of lists holds all calculated values
        FFT_displayComponents = [fft_mag_spectrum, fft_data_phase,
                                 fft_real_spectrum, fft_data_imag]

        FFT_lists = [FFT_mixinglist, FFT_displayComponents]
        '''
        return a list that contains 2 lists
        FFT_list[0] == FFT_mixinglist ->  is a list of fourier components without any shift or multiplying by 20log.
        FFT_list[1] == FFT_displayComponents -> contains the magnitude and real spectrum with the rest of components,
        that are needed in the component display.
        '''
        return FFT_lists

    def mixer(self, component1, component2, image1, image2, sliderRatios):
        # this function is made to get current selection of components-comboBoxes and determine the suitable case to call the mixing calculator

        if component1 == "Magnitude" or component1 == "Phase":
            if component2 == "Phase" or component2 == "Magnitude":
                return (self.mixer_calculator(Cases.MagandPhase, image1, image2, sliderRatios))
            elif component2 == "Uniform phase":
                return (self.mixer_calculator(Cases.MagandUniPhase, image1, image2, sliderRatios))
            else:
                return (self.mixer_calculator(Cases.UniMagandPhase, image1, image2, sliderRatios))

        if component1 == "Uniform magnitude" or component1 == "Uniform phase":
            if component2 == "Uniform phase" or component2 == "Uniform magnitude":
                return (self.mixer_calculator(Cases.UniMagandUniPhase, image1, image2, sliderRatios))
            elif component2 == "Phase":
                return (self.mixer_calculator(Cases.UniMagandPhase, image1, image2, sliderRatios))
            else:
                return (self.mixer_calculator(Cases.MagandUniPhase, image1, image2, sliderRatios))

        if component1 == "Real" or component1 == "Imaginary":
            if component2 == "Imaginary" or component2 == "Real":
                return (self.mixer_calculator(Cases.RealandImag, image1, image2, sliderRatios))

    # @ImagesMixer
    def mixer_calculator(self, case: 'Cases', image1, image2, sliderRatios: list):
        from App import ImagesMixer

        ratios = sliderRatios
        img1 = image1
        img2 = image2

        # case 1
        if case == Cases.MagandPhase:
            mag_mix = np.add(img1[0][0] * ratios[0],
                             img2[0][0] * (1 - ratios[0]))
            phase_mix = np.add(img2[0][1] * (ratios[1]),
                               img1[0][1] * (1 - ratios[1]))

        # case 2
        if case == Cases.MagandUniPhase:
            mag_mix = np.add(img1[0][0] * ratios[0],
                             img2[0][0] * (1 - ratios[0]))
            phase_mix = np.zeros(img2[0][0].shape)

        # case 3
        if case == Cases.UniMagandPhase:
            mag_mix = np.ones(img2[0][0].shape)  # ones array
            phase_mix = np.add((img2[0][1] * ratios[1]),
                               (img1[0][1] * (1 - ratios[1])))

        # case 4
        if case == Cases.UniMagandUniPhase:
            mag_mix = np.ones(img2[0][0].shape)  # ones array
            phase_mix = np.zeros(img2[0][0].shape)

        # case 5
        if case == Cases.RealandImag:
            real_mix = np.add(img1[0][2] * ratios[0],
                              img2[0][2] * (1 - ratios[0]))
            imag_mix = np.add(img2[0][3] * (ratios[1]),
                              img1[0][3] * (1 - ratios[1]))

        if case == Cases.RealandImag:
            imag_mix = (1j * imag_mix)
            new_array = np.add(real_mix, imag_mix)
        else:
            phase_mix = np.exp(1j * phase_mix)
            new_array = np.multiply(phase_mix, mag_mix)

        output = np.real(ifft2(new_array))
        return output  # -> ndarray

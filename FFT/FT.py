import FT
import time
import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft


path = ['data/data1.txt', 'data/data2.txt', 'data/data3.txt',
        'data/data4.txt', 'data/data5.txt', 'data/data6.txt']

# arr = [0, 32767]
#arr = [0, 32767, 32767, 32767, 238, -480, 3580, 693]

data_list = [[], [], [], [], [], []]  # list of lists
length = []

meanSquaredError = []

dft_time = []
fft_time = []

# Reading data of diff lengths
for i in range(len(path)):
    with open(path[i], 'r') as f:
        for line in f.readlines():
            data_list[i].append(int(line))


for i in range(len(data_list)):

    length.append(len(data_list[i]))

    # Calling DFT
    dft_start = time.time()
    dft_array = FT.DFT(data_list[i])
    dft_end = time.time()

    dft_time.append(dft_end - dft_start)

    #Calling FFT
    fft_start = time.time()
    fft_array = FT.FFT(data_list[i])
    fft_end = time.time()

    fft_time.append(fft_end - fft_start)

    #calculating the mean squared error
    dftArray = np.array(dft_array)
    fftArray = np.array(fft_array)
    difference = np.subtract(dftArray, fftArray)
    squared_array = np.square(difference) 
    meanSquaredError.append(np.abs(squared_array.mean()))

#Plotting
plt.subplot(1,2,1)
plt.plot(length,dft_time)
plt.plot(length,fft_time)

plt.xlabel('N')
plt.ylabel('time (sec)')
plt.title('Time Complexity')
plt.legend(["DFT", "FFT"])

plt.subplot(1,2,2)
plt.plot(length, meanSquaredError)

plt.xlabel('N')
plt.ylabel('Mean squared Error')
plt.title('Error')

plt.tight_layout()
plt.show()
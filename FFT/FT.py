import FT
from numpy.fft import fft


path = ['data/data1.txt', 'data/data2.txt', 'data/data3.txt',
        'data/data4.txt', 'data/data5.txt', 'data/data6.txt']

array = []

# arr = [0, 32767]
arr = [0, 32767, 32767, 32767, 238, -480, 3580, 693]
         

""" 
for i in range (len(path)):
    data = #read with path[i]
    fft_array = data #bec fft is void function and takes the data by reference
    #calling lines
    dft = library.DFT(data)
    library.FFT(fft_array)
"""
data_list = [[], [], [], [], [], []]  # list of lists

data_list = [[], [], [], [], [], []]  # list of lists
dft = [[], [], [], [], [], []]
fft = [[], [], [], [], [], []]

for i in range(len(path)):
    with open(path[i], 'r') as f:
        for line in f.readlines():
            data_list[i].append(int(line))

for i in range(len(data_list)):
    fft_array = data_list[i]
    dft[i].append(FT.DFT(data_list[i]))
    fft[i].append(FT.FFT(fft_array))

for i in range(10):
    dft = FT.DFT(data_list[0])
    print('dft', dft[i])

for i in range(10):
    dft = FT.FFT(data_list[0])
    print('fft', dft[i])

for i in range(10):
    x=data_list[0]
    print(x)


# array = FT.DFT(arr)
# x = fft(arr)
# y=FT.FFT(arr)

# print(x)
# print(array)
# print(y)

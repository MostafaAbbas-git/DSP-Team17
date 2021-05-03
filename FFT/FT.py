import ctypes


library = ctypes.CDLL('./lib.so')


path = ['data/data1.txt', 'data/data2.txt', 'data/data3.txt',
         'data/data4.txt', 'data/data5.txt','data/data6.txt']

""" 
for i in range (len(path)):
    data = #read with path[i]
    fft_array = data #bec fft is void function and takes the data by reference
    #calling lines
    dft = library.DFT(data)
    library.FFT(fft_array)
"""

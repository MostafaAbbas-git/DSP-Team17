#include <math.h>
#include <complex>
#include <vector>
#include <iostream>
#include <iomanip>
#include<fstream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>

#define M_PI 3.14159265358979323846

using namespace std;

namespace py = pybind11;

vector<complex<double>> FFT (vector<complex<double>>  fftArray){
    
    int N = fftArray.size();

    if( N == 1) {

        return fftArray;
    }


    vector<complex<double>> even(N/2, 0),odd(N/2,0), fft_Even(N/2,0), fft_Odd(N/2, 0);

    // Splitting
    for(int i = 0; i != N/2; i++){

        even[i]= ( fftArray[2*i] );
        odd[i]= (fftArray [2*i +1]);
    } 

    /* perform the recursive FFT operations on the splitted even and odd vectors 
    *  to split each of them to another even and odd vectors,
    *  until we have one element only that can't be splitted anymore. 
    */
    fft_Even = FFT(even);
    fft_Odd = FFT(odd);

   vector<complex<double>> frequencyBins (N,0);
    
    // Combining the small vectors to make the final fft array
    for(int k = 0; k != N/2; k++){
        
        complex<double> wn_times_Ok = (complex<double>(cos(-2*M_PI *k /N),sin(-2*M_PI *k /N)))*fft_Odd[k];
        frequencyBins[k] = fft_Even[k] + wn_times_Ok;
        frequencyBins[k+N/2] = fft_Even[k] - wn_times_Ok;  
    }

return frequencyBins;

}

// samples is of type vector of complex the same as the output
vector<complex<double>> DFT(vector<complex<double>> data)
{
    int N = data.size();

    // we will restore each value of X[k] into newData to then append it into the vector fftOutput
    complex<double> newData;

    vector<complex<double>> fftOutput;

    // make the size of fftOutput the same as K (input size)
    fftOutput.reserve(N);
    
    for(int k=0; k<N; k++){

        newData = complex<double>(0,0);
        for(int n=0; n<N; n++){

            double realPart = cos(((2*M_PI)/N) * k * n);
            double imaginaryPart = sin(((2*M_PI)/N) * k * n);

            complex<double> w (realPart, -imaginaryPart);

            newData += data[n] * w;
        }

        fftOutput.push_back(newData);
    }

    return fftOutput;

}

PYBIND11_MODULE(FT ,m){
    
    m.def("FFT", &FFT, "A function returns fft");

    m.def("DFT", &DFT, "A function returns dft");


}

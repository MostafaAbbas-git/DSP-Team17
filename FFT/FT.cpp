#include <math.h>
#include <complex>
#include <vector>
#include <iostream>
#include <iomanip>
#include<fstream>
#include <pybind11/pybind11.h>

PYBIND11_MODULE(FT ,m){
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("dft", &DFT, "A function returns dft");

    m.def("fft", &FFT, "A function returns fft");
}

#define M_PI 3.14159265358979323846

using namespace std;

extern "C"
{
    void FFT(vector<complex<double>> & fftArray );
    vector<complex<double>> DFT(vector<complex<double>> data);
}


void FFT (vector<complex<double>> & fftArray){
    
    int N = fftArray.size();

    if( N == 1) return;

    vector<complex<double>> even,odd;

    // Splitting
    for(int i = 0; i != N/2; i++){

        even.push_back( fftArray[2*i] );
        odd.push_back(fftArray [2*i +1]);
    } 

    /* perform the recursive FFT operations on the splitted even and odd vectors 
    *  to split each of them to another even and odd vectors,
    *  until we have one element only that can't be splitted anymore. 
    */
    FFT(even);
    FFT(odd);

    
    // Compining the small vectors to make the final fft array
    for(int k = 0; k < N/2; k++){
        
        complex<double> wn_times_Ok = (complex<double>(cos(-2*M_PI *k /N),sin(-2*M_PI *k /N)))*odd[k];
        fftArray[k] = even[k] + wn_times_Ok;
        fftArray[k+N/2] = even[k] - wn_times_Ok;  
    }

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

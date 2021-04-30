#include <math.h>
#include <complex>
#include <vector>
#include <iostream>
#include <iomanip>
#include<fstream>

using namespace std;

double x;

ifstream inFile;


// samples is of type vector of complex the same as the output
vector<complex<double>> DFT(vector<complex<double>> data)
{
    int N = data.size();

    //int K = N;

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


int main(){



vector<complex<double>> data,dft_data ;

inFile.open("data.txt");

while(inFile >> x){

    data.push_back(complex<double>(x));

}

inFile.clear();
inFile.seekg(0,ios::beg);

dft_data=DFT(data);

for(int i=0; i<11; i++){
    cout<<"DFT "<< dft_data[i] <<'\n';
}

}
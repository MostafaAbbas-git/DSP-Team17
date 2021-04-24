import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui, uic
import logging

""" 
logging.basicConfig(filename="LoggingFile.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='w')

 """
class FTMixer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('FTMixer.ui', self)


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

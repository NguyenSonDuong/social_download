from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
import sys

class Ui_HomeWindow(QMainWindow):

    def __init__(self):
        sys.path.append('.')
        super().__init__()
        uic.loadUi("ui/home/home.ui",self)
        self.setAndRun()

    def setAndRun(self):
        self.show()

        
    
    
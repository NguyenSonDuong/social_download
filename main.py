import sys
import os
from PyQt5.QtWidgets import QApplication
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'message'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'youtube'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ui'))
from ui.home.home import Ui_HomeWindow
def process(funtion_name, messgae):
    print(f"{funtion_name}: {messgae}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    home = Ui_HomeWindow()
    sys.exit(app.exec_())
   

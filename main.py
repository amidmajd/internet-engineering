from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
import sys

import limited_http_client


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('main.ui', self)
        self.initUI()

    def initUI(self):
        self.show()
        self.addressInput.returnPressed.connect(self.go_to_address)
        self.goBtn.clicked.connect(self.go_to_address)

    def go_to_address(self):
        print("loading requested address...")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())

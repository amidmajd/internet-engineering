from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QUrl
from PyQt5.uic import loadUi
import sys
import os

from limited_http_client import Client


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('main.ui', self)
        self.http_client = Client()
        self.initUI()

    def initUI(self):
        # if Enter key or GO button been pressed in input field
        self.addressInput.returnPressed.connect(self.go_to_address)
        self.goBtn.clicked.connect(self.go_to_address)

        self.mainBrowser.setStyleSheet("background-color: white;")

        self.show()

    def go_to_address(self):
        print("loading requested address...")

        address = self.addressInput.text()
        try:
            if len(address) > 3:
                address = self.addressInput.text()
            else:
                raise Exception("Invalid Address!")

            html_response = self.http_client.send_request(address)
            self.mainBrowser.setHtml(html_response['content'])
        except Exception as e:
            self.mainBrowser.setHtml(
                f'''<h1 style='color: red;'>Requested Address is not Reachable!</h1>
                        <h3>{e}</h3>
                '''

            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())

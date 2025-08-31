import sys

from PyQt5.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QWidget, QLabel


class LiveConsole(QWidget):

    def __init__(self, fun):
        super().__init__()
        self.setGeometry(300, 200, 350, 50)
        self.setMinimumSize(self.size())
        self.setWindowTitle("Console")

        l = QVBoxLayout()

        self.text1 = QLineEdit()
        self.text1.returnPressed.connect(lambda: fun(self.text1))
        l.addWidget(QLabel("Live Console"))
        l.addWidget(self.text1)

        self.text2 = QLineEdit()
        self.text2.returnPressed.connect(lambda: fun(self.text2))
        l.addWidget(self.text2)

        self.text3 = QLineEdit()
        self.text3.returnPressed.connect(lambda: fun(self.text3))
        l.addWidget(self.text3)

        self.text4 = QLineEdit()
        self.text4.returnPressed.connect(lambda: fun(self.text4))
        l.addWidget(self.text4)
        self.setLayout(l)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = LiveConsole()
    exit(app.exec())

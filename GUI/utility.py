from PyQt5 import QtGui
from GUI import ThemeColors as tc


def loadPixmap(file, color):
    file = open(file, 'r')
    svg = file.read()
    svg = svg.replace('black', 'rgb'+tc.toRGBStr(color))
    svg = svg.replace('#000000', 'rgb'+tc.toRGBStr(color))
    icon = QtGui.QPixmap.fromImage(
            QtGui.QImage.fromData(bytes((svg.encode()))))

    file.close()
    return icon

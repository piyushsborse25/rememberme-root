from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from GUI import utility, GUIControlSet, ThemeColors as tc, Animations as anime
import math
import config


class ControlButton(QPushButton):
    def __init__(self, parent, name, center: QPointF, checkable=True):
        super().__init__(parent)
        self.setCheckable(checkable)
        self.setObjectName(name)
        self.__posTheta__ = -130
        self.__posRadius__ = 120
        self.__center__ = center
        self.__radius__ = 0
        self.radius = 25
        self.__updatePos__()
        # GUIControlSet.SingleControl.addParameters(
        #     ['posTheta', 'posRadius', 'radius'], self)
        self.__hoverAnime__ = anime.Hover(self, 'radius', self, 25)
        self.clicked.connect(
            lambda val: config.joiner.controlButtonStateChanged.emit(self.objectName(), val))

    # def toggle(self, value):
    #     print('*******togglebutton:', value)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.setIcon(self.__hoverIcon__)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.setIcon(self.__normalIcon__)

    def setIcons(self, normal, hover):
        self.__normalIcon__ = normal
        self.__hoverIcon__ = hover
        self.setIcon(self.__normalIcon__)

    @pyqtProperty(float)
    def posTheta(self):
        return self.__posTheta__

    @posTheta.setter
    def posTheta(self, theta):
        self.__posTheta__ = theta
        self.__updatePos__()

    @pyqtProperty(float)
    def posRadius(self):
        return self.__posRadius__

    @posRadius.setter
    def posRadius(self, radius):
        self.__posRadius__ = radius
        self.__updatePos__()

    @pyqtProperty(QPointF)
    def position(self):
        return QPointF(self.posTheta, self.posRadius)

    @position.setter
    def position(self, point):
        self.posTheta(point.x())
        self.posRadius(point.y())

    @pyqtProperty(float)
    def radius(self):
        return self.__radius__

    @radius.setter
    def radius(self, r):
        self.__radius__ = r
        self.setFixedSize(r * 2, r * 2)
        self.__updatePos__()
        self.setIconSize(QSize(r * 1.2, r * 1.2))
        self.setStyleSheet(f'''
                           border-radius:{int(r)};
                           ''')

    def __updatePos__(self):

        x = self.__posRadius__ * math.cos(math.radians(self.__posTheta__))
        y = self.__posRadius__ * math.sin(math.radians(self.__posTheta__))
        x += self.__center__.x()
        y += self.__center__.y()
        x -= self.width() // 2
        y -= self.height() // 2
        self.move(x, y)


class ControlManager(QObject):
    def __init__(self, placeholder, center, updateMouseEventTransparentRegion):
        super().__init__()
        self.updateMouseEventTransparentRegion = updateMouseEventTransparentRegion
        self.btns = {
            'mic': ControlButton(placeholder, 'mic', center),
            'camera': ControlButton(placeholder, 'camera', center),
            'info': ControlButton(placeholder, 'info', center),
            'close': ControlButton(placeholder, 'close', center),
        }
        self.loadIcons()
        self.__btnGroupRotation__ = 0
        self.__btnsSpacing__ = 0
        self.__btnsRadius__ = 0
        self.__btnsPosRadius__ = 0
        self.__updateBtnsPos__()
        config.joiner.setControlButtonState.connect(
            lambda btn, val: self.btns[btn].setChecked(val))
        GUIControlSet.SingleControl.addParameters(
            ['btnGroupRotation', 'btnsSpacing', 'btnsRadius', 'btnsPosRadius'], self)
        self.placeholder = placeholder
        self.hide()
        self.btns['mic'].setChecked(True)
        self.btns['camera'].setChecked(True)

    def show(self):
        self.placeholder.show()
        self.updateMouseEventTransparentRegion()

    def hide(self):
        self.placeholder.hide()
        self.updateMouseEventTransparentRegion()

    @pyqtProperty(float)
    def btnGroupRotation(self):
        return self.__btnGroupRotation__

    @btnGroupRotation.setter
    def btnGroupRotation(self, value):
        self.__btnGroupRotation__ = value
        self.__updateBtnsPos__()

    @pyqtProperty(float)
    def btnsSpacing(self):
        return self.__btnsSpacing__

    @btnsSpacing.setter
    def btnsSpacing(self, value):
        self.__btnsSpacing__ = value
        self.__updateBtnsPos__()

    @pyqtProperty(float)
    def btnsRadius(self):
        return self.__btnsRadius__

    @btnsRadius.setter
    def btnsRadius(self, value):
        self.__btnsRadius__ = value
        self.__updateBtnsPos__()

    @pyqtProperty(float)
    def btnsPosRadius(self):
        return self.__btnsPosRadius__

    @btnsPosRadius.setter
    def btnsPosRadius(self, value):
        self.__btnsPosRadius__ = value
        self.__updateBtnsPos__()

    def __updateBtnsPos__(self):
        i = 0 - (len(self.btns) - 1) / 2
        for name, button in self.btns.items():
            button.posTheta = self.__btnGroupRotation__ + self.__btnsSpacing__ * i
            button.posRadius = self.__btnsPosRadius__
            button.radius = self.__btnsRadius__

            i += 1

    def loadIcons(self):
        for name, button in self.btns.items():
            normalIcon = QIcon()
            normalIcon.addPixmap(utility.loadPixmap(
                f'GUI/resource/{name}Off.svg', tc.getLighter('text', 60)), normalIcon.Mode.Normal, normalIcon.State.Off)
            normalIcon.addPixmap(utility.loadPixmap(
                f'GUI/resource/{name}On.svg', 'primary'), normalIcon.Mode.Normal, normalIcon.State.On)

            hoverIcon = QIcon()

            hoverIcon.addPixmap(utility.loadPixmap(
                f'GUI/resource/{name}Off.svg', tc.getLighter('text', 80)), normalIcon.Mode.Normal, normalIcon.State.Off)
            hoverIcon.addPixmap(utility.loadPixmap(
                f'GUI/resource/{name}On.svg', tc.getLighter('primary', 120)), normalIcon.Mode.Normal, normalIcon.State.On)

            button.setIcons(normalIcon, hoverIcon)

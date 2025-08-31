import math
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QObject, QPoint, Qt
from PyQt5.QtWidgets import QWidget
from GUI import ThemeColors as tc, Animations as Anime
from random import uniform as rand


class LiveBackground():
    def __init__(self, target: QWidget):
        self.target = target
        self.oldPaintEvent = target.paintEvent
        target.paintEvent = self.paintEvent
        # No of shape drawn in background
        self.shapeCount = 10
        # Minimum/Maximum size of shape
        self.shapes = []
        def randint(a, b): return int(rand(a, b))
        for i in range(self.shapeCount):
            c = tc.getColor(f'ballRing{i%4}')
            h, s, v, a = c.getHsv()
            c.setHsv(h, 255, 255, a)
            self.shapes.append(
                # (target,cx, cy, fr, fTheta, radius, strach,  rotate, color)
                Ellipse(target, 0, 0, 0, 0, 0, 0, 0, 255, c)
            )
            self.propertyList = [
                # ('propety', minVal, maxVal, diff, minDur, maxDur)
                ('cx', -80, target.size().width()+80, 100, 7000, 10000),
                ('cy', -80, target.size().height()+80, 100, 7000, 10000),
                ('fr', -100, 100, 80, 3000, 5000),
                ('fTheta', 0, 360, 120, 3000, 5000),
                ('radius', 150, 300, 30, 3000, 5000),
                ('strach', -40, 40, 10, 3000, 6000),
                ('rotate', 0, 360, 90, 3000, 6000),
                ('colorAlpha', 0, 255, 255, 1000, 3000)
            ]
            self.animeGroup = Anime.RandomAnimationGroup(
                self.shapes, self.propertyList)
            # self.animeGroup.start()

    def update(self):
        self.target.update()

    def paintEvent(self, a0: QPaintEvent):
        self.oldPaintEvent(a0)
        painter = QPainter(self.target)
        # painter.setRenderHint(QPainter.Antialiasing)
        # painter.setCompositionMode(
        #     QPainter.CompositionMode.CompositionMode_DestinationAtop)

        painter.setPen(Qt.GlobalColor.transparent)
        painter.setBackground(tc.getColor('background'))
        painter.fillRect(0, 0, self.target.width(),
                         self.target.height(), tc.getColor('background'))
        painter.setBackgroundMode(Qt.BGMode.TransparentMode)
        for shape in self.shapes:
            shape.drawShape(painter)
        painter.end()


class Ellipse(QObject):
    def __init__(self, target, cx, cy, fr, fTheta, radius, strach,  rotate, colorAlpha, color):
        """
            Draw Ellipse Shape
            cx,cy       : Co-ordinate of center of Ellipse in cartesian system
                          Range : recommented inside of target widget boundaries
            fr,fTheta   : Co-ordinate of center of Ellipse in polar system
                          Range : fr= -100 - 100, fTheta=0 - 360
            radius      : radius of Ellipse
                          Range : 1-infinity
            strach      : strach the horizontal side of Ellipse
                          Range : 0-100
            color       : color of Ellipse
            colorAlpha  : alpha of Ellipse color
                            Range : 0-255
            painter     : QPainter to draw
        """
        super().__init__()
        self._target = target
        self._cx = cx
        self._cy = cy
        self._fr = fr
        self._fTheta = fTheta
        self._radius = radius
        self._strach = strach
        self._rotate = rotate
        self._color = color
        self._colorAlpha = colorAlpha
        # SingleControl.addParameters(
        #     ['_cx', '_cy', '_fr', '_fTheta', '_radius', '_strach', '_rotate'], self)

    def update(self):
        self._target.update()

    @ pyqtProperty(float)
    def cx(self):
        return self._cx

    @ cx.setter
    def cx(self, value):
        self._cx = value
        self.update()

    @ pyqtProperty(float)
    def cy(self):
        return self._cy

    @ cy.setter
    def cy(self, value):
        self._cy = value
        self.update()

    @ pyqtProperty(float)
    def fr(self):
        return self._fr

    @ fr.setter
    def fr(self, value):
        self._fr = value
        self.update()

    @ pyqtProperty(float)
    def fTheta(self):
        return self._fTheta

    @ fTheta.setter
    def fTheta(self, value):
        self._fTheta = value
        self.update()

    @ pyqtProperty(float)
    def radius(self):
        return self._radius

    @ radius.setter
    def radius(self, value):
        self._radius = value
        self.update()

    @ pyqtProperty(float)
    def strach(self):
        return self._strach

    @ strach.setter
    def strach(self, value):
        self._strach = value
        self.update()

    @ pyqtProperty(float)
    def rotate(self):
        return self._rotate

    @ rotate.setter
    def rotate(self, value):
        self._rotate = value
        self.update()

    @ pyqtProperty(QColor)
    def color(self):
        return self._color

    @ color.setter
    def color(self, value):
        self._color = value
        self.update()

    @ pyqtProperty(int)
    def colorAlpha(self):
        return self._color.alpha()

    @ colorAlpha.setter
    def colorAlpha(self, value: int):
        self._color.setAlpha(value)
        self.update()

    def drawShape(self, painter: QPainter):

        grad = QRadialGradient()
        # print(color.getRgb())
        grad.setCenter(0, 0)
        fr = self._fr/100
        if fr > 0.89:
            fr = 0.89
        elif fr < -0.89:
            fr = -0.89

        fTheta = math.radians(self._fTheta)
        grad.setFocalPoint(fr*math.cos(fTheta), fr*math.sin(fTheta))
        grad.setFocalRadius(0.1)
        # grad.setFocalPoint(0, 0)
        grad.setRadius(1)
        grad.setColorAt(0, self._color)
        grad.setColorAt(1, tc.getTransprent())
        # grad.setCoordinateMode(grad.CoordinateMode.StretchToDeviceMode)

        painter.setBrush(grad)
        painter.translate(self._cx, self._cy)
        painter.rotate(self._rotate)
        radius = self._radius / 2
        painter.scale(radius+(radius*self._strach/100), radius)
        # painter.drawEllipse(QPoint(0, 0), 1, 1)
        painter.drawEllipse(QPoint(0, 0), 1, 1)
        painter.resetTransform()

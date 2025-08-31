from PyQt5.QtGui import *
from PyQt5.QtCore import QObject, QPoint, QRect
from PyQt5.QtWidgets import QWidget
from GUI import ThemeColors as tc
from GUI.GUIControlSet import RectControl, SingleControl
import enum


class BallRing(QObject):
    class Mode(enum.Enum):
        Normal = 1
        Loading = 2

    def __init__(self, widget: QWidget, rect: QRect, mode: Mode) -> None:
        super().__init__()

        self.mode = mode
        self.widget = widget
        self.widget.paintEvent = self.paintEvent
        self.setRect(rect)
        self.ringThickness = 8
        self.glowThickness = 0
        # range 0-255
        self.glowStartAlpha = 140
        # range 0-360 rotation of ball ring
        self.rotation = -90
        QRect().getRect
        # 4 integers whose sum must be 360
        # This contain rLength for init
        self.initRLength = QRect(90, 90, 90, 90)
        # This contain rLength for current (get modified by animations)
        self.rLength = self.initRLength
        # range 0-100
        self.totalDarkness = 0

        # Animation Init

        # TotalDarkness
        # self.TDAnime = Anime.BRringTotalDarkness(self)
        # # Ring rotation animation
        # self.rotationAnime = Anime.BRringRotation(self)
        # # Ring colors radian animation
        # self.colorsRadianAnime = Anime.BRringColorRadina(self)
        # # ring Thickness animation
        # self.ringThicknessAnime = Anime.BRringThickness(self)
        # State Init

        # Adding controls
        SingleControl.addParameters(
            ['ringThickness', 'glowThickness', 'glowStartAlpha', 'rotation'], self)
        RectControl.addParameters(['initRLength'], self)
        # AnimationControl.addParameters(
        #     ['rotationAnime', 'TDAnime', 'ringThicknessAnime'], self, int)
        # AnimationControl.addParameters(['colorsRadianAnime'], self, QRect)
        import config
        config.joiner.setBallRingTD.connect(self.setTD)

    def setRect(self, rect):
        self.rect = rect
        self.center = QPoint(rect.x() + rect.width() // 2,
                             rect.y() + rect.height() // 2)
        self.minRadius = rect.width() // 2

    def setStartAlpha(self, a):
        self.glowStartAlpha = a
        self.update()

    def setTD(self, td):
        self.totalDarkness = td
        self.update()

    def update(self):

        self.widget.update()

    def paintEvent(self, a0: QPaintEvent):
        self.grad = QRadialGradient(
            self.center, self.minRadius + self.ringThickness + self.glowThickness)
        # QWidget.paintEvent(self.widget, a0)
        painter = QPainter(self.widget)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QColor(0, 0, 0, 0))

        painter.setBrush(self.grad)
        # cmode = painter.compositionMode()
        # painter.setCompositionMode(
        #     QPainter.CompositionMode.CompositionMode_Source)
        # painter.drawEllipse(self.center, self.minRadius, self.minRadius)
        if self.mode == self.Mode.Normal:
            self.drawRingPart(0, painter, tc.getColor('ballRing0'))
            self.drawRingPart(1, painter, tc.getColor('ballRing1'))
            self.drawRingPart(2, painter, tc.getColor('ballRing2'))
            self.drawRingPart(3, painter, tc.getColor('ballRing3'))
        elif self.mode == self.Mode.Loading:
            self.drawRingPart(0, painter, tc.getColor('loadingStrip'))
            self.drawRingPart(1, painter, tc.getColor('loadingStripBackground'))

        # painter.setCompositionMode(cmode)
        painter.end()

    def drawRingPart(self, rno: int, painter: QPainter, color):
        # Don't draw if arc length is 0
        if self.rLength.getRect()[rno] == 0:
            return

        p1 = self.minRadius / \
            (self.minRadius + self.glowThickness + self.ringThickness)

        p2 = (self.minRadius + self.ringThickness) / \
            (self.minRadius + self.glowThickness + self.ringThickness)
        # inner empty circle
        c1 = tc.getTransprent()
        c2 = tc.getTransprent()

        # Ring color
        c3 = color
        c4 = QColor(c3)
        # Glow color
        c5 = tc.setAlpha(color, self.glowStartAlpha)
        # Dim glow color
        c6 = tc.setAlpha(color, self.glowStartAlpha/4)
        c7 = tc.getTransprent()

        # Setting Total Darkness to c3 to c6
        # Not allowing transprence in TotalDarkness for ring color
        c3 = tc.setTotalDarkness(c3, False, self.totalDarkness/3)
        c4 = tc.setTotalDarkness(c4, False, self.totalDarkness/3)

        # Allowing transprence in TotalDarkness for ring color
        c6 = tc.setTotalDarkness(c6, True, self.totalDarkness)
        c5 = tc.setTotalDarkness(c5, True, self.totalDarkness)

        # inner transpernt circle
        self.grad.setColorAt(0, c1)
        self.grad.setColorAt(p1 - 0.01, c2)

        # Ring
        self.grad.setColorAt(p1, c3)
        self.grad.setColorAt(p2 - 0.01, c4)

        # Bright Glow
        self.grad.setColorAt(p2, c5)

        # Dim glow
        self.grad.setColorAt(p2+(1-p2)/2, c6)
        self.grad.setColorAt(1, c7)

        painter.setBrush(self.grad)
        start = 0
        for i in range(rno):
            start += self.rLength.getRect()[i]

        start += self.rotation

        painter.drawPie(self.crToRect(self.center, self.minRadius + self.ringThickness +
                                      self.glowThickness), -start*16-10, -self.rLength.getRect()[rno]*16-20)

    def crToRect(self, center: QPoint, radius):
        return QRect(center.x()-radius, center.y()-radius, radius*2, radius*2)

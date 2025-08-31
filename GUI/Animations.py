import math
import random as rand
import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor
import random

from GUI.BallRing import BallRing
from GUI.GUIControlSet import AnimationControl


class textFade(QPropertyAnimation):
    """
    Animation for QLable.
    When new text appended, apply fade in animation to appended text 
    """

    def __init__(self, text: QLabel, color: QColor):
        super(textFade, self).__init__()
        self.color = color
        self._textTransprency = 0
        self.text = text
        self.oldText = ""
        self.newText = ""

        self.setTargetObject(self)
        self.setPropertyName(b'textTransprency')
        self.setDuration(100)
        self.setStartValue(0)
        self.setEndValue(255)

    def findChange(self, old: str, new: str):
        i = 0
        j = min(len(old), len(new))
        while i < j:
            if old[i] != new[i]:
                break
            i += 1

        return old[:i], new[i:]

    def start(self, s: str) -> None:
        self.oldText = self.newText
        self.newText = s
        super().start()

    @pyqtProperty(int)
    def textTransprency(self):
        return self._textTransprency

    @textTransprency.setter
    def textTransprency(self, value):
        self._textTransprency = value
        old, new = self.findChange(self.oldText, self.newText)
        op = old + \
             f'<span style="color:rgba({self.color.red()},{self.color.green()},{self.color.blue()},{value})">' + new + '<\span>'
        self.text.setText(op)


class BRingTotalDarkness(QPropertyAnimation):
    """
    This animation make ballRing and it's glow 
    increase and decrease brigthness
    """

    def __init__(self, ballRing: BallRing) -> None:
        super(BRingTotalDarkness, self).__init__()
        self.ballRing = ballRing
        self.setTargetObject(self)
        self.setPropertyName(b'totalDarkness')
        # self.start()

    @pyqtProperty(float)
    def totalDarkness(self):
        return self.ballRing.totalDarkness

    @totalDarkness.setter
    def totalDarkness(self, td: float):
        self.ballRing.totalDarkness = td
        self.ballRing.update()


class BRingRotation(QPropertyAnimation):
    """
    This is rotation animation of ball ring
    """

    def __init__(self, ballRing: BallRing) -> None:
        super(BRingRotation, self).__init__()
        self.ballRing = ballRing
        self.setTargetObject(self)
        self.setPropertyName(b'rotation')
        # self.start()

    @pyqtProperty(float)
    def rotation(self):
        return self.ballRing.rotation

    @rotation.setter
    def rotation(self, td):
        self.ballRing.rotation = td
        self.ballRing.update()


class BRingThickness(QPropertyAnimation):
    """
    This is animation of ball ring to change ring Thickness
    """

    def __init__(self, ballRing: BallRing) -> None:
        super().__init__()
        self.ballRing = ballRing
        self.setTargetObject(self)
        self.setPropertyName(b'ringThickness')

    @pyqtProperty(float)
    def ringThickness(self):
        return self.ballRing.ringThickness

    @ringThickness.setter
    def ringThickness(self, td):
        self.ballRing.ringThickness = td
        self.ballRing.update()


class BRingGlowThickness(QPropertyAnimation):
    """
    This is animation of ball ring to change ring glow thickness
    """

    def __init__(self, ballRing: BallRing) -> None:
        super().__init__()
        self.ballRing = ballRing
        self.setTargetObject(self)
        self.setPropertyName(b'glowThickness')

    @pyqtProperty(float)
    def glowThickness(self):
        return self.ballRing.glowThickness

    @glowThickness.setter
    def glowThickness(self, td):
        self.ballRing.glowThickness = td
        self.ballRing.update()


class BRingColorRadina(QPropertyAnimation):
    """
    This animation changes radian of colors of ring
    """

    def __init__(self, ballRing: BallRing) -> None:
        super(BRingColorRadina, self).__init__()
        self.ballRing = ballRing
        self.setTargetObject(self)
        self.setPropertyName(b'rotation')
        # self.start()

    @pyqtProperty(QRectF)
    def rotation(self):
        return self.ballRing.rLength

    @rotation.setter
    def rotation(self, r: QRectF):
        # r = r.getRect()
        self.ballRing.rLength = r

        self.ballRing.update()


class PopUp(QPropertyAnimation):
    def __init__(self, target: QWidget, maxWidth, maxHeight) -> None:
        super(PopUp, self).__init__()
        self.target = target
        self.setTargetObject(self)
        self.setPropertyName(b'minMaxSize')
        minWidth = maxWidth // 4
        minHeight = maxHeight // 4
        self.setStartValue(QSize(minWidth, minHeight))
        self.setEndValue(QSize(maxWidth, maxHeight))
        self.setDuration(700)
        self.setEasingCurve(QEasingCurve.Type.OutBack)
        self.finished.connect(lambda: target.setMaximumHeight(1000))

    @pyqtProperty(QSize)
    def minMaxSize(self):
        return self.target.minimumSize()

    @minMaxSize.setter
    def minMaxSize(self, s: QSize):
        self.target.setMinimumSize(s)
        self.target.setMaximumSize(s)


class SlideUpDown(QPropertyAnimation):
    def __init__(self, target: QWidget, maxHeight) -> None:
        super().__init__()
        self.target = target
        self.setTargetObject(self)
        self.setPropertyName(b'minMaxHeight')
        self.setStartValue(0)
        self.setEndValue(maxHeight)
        self.setDuration(700)
        self.setEasingCurve(QEasingCurve.Type.InOutBack)

    @pyqtProperty(int)
    def minMaxHeight(self):
        return self.target.minimumHeight()

    @minMaxHeight.setter
    def minMaxHeight(self, s: QSize):
        if s < 0:
            s = 0
        self.target.setMinimumHeight(s)
        self.target.setMaximumHeight(s)

    def slidUp(self):
        self.setDirection(self.Direction.Forward)
        self.start()

    def slidDown(self):
        self.setDirection(self.Direction.Backward)
        self.start()


class FadeInOut(QPropertyAnimation):
    def __init__(self, target: QWidget, ):
        super().__init__()
        self.setStartValue(0)
        self.setEndValue(1)
        self.setPropertyName(b'opacity')
        self.finished.connect(self.fadeOutEnd)
        self.target = target

    def fadeIn(self):
        self.effect = QGraphicsOpacityEffect()
        self.effect.setOpacity(self.startValue())
        self.setTargetObject(self.effect)
        self.target.setGraphicsEffect(self.effect)
        # self.setPropertyName(b'opacity')
        self.setDirection(self.Direction.Forward)
        self.target.show()
        self.start()

    def fadeOut(self):
        self.effect = QGraphicsOpacityEffect()
        self.effect.setOpacity(self.endValue())
        self.setTargetObject(self.effect)
        self.target.setGraphicsEffect(self.effect)
        # self.setPropertyName(b'opacity')
        self.setDirection(self.Direction.Backward)
        self.start()

    def fadeOutEnd(self):
        if self.direction() == self.Direction.Backward:
            self.target.hide()


class Blur(QPropertyAnimation):
    def __init__(self, target: QWidget, ):
        super().__init__()
        self.setStartValue(0)
        self.setEndValue(8)
        self.setDuration(750)
        self.setEasingCurve(QEasingCurve.Type.OutBack)
        self.setPropertyName(b'blurRadius')
        self.target = target

    def blur(self):
        self.effect = QGraphicsBlurEffect()
        self.effect.setBlurRadius(self.startValue())
        self.setTargetObject(self.effect)
        self.target.setGraphicsEffect(self.effect)
        self.setDirection(self.Direction.Forward)
        self.start()

    def clear(self):
        self.effect = QGraphicsBlurEffect()
        self.effect.setBlurRadius(self.startValue())
        self.setTargetObject(self.effect)
        self.target.setGraphicsEffect(self.effect)
        self.setDirection(self.Direction.Backward)
        self.start()


class RandomAnimationGroup():
    def __init__(self, targetList, propertyList):
        super().__init__()
        self.targetList = targetList
        self.animeList = []
        for target in targetList:
            for pro in propertyList:
                self.anime = Random(pro[1], pro[2], pro[3], pro[4], pro[5], target, bytes(
                    (pro[0].encode())))
                self.anime.start()
                self.animeList.append(self.anime)


class SpinInOut(QParallelAnimationGroup):
    def __init__(self, target: QObject):
        super().__init__()
        self.target = target
        duration = 750
        self.groupRotAnime = QPropertyAnimation(
            target, b'btnGroupRotation', self)
        self.groupRotAnime.setStartValue(340)
        self.groupRotAnime.setEndValue(175)
        self.groupRotAnime.setDuration(duration)
        self.groupRotAnime.setEasingCurve(QEasingCurve.Type.OutBack)

        self.spacingAnime = QPropertyAnimation(
            target, b'btnsSpacing', self)
        self.spacingAnime.setStartValue(-10)
        self.spacingAnime.setEndValue(35)
        self.spacingAnime.setDuration(duration)
        self.spacingAnime.setEasingCurve(QEasingCurve.Type.OutBack)

        self.radiusAnime = QPropertyAnimation(
            target, b'btnsRadius', self)
        self.radiusAnime.setStartValue(0)
        self.radiusAnime.setEndValue(25)
        self.radiusAnime.setDuration(750)
        self.radiusAnime.setEasingCurve(QEasingCurve.Type.OutBack)
        a = self.radiusAnime.easingCurve()
        a.setOvershoot(2.2)
        self.radiusAnime.setEasingCurve(a)

        self.posRadiusAnime = QPropertyAnimation(
            target, b'btnsPosRadius', self)
        self.posRadiusAnime.setStartValue(0)
        self.posRadiusAnime.setEndValue(125)
        self.posRadiusAnime.setDuration(duration)
        self.posRadiusAnime.setEasingCurve(QEasingCurve.Type.OutBack)

        self.addAnimation(self.groupRotAnime)
        self.addAnimation(self.spacingAnime)
        self.addAnimation(self.radiusAnime)
        self.addAnimation(self.posRadiusAnime)
        self.finished.connect(self.spinInEnd)

        AnimationControl.addParameters(
            ['groupRotAnime', 'spacingAnime', 'radiusAnime', 'posRadiusAnime'], self, float)

    def spinOut(self, theta):
        self.target.show()
        self.groupRotAnime.setStartValue(theta - 165)
        self.groupRotAnime.setEndValue(theta)
        self.setDirection(self.Direction.Forward)
        self.start()

    def spinIn(self, theta):
        self.groupRotAnime.setStartValue(theta - 165)
        self.groupRotAnime.setEndValue(theta)
        self.setDirection(self.Direction.Backward)
        self.start()

    def spinInEnd(self):
        if self.direction() == self.Direction.Backward:
            self.target.hide()


class Random(QPropertyAnimation):
    def __init__(self, minVal, maxVal, diff, minDur, maxDur, target, property=None):
        super().__init__()
        self.property_ = property
        self.target = target
        self.minVal = minVal
        self.maxVal = maxVal
        self.minDur = minDur
        self.maxDur = maxDur
        self.diff = diff
        if isinstance(target, QPropertyAnimation):
            target.setEndValue(rand.randint(minVal, maxVal))
            target.finished.connect(lambda: self.restart(target))
            self.start = target.start
            self.stop = target.stop
        else:
            self.setEndValue(rand.randint(minVal, maxVal))
            self.setPropertyName(property)
            self.setTargetObject(target)
            self.finished.connect(lambda: self.restart(self))

    def restart(self, target: QPropertyAnimation):
        val = target.currentValue()
        target.setStartValue(val)
        min = val - self.diff
        if (min < self.minVal):
            min = self.minVal
        max = val + self.diff
        if (max > self.maxVal):
            max = self.maxVal

        # print("min: ", min, "max: ", max, self.maxVal)
        target.setEndValue(rand.randint(min, max))
        target.setDuration(rand.randint(self.minDur, self.maxDur))
        # self.setEasingCurve(QEasingCurve.Type(rand.randint(0, 10)))
        target.start()


class Hover(QPropertyAnimation):
    def __init__(self, propertyTarget, property: str, hoverTarget, initRadius):
        super().__init__()
        self.propertyTarget = propertyTarget
        self.property = property
        self.hoverTarget = hoverTarget

        self.target = propertyTarget
        self.setTargetObject(propertyTarget)
        self.setPropertyName(bytes(property.encode()))
        hoverTarget.setMouseTracking(True)
        self.setStartValue(initRadius)
        self.setEndValue(initRadius * 1.2)
        self.setDuration(70)
        self.setEasingCurve(QEasingCurve.Type.OutSine)

        self.oldEnterEvent = hoverTarget.enterEvent
        self.oldLeaveEvent = hoverTarget.leaveEvent
        hoverTarget.enterEvent = self.enterEvent
        hoverTarget.leaveEvent = self.leaveEvent

    def enterEvent(self, event: QEvent):
        self.oldEnterEvent(event)
        self.setDirection(self.Direction.Forward)
        self.start()

    def leaveEvent(self, event):
        self.oldLeaveEvent(event)
        self.setDirection(self.Direction.Backward)
        self.start()


class MoveBallToBoundary(QPropertyAnimation):
    def __init__(self, mainUI, boundary: QRect):
        super(MoveBallToBoundary, self).__init__()
        self.__mainUI__ = mainUI
        self.__boundary__ = boundary
        self.setTargetObject(mainUI)
        self.setPropertyName(b'ballGlobalCenterPos')
        self.setEasingCurve(QEasingCurve.Type.OutExpo)
        self.setDuration(800)

    def move(self):
        end = QPoint(self.__mainUI__.ballGlobalCenterPos)
        ldiff = abs(self.__boundary__.left() - end.x())
        rdiff = abs(self.__boundary__.right() - end.x())
        tdiff = abs(self.__boundary__.top() - end.y())
        bdiff = abs(self.__boundary__.bottom() - end.y())

        l = [ldiff, rdiff, tdiff, bdiff]
        i = l.index(min(l))
        if i == 0:
            end.setX(self.__boundary__.left())
        elif i == 1:
            end.setX(self.__boundary__.right())
        if i == 2:
            end.setY(self.__boundary__.top())
        if i == 3:
            end.setY(self.__boundary__.bottom())

        self.setStartValue(self.__mainUI__.ballGlobalCenterPos)
        self.setEndValue(end)
        self.start()


class Loading(QObject):
    finished = pyqtSignal()

    def __init__(self, ballRing, text, mainUI, finalPos):
        super(Loading, self).__init__()
        self.__progress__ = 0.0
        self.__ballRing__ = ballRing
        self.__text__ = text
        self.progress = 0.0
        self.maxProgressStep = 100
        self.loadPausePer = 70 + random.random() * 25
        self.div = 10

        self.loadAnime = QPropertyAnimation(self, b'progress')
        self.loadAnime.setDuration(150)
        self.loadAnime.finished.connect(self.loadAnimeLoop)

        dur = 1200
        self.afterLoadAnime = QParallelAnimationGroup()

        self.moveAnime = QPropertyAnimation(mainUI, b'ballGlobalCenterPos')
        self.moveAnime.setEndValue(finalPos)
        self.moveAnime.setDuration(dur)
        self.moveAnime.setEasingCurve(QEasingCurve.Type.OutExpo)

        self.glowThicknessAnime = BRingGlowThickness(ballRing)
        self.glowThicknessAnime.setEndValue(25)
        self.glowThicknessAnime.setDuration(dur)

        self.ballRadiusAnime = QPropertyAnimation(mainUI, b'ballRadius')
        self.ballRadiusAnime.setEndValue(45)
        self.ballRadiusAnime.setDuration(dur)
        self.ballRadiusAnime.setEasingCurve(QEasingCurve.Type.OutExpo)

        AnimationControl.addParameters(['moveAnime'], self, None)
        self.afterLoadAnime.addAnimation(self.moveAnime)
        self.afterLoadAnime.addAnimation(self.glowThicknessAnime)
        self.afterLoadAnime.addAnimation(self.ballRadiusAnime)
        self.loadAnimeLoop()

    def completeLoading(self):
        self.loadAnime.setStartValue(self.progress)
        self.loadAnime.stop()
        self.loadAnime.setEndValue(100)
        self.loadAnime.setDuration((100 - self.progress) * 80)
        self.loadAnime.setLoopCount(1)
        self.loadAnime.finished.disconnect(self.loadAnimeLoop)
        self.loadAnime.finished.connect(self.finished.emit)
        self.loadAnime.finished.connect(self.afterLoadAnime.start)
        self.loadAnime.start()


    def loadAnimeLoop(self):
        self.loadAnime.setStartValue(self.loadAnime.endValue())
        self.div += 0.8
        end = self.progress + min(self.maxProgressStep,
                                  (self.loadPausePer - self.progress) / self.div)
        self.loadAnime.setEndValue(end)
        self.loadAnime.start()

    @pyqtProperty(float)
    def progress(self):
        return self.__progress__

    @progress.setter
    def progress(self, per: float):
        self.__text__.setText("{:.0f}%".format(per))
        self.__progress__ = per
        per = per * 360 / 100
        self.__ballRing__.rLength = QRectF(per, 360 - per, 0, 0)
        self.__ballRing__.update()

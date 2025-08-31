import sys
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtGui import *
from GUI import Animations as anime, GUIControlSet, Controls, utility
from GUI import console
from GUI.DataInput import DataInputBox
from GUI.States import *
from GUI.BallRing import BallRing
from GUI.LiveBackground import LiveBackground
from GUI.MesBox import MesBox
import config
import GUI.ThemeColors as tc


class MainUI(QWidget):
    ballClicked = QtCore.pyqtSignal(QtGui.QMouseEvent)

    def __init__(self):
        super(MainUI, self).__init__()
        self.loadStyleSheet()

        uic.loadUi("GUI/UI_Files/MainUI_UI.ui", self)
        center = QPoint(self.width() // 2, self.height() // 2)

        self.moveByCenter(self.ball, center)
        self.moveByCenter(self.controlButtonPlaceholder, center)
        config.controlPanel.add(console.LiveConsole(self.fun))

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        # To remove error of frame nt going outside screen in linux only
        self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        rePaintButton = QPushButton('rePaint')
        rePaintButton.adjustSize()
        rePaintButton.clicked.connect(self.rePaint)
        config.controlPanel.add(rePaintButton)
        self.chatBoxScrollArea.verticalScrollBar().hide()
        self.chatBoxScrollArea.horizontalScrollBar().hide()
        self.background.hide()
        self.initPropertyVariables()
        self.isChatBoxShow = False
        self.initChatBox()
        self.isControlsShow = False
        self.initControls()
        self.initBall()
        self.liveBackground = LiveBackground(self.background)
        self.updateMouseEventTransparentRegion()

    def initAfterLoadingScreen(self):
        self.ballRing.mode = BallRing.Mode.Normal
        self.ballButton.setText('V')
        self.ballButtonTextRadiusRatio = 0.4
        self.ballResizeEvent(None)
        # Allow mouse event

        self.stateManager = StateManager(self.ballRing, 'ideal')

    def initBall(self):
        self.ballButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.ballButtonTextRadiusRatio = 0.2
        self.ballRing = BallRing(
            self.ball, self.ballButton.geometry(), BallRing.Mode.Loading)
        self.oldBallResizeEvent = self.ball.resizeEvent
        self.ballButton.resizeEvent = self.ballResizeEvent
        self.ballRadius = 70

        self.ballHoverAnime = anime.Hover(
            self, 'ballRadius', self.ballButton, 40)
        self.moveBallToBoundaryAnime = anime.MoveBallToBoundary(self, self.__boundary__)
        self.moveBallToBoundaryAnime.finished.connect(self.updateMouseEventTransparentRegion)

        self.isBallMoved = False

        self.oldBallMouseReleaseEvent = self.ballButton.mouseReleaseEvent
        self.ballButton.mouseReleaseEvent = self.ballMouseReleaseEvent

        self.oldBallMouseMoveEvent = self.ballButton.mouseMoveEvent
        self.ballButton.mouseMoveEvent = self.ballMouseMoveEvent

        self.ballGlobalCenterPos = config.screen.center()

        self.loadingAnime = anime.Loading(
            self.ballRing, self.ballButton, self, self.__boundary__.bottomRight())
        self.loadingAnime.finished.connect(self.initAfterLoadingScreen)
        self.loadingAnime.afterLoadAnime.finished.connect(lambda: self.ballButton.removeEventFilter(self))
        # Block Mouse Event
        self.ballButton.installEventFilter(self)

        self.ballButton.mouseDoubleClickEvent = lambda a :self.toggleChatBoxVisibility()
        # self.initAfterLoadingScreen()

    def initControls(self):
        center = QRectF(self.ball.geometry()).center()
        center = center - self.controlButtonPlaceholder.geometry().topLeft()
        self.controlManager = Controls.ControlManager(
            self.controlButtonPlaceholder, center, self.updateMouseEventTransparentRegion)
        self.ControlsSpinInOutAnime = SpinInOut(self.controlManager)

    def initChatBox(self):
        self.chatBoxPolarPosRadius = 340
        self.chatBoxPolarPosTheta = -180
        self.chatBoxFadeAnime = anime.FadeInOut(self.background)
        self.chatBoxFadeAnime.finished.connect(self.updateMouseEventTransparentRegion)
        self.chatBoxBlurAnime = anime.Blur(self.background)
        # GUIControlSet.AnimationControl.addParameters(
        #     ['chatBoxFadeAnime', 'chatBoxBlurAnime'], self, float)

        self.cbLayout = QVBoxLayout(self.chatBox)
        self.cbLayout.setContentsMargins(15, 0, 0, 0)
        self.chatBox.setLayout(self.cbLayout)
        self.cbLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom)
        self.currMesBox: MesBox = None

        # Making rounded corners for background widget
        radius = 20.0
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(
            self.background.rect()), radius, radius)

        mask = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.background.setMask(mask)
        # self.move(QtGui.QCursor.pos())

        self.chatBoxScrollArea.verticalScrollBar().setFixedWidth(5)
        self.chatBoxScrollArea.verticalScrollBar().hide()

        # Set scroll bar always at bottom
        self.chatBoxScrollArea.verticalScrollBar().rangeChanged.connect(
            lambda a, b: self.chatBoxScrollArea.verticalScrollBar().setValue(b))
        self.isKIWDisabled = False
        self.KIWHideTimer = QtCore.QTimer(self)
        self.KIWHideTimer.setSingleShot(True)
        self.KIWHideTimer.timeout.connect(self.hideKIW)
        self.isKIWHidden = True
        self.keyInputWidget.setMinimumWidth(self.background.width())
        # SlideUpDown Animation for keyInputWidget
        self.KIWAnime = anime.SlideUpDown(
            self.keyInputWidget, self.keyInputWidget.minimumHeight())
        self.keyInputWidget.setMinimumHeight(0)
        self.keyInputWidget.setMaximumHeight(0)
        self.keyInput.editingFinished.connect(
            lambda: self.KIWHideTimer.start(2000))
        self.keyInput.focusOutEvent = lambda a: self.KIWHideTimer.start(2000)

        self.keyInput.textChanged.connect(
            lambda a: self.KIWHideTimer.start(10000))
        # GUIControlSet.AnimationControl.addParameters(
        #     ['KIWAnime', 'ballHoverAnime'], self, int)
        GUIControlSet.SingleControl.addParameters(['chatBoxPolarPosTheta', 'chatBoxPolarPosRadius'], self)

        self.loadRunButtonIcon()

        def enterKeyInput():
            if self.keyInput.text() != '':
                self.addMesBox('user', self.keyInput.text())
                config.joiner.keyInput.emit(self.keyInput.text())
                # self.setMesBoxText(self.keyInput.text())
                self.keyInput.blockSignals(True)
                self.keyInput.setText('')
                self.keyInput.blockSignals(False)

        self.run.clicked.connect(enterKeyInput)

    def initPropertyVariables(self):
        self.__ballRadius__ = 0
        self.__ballGlobalCenterPos__: QPoint = QPoint()
        self.__boundary__ = QRect(config.screen)
        boundaryMargin = 80
        self.__boundary__.setX(self.__boundary__.x() + boundaryMargin)
        self.__boundary__.setY(self.__boundary__.y() + boundaryMargin)
        self.__boundary__.setWidth(self.__boundary__.width() - boundaryMargin)
        self.__boundary__.setHeight(self.__boundary__.height() - boundaryMargin)
        self.__chatBoxPolarPos__: QPointF = QPointF()
        self.__chatBoxPolarPosTheta__ = 0
        self.__chatBoxPolarPosRadius__ = 0
        self.__chatBoxPolarPosCenter__ = self.ball.geometry().center()

    # Stop mouse and hover event
    def eventFilter(self, obj, event: QEvent):
        if obj == self.ballButton and \
                ((type(event) == QMouseEvent) or
                 event.type() in
                 (event.Type.Enter, event.Type.Leave)):
            return True
        return super(type(obj), obj).eventFilter(obj, event)

    def loadRunButtonIcon(self):
        self.run.setIcon(QtGui.QIcon(
            utility.loadPixmap('GUI/resource/send.svg', 'text')))
        self.run.setIconSize(QtCore.QSize(30, 30))

    def rePaint(self):
        self.loadStyleSheet()
        self.loadRunButtonIcon()
        self.controlManager.loadIcons()

    def loadStyleSheet(self):
        file = open("GUI/StyleSheet.css", 'r')
        text = file.read()
        table = {
            'keyInputWidgetBackground': f'rgba{tc.toRGBAStr(tc.getSurfaceColor(25))}',
            'unFocusBackground': f'rgba{tc.toRGBAStr(tc.getSurfaceColor(40))}',
            'unFocusBorderColor': f'rgba{tc.toRGBAStr(tc.getSurfaceColor(100))}',
            'hoverBackground': f'rgba{tc.toRGBAStr(tc.setAlpha("text", 20))}',
            'hoverBorderColor': f'rgba{tc.toRGBAStr(tc.setAlpha("text", 120))}',
            'focusBackground': f'rgba{tc.toRGBAStr(tc.getSurfaceColor(50))}',
            'focusBorderColor': f'rgba{tc.toRGBAStr(tc.setAlpha("text", 180))}',
            'ballUnFocusBackground': f'rgba{tc.toRGBAStr("main")}',
            'ballHoverBackground': f'rgba{tc.toRGBAStr("background")}',

            'textColor': f'rgba{tc.toRGBAStr(tc.getColor("text"))}',
            'mesBoxTextBackgroundColor': f'rgba{tc.toRGBAStr(tc.getSurfaceColor(30))}',

            'controlButtonOnBackground': f'rgb{tc.toRGBStr("main")}',
            'controlButtonOnBorderColor': f'rgb{tc.toRGBStr("primary")}',
            'controlButtonOnHoverBorderColor': f'rgb{tc.toRGBStr(tc.getLighter("primary", 120))}',
            'controlButtonOnHoverbackground': f'rgb{tc.toRGBStr("background")}',

            'controlButtonOffBackground': f'rgb{tc.toRGBStr("background")}',
            'controlButtonOffBorderColor': f'rgb{tc.toRGBStr(tc.getLighter("text", 60))}',
            'controlButtonOffHoverBorderColor': f'rgb{tc.toRGBStr(tc.getLighter("text", 80))}',
            'controlButtonOffHoverbackground': f'rgb{tc.toRGBStr(tc.getLighter("background", 120))}',

            'dataInputBoxBorderColor': f'rgba{tc.toRGBAStr("main")}',
            'dataInputEditFocusBackground': f'rgba{tc.toRGBAStr(tc.getSurfaceColor(75))}',
            'DataInputButtonPressedBackground': f'rgba{tc.toRGBAStr("main")}',
            'dataInputBoxDisableButtonBackground': f'rgba{tc.toRGBAStr("surfaceDiabled")}',
            'dataInputBoxDisableButtonBorderColor': f'rgba{tc.toRGBAStr("surfaceBorderDiabled")}',
            'dataInputBoxDisableButtonTextColor': f'rgba{tc.toRGBAStr("surfaceTextDiabled")}',

        }

        for key, value in table.items():
            text = text.replace('/*' + key + '*/', value)
        # print(text)
        self.setStyleSheet(text)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        # Esc key pressed
        if self.isKIWDisabled:
            return
        if event.key() == 16777216:
            self.hideKIW()
        else:
            self.showKIW()
            self.keyInput.setFocus()
            self.keyInput.keyPressEvent(event)

    def showKIW(self):

        if self.isKIWHidden:
            # print('show___')
            # config.joiner.setControlButtonState.emit('mic', False)
            self.isKIWHidden = False
            self.KIWAnime.slidUp()

    def hideKIW(self):
        if not self.isKIWHidden:
            # print('hide_________')
            # config.joiner.setControlButtonState.emit('mic', True)
            self.isKIWHidden = True
            self.setFocus()
            self.KIWAnime.slidDown()

    def addMesBox(self, type, text=None):
        if type == 'assistent':
            self.currMesBox = MesBox('left', text)
            self.cbLayout.addWidget(self.currMesBox)
        if type == 'user':
            self.currMesBox = MesBox('right', text)
            self.cbLayout.addWidget(self.currMesBox)

    def addDataInputBox(self, title, dataFrame):
        print('DataInputBox Inserted')
        config.isBoxOn = True

        self.setChatBoxVisibility(True)
        self.hideKIW()
        self.isKIWDisabled = True
        self.dib = DataInputBox(title, dataFrame, self.beforeDataInputBoxDelete)
        self.cbLayout.addWidget(self.dib)
        self.dib.slidUp()

    def beforeDataInputBoxDelete(self):
        self.cbLayout.removeWidget(self.dib)
        self.isKIWDisabled = False

    def setMesBoxText(self, text: str):
        self.currMesBox.setText(text)

    def fun(self, text):
        try:
            exec(text.text())
        except Exception as e:
            print('Console Error: ', e)

    def ballMouseMoveEvent(self, event: QMouseEvent):
        self.oldBallMouseMoveEvent(event)
        if event.buttons() & Qt.LeftButton:
            self.clearMask()
            self.isBallMoved = True
            x, y = event.globalPos().x(), event.globalPos().y()
            x = max(self.__boundary__.left(), x)
            x = min(self.__boundary__.right(), x)
            y = max(self.__boundary__.top(), y)
            y = min(self.__boundary__.bottom(), y)
            pos = QPoint(x, y)
            self.ballGlobalCenterPos = pos

    def ballMouseReleaseEvent(self, event: QMouseEvent):
        self.oldBallMouseReleaseEvent(event)
        # if ball is moved then don't perform clicked actions
        if self.isBallMoved:
            self.isBallMoved = False
            self.moveBallToBoundaryAnime.move()
        # if controls are showing then hide it anyway
        elif self.isControlsShow:
            self.ControlsSpinInOutAnime.spinIn(self.__centerRefAngle__)
            self.chatBoxBlurAnime.clear()
            self.isControlsShow = False
        # if control are hide and right clicked then show controls
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.ControlsSpinInOutAnime.spinOut(self.__centerRefAngle__)
            self.isControlsShow = True
            self.chatBoxBlurAnime.blur()
        elif event.button() == QtCore.Qt.MouseButton.LeftButton:
            config.joiner.startListening.emit()

    def setChatBoxVisibility(self, show):
        if show and not self.isChatBoxShow:
            self.chatBoxFadeAnime.fadeIn()
            self.updateMouseEventTransparentRegion()
            self.isChatBoxShow = True
        elif not show and self.isChatBoxShow:
            self.chatBoxFadeAnime.fadeOut()
            self.isChatBoxShow = False

    def toggleChatBoxVisibility(self):
        self.setChatBoxVisibility(not self.isChatBoxShow)

    @pyqtProperty(float)
    def ballRadius(self):
        return self.__ballRadius__

    @ballRadius.setter
    def ballRadius(self, val):
        self.__ballRadius__ = val
        center = (self.ball.width() / 2, self.ball.height() / 2)
        self.ballButton.setGeometry(
            center[0] - val, center[1] - val, +val * 2, val * 2)
        self.ballButton.setStyleSheet(f'border-radius:{int(val)}')
        self.ballRing.setRect(self.ballButton.geometry())
        self.ball.update()

    def ballResizeEvent(self, event):
        self.oldBallResizeEvent(event)
        f = self.ballButton.font()
        f.setPointSize(self.ballButtonTextRadiusRatio * self.ballButton.width())
        self.ballButton.setFont(f)

    @pyqtProperty(QPoint)
    def ballGlobalCenterPos(self):
        return self.__ballGlobalCenterPos__

    @ballGlobalCenterPos.setter
    def ballGlobalCenterPos(self, pos):
        center = self.ball.mapTo(self, QPoint(0, 0)) + \
                 QPoint(self.ball.width() / 2, self.ball.height() / 2)
        self.move((pos - center))
        self.__ballGlobalCenterPos__ = pos
        rpos = pos - self.__boundary__.center()
        if (rpos.x() == 0):
            rpos.setX(1)
        theta = math.degrees(math.atan(rpos.y() / rpos.x()))
        if (rpos.x() > 0):
            theta += 180
        self.chatBoxPolarPosTheta = theta
        self.controlManager.btnGroupRotation = theta
        self.__centerRefAngle__ = theta

    @pyqtProperty(float)
    def chatBoxPolarPosTheta(self):
        return self.__chatBoxPolarPosTheta__

    @chatBoxPolarPosTheta.setter
    def chatBoxPolarPosTheta(self, theta):
        self.__chatBoxPolarPosTheta__ = theta
        self.updateChatBoxPos()

    @pyqtProperty(float)
    def chatBoxPolarPosRadius(self):
        return self.__chatBoxPolarPosRadius__

    @chatBoxPolarPosRadius.setter
    def chatBoxPolarPosRadius(self, radius):
        self.__chatBoxPolarPosRadius__ = radius
        self.updateChatBoxPos()

    def updateChatBoxPos(self):
        add = abs(self.__chatBoxPolarPosTheta__) % 90
        if add > 45:
            add = 90 - add

        if add < 18:
            add /= 4
        else:
            add -= 15

        theta = math.radians(self.__chatBoxPolarPosTheta__)

        radius = self.__chatBoxPolarPosRadius__ + add * 2.5
        # print(add,radius)

        x = radius * math.cos(theta)
        y = radius * math.sin(theta) / 1.6
        point = QPointF(x, y) + self.__chatBoxPolarPosCenter__ - QPointF(self.background.size().width() // 2,
                                                                         self.background.size().height() // 2)

        self.background.move(point.toPoint())
        # self.updateMouseEventTransparentRegion()

    def updateMouseEventTransparentRegion(self):
        self.setMask(self.childrenRegion())
        pass

    def moveByCenter(self, widget: QWidget, pos: QPoint):
        pos = QPoint(pos.x() - widget.width() // 2, pos.y() - widget.height() // 2)
        widget.move(pos)


if __name__ == '__main__':

    def fun(text):
        try:
            exec(text.text())
        except Exception as e:
            print('Console Error: ', e)


    app = QApplication(sys.argv)
    mainUI = MainUI()
    mainUI.show()
    # console.LiveConsole(fun)
    exit(app.exec())

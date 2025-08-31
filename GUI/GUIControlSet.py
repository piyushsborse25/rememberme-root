from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *


class ControlPanel(QWidget):
    def __init__(self):
        super(ControlPanel, self).__init__()
        self.layout = FlowLayout()
        self.setLayout(self.layout)
        self.setGeometry(30, 30, 1000, 800)

    def add(self, obj: QWidget):
        obj.setMinimumSize(obj.size())
        self.layout.addWidget(obj)
        # obj.setLayout(FlowLayout())


class SingleControl(QWidget):
    valueChanged = pyqtSignal(str, int, object)

    def __init__(self, title: str, name: str, value: int, shareObj=None):
        super(SingleControl, self).__init__()
        uic.loadUi("GUI/UI_Files/SingalControl.ui", self)
        self.Title.setText(title)
        self.Name.setText(name)
        self.Value.setValue(value)
        self.shareObj = shareObj
        self.Value.valueChanged.connect(
            lambda newVal: self.valueChanged.emit(name, newVal, self.shareObj))
        self.setValue = self.Value.setValue
        import config
        config.controlPanel.add(self)
        self.show()

    @staticmethod
    def addParameters(paraList: list, obj):
        for para in paraList:
            sc = SingleControl(type(obj).__name__, para, getattr(obj, para))

            def fun(name, newVal):
                setattr(obj, name, newVal)
                if hasattr(obj, 'update'):
                    obj.update()
            sc.valueChanged.connect(fun)


class ColorPicker(QWidget):
    def __init__(self, name: str, color: QColor, user: QWidget):
        super(ColorPicker, self).__init__()
        uic.loadUi("GUI/UI_Files/ColorPicker.ui", self)
        self.user = user
        self.color = color
        self.name.setText(name)
        self.dialog = QColorDialog(color, self)
        self.dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel)
        self.preview.setStyleSheet(
            f"background-color: rgba({color.red()}, {color.green()}, {color.blue()},{color.alpha()});")
        # self.dialog.setOptions(
        # self.dialog.ColorDialogOption.NoButtons | self.dialog.ColorDialogOption.ShowAlphaChannel)
        self.preview.mousePressEvent = self.clicked
        self.dialog.currentColorChanged.connect(self.colorChanged)

    def clicked(self, event):
        self.dialog.show()

    def colorChanged(self, newColor: QColor):
        self.color.setRgba(newColor.rgba())
        self.preview.setStyleSheet(
            f"background-color: rgba({newColor.red()}, {newColor.green()}, {newColor.blue()},{newColor.alpha()});")
        self.user.update()

    @staticmethod
    def ThemeColorPickerInit(user: QWidget):
        from GUI.ThemeColors import colorPalette as cp
        for name in cp:
            picker = ColorPicker(name, cp[name], user)
            import config
            config.controlPanel.add(picker)


class RectControl(QWidget):
    valueChanged = pyqtSignal(str, QRect, object)

    def __init__(self, name: str, rect: QRect, user=None, shareObj=None):
        super(RectControl, self).__init__()
        uic.loadUi("GUI/UI_Files/RectControl.ui", self)
        self.user = user
        self.rect: QRect = rect
        self.shareObj=shareObj
        self.name.setText(name)
        self.valX.setValue(rect.x())
        self.valY.setValue(rect.y())
        self.valWidth.setValue(rect.width())
        self.valHeight.setValue(rect.height())

        self.valX.valueChanged.connect(self.onValueChanged)
        self.valY.valueChanged.connect(self.onValueChanged)
        self.valWidth.valueChanged.connect(self.onValueChanged)
        self.valHeight.valueChanged.connect(self.onValueChanged)
        import config
        config.controlPanel.add(self)

    def onValueChanged(self, newVal):
        self.rect.setX(self.valX.value())
        self.rect.setY(self.valY.value())
        self.rect.setWidth(self.valWidth.value())
        self.rect.setHeight(self.valHeight.value())
        if self.user != None and hasattr(self.user, 'update'):
            self.user.update()
        self.valueChanged.emit(self.name.text(), self.rect, self.shareObj)

    def addParameters(paraList: list, obj):
        for para in paraList:
            sc = RectControl(para, getattr(obj, para), obj)


class AnimationControl(QWidget):
    def __init__(self, name: str, anime: QPropertyAnimation):
        super(AnimationControl, self).__init__()
        uic.loadUi("GUI/UI_Files/AnimationControl.ui", self)
        self.pLayout = QHBoxLayout()
        self.pLayout.setSpacing(0)
        self.placeHolder.setLayout(self.pLayout)
        self.Name.setText(name)
        self.Duraction.setValue(anime.duration())
        self.LoopCount.setValue(anime.loopCount())
        self.Play.clicked.connect(anime.start)
        self.Pause.clicked.connect(anime.pause)
        self.Stop.clicked.connect(anime.stop)
        self.Duraction.valueChanged.connect(lambda a: anime.setDuration(a))
        self.LoopCount.valueChanged.connect(lambda a: anime.setLoopCount(a))
        self.Curve.addItems(['Linear', 'InQuad', 'OutQuad', 'InOutQuad', 'OutInQuad', 'InCubic', 'OutCubic', 'InOutCubic', 'OutInCubic', 'InQuart', 'OutQuart', 'InOutQuart', 'OutInQuart', 'InQuint', 'OutQuint', 'InOutQuint', 'OutInQuint', 'InSine', 'OutSine', 'InOutSine', 'OutInSine', 'InExpo', 'OutExpo', 'InOutExpo',
                             'OutInExpo', 'InCirc', 'OutCirc', 'InOutCirc', 'OutInCirc', 'InElastic', 'OutElastic', 'InOutElastic', 'OutInElastic', 'InBack', 'OutBack', 'InOutBack', 'OutInBack', 'InBounce', 'OutBounce', 'InOutBounce', 'OutInBounce', 'InCurve', 'OutCurve', 'SineCurve', 'CosineCurve', 'BezierSpline', 'TCBSpline', 'Custom'])
        self.Curve.setCurrentIndex(int(anime.easingCurve().type().__str__()))

        def fun(i):
            anime.setEasingCurve(QEasingCurve.Type(i))
            anime.start()

        self.Curve.currentIndexChanged.connect(fun)
        import config
        config.controlPanel.add(self)

    def addParameters(paraList: list, obj, property: type):
        for para in paraList:
            anime: QPropertyAnimation = getattr(obj, para)
            sc = AnimationControl(para, anime)

            if property == int or property == float:
                start = SingleControl('', 'start', anime.startValue(), anime)
                end = SingleControl('', 'end', anime.endValue(), anime)
                start.valueChanged.connect(
                    lambda name, val, shareObj: shareObj.setStartValue(val))
                end.valueChanged.connect(
                    lambda name, val, shareObj: shareObj.setEndValue(val))
                sc.pLayout.addWidget(start)
                sc.pLayout.addWidget(end)
            elif property == QRect:
                start = RectControl('start', anime.startValue())
                end = RectControl('end', anime.endValue())
                start.valueChanged.connect(
                    lambda name, val: anime.setStartValue(val))
                end.valueChanged.connect(
                    lambda name, val: anime.setEndValue(val))
                sc.pLayout.addWidget(start)
                sc.pLayout.addWidget(end)
            elif property == QSize:
                r = RectControl('start/end', QRect(anime.startValue().width(),
                                                   anime.startValue().height(),
                                                   anime.endValue().width(),
                                                   anime.endValue().height()),shareObj=anime)

                def fun(str, r: QRect, shareObj):
                    shareObj.setStartValue(QSize(r.x(), r.y()))
                    shareObj.setEndValue(QSize(r.width(), r.height()))

                r.valueChanged.connect(fun)
                sc.pLayout.addWidget(r)


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)

        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margin, _, _, _ = self.getContentsMargins()

        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton,
                                                                QSizePolicy.PushButton, Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton,
                                                                QSizePolicy.PushButton, Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()

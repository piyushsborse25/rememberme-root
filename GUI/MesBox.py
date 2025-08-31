from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from GUI.Animations import PopUp, textFade
from GUI.GUIControlSet import AnimationControl
from GUI import ThemeColors as tc


class MesBox(QWidget):
    width_ = 470
    height_ = 50

    def __init__(self, side: str, text: str = None):
        super(MesBox, self).__init__()
        print("Mes Box Started")
        self.setObjectName('MesBox')
        width_ = MesBox.width_
        height_ = MesBox.height_
        self.setContentsMargins(7, 10, 7, 10)
        # self.setMaximumSize(width_, height_)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        # Range 0-100
        self.textMaxWidthPersentage = 35
        self.setMinimumSize(0, 0)
        self.elevation = 3
        self.text = QLabel()
        self.text.setMaximumWidth(width_ * (100 - self.textMaxWidthPersentage) / 100)
        self.text.setMinimumWidth(width_ * (100 - self.textMaxWidthPersentage) / 100)
        self.text.setObjectName('mesBoxText')
        self.text.setWordWrap(True)
        self.text.setAlignment(Qt.AlignmentFlag.AlignTop)
        # self.text.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        # This adjustSize method give size required for text
        if text == None:
            textX = ''
        else:
            textX = text
        self.text.setText(textX)
        self.text.adjustSize()
        size = self.text.size() + QSize(14, 22)
        self.text.setText('')

        if side == 'right':
            self.layout.setAlignment(Qt.AlignmentFlag.AlignRight)
            # self.layout.addStretch(self.strachPercent)
            self.layout.addWidget(self.text)
        elif side == 'left':
            self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.layout.addWidget(self.text)
            # self.layout.addStretch(self.strachPercent)

        self.textAnime = textFade(self.text, tc.getColor('text'))
        self.popUpAnime = PopUp(
            self.text, size.width(), size.height())

        AnimationControl.addParameters(['popUpAnime'], self, QSize)
        # if text is given then show text after some delay to avoid word wrap glich
        if text != None and text != '':
            QTimer.singleShot(self.popUpAnime.duration() /
                              1.5, lambda: self.setText(text))
        print("Mes Box Started End")
        self.popUpAnime.start()

    def setText(self, text: str):
        self.textAnime.start(text)
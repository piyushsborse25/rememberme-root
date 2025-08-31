from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import config
from GUI import Animations as anime
import sys


class DataInputBox(QFrame):
    def __init__(self, title,dataFrame, beforeDelete):
        super(DataInputBox, self).__init__()
        self.beforeDelete=beforeDelete
        self.setObjectName('DataInputBox')

        self.mainLayout = QVBoxLayout(self)
        self.title=title
        self.titleLabel=QLabel('<b>' + title + '</b>', self)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addSpacing(15)

        self.formLayout = QFormLayout()
        self.slidUpDownAnime = anime.SlideUpDown(self, self.height())
        self.inputes=[]
        self.addInputs(dataFrame)

        self.mainLayout.addLayout(self.formLayout)
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addStretch()
        self.okBtn=QPushButton('OK')
        self.cancelBtn=QPushButton('Cancel')

        self.okBtn.clicked.connect(self.okClicked)
        self.cancelBtn.clicked.connect(self.cancelClicked)

        self.buttonLayout.addWidget(self.okBtn)
        self.buttonLayout.addSpacing(20)
        self.buttonLayout.addWidget(self.cancelBtn)
        self.buttonLayout.addStretch()
        self.buttonLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.buttonLayout)
        self.updateOkButton()


    def slidUp(self):
        self.adjustSize()
        self.slidUpDownAnime.setEndValue(self.height())
        self.slidUp=self.slidUpDownAnime.slidUp()

    def okClicked(self):
        print('DataInputBox Deleted(ok)')
        config.isBoxOn = False

        self.slidDownAndDelete()
        map={}
        for input in self.inputes:
            key=input.whatsThis()
            if isinstance(input,QTextEdit):
                value=input.toPlainText()
            else:
                value=input.text()

            map[key]=value
        config.joiner.dataInputRecived.emit(self.title, 'ok', map)

    def cancelClicked(self):
        print('DataInputBox Deleted(cancel)')
        config.isBoxOn = False

        self.slidDownAndDelete()
        config.joiner.dataInputRecived.emit(self.title, 'cancel', {})

    def slidDownAndDelete(self):
        def delete():
            self.beforeDelete()
            # self.destroy(True,True)

        self.slidUpDownAnime.finished.connect(delete)
        self.slidUpDownAnime.slidDown()

    def addInputs(self, dataFrame):
        for name,isMultiLine,validatorRegex in dataFrame:
            if isMultiLine:
                edit=QTextEdit()
                edit.setMaximumHeight(70)
                if validatorRegex!=None:
                    edit.validator=QRegExpValidator(QRegExp(validatorRegex))
            else:
                edit=QLineEdit()
                if validatorRegex!=None:
                    edit.setValidator(QRegExpValidator(QRegExp(validatorRegex)))

            edit.setWhatsThis(name)
            edit.textChanged.connect(self.updateOkButton)
            self.formLayout.addRow(name, edit)
            self.inputes.append(edit)

    def updateOkButton(self):
        self.okBtn.setEnabled(self.isFormValidity())


    def isFormValidity(self):
        for input in self.inputes:
            if type(input)!=QLineEdit:
                v=input.validator
                text=input.toPlainText()
            else:
                v=input.validator()
                text=input.text()

            if v == None:
                continue

            if v.validate(text,0)[0] != QValidator.Acceptable:
                return False


        return True




if __name__ == '__main__':

    def fun(text):
        try:
            exec(text.text())
        except Exception as e:
            print('Console Error: ', e)


    app = QApplication(sys.argv)
    mainUI = DataInputBox(['name', 'email', 'phone'])
    mainUI.show()
    # console.LiveConsole(fun)
    exit(app.exec())

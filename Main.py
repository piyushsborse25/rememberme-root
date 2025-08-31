import time
import sys

from GUI import console, MainUI, ThemeColors as tc
import config
from GUI.GUIControlSet import *

class Main():
    def __init__(self) -> None:
        tc.setTheme('dark')
        self.controlPanel = ControlPanel()
        config.controlPanel = self.controlPanel

        self.mainUI = MainUI.MainUI()
        ColorPicker.ThemeColorPickerInit(self.mainUI)
        config.joiner.addBox.connect(self.mainUI.addMesBox)
        config.joiner.setMesBoxText.connect(self.mainUI.setMesBoxText)
        config.joiner.completeRemainingLoading.connect(
            self.mainUI.loadingAnime.completeLoading)
        config.joiner.completeRemainingLoading.connect(self.afterLoading)
        config.joiner.controlButtonStateChanged.connect(self.controlButtonStateChangeSlot)
        self.mainUI.loadingAnime.afterLoadAnime.finished.connect(self.fullLoadingAnimeComplededSlot)

        config.joiner.takeDataInput.connect(self.mainUI.addDataInputBox)
        config.joiner.setChatBoxVisibility.connect(self.mainUI.setChatBoxVisibility)
        print("Here")

    def afterLoading(self):
        import MainFuncs
        config.joiner.keyInput.connect(MainFuncs.get_reply_th)
        config.joiner.dataInputRecived.connect(MainFuncs.get_data_th)
        config.joiner.startListening.connect(MainFuncs.toggle_listening_by_click)

    def fullLoadingAnimeComplededSlot(self):
        config.startVision = True

    def controlButtonStateChangeSlot(self, btn, value):
        import MainFuncs
        if btn == 'mic':
            MainFuncs.toggle_mic(value)
        elif btn == 'camera':
            MainFuncs.toggle_camera(value)
        elif btn == 'info':
            MainFuncs.coming_soon(['Hi, I am Vision 2.O, your Desktop Assistant created by Cluster Points', 180])
        elif btn == 'close':
            MainFuncs.coming_soon(['I am Turning off. Thank You...', 172])
            MainFuncs.close_vision()
            app.quit()

    def start(self):
        # self.controlPanel.show()
        self.mainUI.show()
        # self.test.show()


class Joiner(QThread):
    addBox = pyqtSignal(str)
    setMesBoxText = pyqtSignal(str)
    setState = pyqtSignal(str)
    setControlButtonState = pyqtSignal(str, bool)
    controlButtonStateChanged = pyqtSignal(str, bool)
    setBallRingTD = pyqtSignal(int)
    completeRemainingLoading = pyqtSignal()
    keyInput = pyqtSignal(str)
    FullLoadingAnimeCompleted = pyqtSignal()

    setChatBoxVisibility = pyqtSignal(bool)
    startListening = pyqtSignal()

    # titleLabel, clicked button name , data{dataLabel : data}
    dataInputRecived = pyqtSignal(str, str, dict)

    # titleLabel, dataFrame[ [dataLabel, isMultiLine, validatorRegex],[..,..,..],...]
    takeDataInput = pyqtSignal(str, list)

    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        import MainCore as core
        self.completeRemainingLoading.emit()
        print('Loop started')
        while True:
            if config.startVision:
                core.mainLoop()
                break
            time.sleep(0.1)


def fun(text):
    try:
        exec(text.text())
    except Exception as e:
        print('Console Error: ', e)


if __name__ == "__main__":
    print('Vision Started')
    app = QApplication(sys.argv)
    config.screen = app.primaryScreen().availableGeometry()
    joiner = Joiner()
    config.joiner = joiner
    main = Main()
    main.start()
    joiner.main = main
    joiner.start()
    config.controlPanel.add(console.LiveConsole(fun))
    exit(app.exec())

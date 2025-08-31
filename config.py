from GUI.GUIControlSet import ControlPanel
from PyQt5.QtCore import QRect
from Main import Joiner

controlPanel: ControlPanel = None
joiner: Joiner = None
screen: QRect = None
startVision = False

isStarted = False
gender = 'female'
spectrum = True
toggleCamera = True
toggleMic = True

frame = None
isBoxOn = False
manualListening = False

from GUI.Animations import *
import config


class State():
    def __init__(self, totalDarkness, ringThickness, rotation, colorRadian,):
        self.rotation = rotation
        self.colorRadian = colorRadian
        self.totalDarkness = totalDarkness
        self.ringThickness = ringThickness


class Ideal(State):
    def __init__(self, ballRing):
        super().__init__(-3, 4, 45, QRect(90, 90, 90, 90))
        self.anime = BRingTotalDarkness(ballRing)
        self.anime.setStartValue(self.totalDarkness)
        self.anime.setEndValue(80)
        self.anime.setDuration(3000)
        self.anime.setLoopCount(-1)
        self.anime.setEasingCurve(QEasingCurve.Type.SineCurve)
        self.start = self.anime.start
        self.stop = self.anime.stop


class Listning(State):
    def __init__(self, ballRing):
        super().__init__(0, 4, 0, QRect(0, 180, 0, 180))
        self.group = QParallelAnimationGroup()
        self.rotAnime = BRingRotation(ballRing)
        self.clrRadiAnime = BRingColorRadina(ballRing)
        # self.TDAnime = Random(
        #     -5, 50, 50, 70, 130, BRingTotalDarkness(ballRing))

        self.rotAnime.setStartValue(self.rotation)
        self.clrRadiAnime.setStartValue(self.colorRadian)

        self.rotAnime.setEndValue(90)
        self.clrRadiAnime.setEndValue(QRect(180, 0, 180, 0))

        self.rotAnime.setEasingCurve(QEasingCurve.Type.SineCurve)
        self.clrRadiAnime.setEasingCurve(QEasingCurve.Type.SineCurve)

        self.rotAnime.setDuration(3000*1.5)
        self.clrRadiAnime.setDuration(4000*1.5)

        self.group.addAnimation(self.rotAnime)
        self.group.addAnimation(self.clrRadiAnime)
        # self.group.addAnimation(self.TDAnime)

        self.group.setLoopCount(-1)
        self.start = self.group.start
        self.stop = self.group.stop

    # def start(self):
    #     self.group.start()
    #     self.TDAnime.start()


class Processing(State):
    def __init__(self, ballRing):
        super().__init__(0, 4, 0, QRect(0, 180, 0, 180))
        self.group = QParallelAnimationGroup()
        self.rotAnime = BRingRotation(ballRing)
        self.clrRadiAnime = BRingColorRadina(ballRing)

        self.rotAnime.setStartValue(self.rotation)
        self.clrRadiAnime.setStartValue(self.colorRadian)

        self.clrRadiAnime.setEndValue(QRect(180, 0, 180, 0))

        self.rotAnime.setEasingCurve(QEasingCurve.Type.InOutExpo)
        self.clrRadiAnime.setEasingCurve(QEasingCurve.Type.InOutExpo)

        duration = 1500
        self.rotAnime.setDuration(duration)
        self.clrRadiAnime.setDuration(duration)

        self.rotAnime.setDirection(self.rotAnime.Direction.Backward)
        self.clrRadiAnime.finished.connect(self.repetAnime)

        self.group.addAnimation(self.rotAnime)
        self.group.addAnimation(self.clrRadiAnime)
        self.group.setLoopCount(-1)
        # self.clrRadiAnime.setDirection(
        #     self.clrRadiAnime.Direction.Backward)

        self.stop = self.group.stop

    def start(self):
        self.rotAnime.setStartValue(self.rotation)
        self.clrRadiAnime.setStartValue(self.colorRadian)
        self.rotAnime.setEndValue(360)
        self.rotAnime.setDirection(self.rotAnime.Direction.Backward)

        self.clrRadiAnime.setEndValue(QRect(180, 0, 180, 0))
        self.group.start()

    def repetAnime(self):
        s = self.clrRadiAnime.startValue()
        e = self.clrRadiAnime.endValue()
        self.clrRadiAnime.setStartValue(e)
        self.clrRadiAnime.setEndValue(s)


class Speaking(State):
    def __init__(self, ballRing):
        super().__init__(0, 4, 25, QRect(90, 90, 90, 90))
        self.rotAnime = BRingRotation(ballRing)
        self.ringThkRandAnime = Random(
            1, 10, 5, 70, 150, BRingThickness(ballRing))

        self.rotAnime.setStartValue(self.rotation)
        self.rotAnime.setEndValue(55)
        self.rotAnime.setEasingCurve(QEasingCurve.Type.SineCurve)
        self.rotAnime.setDuration(7000)
        self.rotAnime.setLoopCount(-1)

    def start(self):
        self.rotAnime.start()
        self.ringThkRandAnime.start()

    def stop(self):
        self.rotAnime.stop()
        self.ringThkRandAnime.stop()


class StateManager():
    def __init__(self, ballRing: BallRing, state: str):
        self.ballRing = ballRing
        self.stateMap = {
            'ideal': Ideal(ballRing),
            'listning': Listning(ballRing),
            'processing': Processing(ballRing),
            'speaking': Speaking(ballRing),
        }
        self.currState = None
        self.nextState = self.stateMap[state]
        self.animeList = [
            BRingRotation(ballRing),
            BRingColorRadina(ballRing),
            BRingTotalDarkness(ballRing),
            BRingThickness(ballRing)
        ]
        self.group = QParallelAnimationGroup()
        for anime in self.animeList:
            anime.setEasingCurve(QEasingCurve.Type.OutBack)
            self.group.addAnimation(anime)

        self.group.finished.connect(self.__changeToNextState__)
        # self.__changeToNextState__()
        self.initStateGUIControl()
        self.__startJoinAnime__(self.nextState)

    def initStateGUIControl(self):
        config.joiner.setState.connect(self.setState)
        self.stateControl = QComboBox()
        self.stateControl.addItems(
            ['ideal', 'listning', 'processing', 'speaking'])
        self.stateControl.currentTextChanged.connect(
            lambda a: self.setState(a))
        self.stateControl.setMaximumSize(80, 50)
        config.controlPanel.add(self.stateControl)


    def __startJoinAnime__(self,  newState: State):
        self.group.stop()

        duraction = 800

        for anime in self.animeList:
            anime.setDuration(duraction)

        s = self.ballRing.rotation
        e = newState.rotation

        if s < e:
            e_ = e-360
        else:
            e_ = e+360

        if abs(s-e) < abs(s-e_):
            rotation = e
        else:
            rotation = e_

        endValList = [
            rotation,
            newState.colorRadian,
            newState.totalDarkness,
            newState.ringThickness
        ]
        
        startValList = [
            self.ballRing.rotation,
            self.ballRing.rLength,
            self.ballRing.totalDarkness,
            self.ballRing.ringThickness
        ]
        for i in range(4):
            self.animeList[i].setStartValue(startValList[i])
            self.animeList[i].setEndValue(endValList[i])

        # self.animeList[0].setEndValue(0)
        # self.animeList[1].setEndValue(QRect(0, 0, 0, 0,))
        # self.animeList[2].setEndValue(0)
        # self.animeList[3].setEndValue(0)

        self.nextState = newState
        self.group.start()

    def setState(self, newState: str):
        self.stateControl.setCurrentText(newState)

        newState = self.stateMap[newState]
        self.currState.stop()
        self.nextState = newState
        self.__startJoinAnime__(newState)

    def __changeToNextState__(self):
        self.currState = self.nextState
        self.currState.start()

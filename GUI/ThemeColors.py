from PyQt5.QtGui import QColor

colorPalette: dict = {}
theme: dict = {}
# This variables contain range value of TotalDarkness function
maxAlphaDiv = 5
minAlphaDiv = 1
maxDarkness = 200
minDarkness = 85


def getColor(name: str) -> QColor:
    return QColor(colorPalette[name])


def color(method):
    def fun(c, *args):
        if isinstance(c, str):
            c = getColor(c)

        return method(c, *args)

    return fun


def newColor(method):
    def fun(c, *args):
        if isinstance(c, str):
            c = getColor(c)
        elif isinstance(c, QColor):
            c = QColor(c)

        return method(c, *args)

    return fun


@newColor
def setAlpha(c, t: int) -> QColor:
    c.setAlpha(t)
    return c


def getTransprent() -> QColor:
    return QColor(0, 0, 0, 0)


@color
def toRGBStr(c):
    return f'({c.red()},{c.green()},{c.blue()})'


@color
def toRGBAStr(c):
    return f'({c.red()}, {c.green()}, {c.blue()}, {c.alpha()})'


@color
def setTotalDarkness(c: QColor, allowTransprent: bool, threshold: float):
    """
    This method return version of given color
    threshold range fron 0 to 100 
    this darkness is cobination of making color darker and transprent
    but if "allowTransprent" is false then it will only return 
    dark color without changing it's transperence
    """
    global maxAlphaDiv, minAlphaDiv, maxDarkness, maxAlphaDiv

    # converting persentage value (0-100) to decimal(0.0-1.0)
    threshold = threshold/100

    darkness = minDarkness+(maxDarkness-minDarkness)*threshold
    # No need to create new object for QColor c seans
    # c.darker() return QColor in new object

    c = c.darker(darkness)
    if(allowTransprent):
        alphaDiv = minAlphaDiv+(maxAlphaDiv-minAlphaDiv)*threshold
        c.setAlpha(c.alpha()/alphaDiv)

    return c


def getSurfaceColor(elevation):
    """
    get color for Background (background color of cards,textBox)
    elevation is height of Background from background.
    elevation range from 0 100
    """

    c = getColor('surface')
    c.setAlphaF(elevation/100)
    return c


@newColor
def getLighter(c: QColor, value):
    '''Get color with given lightness. value<100 == darker. value>100 == lighter'''
    return c.lighter(value)


def setTheme(name):
    global colorPalette
    colorPalette = theme[name]


# Dark Theme
theme['dark'] = {
    'main': QColor(0, 0, 0),
    # Sky Dark blue
    'ballRing0': QColor(0, 152, 176),
    # Yellow
    'ballRing1': QColor(240, 240, 0),
    # Perpul
    'ballRing2': QColor(189, 35, 250),
    # Pink-red
    'ballRing3': QColor(199, 2, 94),
    'loadingStrip': QColor(0, 84, 186),
    'loadingStripBackground': QColor(7, 43, 98, 150),
    # Text Color
    'text': QColor(255, 255, 255),
    # Background Color of chatBox
    'background': QColor(25, 25, 25),
    # Background Color of MesBox inside chatBox
    'surface': QColor(0, 0, 0),
    'surfaceDiabled':QColor(80,80,80,120),
    'surfaceBorderDiabled':QColor(110,110,110),
    'surfaceTextDiabled':QColor(150,150,150),

}


# Light Theme
theme['light'] = {
    'main': QColor(255, 255, 255),
    # Sky Dark blue
    'ballRing0': QColor(0, 152, 176),
    # Yellow
    'ballRing1': QColor(240, 240, 0),
    # Perpul
    'ballRing2': QColor(189, 35, 250),
    # Pink-red
    'ballRing3': QColor(199, 2, 94),
    # Text Color
    'text': QColor(0, 0, 0),
    # Background Color of chatBox
    'background': QColor(220, 230, 220),
    # Background Color of MesBox inside chatBox
    'surface': QColor(255, 255, 255),

}

theme['dark']['primary'] = theme['dark']['ballRing0']
theme['light']['primary'] = theme['dark']['ballRing0']

colorPalette = theme['dark']
# colorPalette['ball'] = setAlpha('background', 180)

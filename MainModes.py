import cv2
import os
import numpy as np
import config
import math
import threading

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc

import HandDetectionModule as hm
import autopy

import time
import win32api
import win32con

import pyautogui as auto

import speech_recognition as sr

import MainFuncs as call

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

# From Here

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

dectector = hm.HandDetector(trackCon=0.9)

volume_mode_on = True
brightness_mode_on = True
curser_mode_on = True
drawing_mode_on = True


def toggle_volume_mode(value: bool):
    global volume_mode_on
    volume_mode_on = value


def toggle_brightness_mode(value: bool):
    global brightness_mode_on
    brightness_mode_on = value


def toggle_curser_mode(value: bool):
    global curser_mode_on
    curser_mode_on = value


def toggle_drawing_mode(value: bool):
    global drawing_mode_on
    drawing_mode_on = value


def get_coordinates(results, p):
    return results[p][1], results[p][2]


def get_distance(results, p1, p2):
    x1, y1 = get_coordinates(results, p1)
    x2, y2 = get_coordinates(results, p2)
    return int(math.hypot(x2 - x1, y2 - y1))


# To Here

def volume_mode():
    while volume_mode_on:
        frame = cv2.flip(config.frame, 1)

        # Code Here
        results = dectector.findHandPosition(frame, draw=True)

        if len(results) != 0:
            p1, p2 = 4, 8
            length = get_distance(results, p1, p2)

            volRange = volume.GetVolumeRange()
            minVol = volRange[0]
            maxVol = volRange[1]

            filteredValue = np.interp(length, [20, 150], [minVol, maxVol])
            volume.SetMasterVolumeLevel(filteredValue, None)


def brightness_mode():
    while brightness_mode_on:
        frame = cv2.flip(config.frame, 1)

        # Code Here
        results = dectector.findHandPosition(frame, draw=True)

        if len(results) != 0:
            p1, p2 = 8, 12
            length = get_distance(results, p1, p2)

            filteredValue = np.interp(length, [20, 150], [0, 100])
            sbc.fade_brightness(filteredValue, increment=10)


wScr, hScr = autopy.screen.size()
wCam, hCam = (1280, 720)


def curser_mode():
    while curser_mode_on:
        frame = cv2.flip(config.frame, 1)

        # Code Here
        results = dectector.findHandPosition(frame, draw=True)

        if len(results) != 0:
            p1 = get_coordinates(results, 8)

            fingers = dectector.fingersUp()

            if fingers[1] == 1 and fingers[2] == 1:
                xp = np.interp(p1[0], (200, wCam - 200), (0, wScr))
                yp = np.interp(p1[1], (200, hCam - 200), (0, hScr))

                autopy.mouse.move(xp, yp)
                cv2.circle(frame, p1, 8, (0, 255, 0), cv2.FILLED)

            if fingers[1] == 1 and fingers[2] == 1:
                dist = get_distance(results, 8, 12)

                if dist < 20:
                    autopy.mouse.click()


def drawing_mode():
    xp = None
    counter = 0
    cflag = True

    width = 1280
    height = 720

    canvas = cv2.imread('MyCanvas.png')

    canvas = cv2.resize(canvas, (width, height))
    canvas_color = (0, 0, 0)
    canvas_brush_size = 5

    while drawing_mode_on:

        frame = cv2.flip(config.frame, 1)
        frame = cv2.resize(frame, (width, height))

        # Code Here
        results = dectector.findHandPosition(frame, draw=True)
        if len(results) != 0:

            p1 = get_coordinates(results, 8)

            if p1[0] > 1100:
                if p1[1] < 410:
                    canvas_color = (0, 0, 0)
                elif p1[1] < 440:
                    canvas_color = (112, 48, 162)
                elif p1[1] < 480:
                    canvas_color = (1, 112, 193)
                elif p1[1] < 530:
                    canvas_color = (254, 0, 2)
                elif p1[1] < 570:
                    canvas_color = (255, 102, 0)
                elif p1[1] < 610:
                    canvas_color = (255, 255, 1)
                elif p1[1] < 650:
                    canvas_color = (0, 175, 82)

            if p1[0] < 200:
                if p1[1] < 460:
                    canvas_brush_size = 5
                elif p1[1] < 490:
                    canvas_brush_size = 7
                elif p1[1] < 520:
                    canvas_brush_size = 9
                elif p1[1] < 550:
                    canvas_brush_size = 11
                elif p1[1] < 580:
                    canvas_brush_size = 13
                elif p1[1] < 610:
                    canvas_brush_size = 15

            if p1[0] > 1080 and p1[1] < 150 and cflag:
                cv2.imwrite(f'mySaved{counter}Img.png', canvas)
                print("Here")
                cflag = False

            if 160 < p1[0] < 1090 and 80 < p1[1] < 630:

                dist = get_distance(results, 4, 8)
                dist_e = get_distance(results, 8, 20)

                if dist > 40:
                    if dist_e > 120:
                        if xp is None:
                            xp = p1

                        cv2.line(canvas, xp, p1, canvas_color, canvas_brush_size)
                        xp = p1
                    else:
                        cv2.circle(canvas, p1, 50, (255, 255, 255), cv2.FILLED)
                        xp = None
                else:
                    xp = None

        cv2.imshow("Drawing Board", canvas)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def isNumLockOn():
    return win32api.GetKeyState(win32con.VK_NUMLOCK) == 1

def auto_typer_mode(file_path='readme.txt'):
    if not os.path.exists(file_path):
        with open(file_path, 'x') as f:
            f.truncate(0)
            os.startfile(file_path)
    else:
        with open(file_path, 'a+') as f:
            os.startfile(file_path)
            time.sleep(2)
            if len(f.readline().strip()) == 0:
                auto.hotkey('end')
            else:
                auto.hotkey('end', 'enter')

    r = sr.Recognizer()
    recent = ''
    # value = True

    while True:

        # window_list = str(Window.get_foreground().title).split('-')
        # window_list = [item.strip() for item in window_list]
        # file_name = window_list[0].split("\\")[-1]
        #
        # if file_name != file_path:
        #     if value:
        #         print('Please Focus on File')
        #     value = False
        #     continue
        #
        # value = True

        with sr.Microphone() as source:
            print('Typer is Listening...')
            config.joiner.setState.emit('listning')
            r.pause_threshold = 1

            r.non_speaking_duration = 1
            try:
                audio = r.listen(source, 5, 5)
                print('Typer is Recognizing...')
                config.joiner.setState.emit('ideal')
                query = r.recognize_google(audio)
                print('Now Typing...')

                if query == 'turn off voice typing mode':
                    call.raw_speak('Ok, Turning off voice typing mode')
                    break

                if query == 'save':
                    auto.hotkey('ctrl', 's')

                elif query == 'enter':
                    auto.press('enter')

                elif query == 'tab':
                    auto.press('tab')

                elif query == 'delete':
                    temp = [str(item).strip() for item in recent.split(' ') if item != '']
                    temp = temp[-1]
                    rec_len = len(temp)
                    recent = recent[:-rec_len - 1]
                    for _ in range(rec_len + 1):
                        auto.press('backspace')

                elif query == 'delete line':
                    if isNumLockOn():
                        auto.press('numlock')

                    auto.hotkey('shift', 'home')
                    auto.press('delete')

                elif query == 'delete all':
                    auto.hotkey('ctrl', 'a')
                    auto.press('delete')
                else:
                    recent = f'{recent} {query}'
                    auto.typewrite(f'{query} ', interval=0.05)

            except Exception as e:
                print('Typer Says, Say Something')


def volume_mode_th():
    thread = threading.Thread(target=volume_mode)
    thread.start()


def brightness_mode_th():
    thread = threading.Thread(target=brightness_mode)
    thread.start()


def curser_mode_th():
    thread = threading.Thread(target=curser_mode)
    thread.start()


def drawing_mode_th():
    thread = threading.Thread(target=drawing_mode)
    thread.start()

from collections import Counter

import speech_recognition as sr
import pyttsx3
import threading
import config

import cv2
import cvlib as cv
from PIL import Image

import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
import face_recognition
import os
import time
import random

import webbrowser
import wikipedia
from email.message import EmailMessage
import smtplib
from datetime import datetime
from youtubesearchpython import Search
from googlesearch import search

import re
import math
import glob
from multiprocessing.pool import ThreadPool

from tensorflow.keras.models import load_model
from nltk.stem import WordNetLemmatizer
import joblib

# Mode Import
import MainModes as modes

import pyautogui as auto

try:
    import pywhatkit
except Exception:
    print('Please connect to Internet.')
    exit()

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

# Chatting Environment
model_name = 'CB_model_30'

wordnet = WordNetLemmatizer()
tfidf = joblib.load(f'{model_name}\\CB_tfidf_Vec')

model = load_model(f'{model_name}\\ChatBot.model')
input_len, output_len, tags, intents = joblib.load(f'{model_name}\\ModelInfo.pkl')

# Camera No
camera_no = 0


def infinite():
    webcaminf = cv2.VideoCapture(camera_no)
    while config.toggleCamera:
        status, frame = webcaminf.read()
        config.frame = frame
    config.frame = None


def infinite_th():
    cm_thread = threading.Thread(target=infinite)
    cm_thread.start()


infinite_th()


def toggle_camera(value: bool):
    print('camera', value)

    if value:
        # time.sleep(0.2)
        print('video started again')
        infinite_th()
        camera_thread = threading.Thread(target=raw_camera_start)
        camera_thread.start()

    config.toggleCamera = value


def toggle_mic(value: bool):
    print('mic', value)
    config.toggleMic = value
    if value:
        print('mic started again')
        listening_thread = threading.Thread(target=listening_loop)
        listening_thread.start()


def toggle_listening_by_click():
    config.manualListening = True


yolo_model = cv2.dnn.readNet("Yolo_model_80/yolov3.weights", "Yolo_model_80/yolov3.cfg")

with open("Yolo_model_80/coco.names", "r") as file:
    class_list = [name.strip() for name in file.readlines()]

layer_names = yolo_model.getLayerNames()
output_layers = [layer_names[i - 1] for i in yolo_model.getUnconnectedOutLayers()]


def get_yolo_dict(iterator=1):
    class_names = []

    for itr in range(iterator):

        if config.frame is None:
            raw_speak(f'Camera is OFF, Please turn it ON')
            return {}

        # Load the Image
        img = cv2.resize(config.frame, None, fx=0.4, fy=0.4)
        height, width, channels = img.shape

        # Making Blob
        blob_set = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

        # Setting Blob
        yolo_model.setInput(blob_set)
        outputs = yolo_model.forward(output_layers)

        boxes_list = []
        confidence_list = []
        class_id_list = []

        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.6:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)

                    # Rectangle Coordinates
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - (w / 2))
                    y = int(center_y - (h / 2))

                    boxes_list.append([x, y, w, h])
                    class_id_list.append(class_id)
                    confidence_list.append(float(confidence))

        indexes = cv2.dnn.NMSBoxes(boxes_list, confidence_list, 0.5, 0.4)

        for i in range(len(boxes_list)):
            if i in indexes:
                label = str(class_list[class_id_list[i]])
                class_names.append(label)

    obj_dict = dict(Counter(class_names))

    return obj_dict


def dict_reader(my_dict):
    if 'person' in my_dict.keys() and my_dict['person'] > 1:
        val = my_dict['person']
        my_dict.pop('person')
        my_dict['people'] = val

    obj_key_list = list(my_dict.keys())

    if len(list(my_dict.keys())) == 0:
        return 'nothing'

    if len(obj_key_list) == 1:
        return f'{my_dict[obj_key_list[0]]} {obj_key_list[0]}'

    res = ''
    for i in range(0, len(obj_key_list) - 1):
        res += f'{my_dict[obj_key_list[i]]} {obj_key_list[i]}'
    res += f' and {my_dict[obj_key_list[-1]]} {obj_key_list[-1]}'
    return res


def get_reply_th(query: str = 'none'):
    ty_thread = threading.Thread(target=get_reply, args=(query, True))
    ty_thread.start()


def get_data(title, button, data):
    global fixName

    print('Here in Get Data', title, button, data)

    if button == 'cancel':
        return

    if title == 'Enter Your Name':
        name = data['Name']
        remember_me(name)

        speak_th([f'Glad to meet you {name}'])
        fixName = name
        acquire_camera()

    elif title == 'Email Details':
        revEmail = data['Reciever Email']
        sub = data['Email Subject']
        message = data['Email Message']

        speak_th(['Sending Email'])
        send_email(revEmail, sub, message)

    elif title == 'Whatsapp Details':
        mobile = data['Mobile number']
        message = data['Enter Message']

        send_whats_msg(mobile, message)


def get_data_th(title, button, data):
    data_thread = threading.Thread(target=get_data, args=(title, button, data))
    data_thread.start()


def get_reply(query: str = 'none', delay=False):
    global fixName

    try:
        if delay:
            time.sleep(1.5)

        print('in reply Query :', query)

        pred_tag, confidence = predict_class(query)
        if confidence < 70:
            # speak_th(["Sorry, I didn't Understood"])
            print(f'Low Confidence on {pred_tag}')
            # return

        if query == 'exit vision':
            close_vision()
            return

        if pred_tag == "remember me":

            if config.frame is None:
                raw_speak(f'Camera is OFF, Please turn it ON')
                return

            speak_th(['Yes, Of Course, what\'s your name?'])
            release_camera()

            config.joiner.takeDataInput.emit("Enter Your Name", [
                ['Name', False, '.+']
            ])

        elif pred_tag == "identify":
            name = fixName
            if name != 'none':
                raw_speak(f'I know you, you are {name}.')
            else:
                raw_speak(f'Sorry, I dont know you.')

        # YOLO
        elif 'what is this' in query or 'what\'s on screen' in query:
            yolo_dict = get_yolo_dict()

            if len(yolo_dict.keys()) != 0:
                obj_str = dict_reader(yolo_dict)
                raw_speak(f'I can see {obj_str}')
            elif config.frame is not None:
                raw_speak(f'Sorry, I see nothing')

        # Mode 1
        elif 'turn on volume mode' in query:
            if config.frame is None:
                raw_speak(f'Camera is OFF, Please turn it ON')
            else:
                speak_th(['Ok, Turning on Volume Mode'])
                modes.toggle_volume_mode(True)
                modes.volume_mode_th()

        elif 'turn off volume mode' in query:
            speak_th(['Ok, Turning off Volume Mode'])
            modes.toggle_volume_mode(False)

        # Mode 2
        elif 'turn on brightness mode' in query:
            if config.frame is None:
                raw_speak(f'Camera is OFF, Please turn it ON')
            else:
                speak_th(['Ok, Turning on Brightness Mode'])
                modes.toggle_brightness_mode(True)
                modes.brightness_mode_th()

        elif 'turn off brightness mode' in query:
            speak_th(['Ok, Turning off Brightness Mode'])
            modes.toggle_brightness_mode(False)

        # Mode 3
        elif 'turn on cursor mode' in query:
            if config.frame is None:
                raw_speak(f'Camera is OFF, Please turn it ON')
            else:
                speak_th(['Ok, Turning on Cursor Mode'])
                modes.toggle_curser_mode(True)
                modes.curser_mode_th()

        elif 'turn off cursor mode' in query:
            speak_th(['Ok, Turning off Cursor Mode'])
            modes.toggle_curser_mode(False)

        # Mode 4
        elif 'turn on drawing mode' in query:
            if config.frame is None:
                raw_speak(f'Camera is OFF, Please turn it ON')
            else:
                speak_th(['Ok, Turning on Drawing Mode'])
                modes.toggle_drawing_mode(True)
                modes.drawing_mode_th()

        # Mode 5
        elif 'turn on voice typing mode' in query:
            speak_th(['Ok, Turning on Voice typing Mode'])
            modes.auto_typer_mode()

        elif 'turn off drawing mode' in query:
            speak_th(['Ok, Turning off Drawing Mode'])
            modes.toggle_drawing_mode(False)

        elif 'play' in query and 'on youtube' in query:
            query = remove_words(query, ['vision', 'search', 'play', 'on youtube'])
            speak_th([f"Ok, Playing {query} on youtube"])
            search_on_youtube(query, False)

        elif pred_tag == "on youtube":
            query = remove_words(query, ['vision', 'search', 'play', 'on youtube'])
            speak_th([f"Ok, Searching {query} on youtube"])
            search_on_youtube(query, True)

        elif pred_tag == "search":
            query = remove_words(query, ['vision', 'search', 'on google'])
            speak_th([f"Ok, Searching {query} on google"])
            search_on_google(query, True)

        elif pred_tag == "website":
            query = remove_words(query, ['vision', 'open', 'website'])
            speak_th([f"Ok, Opening {query} website"])
            search_on_google(query, False)

        elif pred_tag == "on wikipedia":
            query = remove_words(query, ['vision', 'search', 'on wikipedia', 'who is'])
            results = search_on_wikipedia(query)
            print(results)
            speak_th([results])

        elif pred_tag == "open software":
            open_software(query)

        elif pred_tag == "whatsapp":

            raw_speak('Enter Whatsapp Details')

            config.joiner.takeDataInput.emit('Whatsapp Details', [
                ['Mobile number', False, "^(\+\d{1,3}[- ]?)?\d{10}$"],
                ['Enter Message', True, ".+"]
            ])

        elif pred_tag == "email":

            raw_speak('Enter Emaill Details')

            config.joiner.takeDataInput.emit('Email Details', [
                ['Reciever Email', False, "^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$"],
                ['Email Subject', False, ".+"],
                ['Email Message', True, ".+"]
            ])

        elif pred_tag == "open instagram":
            query = remove_words(query, ['vision', 'open'])
            speak_th(['Opening Instagram account'])
            search_on_google(query + 'instagram account', on_search_bar=False)

        elif pred_tag == "open facebook":
            query = remove_words(query, ['vision', 'open', 'facebook'])
            speak_th(['Opening Facebook account'])
            search_on_google(query + 'facebook account', on_search_bar=False)

        elif pred_tag == "open twitter":
            query = remove_words(query, ['vision', 'open', 'twitter'])
            speak_th(['Opening Twitter account'])
            search_on_google(query + 'twitter account', on_search_bar=False)

        elif pred_tag == "play movie":
            raw_speak('Okay, which movie do you like to play?')
            movie_name = raw_listen().lower()
            print('Movie : ', movie_name)
            speak_th(['Playing your Movie'])
            video_player(movie_name)

        elif pred_tag == "play song":
            raw_speak('Okay, which song do you like to play?')
            song_name = raw_listen().lower()
            print('Song : ', song_name)
            speak_th(['Playing your Song'])
            audio_player(song_name)

        elif 'add' in query:
            ans = basic_math(query, 'add')
            raw_speak(f'Answer is {ans}')

        elif 'subtract' in query:
            ans = basic_math(query, 'sub')
            raw_speak(f'Answer is {ans}')

        elif 'multiply' in query:
            ans = basic_math(query, 'mul')
            raw_speak(f'Answer is {ans}')

        elif 'divide' in query:
            ans = basic_math(query, 'div')
            raw_speak(f'Answer is {ans}')

        elif 'what is square of' in query:
            ans = square_of(query)
            raw_speak(f'Answer is {ans}')

        elif 'what is cube of' in query:
            ans = cube_of(query)
            raw_speak(f'Answer is {ans}')

        elif 'raised to' in query or \
                'raise to' in query:
            ans = power_of(query)
            raw_speak(f'Answer is {ans}')

        elif 'exit' in query:
            speak_th(['Okay bye, I will See you later.'])
            exit(0)

        else:
            if query != 'none':
                if confidence >= 75:
                    response = get_response(pred_tag)
                    speak_th([response])
                else:
                    speak_th(["Sorry, I didn't Understood"])
        print('out get reply')
    except Exception as e:
        print(f"Error in get_reply: {e}")


active = True


def listening_loop():
    global active
    # Main Loop
    while config.toggleMic:

        if config.isBoxOn:
            # time.sleep(1)
            continue

        if active:
            get_hello_vision()
        config.manualListening = False

        # Animation Start
        config.joiner.setChatBoxVisibility.emit(True)
        query = raw_listen().lower()

        if query == 'none':
            active = True
            config.joiner.setState.emit('ideal')
        else:
            active = False
            config.joiner.setState.emit('processing')

        # Animation End
        get_reply(query)


def filter_text(text):
    text = re.sub('\\W', ' ', text)
    text = text.lower()
    text = text.split()
    text = [wordnet.lemmatize(word=word) for word in text]
    text = ' '.join(text)
    return text


def predict_class(text):
    # Vectorized string
    pred_list = [filter_text(text)]
    pred_vec = tfidf.transform(pred_list)
    pred_vec = pred_vec.toarray()

    # Predict Probability
    probability = model.predict(pred_vec)

    # Predict Class
    value = np.argmax(probability)
    pred_tag = tags[int(value)]

    confidence = int(np.max(probability) * 100)

    return pred_tag, confidence


recent_dict = {}
for tag in tags:
    recent_dict[tag] = ""


def get_hello_vision():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        r.non_speaking_duration = 1

        while config.toggleMic:

            if config.manualListening:
                return

            try:
                print('Listening Hi Vision...')
                audio = r.listen(source, 5, 5)
                print(audio)
                query = r.recognize_google(audio)
                print('Done Recognizing Hi Vision...' + query)

                if query in ['hello vision', 'hi vision', 'hey vision', 'ok vision', 'wandavision']:
                    break
            except Exception as e:
                print(f"Error in get_hello_vision: {e}")


def get_response(pred_tag):
    for intent in intents:
        tag = intent['tag']

        if pred_tag == tag:
            response_list = intent['responses']
            response = random.choice(response_list)

            if response == '':
                return ''

            if recent_dict[pred_tag] == response:
                response = get_response(pred_tag)
            else:
                recent_dict[pred_tag] = response
            return response


def get_disks_list():
    disk_list = os.popen("fsutil fsinfo drives").read()
    disk_list = re.sub('\W', ' ', disk_list).replace('Drives', '')
    disk_list = [disk for disk in disk_list if disk.isalpha()]
    disk_list.remove(disk_list[0])
    return disk_list


def get_files_from_disk(format_str):
    disk_list = get_disks_list()
    final_files = []

    for format in format_str:
        for disk in disk_list:
            try:
                files = glob.glob(f'{disk}:\**\*.{format}', recursive=True)
                final_files = final_files + files
            except Exception:
                pass
    names = [os.path.split(name)[-1] for name in final_files]
    names_list = []
    for name in names:
        splitted = name.split('.')
        name = ''.join(splitted[:len(splitted) - 1])
        names_list.append(name.lower())

    final_dict = {}
    for name, path in zip(names_list, final_files):
        final_dict[name] = path.lower()

    return final_dict


pool = ThreadPool(processes=2)

vid_process_result = pool.apply_async(get_files_from_disk, args=(['mp4', 'mkv'],))
aud_process_result = pool.apply_async(get_files_from_disk, args=(['mp3'],))

video_files_dict = vid_process_result.get()
audio_files_dict = aud_process_result.get()


def video_player(file_name):
    global video_files_dict
    found = False
    for key in video_files_dict.keys():
        if file_name in key:
            os.startfile(video_files_dict[key])
            found = True
            break
    if not found:
        print('Didn\'t find it in directiory.')


def audio_player(file_name):
    global audio_files_dict
    found = False
    for key in audio_files_dict.keys():
        if file_name in key:
            os.startfile(audio_files_dict[key])
            found = True
            break
    if not found:
        print('Didn\'t find it in directiory.')


def begin():
    hour = int(datetime.now().hour)
    section = None

    if 0 <= hour < 12:
        section = 'Morning'
    elif 12 <= hour < 16:
        section = 'Afternoon'
    else:
        section = 'Evening'

    raw_speak(f'Good {section}, I am Vision Sir. Please tell me how may I help you', 170)


listen_return_value = 'None'


def runtime_type_lis(speech):
    # speech += ' '
    # for i in range(1, len(speech) + 1, 2):
    #     time.sleep(0.12)
    #     config.joiner.setMesBoxText.emit(speech[:i])
    # time.sleep(0.2)

    config.joiner.setMesBoxText.emit(speech)


def raw_listen():
    global listen_return_value

    config.joiner.setState.emit('listning')

    config.spectrum = True
    # ty_thread = threading.Thread(target=spec.get_spectrum)
    # ty_thread.start()

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')
        r.pause_threshold = 1
        r.non_speaking_duration = 1
        try:
            audio = r.listen(source, 5, 5)
            print('Recognizing...')
            query = r.recognize_google(audio)

            if query != '':
                config.joiner.addBox.emit('user')
                runtime_type_lis(query)
            # ty_thread = threading.Thread(target=runtime_type_lis, args=(query,))
            # ty_thread.start()

            print('Done Recognizing...')
        except Exception as e:
            print('Say Something')
            return 'none'
    listen_return_value = query
    config.spectrum = False

    config.joiner.setState.emit('ideal')
    return query


def runtime_type(speech):
    speech += ' '
    for i in range(1, len(speech) + 1, 2):
        time.sleep(0.12)
        config.joiner.setMesBoxText.emit(speech[:i])


def raw_speak(speech='', newVoiceRate=170):
    config.joiner.setState.emit('speaking')
    gender = config.gender
    # print(gender)

    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('rate', newVoiceRate)
        if gender == 'male':
            engine.setProperty('voice', voices[0].id)
        else:
            engine.setProperty('voice', voices[2].id)

        if speech != '':
            config.joiner.addBox.emit('assistent')
            type_thread = threading.Thread(target=runtime_type, args=(speech,))
            type_thread.start()

        engine.say(speech)
        engine.runAndWait()
        engine.stop()
        time.sleep(0.5)
    except Exception:
        print('Clash Occured')

    config.joiner.setState.emit('ideal')


def speak_th(my_args_list):
    # speakThread = threading.Thread(target=raw_speak, args=my_args_list)
    # speakThread.start()
    raw_speak(my_args_list[0])


def listen_th():
    listenThread = threading.Thread(target=raw_listen)
    listenThread.start()
    listenThread.join()
    return listen_return_value


def getRandomSpeech(name):
    welcome = [
        f'Welcome {name}',
        f'Hello {name} How are you ?',
        f'Nice to meet you {name}',
        f'Pleasure to meet you {name}',
        f'Hey {name} it\'s Good to see you',
        f'Hi {name} and welcome',
        f'What\'s up {name}',
        f'How\'s it going {name}'
    ]
    return random.choice(welcome)


def findEncodings(images):
    encodeList = []

    for i in range(len(images)):
        img = images[i]
        height, width, channels = img.shape
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(face_image=img, known_face_locations=[(0, width, height, 0)])[0]
        encodeList.append(encode)
    return encodeList


fixName = 'none'
has_camera_permission = True

path = 'images'
images = []
classNames = []
gender_classes = ['male', 'female']
myList = None
encodeListKnown = None


def release_camera():
    global has_camera_permission
    has_camera_permission = False
    print('Camera released.')


def acquire_camera():
    global has_camera_permission
    global encodeListKnown
    global myList

    images.clear()
    classNames.clear()
    myList = os.listdir(path)
    for item in myList:
        currImg = cv2.imread(f'{path}/{item}')
        images.append(currImg)
        classNames.append(os.path.splitext(item)[0])

    encodeListKnown = findEncodings(images)

    has_camera_permission = True
    print('Camera acquired.')


gender_model = tf.keras.models.load_model('Gender_Model_02/gender_detection.model')


def raw_camera_start():
    global fixName
    global has_camera_permission
    global encodeListKnown
    global myList

    myList = os.listdir(path)
    for item in myList:
        currImg = cv2.imread(f'{path}/{item}')
        images.append(currImg)
        classNames.append(os.path.splitext(item)[0])

    encodeListKnown = findEncodings(images)

    while config.toggleCamera:

        if config.frame is None:
            continue

        if has_camera_permission:

            status, frame = 0, config.frame

            # Normalize
            imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            faceCurrFrame = face_recognition.face_locations(imgS)
            encodeCurrFrame = face_recognition.face_encodings(imgS, faceCurrFrame)

            name = 'unknown'
            gender_label = 'male'

            # loop through detected faces
            for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDist = face_recognition.face_distance(encodeListKnown, encodeFace)

                matchIndex = np.argmin(faceDist)

                if matches[matchIndex]:
                    # Name for Face Recognisition
                    name = classNames[matchIndex].capitalize()

                    # get corner points of face rectangle
                    startY, endX, endY, startX = faceLoc
                    startY, endX, endY, startX = startY * 4, endX * 4, endY * 4, startX * 4

                    # crop the detected face region
                    face_crop = np.copy(frame[startY:endY, startX:endX])
                    if (face_crop.shape[0]) < 10 or (face_crop.shape[1]) < 10:
                        continue

                    # preprocessing for gender detection model
                    face_crop = cv2.resize(face_crop, (96, 96))
                    face_crop = face_crop.astype("float") / 255.0
                    face_crop = img_to_array(face_crop)
                    face_crop = np.expand_dims(face_crop, axis=0)

                    # apply gender detection on face
                    # model.predict return a 2D matrix, ex: [[9.9993384e-01 7.4850512e-05]]
                    conf = gender_model.predict(face_crop)[0]

                    # get label with max accuracy
                    index = np.argmax(conf)
                    gender_label = gender_classes[index]
                    config.gender = gender_label

            time.sleep(0.5)
            if fixName != name:
                if name != 'unknown':
                    passName = getRandomSpeech(name)
                    # For Main Voice
                    raw_speak(passName, 150)
                    fixName = name

            # cv2.imshow('Identifying...', frame)


def remember_me(name):
    # Check if name is already exist
    path = f'images/'
    remem_list = [file.split('.')[0] for file in os.listdir(path=path) if not os.path.isdir(file)]
    if name in remem_list:
        speak_th(['Name is already exists, please try another one.'])
        return False

    time = 0

    while True:

        status, frame = 0, config.frame
        face, confidence = cv.detect_face(frame)

        for idx, f in enumerate(face):
            (startx, starty) = f[0], f[1]
            (endx, endy) = f[2], f[3]

            cv2.rectangle(frame, (startx - 15, starty - 15), (endx + 15, endy + 15), (0, 255, 0), 2)

            Y = starty - 25 if starty - 25 > 25 else starty + 25
            cv2.putText(frame, 'Taking Image', (startx, Y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 0), 2)

            # cropping face in rectangle
            face_crop = frame[starty - 15:endy + 15, startx - 15:endx + 15]
            face_crop = Image.fromarray(face_crop)
            face_crop.save(f'images/{name}.png')

        # cv2.imshow("Frame", frame)

        time = time + 1
        if time == 20:
            break

    cv2.destroyAllWindows()
    print('Image Captured.')
    return True


def camera_start_th():
    cameraThread = threading.Thread(target=raw_camera_start)
    cameraThread.start()


def send_whats_msg(mobile_no, msg):
    hour = datetime.now().hour
    min = datetime.now().minute
    sec = datetime.now().second
    wait = 10
    if (60 - sec) <= wait:
        min_pass = min + 2
    else:
        min_pass = min + 1
    try:
        mobile_no = '+91' + mobile_no
        pywhatkit.sendwhatmsg(mobile_no, msg, hour, min_pass, wait_time=wait)
    except Exception:
        print('Some, Error Occured')


def send_email(reciever, subject, message, sender='arihripiyu@gmail.com', senderpass='50995099'):
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = reciever
        msg.set_content(message, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender, senderpass)
            smtp.send_message(msg)

    except Exception as e:
        print('Error Occured', e)


def remove_words(string, words_list):
    for word in words_list:
        string = string.replace(word, '')
    return string


def open_website(url):
    webbrowser.open(url)


def search_on_youtube(query='', on_search_bar=False):
    if not on_search_bar:
        # print('Hi there')
        allsearch = Search(query, limit=1)
        result = allsearch.result()
        details = result['result'][0]

        title = details['title']
        duration = details['duration']
        link = details['link']
        publishedTime = details['publishedTime']

        speak_th([f'Playing video {title} {duration} minutes long on youtube. published {publishedTime}'])
    else:
        link = f'https://www.youtube.com/results?search_query={query}'

    open_website(link)
    time.sleep(6)
    auto.hotkey("tab")
    time.sleep(1)
    auto.hotkey("f")


def search_on_google(query='', on_search_bar=False):
    if not on_search_bar:
        results = search(query, num=1, stop=1, pause=1.0)
        website = next(results)
        webbrowser.open(website)
    else:
        link = f'https://www.google.com/search?q={query}'
        webbrowser.open(link)


def search_on_wikipedia(query):
    return wikipedia.summary(query, sentences=2)


def open_software(query):
    found = False
    path = 'C:\\Users\\HP\\Desktop\\Softs Path'
    file_list = [file.lower() for file in os.listdir(path) if file.endswith('.lnk')]
    key_list = [key.split('.')[0] for key in file_list]
    path_list = [os.path.join(path, key) for key in file_list]

    app_list = {}
    for key, value in zip(key_list, path_list):
        app_list[key] = value

    for soft in app_list.keys():
        for word in soft.split():
            if word in query:
                found = True
                speak_th([f'Opening {soft}'])
                os.startfile(app_list[soft])
                break
            else:
                break
        if found:
            break

    if not found:
        speak_th(['Sorry, I Cant find required Software'])


def get_numlist(str):
    digit_list = re.sub('\D', ' ', str).split(' ')
    no_list = [digit for digit in digit_list if digit.isdigit()]
    no_list = [int(digit) for digit in no_list]
    return no_list


def basic_math(str, task):
    nums = get_numlist(str)
    nums.sort(reverse=True)

    if task == 'add':
        sum = 0
        for no in nums:
            sum = sum + no
        return sum

    elif task == 'sub':
        diff = max(nums)
        nums = nums[1:]

        for no in nums:
            diff = diff - no
        return diff

    elif task == 'mul':
        mul = 1
        for no in nums:
            mul = mul * no
        return mul

    elif task == 'div':
        div = max(nums)
        nums = nums[1:]
        for no in nums:
            div = div / no
        return div


def power_of(str):
    nums = get_numlist(str)
    return int(math.pow(nums[0], nums[1]))


def square_of(str):
    nums = get_numlist(str)
    return int(math.pow(nums[0], 2))


def cube_of(str):
    nums = get_numlist(str)
    return int(math.pow(nums[0], 3))

def coming_soon(my_args_list):
    speakThread = threading.Thread(target=raw_speak, args=my_args_list)
    speakThread.start()

def close_vision():
    print('closed')
    config.isBoxOn = False
    config.manualListening = True
    config.toggleMic = False
    config.toggleCamera = False
    config.isStarted = False

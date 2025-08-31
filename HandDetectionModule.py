import cv2
import mediapipe as mp


class HandDetector():
    def __init__(self, mode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.model_complexity = modelComplexity,
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.handsObj = self.mpHands.Hands(static_image_mode=False, max_num_hands=maxHands,
                                           model_complexity=modelComplexity, min_detection_confidence=detectionCon,
                                           min_tracking_confidence=trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def __findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.handsObj.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for hand in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, hand, self.mpHands.HAND_CONNECTIONS)

    def findHandPosition(self, img, handNo=0, draw=True):
        self.__findHands(img, draw)
        self.handDetailsList = []
        if self.results.multi_hand_landmarks:

            hand = self.results.multi_hand_landmarks[handNo]

            for id, loc in enumerate(hand.landmark):
                h, w, c = img.shape
                cx, cy = int(loc.x * w), int(loc.y * h)
                self.handDetailsList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 12, (255, 255, 0), 1)

        return self.handDetailsList

    def fingersUp(self):
        fingers = []

        # Thumb
        if self.handDetailsList[self.tipIds[0]][1] < self.handDetailsList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # For Fingers

        for id in range(1, 5):
            if self.handDetailsList[self.tipIds[id]][2] < self.handDetailsList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers
from multiprocessing import Process
from threading import Thread
import VolumeController
#gui resources 
import tkinter as tk
from tkinter.ttk import Radiobutton
from tkinter import PhotoImage
from PIL import ImageTk, Image
#gesture resources 
from function import *
from keras.utils import to_categorical
from keras.models import model_from_json
from keras.layers import LSTM, Dense
from keras.callbacks import TensorBoard
#volume control libraries
import cv2 
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np 


class GUI:
    def __init__(self,root):
        self.root = root
        self.root.title("Wireless Sound Control")
        self.root.geometry("1000x600")
        self.root.minsize(300,200)

        self.upperframe = tk.Frame(self.root,background='white',height=20)
        self.upperframe.pack(side='top',fill='x',padx=0,anchor='n',pady=10)

        self.label = tk.Label(self.upperframe,text='Wireless Sound Control',font='times 18 bold',background='white')
        self.label.pack(side='top',pady=10)

        self.canv = tk.Canvas(self.upperframe)
        self.canv.pack(side='top')

        self.button_1 = Radiobutton(self.canv,text='Typing')
        self.button_1.pack(side='left',pady=5,padx=10)

        self.button_2 = Radiobutton(self.canv,text='Notepad')
        self.button_2.pack(side='right',pady=5,padx=10)

        self.bottomframe = tk.Frame(self.root,background='lightgrey')
        self.bottomframe.pack(expand=True,fill='both',side='top',anchor='n')

        self.notepad = tk.Text(self.bottomframe,)
        self.notepad.pack(fill='both',side='left')

        #Capture video frames
        cap = cv2.VideoCapture(1)
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.camera = tk.Label(self.bottomframe,width=400,height=500,image=imgtk)
        self.camera.pack(side='right')

        self.gesture_Thread = Thread(target=self.get_alpha_from_gesture)
        self.gesture_Thread.setDaemon(True)
        self.gesture_Thread.start()
        
        self.root.mainloop()


    def get_alpha_from_gesture(self):
        json_file = open("model.json", "r")
        model_json = json_file.read()
        json_file.close()
        model = model_from_json(model_json)
        model.load_weights("model.h5")

        colors = []
        for i in range(0,20):
            colors.append((245,117,16))
        print(len(colors))
        def prob_viz(res, actions, input_frame, colors,threshold):
            output_frame = input_frame.copy()
            for num, prob in enumerate(res):
                cv2.rectangle(output_frame, (0,60+num*40), (int(prob*100), 90+num*40), colors[num], -1)
                cv2.putText(output_frame, actions[num], (0, 85+num*40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
                
            return output_frame


        # 1. New detection variables
        sequence = []
        sentence = []
        accuracy=[]
        predictions = []
        threshold = 0.8 
        out_alpha = ''

        cap = cv2.VideoCapture(1)
        # cap = cv2.VideoCapture("https://192.168.43.41:8080/video")
        # Set mediapipe model

        with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:
            while cap.isOpened():

                #gestrue recognize here
                ret, frame = cap.read()
                cropframe=frame[40:400,0:300]
                # print(frame.shape)
                frame=cv2.rectangle(frame,(0,40),(300,400),255,2)
                # frame=cv2.putText(frame,"Active Region",(75,25),cv2.FONT_HERSHEY_COMPLEX_SMALL,2,255,2)
                image, results = mediapipe_detection(cropframe, hands)
                # print(results)
                
                # Draw landmarks
                # draw_styled_landmarks(image, results)
                # 2. Prediction logic
                keypoints = extract_keypoints(results)
                sequence.append(keypoints)
                sequence = sequence[-30:]

                try: 
                    if len(sequence) == 30:
                        res = model.predict(np.expand_dims(sequence, axis=0))[0]
                        # print(actions[np.argmax(res)])
                        predictions.append(np.argmax(res))
                        
                        
                    #3. Viz logic
                        if np.unique(predictions[-10:])[0]==np.argmax(res): 
                            if res[np.argmax(res)] > threshold: 
                                new = actions[np.argmax(res)]
                                if new != out_alpha:
                                    print("inserting..")
                                    self.notepad.insert('end', new)
                                    out_alpha = new

                                if len(sentence) > 0: 
                                    if actions[np.argmax(res)] != sentence[-1]:
                                        sentence.append(actions[np.argmax(res)])
                                        accuracy.append(str(res[np.argmax(res)]*100))
                                else:
                                    sentence.append(actions[np.argmax(res)])
                                    accuracy.append(str(res[np.argmax(res)]*100)) 

                        if len(sentence) > 1: 
                            sentence = sentence[-1:]
                            accuracy=accuracy[-1:]

                        # Viz probabilities
                        # frame = prob_viz(res, actions, frame, colors,threshold)
                except Exception as e:
                    # print(e)
                    pass
                    
                cv2.rectangle(frame, (0,0), (300, 40), (245, 117, 16), -1)
                cv2.putText(frame,"Output: -"+' '.join(sentence)+''.join(accuracy), (3,30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                
                # Show to screen
                b,g,r = cv2.split(frame)
                img = cv2.merge((r,g,b))
                im = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(image=im) 
                self.camera.configure(image=imgtk)
                # Break gracefully

if __name__ == '__main__':
    # sound_control_Process = Process(target=VolumeController.start_sound_control)
    # sound_control_Process.start()

    tk_object = tk.Tk()
    window = GUI(root = tk_object)

    # sound_control_Process.kill()
    

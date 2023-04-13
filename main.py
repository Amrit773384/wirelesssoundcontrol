from multiprocessing import Process
from threading import Thread
import VolumeController
#gui resources 
import tkinter as tk
from tkinter.ttk import Radiobutton
from tkinter import PhotoImage
from PIL import ImageTk, Image
#gesture resources 
# from function import *
# from keras.utils import to_categorical
# from keras.models import model_from_json
# from keras.layers import LSTM, Dense
# from keras.callbacks import TensorBoard
#volume control libraries
import cv2 
# import mediapipe as mp
# from math import hypot
# from ctypes import cast, POINTER
# from comtypes import CLSCTX_ALL
# from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
# import numpy as np 


class GUI:
    def __init__(self,root):
        self.root = root
        self.root.title("Wireless Sound Control")
        self.root.geometry("600x700")
        self.root.resizable(False,False)

        self.upperframe = tk.Frame(self.root,background='white',height=400,width=600)
        self.upperframe.pack(side='top',fill='x',anchor='n',padx=10,pady=10)
        self.cap = cv2.VideoCapture(1)
        img = self.cap.read()[1]
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(img).resize((self.upperframe['width'],self.upperframe['height']),Image.Resampling.LANCZOS)) 
        self.camera = tk.Label(self.upperframe,image=img)
        self.camera.pack(side='right')


        self.notepad_frame = tk.Frame(self.root,width=600,height=200) 
        self.notepad_frame.pack(expand=False,side='top')

        self.notepad = tk.Text(self.notepad_frame,font='consolas 14',height=7)
        self.notepad.pack(side='top',padx=10)


        self.bottomframe = tk.Frame(self.root,height=100,width = 600)
        self.bottomframe.pack(fill='both',side='top',padx=10,pady=10)

        commonfont = 'arial 16 '

        self.space_button = tk.Button(self.bottomframe,
                                    text="Space",
                                    font=commonfont,
                                    background='AntiqueWhite1',
                                    padx=20,pady=10,
                                    command=lambda:self.notepad.insert('end', ' ')
                                    )
        self.space_button.grid(row=0,column=0,padx=55,pady=10)
        
        self.clear_button = tk.Button(self.bottomframe,
                                    text='Clear',
                                    font=commonfont,
                                    background='lightgreen',
                                    padx=20,pady=10,
                                    command=lambda:self.notepad.delete(1.0,'end')
                                    )
        self.clear_button.grid(row=0,column=1,pady=10)

        self.savetext_button = tk.Button(self.bottomframe,
                                    text='Save',
                                    font=commonfont,
                                    background='skyblue',
                                    padx=20,pady=10,
                                    command=self.save
                                    )
        self.savetext_button.grid(row=0,column=2,padx=55,pady=10)

        # self.gesture_Thread = Thread(target=self.get_alpha_from_gesture)
        # self.gesture_Thread.setDaemon(True)
        # self.gesture_Thread.start()
        self.notepad.focus_set()
        # while True :
        #     try:
        #         img = self.cap.read()[1]
        #         img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        #         img = ImageTk.PhotoImage(Image.fromarray(img).resize((self.upperframe['width'],self.upperframe['height']),Image.Resampling.LANCZOS)) 
        #         self.camera['image'] = img
        #         self.root.update()
        #     except:break
    def save(self):
        print(self.notepad.get(1.0, 'end'))
        print("text save ..")
        
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
                img = cap.read()[1]
                img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(Image.fromarray(img)) 
                self.camera.configure(image=img)
                self.root.update()
                # Break gracefully

if __name__ == '__main__':
    # sound_control_Process = Process(target=VolumeController.start_sound_control)
    # sound_control_Process.start()

    tk_object = tk.Tk()
    window = GUI(root = tk_object)

    # sound_control_Process.kill()
    

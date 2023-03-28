#gui resources 
import tkinter as tk
from tkinter.ttk import Radiobutton
from tkinter import PhotoImage

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

        self.root.mainloop()
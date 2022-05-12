import tkinter as tk
import cv2
import os
from tkinterdnd2 import *

window = tk.Tk()
window.geometry("700x300")
window.title("Vehicle Detection")

instructions = tk.Label(text="Run this program to begin displaying results of processed ")

def processVideoApply():
  print(input_video_val.get())

root_label = tk.Label(window, text="Root Directory")
root_label.grid(row = 0, column = 0, sticky = 'w', pady = 2)
root_val = tk.Entry(window, bd =5, w="100")
root_val.insert(0, os.getcwd() )
root_val.grid(row = 0, column = 1, sticky = 'w', pady = 2)

input_video_label = tk.Label(master=window, text="Input Video")
input_video_label.grid(row = 1, column = 0, sticky = 'w', pady = 2,)
input_video_val = tk.Entry(master=window, bd=5,w="100")
apply_video_btn = tk.Button( master=window, text="Apply", command=processVideoApply )
apply_video_btn.grid(row = 1, column = 2, sticky = 'w', pady = 2)
input_video_val.grid(row = 1, column = 1, sticky = 'w', pady = 2)
input("Press Enter to continue...")
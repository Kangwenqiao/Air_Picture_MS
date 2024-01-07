#main.py
import tkinter as tk

from GUI import ObjectDetectionGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = ObjectDetectionGUI(root, 'background.jpg')
    root.mainloop()
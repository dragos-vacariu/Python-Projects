import tkinter as tk
from tkinterdnd2 import *

def drop(event):
    entry_sv.set(event.data)

root = TkinterDnD.Tk()
root.geometry("390x60+0+0")
entry_sv = tk.StringVar()
entry = tk.Entry(root, textvar=entry_sv, width=80)
entry.pack(fill=tk.X)
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)
root.mainloop()
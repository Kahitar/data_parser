from tkinter import *
from tkinter import filedialog

root = Tk()

top = Toplevel()
top.wm_attributes('-topmost', 1)
top.withdraw()
top.protocol('WM_DELETE_WINDOW', top.withdraw)

def do_dialog():
    oldFoc = top.focus_get()
    print(filedialog.askdirectory())
    if oldFoc: oldFoc.focus_set()

b0 = Button(top, text='choose dir', command=do_dialog)
b0.pack(padx=100, pady=100)

def popup():
    top.deiconify()
    b0.focus_set()

b1 = Button(root, text='popup', command=popup)
b1.pack(padx=100, pady=100)
root.mainloop()
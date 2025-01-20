import tkinter as tk

class ToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text

        def enter(event):
            self.showTooltip()
        def leave(event):
            self.hideTooltip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def showTooltip(self):
        self.tooltipwindow = tw = tk.Toplevel(self.widget)
        print(self.tooltipwindow)
        tw.wm_overrideredirect(1) # window without border and no normal means of closing
        tw.wm_geometry("+{}+{}".format(self.widget.winfo_rootx(), self.widget.winfo_rooty()+50))
        label = tk.Label(tw, text = self.text, background = "#ffffe0", relief = 'solid', borderwidth = 1, fg="black", width=60)
        label.pack()


    def hideTooltip(self):
        if self.tooltipwindow != None:
            self.tooltipwindow.destroy()
            self.tooltipwindow = None
            print("Destroyed")
        
       
root = tk.Tk() 

your_widget = tk.Button(root, text = "Hover me!")
your_widget.place(x=10, y=10)
ToolTip(widget = your_widget, text = "Hover text!")

root.mainloop()
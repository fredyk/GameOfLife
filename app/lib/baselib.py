import os, sys
from Tkinter import *
from .thread import Thread
from time import sleep, time as now

# Update 2015/12/21

class BaseControl(Thread):

    NAME = "App"
    
    def __init__(self, gui):
        Thread.__init__(self)
        self.gui = gui
        self.opened_files = []
        self.afterStop(self.stopThread)
    
    def run(self):
        self.gui.basicStyle()
        self.gui.setStyle()
        self.main()
    
    def addOpenFile(self, _file):
        self.opened_files.append(_file)
        return _file
    
    def setStatus(self, st):
        self.tkthread.after_gui(
            self.gui.status_label.config,
            text=self.NAME + " - " + st
            )
    
    def resetStatus(self):
        self.tkthread.after_gui(
            self.gui.status_label.config,
            text=self.NAME
            )
    
    def resetTitle(self):
        self.gui.title(self.NAME)
    
    def stopThread(self):
        for of in self.opened_files:
            if of is not None and not of.closed:
                try:
                    of.flush()
                    of.close()
                    print "closed", of.name
                except Exception as e:
                    print "could not close",of.name,e

class GUI(Tk):
    
    SIZES = [ (1024, 768), (1905, 1005), (1860, 1030) ]

    def __init__(self, control = None):
        if control is None:
            raise ValueError("Control argument cannot be None")
        Tk.__init__(self)
        self.w = 800
        self.h = 600
        self.control = control(self)
        self.control.afterStop(self.destroy)
        self.title(self.control.NAME)
        self.protocol("WM_DELETE_WINDOW", self.control.stop)
        self.after(100, self.control.start)

    def start(self):
        self.mainloop()

    def basicStyle(self):
        self.geometry("%dx%d+0+0" % (self.w, self.h) )
        self.main_frame = Frame(self,bg="white", width=self.w + 4,
                                height = self.h + 4)
        self.main_frame.place(relx=0,rely=0,x=-2,y=-2)
        self.status_frame = Frame(self.main_frame,bg="lightgray",
            width=self.w + 4,
            height=30)
        self.status_frame.place(rely=1,x=0,y=0,anchor=SW)
        self.status_label = Label(self.status_frame,
            bg="lightgray",
            text=self.control.NAME+\
            " - Iniciando...")
        self.status_label.place(rely=1,y=-5,x=10,anchor=SW)
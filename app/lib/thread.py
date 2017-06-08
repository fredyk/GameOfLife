import os, sys, threading, re
from time import sleep, time as now
from butils import Butils
from Tkinter import TclError

# Update 2015/12/21

# __all__ = [ "Thread", "Runner", "TkThread" ]

class Thread(threading.Thread):


    def __init__(self, *args, **kargs):
        threading.Thread.__init__(self)
        self.args = args
        self.kargs = kargs
        self.verbose = True
        self.stopped = False
        self.paused = True
        self.threads = None
        self.on_start = []
        self.on_stop = []
        self.after_stop = []

    def onStart(self, callback, *args, **kargs):
        if (self.on_start is None): self.on_start = []
        self.on_start.append( ( callback, args, kargs ) )

    def onStop(self, callback, *args, **kargs):
        if (self.on_stop is None):
            self.on_stop = []
        print "added", callback
        self.on_stop.append( ( callback, args, kargs ) )

    def afterStop(self, callback, *args, **kargs):
        if (self.after_stop is None): self.after_stop = []
        print "added", callback
        self.after_stop.append( ( callback, args, kargs ) )

    def run(self):
        if self.on_start is None:
            return 0
        print self.on_start
        for ons in self.on_start:
            ons[0]( *ons[1], **ons[2] )

    def getConfig(self):
        return ("info", self, {"args" : self.args, "kargs" : self.kargs} )

    def __str__(self):
        return str(self.__class__) + ", " + str(self.getConfig())

    def addThread(self, thread):
        if thread is not None and "stop" in dir(thread):
            if self.threads is None:
                self.threads = []
            self.threads.append(thread)

    def getThreads(self):
        return self.threads or []

    def noVerbose(self):
        self.verbose = False

    def isRunning(self):
        return not self.stopped

    def isBusy(self):
        return not self.paused

    def isPaused(self):
        return self.paused

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        if self.isRunning():
            for tp in self.on_stop:
                print tp[0]( *tp[1], **tp[2] )
            for t in self.getThreads():
                print t.stop()
            self.stopped = True
            for tp in self.after_stop:
                print tp[0]( *tp[1], **tp[2] )
            return ( "stopped", self)
        else:
            return ( "already stopped", self )

class Runner(Thread):

    def run(self):
        callback = self.kargs["callback"]
        args = None
        kargs = None
        if("args" in self.kargs):
            args = self.kargs["args"]
        if("kargs" in self.kargs):
            kargs = self.kargs["kargs"]

        if self.verbose:
            print "callback info", callback, args, kargs
        try:
            if(bool(args)^bool(kargs)):
                if(bool(args)):
                    return callback(*args)#, **kargs)
                else:
                    return callback(**kargs)
            elif(args):
                return callback(*args, **kargs)
            else:
                return callback()
        except TclError as e: print e
        self.stop()

class TkThread(Thread):

    class Task():


        def __init__(self, _time, callback, *args, **kargs):
            self.time = _time
            self.callback = callback
            self.args = args
            self.kargs = kargs

        def getTime(self):
            return self.time

        def setTime(self, _time):
            self.time = _time

        def getCallback(self):
            return self.callback

        def getArgs(self):
            return self.args

        def getKargs(self):
            return self.kargs

        def __str__(self):
            return "<%s %s%s%s%s>" % (
                "Task instance",
                str(self.time),
                str(self.callback),
                str(self.args),
                str(self.kargs)
                )

    delay      = 0.067

    def __init__(self, *args, **kargs):
        Thread.__init__(self, *args, **kargs)
        print self.getConfig()
        self.onStart(self.main)
        self.idle_tasks = []
        self.last_time  = 0
        self.started = False
        self.on_finish = None
        self.of_args = ()
        self.of_kargs = {}

    def nestedRun(self,callbacks, *args, **kargs):
        res = callbacks[-1](*args, **kargs)
        for cb in callbacks[::-1][1:]:
            res = cb(res)
            print res,
        print
        # return callback1(callback2(*args, **kargs))
        return res

    def after(self, delay, callback, *args, **kargs):
        if(callback is not None):
            _time = self._toAbsTime(delay)
            if(not(self.started)):
                _time = 0 - delay
            task = self.Task( _time, callback, *args, **kargs )

            self.idle_tasks.append( task )
            return task
        return False

    def after_idle(self, callback, *args, **kargs):
        return self.after(0, callback, *args, **kargs)

    def after_gui(self, callback, *args, **kargs):
        return self.after(Butils.base_delay, callback, *args, **kargs)

    def _toAbsTime(self, delay, init = None):
        return (init or now()) + delay/1000.0

    def getIdleTasks(self):
        return [(task, str(task)) for task in self.idle_tasks]

    def main(self):
        self.mainloop()

    def mainloop(self):
        self.started = True
        for task in self.idle_tasks:
            if(task.getTime() < 0):
                task.setTime( self._toAbsTime( 0 - task.getTime(),
                                init = now() ) )

        while (not(self.stopped)):
            init = now()
            _error = True
            while (_error):
                try:
                    self.idle_tasks.sort(key=lambda x: x.time)
                    _error = False
                except ValueError: pass

            while( (len(self.idle_tasks) > 0) and (self.idle_tasks[0].getTime() < init) ):
                task = self.idle_tasks.pop(0)
                callback = task.getCallback()
                args = task.getArgs()
                kargs = task.getKargs()
                if(callback):
                    try:
                        if( bool(args) ^ bool(kargs) ):
                            if(args):
                                callback( *args )
                            else:
                                callback( **kargs )
                        elif( args ):
                            callback( *args, **kargs )
                        else:
                            callback()
                        if(self.verbose):
                            print {"now" : init, "task time" : task.getTime(),
                                "diff" : (init - task.getTime()) / 1000.0,
                                "task" : str(task)}
                    except TclError as e:
                        if(self.verbose):
                            print e

            _sleep = max(0, self.delay - now() + init)
            if(len(self.idle_tasks)>1)and self.verbose:
                print "\n\nQUEUED", len(self.idle_tasks), "TASKS to ", _sleep, "seconds\n"

            sleep( _sleep )
        print self.stop()
        # if self.on_finish is not None:
        #     self.on_finish(*self.of_args, **self.of_kargs)

    def onFinish(self, callback, *args, **kargs):
        # callback()
        self.on_finish = callback
        self.of_args = args
        self.of_kargs = kargs
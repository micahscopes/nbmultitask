from ipywidgets import Button, Layout
from threading import Thread
from multiprocessing import Process, Queue, Event
from logging.handlers import QueueHandler
from ipywidgets import Output
from IPython.display import display
from contextlib import contextmanager
from time import sleep
import sys
import random

from logging import Handler
class LogToQueue(Handler):
    def __init__(self,queue=None):
        self.q = queue if queue else Queue()
        Handler.__init__(self)
    def write(self,x):
        return self.q.put(x)
    def put(self,x):
        return self.q.put(x)
    def get(self):
        return self.q.get()
    def empty(self):
        return self.q.empty()
    def print(self,x,end='\n'):
        self.write(str(x)+end)

@contextmanager
def empty_context():
    yield None

EmptyContext = empty_context()

def withLogAndControls(superclass):
    class Processor(superclass):
        def __init__(self, *init_args, loop=False, log_refresh_time=0.05, use_terminate=True, args=(), kwargs={}, **init_kwargs):
            self.use_terminate = use_terminate
            self.loop = loop
            self.output = Output()
            self.started = Event()
            self.exiting = Event()
            self.exited = Event()

            self.start_stop_button = Button(description='start')
            self.start_stop_button.on_click(self.__toggle_start_stop__)
            self.start_stop_button.button_style = 'success'
            
            self.refresh_log_button = Button(description='refresh log')
            self.refresh_log_button.on_click(lambda evt: self.refresh_log())
            self.clear_log_button = Button(description='clear log')
            self.clear_log_button.on_click(lambda evt: self.clear_log())

            self.watch_log_button = Button(description='watch')
            self.watch_log_button.button_style = 'primary'
            self.watch_log_button.on_click(self.__toggle_watch_log__)
            
            
            self.log = LogToQueue()
            if issubclass(self.__class__,Thread): 
                kwargs['thread_print'] = self.log.print
            self.log_refresh_time = log_refresh_time
            self.watching_log = Event()
            
            superclass.__init__(self,*init_args, args=args, kwargs=kwargs, **init_kwargs)

        def refresh_log(self):
            refreshed_once = False

            while self.watching_log.is_set() or not refreshed_once:
                refreshed_once = True
                if self.exited.is_set():
                    self.watching_log.clear()
                    self.__disable_buttons_after_exited__()

                while not self.log.empty():
                    msg = self.log.get()
                    with self.output:
                        print(msg,end='')
                    if self.exited.is_set() and self.log.empty():
                        return

                sleep(self.log_refresh_time) # save a few CPU cycles

        def watch(self):
            self.watching_log.set()
            self.watch_log_button.description = 'stop watching'
            self.watch_log_button.button_style = 'warning'
            # This thread will watch the log as long as self.watching_log is set.
    #         self.refresh_log()
            Thread(target=self.refresh_log,name='watching log for %s' % str(self)).start()

        def stop_watching(self):
            self.watching_log.clear()
            self.watch_log_button.description = 'watch'
            self.watch_log_button.button_style = 'primary'

        def clear_log(self,wait=False):
            self.output.clear_output(wait=wait)            
            
        def show_log(self):
            display(self.output)

        def start(self):            
            super().start()
            self.started.set()
            with self.output:
                print(self)
                print('running...')

            self.start_stop_button.description = 'stop'
            self.start_stop_button.button_style = 'danger'

        def stop(self):
            if not self.started.is_set():
                return

            if hasattr(self,'terminate') and self.use_terminate:
                self.terminate()
                with self.output:
                    print('terminating...')
                self.exited.set()
            else:
                with self.output:
                    print('letting work finish before stopping...')

                self.exiting.set()

                self.exited.wait()
                self.exiting.clear()
            
            sleep(0.1) # Need to wait a little bit before the Process object's status is `stopped`
            with self.output:
                print(self)
                
            self.__disable_buttons_after_exited__()

        def run(self):
            if issubclass(self.__class__,Process):
                sys.stdout = self.log
                sys.stderr = self.log

            fn = self._target if self._target is not None else getattr(self,'work')
            
            if self.loop:
                while not self.exiting.is_set():
                    fn(*self._args,**self._kwargs)
            else:
                fn(*self._args,**self._kwargs)

            
            # when the work is done, signal that we are finished
            self.exited.set()
        
        def __disable_buttons_after_exited__(self):
            self.start_stop_button.description = 'finished'
            self.start_stop_button.button_style = ''
            self.start_stop_button.disabled = True
            self.watch_log_button.close()
        
        def __toggle_start_stop__(self,e=None):
            if not self.started.is_set() and not self.exited.is_set():
                self.start()
            else:
                self.stop()

        def __toggle_watch_log__(self,e=None):
            if not self.watching_log.is_set() and not self.exited.is_set():
                self.watch()
            elif not self.exited.is_set():
                self.stop_watching()
            elif self.exited.is_set():
                self.stop_watching()
                
        def show_start_stop_buttons(self):
            display(self.start_stop_button)

        def show_log_buttons(self):
            display(self.watch_log_button)
            display(self.clear_log_button)

        def control_panel(self):
            self.show_start_stop_buttons()
            self.show_log_buttons()
            self.show_log()

    return Processor
    
ProcessWithLogAndControls = withLogAndControls(Process)
ThreadWithLogAndControls = withLogAndControls(Thread)

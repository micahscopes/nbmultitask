# nbmultitask
multithreading/multiprocessing with ipywidgets and jupyter notebooks

## example usage
The following will return a "control panel" with buttons for starting and monitoring the thread.
```python
from nbmultitask import ThreadWithLogAndControls
from time import sleep

# the target function will be passed a function called `thread_print`
def fn(thread_print):
    i = 1
    # be careful with loops... (in order for the stop button to work)
    while i <= 5:
        thread_print('%i...' % i)
        sleep(1.5)
        i+=1

task = ThreadWithLogAndControls(target=fn, name="do some stuff")
task.control_panel()
```

Please see the [`examples.ipynb`](http://nbviewer.jupyter.org/github/micahscopes/nbmultitask/blob/39b6f31b047e8a51a0fcb5c93ae4572684f877ce/examples.ipynb) for more usage examples.

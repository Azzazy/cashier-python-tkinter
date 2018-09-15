# Cashier App using Python and Tkinter

## How to run
### Use python3 to run by

    python3 src/hello.py

### To generate .exe 
To generate Windows 64bit using docker from Ubuntu

    docker run -v "$(pwd):/src/" cdrx/pyinstaller-windows

To generate 32bit from a vritual machine

    C:\Users\muhammad\AppData\Local\Programs\Python\Python37-32\python -m PyInstaller --onefile C:\Users\muhammad\Documents\cashier-python-tkinter\src\main.py --distpath C:\Users\muhammad\Documents\cashier-python-tkinter\src\out\ --specpath C:\Users\muhammad\Documents\cashier-python-tkinter\src\

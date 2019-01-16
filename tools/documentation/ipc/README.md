# Inter-process Communication IARC-2019
IPC is a tool to create and manage a separate process.

## Configuration
The inter-process communication should be run from within the tools directory or in the directory 
containing tools. If that is not the case, in IPC.__init__ the filename variable should be changed.

Constants
    
    Command to start python 2.7
        py2command = 'python'
    
    Command to start python 3.6 (can rename python.exe in Python3 folder to python3.exe)
        py3command = 'python3'  

Parameters
    
    version: 2/3, default=2
        Version of python to create subprocess in.

    reader: bool, default=True
        Whether or not to use the shell reader. Sometimes needed to see process output.

    thread_stop: threading.Event, default=threading.Event
        The thread stop to be used by shell reader, pass in own thread stop or allow it to create its own.

## Operating
Sometimes first run after clone doesnt work!

__IPC.send(data)__ to send data to subprocess.

__IPC.alive__ (bool) to see created process is still running.

__IPC.quit()__ to safely close the IPC.


## Troubleshooting
If you have issues or suggestions, message Cole Dieckhaus on slack or email @ csdhv9@mst.edu.
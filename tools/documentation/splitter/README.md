# Data Splitter IARC-2019
The data splitter is a tool to easily manage where output data goes. 
Can easily toggle what tools to send data without having to change any code, just one parameter.


## Configuration

Parameters
    
    logger_desired_headers: list, default=[]
        Headers for logger to log data for. Logger object not created if no headers given.

    use_rtg: bool, default=True
        Whether to use the real time grapher or not.

    version: 2 / 3, default=2
        Version of python to create rtg subprocess in. Not used if use_rtg=False.
        
    
## Operating
__DataSplitter.tools_active__ Returns the objects of all active tools.
__DataSplitter.send(Data)__ Send data to all active tools. 
__DataSplitter.exit()__ Safely exit all tools.


## Troubleshooting
If you have issues or suggestions, message Cole Dieckhaus on slack or email @ csdhv9@mst.edu.
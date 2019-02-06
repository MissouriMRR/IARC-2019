# Logger IARC-2019
Logging for the drone, meant to work on board.

## Configuration
When a Logger object is created, the desired_headers parameter should be set to a list of headers of data streams to be 
logged from the dictionaries of received data.

The filename to save the log file to will automatically be chosen. There should be a __'generated_logs'__
file in tools/

The logger will not work if the main file that runs it is not in the IARC directory or the tools directory.
To fix this add a generated_logs directory to the main running file's directory.

## Operating

__Logger.update()__ can be called to pass in data. 
The time that the logger receives the data is the time that gets logged.
The logger will parse the passed in data looking for the headers in desired_headers.

Data should be passed into the update function in the format
    
    {header(str): data(number)}
    
__logger.exit()__ function should be called to safely close the logger.

## Troubleshooting
If you have issues or suggestions, message Cole Dieckhaus or Jon Ogden on slack.
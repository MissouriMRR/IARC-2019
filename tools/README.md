# Tools IARC-2019

![tools diagram](documentation/tools_layout.png)

## Data Splitter
Starts and sends data to both the logger and ipc(real time grapher).

Meant to be __implemented directly into flight code__ so that the logger and RTG do not have to 
be implemented separately.

Created and manages *Logger* and or *IPC*(both can be toggled in obj parameters).

Run in 2.7, __unit test automatically runs__ with script being run.

More details in documentation/splitter/README.md

## Logger
Logs data as it comes in from the drone in real time.

Optimally is __created and managed by data_splitter__ so that more data destinations can be added easily.

Created and managed by *data_splitter* and creates logs in generated_logs/.

Run in 2.7 or 3.6, __unit test automatically runs__ with script being run.

More details in documentation/log/README.md

## Inter-process Communication
Creates and interacts with a subprocess. Currently used to keep the real_time_graphing process
separate from main. This is beneficial because matplotlib needs to be in main thread and that may
cause issues when the rtg needs to interact with other code.

Optimally is __created and managed by data_splitter__ so that more data destinations can be added easily.

Created and managed by *data_splitter*, creates and manages *rtg_cache*.

Run in 2.7, __unit test automatically runs__ with script being run.

More details in documentation/ipc/README.md

## RTG Cache
Caches data for real time grapher. Meant to be used with Inter-process Communication.

__RTGCache.start()__ Call rtg.run() and begin reading input from stdin.

Optimally is __used with the inter-process communication__ to keep the matplotlib instance in the main
thread without interfering with other code.

Created and managed by *inter-process communication*, creates and manages *real time grapher*.

Run in 2.7 or 3.6, __unit test can be run from main if uncommented__.

## Real Time Grapher
Graphs data as it comes in from drone in real time. Run with the inter-process communication.

IF IN UBUNTU: Need to have apt package python-tk otherwise the IPC will throw weird errors!

Currently is most easily __implemented with rtg_cache__.

Created and managed by *rtg_cache*, outputs with matplotlib.

Run in 2.7 or 3.6, __unit test automatically runs__ with script being run.

More details in real_time_graph/README.md

## Config Maker (To be phased out)
Creates config files for RTG and Log Grapher.

Meant to be run independently.

Makes use of *tab_manager*, which makes use of *graph_node*.

Run old_config_maker/gui_main in 3.6, __config maker automatically runs__ with script.

More details in old_config_maker/README.md
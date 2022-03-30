#OVERVIEW
Application TMH-PV-sim, was created to read home power consumption and comparing it with the simulated generated power by photovoltaic solarcells. As long as power consumption field measurements are not available program creates synthetic power consumption. 
###ARCHITECTURE
Whole workflow of the data can be summarized in the following architecture:
```
METER -> BROKER -> SIMULATOR -> POSTPROCESSING
```
* METER: power consumption data. Might be synthetic or from field
* BROKER: transfers meter data to the main application
* SIMULATOR: reads data from broker (and with the same from meter) and based on them compare power consumption with simulated generation of power by photovoltaic panels
* POSTPROCESSING: saves data in .csv and .png form, after whole process is finished

Due to the architecture, at this level of program usage, multiprocessing was needed to run parallelly both: ```METER``` and ```SIMULATOR``` blocks.
###PARAMETERS
All required for the program parameters should be defined in the ```config.toml``` file. Main parameters are defined below, additional required parameters will be defied later in this file.
* ```naming_prefix``` string, prefix added to the save names 
* ```verbosity``` string, ```Low``` or ```High``` we can turn of or on printing in the console
* ```sampling``` integer, how often we want to make measurement (in seconds)
* ```plot``` boolean, do plot should be generated and saved
* ```working_protocol``` string, program work condition ```Continuous``` or ```DateRange```
* ```host``` string, host address (```localhost``` or ```ip```)
* ```queue``` string, ```BROKER``` queue to send message 
* ```maximal_power_W``` float, ```METER``` maximal measurement level. Measurements over range will be marked as 1 in the output column ```over_range [bool]```
* ```power_consumption_peak_W``` float, information used to generate synthetic measurement signal. Describes maximal power consumption in Watts
* ```constant_power_consumption_W``` float, information used to generate synthetic measurement signal. Describes constant power consumption of measured object like home refrigerator in Watts
* ```latitude_deg``` string, geographical latitude in deg of the photovoltaic solar cell
* ```longitude_deg``` string, geographical longitude in deg of the photovoltaic solar cell
* ```area_m2``` float, active area in square meters of the photovoltaic installation used for simulation 
* ```efficiency``` float, sunlight-electricity conversion efficiency of the photovoltaic panel
###PROTOCOLS
Program have two main working protocols:
* ```Continuous```: application works continuously until keyboard interruption (ctrl+c) will kill the application. This protocol needs to have defined one
  * ```continuous_protocol_lines_to_save``` defines how many measurements should be stored and further saved in single .csv result file
* ```DateRange```: application works in given date-time range
  * ```date_range_protocol_datetime_end``` defines beginning of the simulation
  * ```date_range_protocol_datetime_beg``` defines end of the simulation

#DEPENDENCIES INSTALLATION
To make first run you need to have installed all required ```Python 3.8``` libraries listed in the ```requirements.txt``` file. This file also is read by ```setup.sh``` script and install them under python localization given in ```config.toml``` as ```python_path``` parameter. This script install also required third party software ```RabbitMQ```. Two additional parameters appears in ```config.toml``` for the firs run:
* ```python_libraries_installation``` boolean, set tu true if you want to install python libraries, otherwise set to false
* ```rabbitmq_installation``` boolean, set tu true if you want to install Rabbit MQ, otherwise set to false

To run setup, just type in the terminal opened in the application root folder:
```commandline
bash setup.sh
```
During the setup process, password giving might appear.
#RUN
To run the application, fulfill properly all ```config.toml``` parameters with special focus on the protocols parameters. Chose one of two protocols, and fulfill corresponding to it parameters. Describe all parameters of ```METER``` and photovoltaic panels. After this to run the program just type in the terminal opened in the application root folder:
```commandline
python3.8 main.py
```
Or in the PyCharm Python console
```python
runfile("./main.py")
```
#ADDITIONAL NOTES
* Proposed are two manual tests for both protocols. To do that, set in ```config.toml``` parameters as:
  * ```Continuous```Test case - should start to return .csv file and .png image with 10 points each. In this case to see best differences it is proposed to change computer time to ~14.55, or just run it this hour.
    * ```naming_prefix = "test_Continuous"```
    * ```verbosity = "High"```
    * ```sampling = 2```
    * ```plot = true```
    * ```working_protocol = "Continuous"```
    * ```continuous_protocol_lines_to_save = 10```
  * ```DateRange``` Test case - should return whole day power consumption .csv data and .png
    * ```naming_prefix = "test_DateRange"```
    * ```verbosity = "Low"```
    * ```sampling = 60```
    * ```plot = true```
    * ```working_protocol = "DateRange"```
    * ```date_range_protocol_datetime_beg = "2021-12-01 00:00:00"```
    * ```date_range_protocol_datetime_end = "2021-12-01 23:59:00"```
* All results will be saved in the ```result``` folder
* All libraries were written in the ```src``` folder
* Homework description is in the ```dock``` folder
* For simulation PVlib was used: https://github.com/pvlib/pvlib-python
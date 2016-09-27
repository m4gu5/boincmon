boincmon
========

What
----
boincmon is a script which turns your Raspberry Pi with an attached Adafruit i2c 16x2 RGB LCD Plate into... well, into a BOINC Monitor! It periodically checks if your hosts are online and if they are shows their current status.
#### Output as of now
* \# of running tasks.
* \# of uploading tasks
* \# of downloading tasks

Pics
----
#### Splash screen
![alt tag](https://pbs.twimg.com/media/CL0OIyWWwAIeU6j.jpg)
#### 5 running tasks
![alt tag](https://pbs.twimg.com/media/CL0OI1NWoAABngj.jpg)
#### host down
![alt tag](https://pbs.twimg.com/media/CL0OIVMWwAEMB2s.jpg)
#### 5 running, 9 uploading tasks
![alt tag](https://pbs.twimg.com/media/CL0OI3hWwAAt_DS.jpg)
#### 0 running, 9 uploading tasks
![alt tag](https://pbs.twimg.com/media/CL0OPTdWgAArQh-.jpg)

How
---
boincmon uses a xml configuration file in which you store your hosts to be monitored.
The script then uses the boinccmd command to periodically query the hosts.

To make things more clear, here is an example of a simple configuration file.
```
<?xml version="1.0" encoding="UTF-8"?>
<hosts>
	<!-- Insert your hosts here -->
	<host name="&lt;your_alias&gt;">
		<!-- IP Address -->
		<address>127.0.0.1</address>
		<!-- Password defined in gui_rpc_auth.cfg. Leave empty if no password was set. -->
		<password></password>
                <!-- Number of tasks which are expected to run simultaneously on this host. -->
		<!-- This is usually the number of threads the CPU supports + 1 if there are running GPU tasks + 1 if you run WUProp -->
		<!-- If fewer tasks run at any time the display color will change to yellow. -->
                <optimum_task_count>4</optimum_task_count>
	</host>
</hosts>
```

Such Colors
-----------
The basic concept is easy: 
Green background + smiling face: **Everything ok!**

Yellow background + smiling face: The host is not fully utilized.

Red background + sad face: **We have a problem!**

If suddenly skulls appear on your LCD, the current host is probably down.

Basic setup
-----------
It is assumed that you already had set up your LCD display properly and have the LCD libs on your Raspi. (See <https://github.com/adafruit/Adafruit_Python_CharLCD>)

* Install boincmgr package
    * Raspbian: 

        `# apt-get install boinc`

* Assign static ip addresses on remote hosts to be monitored
* Allow Raspi to access BOINC on remote hosts via remote_hosts.cfg
* Create/Modify xml configuration _boinc_hosts.xml_
* Copy the file _Adafruit_CharLCD.py_ into the program directory

    `$ cp Adafruit_Python_CharLCD/Adafruit_CharLCD/Adafruit_CharLCD.py boincmon/`
    
* Run as root

    `$ sudo python boincmon.py`
    
Root privileges are required in order to access the LCD display.


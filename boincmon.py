#!/usr/bin/python

# Author: @m4gu5
# BOINC CPID: a0462ef12d6f11deac43fb0fb3c8e86c
# You are free to copy, share and modify this script

import Adafruit_CharLCD as LCD
import argparse
import xml.etree.ElementTree as xml
import re
import subprocess
import time


NEWLINE = '\n'
PING_COUNT = 3
GET_HOSTS_RETRY_INTERVAL = 10

ACTIVE_TASKS_PATTERN = '^\s*active_task_state: (1|9|EXECUTING)$'
UPLOADING_TASKS_PATTERN = '^\s*state: (4|uploading)$'
DOWNLOADING_TASKS_PATTERN = '^\s*state: (1|downloading)$'

# Char codes depend on create_custom_chars()
SMILING_FACE_CHAR = '\x01'
SAD_FACE_CHAR = '\x02'
RUNNING_GUY_CHAR = '\x03'
SKULL_CHAR = '\x04'
UPLOAD_CHAR = '\x05'
DOWNLOAD_CHAR = '\x06'

PROGRAM_BANNER = SKULL_CHAR + '   boincmon   ' + SKULL_CHAR

def create_custom_chars():
    """Creates custom characters to be used by the lcd display. Characters were created using http://www.quinapalus.com/hd44780udg.html."""
    # Smiling face
    lcd.create_char(1, [0,10,0,17,17,14,0,0])
    # Sad face
    lcd.create_char(2, [0,10,0,0,14,17,0,0])
    # Running guy
    lcd.create_char(3, [0,4,1,14,20,6,9,16])
    # Skull
    lcd.create_char(4, [0,14,31,21,31,14,10,0])
    # Upload
    lcd.create_char(5, [0,4,14,21,4,5,5,0])
    # Download
    lcd.create_char(6, [0,20,20,4,21,14,4,0])

def show_splash():
    lcd.clear()
    lcd.set_color(0.0, 1.0, 1.0)
    lcd.message(PROGRAM_BANNER + NEWLINE + 'Happy Crunching!')

def get_boinc_hosts(filename):
    """Parses the xml file containing the host definitions and returns the hosts in the following format: {hostname : {'address' : address, 'password' : password, 'optimum_task_count' : optimum_task_count}}.
    :param filename: The name of the file which contains the host definitions.
    """
    hosts_dict = {}
    hosts = xml.parse(filename).getroot()
    for host in hosts.findall('host'):
        name = host.get('name')
        try:
            address = host.find('address').text
            password = host.find('password').text
        except AttributeError:
            # Some child could not be found
            continue
        try:
            optimum_task_count = host.find('optimum_task_count').text
        except AttributeError:
            optimum_task_count = -1

        errors_occured = False

        # Handle null values
        if address == None:
            continue
        name = address if name == None else name
        password = '' if password == None else password

        host_config = {}
        host_config['address'] = address
        host_config['password'] = password
        host_config['optimum_task_count'] = int(optimum_task_count)
        hosts_dict[name] = host_config
    return hosts_dict

def is_host_reachable(address):
    """Check if host at ip address is online by pinging it.
    :param address: The ip address of the host to check.
    """
    p = subprocess.Popen(['ping', '-c', str(PING_COUNT), address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    p.stdout.close()
    p.stderr.close()
    return p.returncode == 0

def create_hostname_line(hostname, status_icon):
    hostname_line = hostname
    if len(hostname) > 15:
        hostname_line = hostname_line[:14]
    while len(hostname_line) < 15:
        hostname_line += ' '
    return hostname_line + status_icon

def get_occurences(pattern, tasks):
    """Gets the number of occurences of a regex in a string.
    :param pattern: The pattern to search for.
    :param tasks: The string in which the pattern will be searched.
    """
    count = 0
    for line in tasks.split(NEWLINE):
        if re.search(pattern, line):
            count += 1
    return count

def get_tasks(address, password):
    """Gets the output of boinccmd --get_tasks for a specified host.
    :param address: The ip address of the host.
    :param password: The password of the host.
    """
    p = subprocess.Popen(['boinccmd', '--host', address, '--passwd', password, '--get_tasks'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    p.stdout.close()
    p.stderr.close()
    return out

def get_number_of_active_tasks(tasks):
    return get_occurences(ACTIVE_TASKS_PATTERN, tasks)

def get_number_of_uploading_tasks(tasks):
    return get_occurences(UPLOADING_TASKS_PATTERN, tasks)

def get_number_of_downloading_tasks(tasks):
    return get_occurences(DOWNLOADING_TASKS_PATTERN, tasks)

def create_host_info_line(running_count, upload_count, download_count):
    """Creates the line containing the number of running/uploading/downloading tasks.
    :param running_count: The number of running tasks.
    :param upload_count: The number of uploading tasks.
    :param download_count: The number of downloading tasks.
    """
    running_count_str = str(running_count) if running_count > -1 else SKULL_CHAR
    upload_count_str = str(upload_count) if upload_count > -1 else SKULL_CHAR
    download_count_str = str(download_count) if download_count > -1 else SKULL_CHAR
    host_info_line = RUNNING_GUY_CHAR + ' ' + running_count_str + '  '
    host_info_line += UPLOAD_CHAR + ' ' + upload_count_str + '  '
    host_info_line += DOWNLOAD_CHAR + ' ' + download_count_str + '  '
    return host_info_line

def create_host_screen(hostname, active_tasks, uploading_tasks, downloading_tasks, optimum_task_count):
    """Displays the output for a host.
    :param hostname: The name of the host.
    :param boinc_active: Indicates if BOINC is running on the host.
    :param active_tasks: The number of active tasks.
    :param uploading_tasks: The number of uploading tasks.
    :param downloading_tasks: The number of downloading tasks.
    :param optimum_task_count: The number of tasks which should normally run simultaneously.
    """
    status_icon = SAD_FACE_CHAR
    lcd.clear()
    if active_tasks > 0:
        status_icon = SMILING_FACE_CHAR
        if active_tasks >= optimum_task_count:
            lcd.set_color(0.0, 1.0, 0.0)
        else:
            lcd.set_color(1.0, 1.0, 0.0)
    else:
        lcd.set_color(1.0, 0.0, 0.0)
    lcd.message(create_hostname_line(hostname, status_icon) + NEWLINE + create_host_info_line(active_tasks, uploading_tasks, downloading_tasks))


parser = argparse.ArgumentParser(description='BOINC monitoring script for the Raspberry Pi using an Adafruit RGB LCD Plate')
parser.add_argument('-i', '--interval', default=4, help='Number of seconds each host info should be displayed (default: 4)', dest='interval', type=int)
parser.add_argument('-c', '--config', default='boinc_hosts.xml', help='XML configuration file which contains the host definitions', dest='hosts_config_path', type=str)
parser.add_argument('--skip-offline', action='store_true', help='Do not display info for offline hosts', default=None)
args = parser.parse_args()

# init lcd
lcd = LCD.Adafruit_CharLCDPlate()
show_splash()

create_custom_chars()

interval = args.interval
hosts_config_path = args.hosts_config_path
skip_offline = False
if args.skip_offline:
    skip_offline = True

while True:
    hosts = get_boinc_hosts(hosts_config_path)
    if len(hosts) == 0:
        lcd.clear()
        lcd.set_color(1.0, 0.0, 1.0)
        lcd.message(PROGRAM_BANNER + NEWLINE + 'No hosts found ' + SAD_FACE_CHAR)
        time.sleep(GET_HOSTS_RETRY_INTERVAL)
        continue
    for hostname, host_config in hosts.iteritems():
        address = host_config.get('address')
        password = host_config.get('password')
        optimum_task_count = host_config.get('optimum_task_count')

        active_tasks = -1
        uploading_tasks = -1
        downloading_tasks = -1

        if is_host_reachable(address):
            tasks = get_tasks(address, password)
            active_tasks = get_number_of_active_tasks(tasks)
            uploading_tasks = get_number_of_uploading_tasks(tasks)
            downloading_tasks = get_number_of_downloading_tasks(tasks)
        elif skip_offline:
            continue
        create_host_screen(hostname, active_tasks, uploading_tasks, downloading_tasks, optimum_task_count)
        time.sleep(interval)

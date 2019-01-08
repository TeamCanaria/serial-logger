"pip install pySerial"
"pip install DateTime"

import serial                              # Python library to read data from Raspberry Pi serial
from datetime import datetime, timedelta   # Python library to check datetime
import os                                  # Python library to use operating system dependent functionality
import sys
import serial.tools.list_ports

# Print detect USB port for the device
print("Establish USB Serial Connection")
list = serial.tools.list_ports.comports()
connected = []
for element in list:
    connected.append(element.device)

if not connected:
    print('Device not found')
    sys.exit()

print("Available COM ports: " + str(connected))
port_needed = input("Connected Port:")
#read_serial = serial.Serial(port_needed, 115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
read_serial = serial.Serial(port_needed, 115200)
# Create file name which match the date
current_time = datetime.now()
file_name = current_time.strftime("%Y-%m-%d")
board_no = 'board_4'
user = input("Input User's Name:")
file_name = file_name+'_'+user+'.csv'
print(file_name)

# Create columns for the data file
def print_first_line(written_file):
    written_file.write('Date,')
    written_file.write('Patient_ID,')
    written_file.write('Red_Signal')
    written_file.write('\n')
    return written_file

# Check file already exist in local machine
def check_file_exist(file_name):
    if file_name not in os.listdir(os.curdir):
        # File does not exist, create new file
        written_file = open(file_name, "w")
        written_file = print_first_line(written_file)
    else:
        # File already exist, append new rows
        written_file = open(file_name, "a")
    return written_file

# Updating the data locally
def update_file_signal(file_write):
    print("Update file")
    file_write.close()                                       # Close the file for uploading
    file_write = open(file_write.name, "a")
    return file_write

# Update file every a duration of time
update_time = 5           # duration how often the local file be updated
state = "RUN"
print('Creating file csv')
file_signal = check_file_exist(file_name)
update_flag = datetime.now() + timedelta(minutes = update_time)
print("Read data from Serial")
try:
    while 1:
        data = read_serial.readline()  # Data from serial separate by newline character
        data = data.strip()            # Remove newline character of Arduino IDE
        data = data.decode("utf-8")
        if not(data.isdigit()):
            if data == 'Pause':	       # If signal is F meaning that patient is fatigue
                state = 'PAUSE'
                print(state)
                file_signal.close()
                continue
            elif data == 'Start':
                state = "RUN"
                file_signal = open(file_signal.name, "a")
                continue

        if state == "RUN":
            file_signal.write(datetime.now().strftime("%H:%M:%S.%f") + ",")    # Record time corresponding to the signal
            file_signal.write(user + ",")    # Write to column Patient Id
            #file_signal.write(data.decode("utf-8"))
            file_signal.write(data)
            print(str(datetime.now().hour)+":"+str(datetime.now().minute) +":"+str(datetime.now().second)+"   "+data+" "+"RUN")
            #print(datetime.now().minute+data+'  '+state)
            file_signal.write("\n")

	# Time to update s3
        if datetime.now() >= update_flag:         # Update the file
            file_signal = update_file_signal(file_signal)
            update_flag = datetime.now() + timedelta(minutes = update_time)
        # New day, program create new data file
        if (current_time.day != datetime.now().day) or (current_time.month != datetime.now().month) \
                or (current_time.year != datetime.now().year):
                    file_signal = update_file_signal(file_signal)
                    current_time = datetime.now()
                    file_name = current_time.strftime("%Y-%m-%d") +'_'+User+'.csv'
                    file_signal = check_file_exist(file_name)
                    update_flag = datetime.now() + timedelta(minutes = update_time)

except KeyboardInterrupt:
    file_signal.close()
    print("End")

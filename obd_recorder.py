#!/usr/bin/env python

import obd_io
import serial
import platform
import obd_sensors
from datetime import datetime
import time
import getpass
import os
from sense_hat import SenseHat
from time import sleep


USE_SENSE_HAT = 1

R = [255, 0, 0]
G = [0, 255, 0]
B = [0, 0, 255]
Bk = [0, 0, 0]
O = [100, 100, 100]  # background
W = [255, 255, 255]

pepe = [
O, O, O, O, O, O, O, O,
O, G, G, O, O, G, G, O,
G, G, G, G, G, G, G, O,
G, G, W, Bk, G, W, Bk, O,
G, G, G, G, G, G, G, O,
B, G, R, R, R, R, R, O,
B, G, G, G, G, G, O, O,
B, B, B, B, B, B, O, O
]


def init_pepe():
    sense.clear()
    sense.low_light = True
    sense.set_pixels(pepe)
    sense.flip_v()

def flip_pepe():
    sense.flip_h()
    sleep(0.25)
    

from obd_utils import scanSerial

class OBD_Recorder():
    # def __init__(self, path, log_items):
    def __init__(self, path):
        if USE_SENSE_HAT == 1:
            sense.clear()
            sense.set_pixel(0, 7, 255,0,0)
        self.port = None
        try: 
            self.connect()
        except:
            raise Exception("Not connected to OBD device")
        # self.sensorlist = []
        self.supportedSensors = self.getSupportedSensorList()
        localtime = time.localtime(time.time())
        filename = path+"car-"+str(localtime[0])+"-"+str(localtime[1])+"-"+str(localtime[2])+"-"+str(localtime[3])+"-"+str(localtime[4])+"-"+str(localtime[5])+".log"
        self.log_file = open(filename, "w", 128)
        # sensornames = [i.name for i in obd_sensors.SENSORS]
        supportedSensorNames = [s[1].name for s in self.supportedSensors]  # create the columns of the log file
        string = "Time," + ','.join(supportedSensorNames) + ",DTC_bytes,DTC\n"
        #self.log_file.write("Time,RPM,MPH,Throttle,Load,Fuel Status\n")
        self.log_file.write(string)

        # for item in log_items:
        #     self.add_log_item(item)

        self.gear_ratios = [34/13, 39/21, 36/23, 27/20, 26/21, 25/22]
        #log_formatter = logging.Formatter('%(asctime)s.%(msecs).03d,%(message)s', "%H:%M:%S")

    def connect(self):
        portnames = scanSerial()
        #portnames = ['COM10']
        print portnames
        for port in portnames:
            self.port = obd_io.OBDPort(port, None, 2, 2)
            if(self.port.State == 0):
                self.port.close()
                self.port = None
            else:
                break

        if(self.port):
            print "Connected to "+self.port.port.name
            
    def is_connected(self):
        return self.port
        
    def add_log_item(self, item):
        for index, e in enumerate(obd_sensors.SENSORS):
            if(item == e.shortname):
                self.sensorlist.append(index)
                print "Logging item: "+e.name
                break    
            
    def getSupportedSensorList(self):
        if(self.port is None):
            print "Not connected to ECU when getting supported PIDs"
            return None  # nothing can be done if not connected

        print "Connected to ECU. Getting supported PIDs..."
        #Find supported sensors - by getting PIDs from OBD
        # its a string of binary 01010101010101 
        # 1 means the sensor is supported        
        self.supp_01_20 = self.port.sensor(0)[1]
        self.supp_21_40 = self.port.sensor(32)[1]  # PID 32
        self.supp_41_60 = self.port.sensor(64)[1]  # PID 64
        # self.supp_61_80 = self.port.sensor(60)[1]
        print "PIDs 01 to 20: " + str(self.supp_01_20)
        print "PIDs 21 to 40: " + str(self.supp_21_40)
        print "PIDs 41 to 60: " + str(self.supp_41_60)
        
        # self.supp_81_A0 = self.port.sensor(80)[1]
        # self.supp_A1_C0 = self.port.sensor(100)[1]
        # self.supp_C1_E0 = self.port.sensor(120)[1]
        self.supportedSensorList = []
        self.unsupportedSensorList = []

        self.loopPIDbinary(self.supp_01_20, 0)
        self.loopPIDbinary(self.supp_21_40, 32)
        self.loopPIDbinary(self.supp_41_60, 64)
        # self.loopPIDbinary(self.supp_61_80, 60)
        # self.loopPIDbinary(self.supp_81_A0, 80)
        # self.loopPIDbinary(self.supp_A1_C0, 100)
        # self.loopPIDbinary(self.supp_C1_E0, 120)

        return self.supportedSensorList  # [[1, Sensor("dtc_status", ...)], [2, Sensor("dtc_ff", ...], ...]


    def loopPIDbinary(self, supp, offset):
        # loop through PIDs binary
        for i in range(0, len(supp)-1):  # len(supp)-1 to exclude PID "Supported PID"
            idx = i + 1 + offset
            if supp[i] == "1":
                # store index of sensor and sensor object
                self.supportedSensorList.append([idx, obd_sensors.SENSORS[idx]])
            else:
                self.unsupportedSensorList.append([idx, obd_sensors.SENSORS[idx]])

            
    def record_data(self):
        if(self.port is None):
            self.remove_log_file()
            return None
        
        print "Logging started"
        while 1:
            localtime = datetime.now()
            current_time = str(localtime.hour)+":"+str(localtime.minute)+":"+str(localtime.second)+"."+str(localtime.microsecond)
            log_string = current_time
            results = {}
            # for index in self.sensorlist:
            for s in self.supportedSensors:  # log the values of each PID one by one
                (name, value, unit) = self.port.sensor(s[0])
                log_string = log_string + ","+str(value)
                # results[obd_sensors.SENSORS[index].shortname] = value;
                results[s[1].shortname] = value

            gear = self.calculate_gear(results["rpm"], results["speed"])
            # log_string = log_string #+ "," + str(gear)
            log_string = log_string + "," + self.port.get_dtc()
            self.log_file.write(log_string+"\n")

            
    def calculate_gear(self, rpm, speed):
        if speed == "" or speed == 0:
            return 0
        if rpm == "" or rpm == 0:
            return 0

        rps = rpm/60
        mps = (speed*1.609*1000)/3600
        
        primary_gear = 85/46 #street triple
        final_drive  = 47/16
        
        tyre_circumference = 1.978 #meters

        current_gear_ratio = (rps*tyre_circumference)/(mps*primary_gear*final_drive)
        
        #print current_gear_ratio
        gear = min((abs(current_gear_ratio - i), i) for i in self.gear_ratios)[1] 
        return gear
    
    def remove_log_file(self):
        if os.path.isfile(self.log_file.name):
            os.remove(self.log_file.name)
        else:    ## Show an error ##
            print "Error: %s file not found" % str(self.log_file)      
        
sense = SenseHat()        
username = getpass.getuser()  
# logitems = ["rpm", "speed", "throttle_pos", "load", "fuel_status"]
# logitems = [i.shortname for i in obd_sensors.SENSORS]  # log data from all the available sensors
# o = OBD_Recorder('/home/'+username+'/pyobd-pi/log/', logitems)
# try:
#     o.connect()
# except:
#     o.remove_log_file()
#     raise Exception('Not connected to OBD device')

# if not o.is_connected():
#     print "Not connected"
#     sense.clear()
#     sense.set_pixel(0, 7, 255,0,0)
# else:
#     if USE_SENSE_HAT == 1:
#         init_pepe()
#         for i in range(20):
#             flip_pepe()
#         sense.clear()
#         sense.set_pixel(0, 7, 0,255,0)
    
#     o.record_data()
    
o = OBD_Recorder('/home/'+username+'/pyobd-pi/log/')

if not o.is_connected():
    print "Not connected"
    sense.clear()
    sense.set_pixel(0, 7, 255,0,0)
else:
    if USE_SENSE_HAT == 1:
        init_pepe()
        for i in range(20):
            flip_pepe()
        sense.clear()
        sense.set_pixel(0, 7, 0,255,0)
    
    o.record_data()
    
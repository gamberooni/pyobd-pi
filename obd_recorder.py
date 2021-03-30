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


def init_led():
    sense.low_light = True
    sense.set_pixels(pepe)
    sense.flip_v()

def pepe_led():
    sense.flip_h()
    sleep(0.25)
    

from obd_utils import scanSerial

class OBD_Recorder():
    def __init__(self, path, log_items):
        if USE_SENSE_HAT == 1:
            sense.clear()
            sense.set_pixel(0, 7, 255,0,0)
        self.port = None
        self.sensorlist = []
        localtime = time.localtime(time.time())
        filename = path+"car-"+str(localtime[0])+"-"+str(localtime[1])+"-"+str(localtime[2])+"-"+str(localtime[3])+"-"+str(localtime[4])+"-"+str(localtime[5])+".log"
        self.log_file = open(filename, "w", 128)
        sensornames = [i.name for i in obd_sensors.SENSORS]
        sensors = ','.join(sensornames)
        string = "Time," + sensors + "\n"
        #self.log_file.write("Time,RPM,MPH,Throttle,Load,Fuel Status\n")
        self.log_file.write(string)

        for item in log_items:
            self.add_log_item(item)

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
            for index in self.sensorlist:
                (name, value, unit) = self.port.sensor(index)
                log_string = log_string + ","+str(value)
                results[obd_sensors.SENSORS[index].shortname] = value;

            gear = self.calculate_gear(results["rpm"], results["speed"])
            log_string = log_string #+ "," + str(gear)
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
logitems = [i.shortname for i in obd_sensors.SENSORS]  # log data from all the available sensors
o = OBD_Recorder('/home/'+username+'/pyobd-pi/log/', logitems)
try:
    o.connect()
except:
    o.remove_log_file()
    raise Exception('Not connected to OBD device')

if not o.is_connected():
    print "Not connected"
else:
    if USE_SENSE_HAT == 1:
        init_led()
        for i in range(20):
            pepe_led()
        sense.clear()
        sense.set_pixel(0, 7, 0,0,255)
    
    o.record_data()
    

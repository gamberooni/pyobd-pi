#!/usr/bin/env python
###########################################################################
# obd_sensors.py
#
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)
# Copyright 2009 Secons Ltd. (www.obdtester.com)
#
# This file is part of pyOBD.
#
# pyOBD is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pyOBD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyOBD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###########################################################################

def hex_to_int(str):
    i = eval("0x" + str, {}, {})
    return i

def maf(code):
    print "hex maf: " + str(code)
    code = hex_to_int(code)
    print "dec maf: " + str(code)
    return code * 0.00132276

def throttle_pos(code):
    code = hex_to_int(code)
    return code * 100.0 / 255.0

def intake_m_pres(code): # in kPa
    code = hex_to_int(code)
    return code / 0.14504
  
def rpm(code):
    code = hex_to_int(code)
    return code / 4

def speed(code):
    code = hex_to_int(code)
    return code

def percent_scale(code):
    code = hex_to_int(code)
    return code * 100.0 / 255.0

def percent_scale_offset(code):
    code = hex_to_int(code)
    return (code * 100.0 / 255.0) - 100.0

def timing_advance(code):
    code = hex_to_int(code)
    return (code - 128) / 2.0

def sec_to_min(code):
    code = hex_to_int(code)
    return code / 60

def temp(code):
    code = hex_to_int(code)
    return code - 40 

def cat_temp(code):
    code = hex_to_int(code)
    return (code / 10.0) - 40.0

def cpass(code):
    #fixme
    return code

def fuel_trim_percent(code):
    code = hex_to_int(code)
    #return (code - 128.0) * 100.0 / 128
    return (code - 128) * 100 / 128

def distance(code):
    code = hex_to_int(code)    
    return code

def fuel_rail_pres(code):
    code = hex_to_int(code)
    return code * 0.079

def fuel_rail_gauge_pres(code):
    code = hex_to_int(code)
    return code * 10    

def equivalence_ratio(code):
    code = hex_to_int(code)
    return code * 2 / 65536

def o2_current(code):
    code = hex_to_int(code)
    return code - 128

def evap_vapor_pres(code):
    code = hex_to_int(code)
    return code / 4.0

def voltage(code):
    code = hex_to_int(code)
    return code / 1000.0

def dtc_decrypt(code):
    #first byte is byte after PID and without spaces
    num = hex_to_int(code[:2]) #A byte
    res = []

    if num & 0x80: # is mil light on
        mil = 1
    else:
        mil = 0
        
    # bit 0-6 are the number of dtc's. 
    num = num & 0x7f
    
    res.append(num)
    res.append(mil)
    
    numB = hex_to_int(code[2:4]) #B byte
      
    for i in range(0,3):
        res.append(((numB>>i)&0x01)+((numB>>(3+i))&0x02))
    
    numC = hex_to_int(code[4:6]) #C byte
    numD = hex_to_int(code[6:8]) #D byte
       
    for i in range(0,7):
        res.append(((numC>>i)&0x01)+(((numD>>i)&0x01)<<1))
    
    res.append(((numD>>7)&0x01)) #EGR SystemC7  bit of different 
    
    #return res
    return "#"

def hex_to_bitstring(str):
    bitstring = ""
    for i in str:
        # silly type safety, we don't want to eval random stuff
        if type(i) == type(''): 
            v = eval("0x%s" % i)
            if v & 8 :
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 4:
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 2:
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 1:
                bitstring += '1'
            else:
                bitstring += '0'                
    return bitstring

class Sensor:
    def __init__(self, shortName, sensorName, sensorcommand, sensorValueFunction, u):
        self.shortname = shortName
        self.name = sensorName
        self.cmd  = sensorcommand
        self.value= sensorValueFunction
        self.unit = u

SENSORS = [
    # follows the actual OBD PIDs order in Wiki
    Sensor("pids"                  , "Supported PIDs"				, "0100" , hex_to_bitstring     ,""       ), 
    Sensor("dtc_status"            , "S-S DTC Cleared"				, "0101" , dtc_decrypt          ,""       ),    
    Sensor("dtc_ff"                , "DTC C-F-F"					, "0102" , cpass                ,""       ),      
    Sensor("fuel_status"           , "Fuel System Status"			, "0103" , cpass                ,""       ),
    Sensor("load"                  , "Calc Load Value"				, "0104" , percent_scale        ,""       ),    
    Sensor("temp"                  , "Coolant Temp"					, "0105" , temp                 ,"C"      ),
    Sensor("short_term_fuel_trim_1", "S-T Fuel Trim"				, "0106" , fuel_trim_percent    ,"%"      ),
    Sensor("long_term_fuel_trim_1" , "L-T Fuel Trim"				, "0107" , fuel_trim_percent    ,"%"      ),
    Sensor("short_term_fuel_trim_2", "S-T Fuel Trim"				, "0108" , fuel_trim_percent    ,"%"      ),
    Sensor("long_term_fuel_trim_2" , "L-T Fuel Trim"				, "0109" , fuel_trim_percent    ,"%"      ),
    Sensor("fuel_pressure"         , "FuelRail Pressure"			, "010A" , cpass                ,""       ),
    Sensor("manifold_pressure"     , "Intk Manifold"				, "010B" , intake_m_pres        ,"psi"    ),
    Sensor("rpm"                   , "Engine RPM"					, "010C" , rpm                  ,""       ),
    Sensor("speed"                 , "Vehicle Speed"				, "010D" , speed                ,"KMH"    ),
    Sensor("timing_advance"        , "Timing Advance"				, "010E" , timing_advance       ,"degrees"),
    Sensor("intake_air_temp"       , "Intake Air Temp"				, "010F" , temp                 ,"F"      ),
    Sensor("maf"                   , "AirFlow Rate(MAF)"			, "0110" , maf                  ,"lb/min" ),
    Sensor("throttle_pos"          , "Throttle Position"			, "0111" , throttle_pos         ,"%"      ),
    Sensor("secondary_air_status"  , "2nd Air Status"				, "0112" , cpass                ,""       ),
    Sensor("o2_sensor_positions"   , "Loc of O2 sensors"			, "0113" , cpass                ,""       ),
    Sensor("o211"                  , "O2 Sensor: 1 - 1"				, "0114" , fuel_trim_percent    ,"%"      ),
    Sensor("o212"                  , "O2 Sensor: 1 - 2"				, "0115" , fuel_trim_percent    ,"%"      ),
    Sensor("o213"                  , "O2 Sensor: 1 - 3"				, "0116" , fuel_trim_percent    ,"%"      ),
    Sensor("o214"                  , "O2 Sensor: 1 - 4"				, "0117" , fuel_trim_percent    ,"%"      ),
    Sensor("o221"                  , "O2 Sensor: 2 - 1"				, "0118" , fuel_trim_percent    ,"%"      ),
    Sensor("o222"                  , "O2 Sensor: 2 - 2"				, "0119" , fuel_trim_percent    ,"%"      ),
    Sensor("o223"                  , "O2 Sensor: 2 - 3"				, "011A" , fuel_trim_percent    ,"%"      ),
    Sensor("o224"                  , "O2 Sensor: 2 - 4"				, "011B" , fuel_trim_percent    ,"%"      ),
    Sensor("obd_standard"          , "OBD Designation"				, "011C" , cpass                ,""       ),
    Sensor("o2_sensor_position_b"  , "Loc of O2 sensor" 			, "011D" , cpass                ,""       ),
    Sensor("aux_input"             , "Aux input status"				, "011E" , cpass                ,""       ),
    Sensor("engine_time"           , "Engine Start MIN"				, "011F" , sec_to_min           ,"min"    ),
    Sensor("pids_21_to_40"         , "Supported PIDs 21 to 40"      , "0120" , hex_to_bitstring     ,""       ),
    Sensor("distance_mil"          , "Distance Traveled with MIL on", "0121" , distance             ,"km"     ),
    Sensor("fuel_rail_pres"        , "Fuel Rail Pressure"           , "0122" , fuel_rail_pres       ,"kPa"    ),
    Sensor("fuel_rail_gauge_pres"  , "Fuel Rail Gauge Pressure"     , "0123" , fuel_rail_gauge_pres ,"kPa"    ),
    Sensor("o21_ratio"             , "O2 Sensor: 1 - ratio"         , "0124" , equivalence_ratio    ,""       ),
    Sensor("o22_ratio"             , "O2 Sensor: 2 - ratio"         , "0125" , equivalence_ratio    ,""       ),
    Sensor("o23_ratio"             , "O2 Sensor: 3 - ratio"         , "0126" , equivalence_ratio    ,""       ),
    Sensor("o24_ratio"             , "O2 Sensor: 4 - ratio"         , "0127" , equivalence_ratio    ,""       ),
    Sensor("o25_ratio"             , "O2 Sensor: 5 - ratio"         , "0128" , equivalence_ratio    ,""       ),
    Sensor("o26_ratio"             , "O2 Sensor: 6 - ratio"         , "0129" , equivalence_ratio    ,""       ),
    Sensor("o27_ratio"             , "O2 Sensor: 7 - ratio"         , "012A" , equivalence_ratio    ,""       ),
    Sensor("o28_ratio"             , "O2 Sensor: 8 - ratio"         , "012B" , equivalence_ratio    ,""       ),
    Sensor("cmd_egr"               , "Commanded EGR"                , "012C" , percent_scale        ,"%"      ),
    Sensor("egr_error"             , "EGR Error"                    , "012D" , percent_scale        ,"%"      ),
    Sensor("cmd_evap_purge"        , "Commanded evap purge"         , "012E" , percent_scale        ,"%"      ),
    Sensor("fuel_tank_level_ip"    , "Fuel tank level input"        , "012F" , percent_scale        ,"%"      ),
    Sensor("code_cleared_warmups"  , "Code cleared warmups"         , "0130" , cpass                ,""       ),
    Sensor("code_cleared_dist"     , "Code cleared distance"        , "0131" , distance             ,"km"     ),
    Sensor("evap_sys_vapor_pres"   , "Evap system vapor pressure"   , "0132" , evap_vapor_pres      ,"Pa"     ),
    Sensor("abs_barometric_pres"   , "Abs barometric pressure"      , "0133" , cpass                ,""       ),
    Sensor("o21_current"           , "O2 Sensor: 1 - current"       , "0134" , o2_current           ,"mA"     ),  # need to investigate
    Sensor("o22_current"           , "O2 Sensor: 2 - current"       , "0135" , o2_current           ,"mA"     ),
    Sensor("o23_current"           , "O2 Sensor: 3 - current"       , "0136" , o2_current           ,"mA"     ),
    Sensor("o24_current"           , "O2 Sensor: 4 - current"       , "0137" , o2_current           ,"mA"     ),
    Sensor("o25_current"           , "O2 Sensor: 5 - current"       , "0138" , o2_current           ,"mA"     ),
    Sensor("o26_current"           , "O2 Sensor: 6 - current"       , "0139" , o2_current           ,"mA"     ),
    Sensor("o27_current"           , "O2 Sensor: 7 - current"       , "013A" , o2_current           ,"mA"     ),
    Sensor("o28_current"           , "O2 Sensor: 8 - current"       , "013B" , o2_current           ,"mA"     ),
    Sensor("cat_temp11"            , "Catalyst temp: 1 - 1"         , "013C" , cat_temp             ,"C"      ),
    Sensor("cat_temp21"            , "Catalyst temp: 2 - 1"         , "013D" , cat_temp             ,"C"      ),
    Sensor("cat_temp12"            , "Catalyst temp: 1 - 2"         , "013E" , cat_temp             ,"C"      ),
    Sensor("cat_temp22"            , "Catalyst temp: 2 - 2"         , "013F" , cat_temp             ,"C"      ),
    Sensor("pids_41_to_60"         , "Supported PIDs 41 to 60"      , "0140" , hex_to_bitstring     ,""       ),
    Sensor("drive_cycle_mon_stat"  , "Drive cycle monitor status"   , "0141" , hex_to_bitstring     ,""       ),
    Sensor("control_module_volt"   , "Control module voltage"       , "0142" , voltage              ,"%"      ),  
    Sensor("abs_load"              , "Absolute load"                , "0143" , cpass                ,""       ),  # to fix
    Sensor("cmd_air_fuel_ratio"    , "Commanded air-fuel Ratio"     , "0144" , equivalence_ratio    ,""       ),
    Sensor("rel_throttle_pos"      , "Rel throttle position"        , "0145" , percent_scale        ,"%"      ),
    Sensor("ambient_air_temp"      , "Ambient air temp"             , "0146" , temp                 ,"C"      ),
    Sensor("abs_throttle_pos_B"    , "Abs throttle pos B"           , "0147" , percent_scale        ,"%"      ),
    Sensor("abs_throttle_pos_C"    , "Abs throttle pos C"           , "0148" , percent_scale        ,"%"      ),
    Sensor("acc_pedal_pos_D"       , "Acc pedal pos D"              , "0149" , percent_scale        ,"%"      ),
    Sensor("acc_pedal_pos_E"       , "Acc pedal pos E"              , "014A" , percent_scale        ,"%"      ),
    Sensor("acc_pedal_pos_F"       , "Acc pedal pos F"              , "014B" , percent_scale        ,"%"      ),
    Sensor("cmd_throttle_actuator" , "Commanded throttle actuator"  , "014C" , voltage              ,"V"      ),
    Sensor("engine_mil_time"       , "Engine Run MIL"				, "014D" , cpass                ,"min"    ),
    Sensor("code_cleared_time"     , "Time since codes cleared"     , "014E" , cpass                ,"min"    ),
    Sensor("max_values"            , "Max values"                   , "014F" , cpass                ,""       ),  # to fix
    Sensor("pids_61_to_80"         , "Supported PIDs 61 to 80"      , "0160" , hex_to_bitstring     ,""       ),
    # Sensor("pids_81_to_A0"         , "Supported PIDs 81 to A0"      , "0180" , hex_to_bitstring ,""       ),
    # Sensor("pids_A1_to_C0"         , "Supported PIDs A1 to C0"      , "01A0" , hex_to_bitstring ,""       ),
    # Sensor("pids_C1_to_E0"         , "Supported PIDs C1 to E0"      , "01C0" , hex_to_bitstring ,""       ),    
    ]
     
    
#___________________________________________________________

def test():
    for i in SENSORS:
        print i.name, i.value("F")

if __name__ == "__main__":
    test()

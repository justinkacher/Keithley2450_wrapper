import time
import socket
import numpy as np
from statistics import mean


TCP_IP = "169.254.201.87"
TCP_Port = 5025
device = socket.socket()

#check all functions on keithley, not proven
class keithley:

    def send(command):
        comand += "\n"
        device.send(command.encode())
        return

    def recieve():
        return keithley.recv(1024).decode()

    def query(command):
        send(command)
        return recieve()

    def lan_connection():
        TCP_IP = input("TCP IP Number: ")
        device.connect((TCP_IP,TCP_Port))


        send("RST")
        print("ID: ",query("*IDN?"))
        send('OUTP:SMOD HIMP')
        
    def get_voltage():
        send('SOUR:VOLT:RANG 20')
        send('OUTP ON')
        time.sleep(.15)
        reading = query('MEAS:VOLT? "debuffer1", READ')
        return float(reading)

    def get_avg_voltage():

        send("*RST")
        send('SOUR:VOLT:RANG 20')
        vocL = []
        for i in range(5):
            volt = get_voltage()
            vocL.append(volt)
            
        Voc = mean(vocL)

        return Voc

    def get_current():
        reading = query('MEAS:CURR? "defuffer1",READ')
        return reading

    def get_avg_curr():
        send('*RST')
        send('SOUR:CURR:RANG 2')
        curr = []
        for i in range(5):
            current = get_current()
            curr.append(current)
        current = mean(curr)
        return current

    def dc_Impedance():

        # set relay to sense 
        
        sourceVoltage = 2.65  # Charging: VSource > VBattery; Discharging: VS < VB # 18650 is 3.7v; max charging is 4.2v and min discharge final is 2.75
        voltageRange = 20  # 20mV, 200mV, 2V, 20V, 200V
        sourceLimit = np.linspace(0.1, 1, 10)     # returns array; start value, end value, number of points
        
        currentRange = 1.05  # Max 1.05A
        
        send('*RST')  # first line is to reset the instrument
        send('OUTP:SMOD HIMP')  # turn on high-impedance output mode
        send('SENS:CURR:RSEN ON')  # set to 4-wire sense mode  # OFF = 2-Wire mode
        send('SENS:FUNC "CURR"')  # set measure, sense, to current
        send(f'SENS:CURR:RANG {currentRange}')  # set current range # can also be 'SENS:CURR:RANG:AUTO ON'
        send('SENS:CURR:UNIT AMP')  # set measure units to Ohm, can also be Watt or Amp
        send('SOUR:FUNC VOLT')  # set source to voltage
        send(f'SOUR:VOLT {sourceVoltage}')  # set output voltage => discharge or charge test
        send('SOUR:VOLT:READ:BACK ON')  # turn on source read back
        send('SOUR:VOLT:RANG {voltageRange}')  # set source range
        send(f'SOUR:VOLT:ILIM {sourceLimit[0]}')  # set source (current) limit
        send('OUTP ON')  # turn on output, source
        
        # loop 10 times to and return the average DC impedance
        currentL_impedance = []
        voltL_impedance = []
        for i in range(len(sourceLimit)):
            send(f'SOUR:VOLT:ILIM {sourceLimit[i]}')  # set source (current) limit
            time.sleep(0.25)
        
            curr = query('READ? "defbuffer1"')
            currentL_impedance.append(float(curr))
        
            volt =query('READ? "defbuffer1", SOUR')  # a ? is used for a query command otherwise is a set command
                                                            # defbuffer1 returns sense value
            voltL_impedance.append(float(volt))
            # print(curr)
            # print(sourceLimit[i])
        send('OUTP OFF')  # turn off keithley
        
        impedanceL = []
        for i in range(len(voltL_impedance)-1):
            #print(type(voltL_impedance))
            DC_impedance = (voltL_impedance[i] - voltL_impedance[i+1]) / (currentL_impedance[i] - currentL_impedance[i+1])
            # print(DC_impedance)
            impedanceL.append(DC_impedance)
        
        impedance_Avg = mean(impedanceL)
        
        impedance = impedance_Avg*1000   # to get to milli- Ohms

        return impedance

    def voltage_output_on(voltage_level):
        voltage_level = voltage_level
        send(f'SOUR:VOLT:{voltage_level}')

    def current_output_on(current_level):
        current_level = current_level
        send(f'SOUR:CURR:{current_level}')

    def sense_mode(mode):  
    #'remote' or 'local'
        if mode == 'remote':
            send('CONF:REM:SENS ON')
        if mode == 'local':
            send('CONF:REM:SENS OFF')
        else:
            raise Exception("sense_mode() takes 'remote' or 'local' arguments")

keithley.lan_connection()
input()



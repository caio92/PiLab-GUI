from w1thermsensor import W1ThermSensor
import gc
#import sys
from time import sleep
import threading
import RPi.GPIO as GPIO
from hx711py3.scale import Scale
from hx711py3.hx711 import HX711

import pdb

class Tank():
    def __init__(self, name, GPIOPin, thermSensorId, tempUnit, textVar, updated):
        self.tankInfo = {
                "name": name,
                "GPIOPin": GPIOPin,
                "thermSensorId": thermSensorId,
                "tempUnit": tempUnit,
                "textVar": textVar,
                "updated": updated
                }

class PeripheralsController():
    
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        
        self.setupTime = 3
        self.tanks = {}
        self.usedPins = []
        self.activeTanks = []
        self.tempReader = TemperatureReader(self)
        
        self.tempUnit = "°C"
        
        self.threadLock = threading.Lock()
        
        self.registeredTanks = False
        
        self.scaleActive = False
        self.scaleOut = None
        self.scaleReader = ScaleReader(self)
        
        self.scale = Scale(source=HX711(dout=38, pd_sck=40))
        self.scale.powerDown()
        
        if gc.isenabled():
            print("GC Enabled!")
        
    def CheckPin(self, pin):
        if pin not in self.usedPins:
            return True
        else:
            return False

    def AddTank(self, name, GPIOPin, thermSensorId=None, tempUnit=W1ThermSensor.DEGREES_C, textVar=None, updated=False):
        if name not in self.tanks:
            if self.CheckPin(GPIOPin):
                self.tanks[name] = Tank(name, GPIOPin, thermSensorId, tempUnit, textVar, updated)
                self.registeredTanks = False
                return True
            else:
                #pin already in use
                return False
        else:
            #tank name already exists.
            return False
            
    def UpdateTank(self, tankName, GPIOPin=None, thermSensorId=None, tempUnit=None, textVar=None, updated=True):

        updatedTank = Tank(tankName, GPIOPin, thermSensorId, tempUnit, textVar, updated)
        #removes None keys
        updatedTank.tankInfo = {k:v for k,v in updatedTank.tankInfo.items() if v is not None}
        
        if tankName in self.tanks:
            self.tanks[tankName].tankInfo.update(updatedTank.tankInfo)
            if tempUnit is not None:
                if tankName in self.activeTanks:
                    self.tanks[tankName].tankInfo["textVar"].set("Changing temperature unit...")
                    
                self.tanks[tankName].tankInfo["updated"] = False
                if tempUnit == W1ThermSensor.DEGREES_C:
                    self.tempUnit = "°C"
                else:
                    self.tempUnit = "°F"
                
            if "GPIOPin" in updatedTank.tankInfo:
                self.registeredTanks = False
                self.tanks[tankName].tankInfo["updated"] = False
            return True
        else:
            #tank doesn't exist. Should be added
            return False

    def TestProbe(self):
        while True:
            try:
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(delta)
                GPIO.output(pin, GPIO.LOW)
                time.sleep(delta)
                
            except (KeyboardInterrupt, SystemExit):
                GPIO.cleanup()

    def RegisterTherms(self):
        
        sensors = []

        for tank in self.tanks:
            if not self.tanks[tank].tankInfo["updated"]:
                GPIO.setup(self.tanks[tank].tankInfo["GPIOPin"], GPIO.OUT)
                GPIO.output(self.tanks[tank].tankInfo["GPIOPin"], GPIO.HIGH)
                sleep(self.setupTime)
            
                for sensor in W1ThermSensor.get_available_sensors():
                    if sensor.id not in sensors:
                        sensors.append(sensor.id)
                        self.tanks[tank].tankInfo["thermSensorId"] = sensor.id
                        
        self.registeredTanks = True
        
    def GetTemperature(self, tankName):
        sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, self.tanks[tankName].tankInfo["thermSensorId"])
        temperature = sensor.get_temperature(self.tanks[tankName].tankInfo["tempUnit"])
        if tankName in self.activeTanks:
            if self.tanks[tankName].tankInfo["updated"]:
                formTemp = '%.2f %s' % (temperature, self.tempUnit)
                self.tanks[tankName].tankInfo["textVar"].set(formTemp)
            else:
                self.tanks[tankName].tankInfo["updated"] = True

    def ActivateTank(self, tankName):
        if tankName in self.tanks:
            if not self.registeredTanks:
                self.RegisterTherms()
                
            self.tanks[tankName].tankInfo["textVar"].set("Reading temperature...")

            if self.activeTanks:
                self.activeTanks.append(tankName)
            else:
                self.activeTanks.append(tankName)
                self.getTempThread = threading.Thread(target=self.tempReader.Start)
                self.getTempThread.start()
                print("Started reading temperatures")
        else:
            #invalid tank name
            return False
            
    def DeactivateTank(self, tankName):
        if tankName in self.activeTanks:
            self.activeTanks.remove(tankName)
            if not self.activeTanks and self.getTempThread.is_alive():
                self.getTempThread.join()
                print("Stopped reading temperatures")
            self.tanks[tankName].tankInfo["textVar"].set("")
        else:
            #invalid tank name
            return False
            
    def cleanup(self):
        GPIO.cleanup()
    
    def calibrate_scale(self):
        referenceSet = False
        
        hx = HX711(dout=38, pd_sck=40)
        hx.powerUp()
        
        input("Remove all objects on the scale and press [Enter] to continue.")
        
        val1 = hx.getWeight()
        
        input("Place the reference weight on the scale and press [Enter] to continue.")
        
        while not referenceSet:
            try:
                inWeight = float(input("Insert the weight (in grams) of your reference: "))
                referenceSet = True
            except ValueError:
                print("Please, insert a valid number")
        
        val2 = hx.getWeight()
        
        reference = (val1 - val2)/inWeight
        
        print("Your reference unit is: {0: 4.4f}".format(val))
        
        hx.powerDown()
        
        return reference
    
    def set_scale_reference(self, reference):
        self.scale.setReferenceUnit(reference)
        
    def get_measure(self):
        self.scaleOut.set(self.scale.getMeasure())
        
    def activate_scale(self):
        if not self.scaleActive:
            self.scaleActive = True
            self.getWeightThread = threading.Thread(target=self.scaleReader.Start)
            self.getWeightThread.start()
            print("Started reading scale")
        
    def deactivate_scale(self):
        self.scaleActive = False
        if self.scaleActive and self.getWeightThread.is_alive():
            self.getWeightThread.join()
            
        print("Stopped reading scale")

    def set_scale_out(self, textVar):
        self.scaleOut = textVar

class TemperatureReader():
    def __init__(self, pController):
        self.pController = pController  
    
    def Start(self):
        while self.pController.activeTanks:
            for tank in self.pController.activeTanks:
                self.pController.GetTemperature(tank)       

class ScaleReader():
    def __init__(self, pController):
        self.pController = pController  
    
    def Start(self):
        self.pController.scale.powerUp()
        
        while self.pController.scaleActive:
            self.pController.get_measure()
            
        self.pController.scale.powerDown()

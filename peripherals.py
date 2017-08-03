from w1thermsensor import W1ThermSensor
import gc
import sys
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
    
    def __init__(self, app):
        GPIO.setmode(GPIO.BOARD)
        
        self.app = app
        
        self.scaleInfo = []
        
        self.setupTime = 3
        self.tanks = {}
        self.usedPins = []
        self.activeTanks = []
        self.tempReader = TemperatureReader(self)
        
        #if app.config["Temperature"]["TemperatureUnit"] == "celsius":
        #    self.tempUnit = "°C"
        #else:
        #    self.tempUnit = "°F"
        
        #self.scaleLock = threading.Lock()
        
        self.registeredTanks = False
        
        self.scaleActive = False
        self.scaleOut = None
        self.scaleReader = ScaleReader(self)
        
        self.dout = 38
        self.pd_sck = 40
        
        #GPIO.setup(self.dout, GPIO.IN)
        
        self.scale = Scale(source=HX711(dout=self.dout, pd_sck=self.pd_sck))
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
                    text = self.app.interfaceText["GetTemperatures"]["Labels"]["ChangingUnit"]
                    self.tanks[tankName].tankInfo["textVar"].set(text)
                    
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
                formTemp = self.tempDecimalString % (temperature, self.tempUnit)
                self.tanks[tankName].tankInfo["textVar"].set(formTemp)
            else:
                self.tanks[tankName].tankInfo["updated"] = True

    def ActivateTank(self, tankName):
        if tankName in self.tanks:
            if not self.registeredTanks:
                self.RegisterTherms()
            text = self.app.interfaceText["GetTemperatures"]["Labels"]["ReadingTemp"]    
            self.tanks[tankName].tankInfo["textVar"].set(text)

            if self.activeTanks:
                self.activeTanks.append(tankName)
            else:
                self.activeTanks.append(tankName)
                self.getTempThread = threading.Thread(target=self.tempReader.Start, daemon=True)
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
        
        hx = HX711(dout=self.dout, pd_sck=self.pd_sck)
        hx.reset()
        
        input("Remove all objects on the scale and press [Enter] to continue.")
        hx.tare()
        #GPIO.add_event_detect(self.dout, GPIO.FALLING, callback=hx.getWeight)
        val1 = hx.getWeight()
        
        input("Place the reference weight on the scale and press [Enter] to continue.")
        
        while not referenceSet:
            try:
                inWeight = float(input("Insert the weight (in grams) of your reference: "))
                referenceSet = True
            except ValueError:
                print("Please, insert a valid number")
        
        sleep(1)
        val2 = hx.getWeight()
        
        #reference = (val1 - val2)/inWeight
        reference = (val2 - val1)/inWeight
        #reference = val2/inWeight
        
        print("Your reference unit is: {0: 4.4f}".format(reference))
        
        hx.powerDown()
        GPIO.remove_event_detect(self.dout)
        
        return reference
    
    def set_scale_reference(self, reference):
        self.scale.setReferenceUnit(reference)
        
    def get_measure(self, channel=None):
        #scaleMeasure = self.scale.getMeasure()
        try:
            #scaleMeasure = self.scale.getWeight()
            scaleMeasure = self.scale.getMeasure()
            button = self.scaleButton.GetButton()
            button.config(anchor='n')
            
            if len(self.scaleInfo) > 1:
            
                scaleDiff = abs(scaleMeasure - float(self.scaleInfo[1]))
                
                if scaleDiff > 0.05:
                    self.scaleInfo.pop(1)
                    
                    self.scaleInfo.append(self.scaleDecimalString.format(scaleMeasure))
                    self.scaleButton.SetText(''.join(self.scaleInfo))
            else:
                self.scaleInfo.append(self.scaleDecimalString.format(scaleMeasure))
                self.scaleButton.SetText(''.join(self.scaleInfo))

            #sleep(0.2)
        except: 
            print("Deu erro no get_measure", sys.exc_info()[0], sys.exc_info()[1])
        
    def activate_scale(self):
        #pdb.set_trace()
        if not self.scaleActive:
            self.scaleActive = True
            self.getWeightThread = threading.Thread(target=self.scaleReader.Start, daemon=True)
            self.getWeightThread.start()
            print("Started reading scale")
        
        #self.scaleActive = True
        #self.scale.reset()
        #self.scale.tare()
        #GPIO.add_event_detect(self.dout, GPIO.FALLING, callback=self.get_measure) 
        
    def deactivate_scale(self):
        #pdb.set_trace()
        self.scaleActive = False
        #GPIO.remove_event_detect(self.dout)
        #self.scaleButton.ToggleText()
        #button = self.scaleButton.GetButton()
        #button.config(anchor='center')
        if self.getWeightThread.is_alive():
            self.getWeightThread.join(timeout=1)
            
        print("Stopped reading scale")

    def set_scale_out(self, guiButton):
        #self.scaleOut = textVar
        self.scaleButton = guiButton
        
        buttonText = guiButton.buttonText[1]
        #buttonText = [guiButton.buttonText[1]]
        #buttonText.append(guiButton.readingText)
        
        #self.scaleInfo.append(''.join(buttonText))
        self.scaleInfo.append(guiButton.buttonText[1])

    def stop_all(self):
        print("Stopping all active threads")
        try:
            if self.getWeightThread.is_alive():
                self.deactivate_scale()
        except:
            print("No scale threads to stop")
                
        try:
            if self.getTempThread.is_alive():
                for tank in self.activeTanks:
                    self.DeactivateTank(tank)
        except:
            print("No temperature threads to stop")

        print("Stopped all active threads")

    def set_precision(self):
        decimals = self.app.config["Temperature"]["DecimalPlaces"]
        self.tempDecimalString = "".join(["%.", decimals, "f %s"])
        
        decimals = self.app.config["Scale"]["DecimalPlaces"]
        self.scaleDecimalString = "".join(["{0: 4.", decimals, "f}"])

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
        try:
            self.pController.scale.reset()
            self.pController.scale.tare()
            while self.pController.scaleActive:
                self.pController.get_measure()
            
            self.pController.scale.powerDown()
    
        except:
            print("Deu erro scale thread: ", sys.exc_info()[0], sys.exc_info()[1])

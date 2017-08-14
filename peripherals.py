from w1thermsensor import W1ThermSensor
import gc
import sys
from time import sleep
from time import time
from collections import deque
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
        
        self.stepper = Stepper(self)
        
        #if app.config["Temperature"]["TemperatureUnit"] == "celsius":
        #    self.tempUnit = "°C"
        #else:
        #    self.tempUnit = "°F"
        
        self.scaleLock = threading.Lock()
        
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
        #
        #self.scaleLock.release()
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

    def run_recipe(self, agitations, duration, temperature, preferences=None):
        #pdb.set_trace()
        self.stepper.start(duration, agitations)
        
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
            
            self.pController.scaleButton.ToggleText()
            button = self.pController.scaleButton.GetButton()
            button.config(anchor='center')
    
        except:
            print("Deu erro scale thread: ", sys.exc_info()[0], sys.exc_info()[1])

class Stepper():
    def __init__(self, pController, mode="half-step", coils=[31,33,35,37]):        
        self.runningEvent = threading.Event()
        self.runningEvent.set()
        
        self.invertFlag = False
        self.recipeTimeoutFlag = False
        
        self.pController = pController
        
        self.coil_pins = coils
        
        for pin in self.coil_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        half_step = [[1,0,0,1],
                     [1,0,0,0],
                     [1,1,0,0],
                     [0,1,0,0],
                     [0,1,1,0],
                     [0,0,1,0],
                     [0,0,1,1],
                     [0,0,0,1]]
        
        if mode == "single-phase":
            self.coilSeq = [half_step[1], half_step[3], half_step[5], half_step[7]]
        elif mode == "two-phase":
            self.coilSeq = [half_step[0], half_step[2], half_step[4], half_step[6]]
        else:
            self.coilSeq = half_step
        
        self.stepCount = len(self.coilSeq)
        self.dirStep = range(self.stepCount)
        
        self.invertRatio = 8
        
    def change_direction(self):
        self.dirStep = list(reversed(self.dirStep))
        self.invertFlag = False
    
    def step_motor(self, delay=1/1000):        
        while not self.recipeTimeoutFlag:    
            for j in self.dirStep:
                self.set_step(self.coilSeq [j][0], self.coilSeq [j][1], self.coilSeq [j][2], self.coilSeq [j][3])
                sleep(delay)
                
            if self.invertFlag:
                self.change_direction()
                
            self.runningEvent.wait()
                
    def set_step(self, w1, w2, w3, w4):
        GPIO.output(self.coil_pins[0], w1)
        GPIO.output(self.coil_pins[1], w2)
        GPIO.output(self.coil_pins[2], w3)
        GPIO.output(self.coil_pins[3], w4)

    def watchman(self):
        
        isRunning = True
        self.agitationTimeouts = self.set_timeouts(True)
        invertTime = float(self.agitations[0]["duration"])/self.invertRatio + time()
                
        while not self.recipeTimeoutFlag:
            if self.recipeTimeout <= time():
                self.recipeTimeoutFlag = True
                #forces rest period to end
                self.runningEvent.set()
                #print("Acabou em", time())
                
            elif self.agitationTimeouts[0][0] <= time():
                #agitation[i][0] checks total time
                self.agitation_done(True)
                self.agitationTimeouts = self.set_timeouts()
                isRunning = True
                self.runningEvent.set()    
                #print("Trocou agitação em", time())
                
            elif self.agitationTimeouts[0][1] <= time() and isRunning:
                #agitation[i][1] checks duration
                self.runningEvent.clear()
                isRunning = False
                self.agitationTimeouts[0][2] = time() + float(self.agitations[0]["interval"])
                self.invertFlag = True
                #print("Parou agitação em", time())
                
            elif self.agitationTimeouts[0][2] <= time() and not isRunning:
                #agitation[i][2] checks rest interval
                self.runningEvent.set()
                isRunning = True
                newTime = time()
                self.agitationTimeouts[0][1] = newTime + float(self.agitations[0]["duration"])
                invertTime = float(self.agitations[0]["duration"])/self.invertRatio + newTime
                #print("Retomou agitação em", time())
                
            elif invertTime <= time() and isRunning and not self.invertFlag:
                self.invertFlag = True
                invertTime += float(self.agitations[0]["duration"])/self.invertRatio
                #print("Inverteu", time())
                
            #re-checks values every 1s    
            sleep(1)
        
    def set_timeouts(self, updateAll=True):
        agitationTimeouts = deque([])
        
        for agitation in self.agitations:
            if agitation["totalTime"]:
                timeNow = time()
                timeouts = [float(agitation["totalTime"]) + timeNow, float(agitation["duration"]) + timeNow, float(agitation["interval"]) + timeNow]
            else:
                timeNow = time()
                timeouts = [float("inf"), float(agitation["duration"]) + timeNow, float(agitation["interval"]) + timeNow]
                    
            agitationTimeouts.append(timeouts)
                
        if updateAll:    
            self.recipeTimeout = time() + float(self.recipeDuration)
                                          
        return agitationTimeouts
    
    def agitation_done(self, loop=False):
        if len(self.agitations) > 1 and len(self.agitationTimeouts) > 1:
            agitationDone = self.agitations.popleft()
            timeoutDone = self.agitationTimeouts.popleft()
        
            if loop:
                self.agitations.append(agitationDone)
                self.agitationTimeouts.append(timeoutDone)
            
    def start(self, rDuration, agitations):
        self.agitations = deque(agitations)
        self.recipeDuration = rDuration
        
        try:
            self.watchmanThread = threading.Thread(target=self.watchman, daemon=True)
            
            #tArgs = [rTime, self.recipeFlag, self.recipeTimeout]
            self.runRecipeThread = threading.Thread(target=self.step_motor, daemon=True)
            
            self.watchmanThread.start()
            self.runRecipeThread.start()
    
        except:
            print("Deu erro stepper thread: ", sys.exc_info()[0], sys.exc_info()[1])

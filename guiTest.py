# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import font
from tkinter.ttk import Combobox
from w1thermsensor import W1ThermSensor

import os
import json
import peripherals

import pdb

scaleText = ["Ligar\nBalança", "Desligar\nBalança"]
scaleReadingText = "\n\n Leitura atual:\nMUITOS KGs"
onOffText = ["Turn\nOn", "Turn\nOff"]
runText = ["Run", "Running"]

defaultDir = "./ConfigFiles/"

recipesFile = defaultDir + "recipes.conf"
agitationFile = defaultDir + "agitation.conf"

class DataController:
    def __init__(self):
        self.agitations = {}
        self.recipes = {}
        self.categories = ["All"]
        self.films = ["All"]
        self.agitationWidgets = {}
        self.recipesWidgets = {}
        
    def add_widget(self, widget, wType, name):
        if wType == "recipe":
            self.recipesWidgets.update({name: widget})
        else:
            self.agitationWidgets.update({name: widget})

    def add_recipe(self, recipe, name=None, isUpdate=False):        
        
        if isUpdate:
            self.recipes.update(recipe)
            self.rebuild_lists()
            self.update_widgets("recipe")
        
        else:
            if name is None:
                for entry in recipe:
                    if recipe[entry]["category"] not in self.categories:
                        self.categories.append(recipe[entry]["category"])
                    
                    if recipe[entry]["film"] not in self.films:
                        self.films.append(recipe[entry]["film"])
                        
                    if entry not in self.recipes:
                        self.update_widgets("recipe", entry, True)
                
                self.recipes.update(recipe)
            else:
                if recipe["category"] not in self.categories:
                    self.categories.append(recipe["category"])
                    
                if recipe["film"] not in self.films:
                    self.films.append(recipe["film"])
                        
                if name not in self.recipes:
                    self.recipes.update({ name: recipe})
                    self.update_widgets("recipe", name, True)
            
    def add_agitation(self, pattern, name):
        
        if list(pattern.keys())[0] == name:
            pattern = pattern[name]
                
        if name not in self.agitations:
            self.agitations.update({name: pattern})
            self.update_widgets("agitation", name, True)
        else:
            self.agitations.update({name: pattern})
    
    def rebuild_lists(self):
        self.categories = ["All"]
        self.films = ["All"]
        
        for recipe in self.recipes:
            if self.recipes[recipe]["category"] not in self.categories:
                self.categories.append(self.recipes[recipe]["category"])
            if self.recipes[recipe]["film"] not in self.films:
                self.films.append(self.recipes[recipe]["film"])
            
    def update_widgets(self, wType, item=None, isInsert=None):
        if wType == "recipe":
            widgets = self.recipesWidgets
            widgets["categoryBox"].configure(value=self.categories)
            widgets["filmBox"].configure(value=self.films)
            widgets["nameBox"].configure(value=list(self.recipes.keys()))
        else:
            widgets = self.agitationWidgets
            widgets["agitationBox"].configure(value=list(self.agitations.keys()))
        
        if item is not None:
            if isInsert:
                if "listBox" in widgets:
                    if isinstance(item, str):
                        widgets["listBox"].insert(END, item)
                    else:
                        for key in item:
                            widgets["listBox"].insert(END, key)
            else:
                if "listBox" in widgets:
                    widgets["listBox"].delete(item)
                if wType == "recipe":
                    self.rebuild_lists()
                    widgets["categoryBox"].configure(value=self.categories)
                    widgets["filmBox"].configure(value=self.films)

    def import_data(self, dataIn, dataType):
        if dataIn:
            if dataType == "recipe":
                for data in dataIn:
                    if self.validate_data({data: dataIn[data]}, dataType, app):
                        self.add_recipe(dataIn[data], data)
                        
            else:
                for data in dataIn:
                    if self.validate_data({data: dataIn[data]}, dataType, app):
                        self.add_agitation(dataIn[data], data)
                            
    def check_float(self, data):
        try:
            float(data)
        except ValueError:
            return False
        
        return True
        
    def validate_data(self, data, dataType, callingFrame):
        
        willUpdate = False
        
        #defaultText = ""
        #errorText = ""
         
        defaultText = errorText = "".join(["Error at ", list(data.keys())[0], "\n"]) 
                
        if dataType == "recipe":
            updateText = ["You're about to replace recipe", "and it cannot be undone.\n Continue?"]
            warningTitle = "Recipe error: "
        else:
            updateText = ["You're about to replace agitation pattern", "and it cannot be undone.\n Continue?"]
            warningTitle = "Agitation error: "
         
        for item in data:
            
            warningTitle = "".join([warningTitle, item])
            
            updateText.insert(1, item)
            updateText = " ".join(updateText)
            
            if item == "":
                errorText = "".join([errorText, "Name cannot be blank.\n"])
            elif item in self.recipes and dataType == "recipe":
                willUpdate = True
            elif item in self.agitations and dataType == "agitation":
                willUpdate = True
                
            for info in data[item]:
                if info == "duration":
                    if data[item][info] == "":
                        errorText = "".join([errorText, "Duration cannot be blank.\n"])
                    elif not self.check_float(data[item][info]):
                        if ',' in data[item][info]:
                            errorText = "".join([errorText, "Duration: use . as decimal separator.\n"])
                        else:
                            errorText = "".join([errorText, "Duration must be a numeric value.\n"])
                    elif float(data[item][info]) <= 0:
                        errorText = "".join([errorText, "Duration must be greater than 0.\n"])
                    continue
                    
                elif dataType == "recipe":
                    if info == "film":
                        if data[item][info] == "":
                            data[item][info] = "all"
                        continue
                    elif info == "category":
                        if  data[item][info] == "":
                            data[item][info] = "all"
                        continue
                    elif info == "temperature":
                        if not self.check_float(data[item][info]):
                            if ',' in data[item][info]:
                                errorText = "".join([errorText, "Temperature: use . as decimal separator.\n"])
                            else:
                                if data[item][info] != "":
                                    errorText = "".join([errorText, "Temperature must be a numeric value.\n"])
                        elif float(data[item][info]) <= 0:
                            errorText = "".join([errorText, "Temperature must be greater than 0.\n"])
                        continue
                    if info == "agitation":
                        for agitation in data[item][info]:
                            if agitation == "":
                                errorText = "".join([errorText, "Agitation pattern cannot be blank.\n"])
                            elif agitation not in self.agitations:
                                text = ["Agitation pattern", "doesn't exist.\n"]
                                text.insert(1, data[item][info])
                                text = " ".join(text)
                                errorText = "".join([errorText, text])
                        continue
                else:
                    if info == "interval":
                        if data[item][info] == "":
                            errorText = "".join([errorText, "Interval cannot be blank.\n"])
                        elif not self.check_float(data[item][info]):
                            if ',' in data[item][info]:
                                errorText = "".join([errorText, "Interval: use . as decimal separator.\n"])
                            else:
                                errorText = "".join([errorText, "Interval must be a numeric value.\n"])
                        elif float(data[item][info]) <= 0:
                            errorText = "".join([errorText, "Interval must be greater than 0.\n"])
                        continue
                    elif info == "repetitions":
                        if not data[item][info].isdigit():
                            if data[item][info] != "":
                                errorText = "".join([errorText, "Repetitions must be an integer greater than 0.\n"])
                        continue
                    elif info == "totalTime":
                        if not self.check_float(data[item][info]):
                            if ',' in data[item][info]:
                                errorText = "".join([errorText, "Total time: use . as decimal separator.\n"])
                            elif data[item][info] != "":
                                errorText = "".join([errorText, "Total time must be a numeric value.\n"])
                        elif float(data[item][info]) <= 0:
                            errorText = "".join([errorText, "Total time must be greater than 0.\n"])
                        continue
        
        if errorText != defaultText:
            GUIWarningWindow(errorText, warningTitle=warningTitle, twoButton=False)
            return False
        elif willUpdate:
            
            #if dataType == "agitation":
                #conflicts = self.check_dependencies(list(data.keys())[0])
                        
                #if conflicts:
                    #errorText=["Not allowed.\nThe following recipes depend on this pattern:\n"]
                    #errorText = " ".join(errorText.extend(conflicts))
                    #GUIWarningWindow(errorText, twoButton=False)
                    #return False
            
            warning = GUIWarningWindow(updateText, warningTitle=warningTitle)
            warning.yesButton.configure(command=lambda: callingFrame.save_data(True, warning))
            warning.noButton.configure(command=lambda: warning.Destroy())
            
            return False
            
        elif errorText == defaultText and not willUpdate:
            return True

    def delete_entry(self, entry, entryType):
        if entryType == "recipe":
            if entry in self.recipes:
                del self.recipes[entry]
                app.write_json(entryType)
                return True
            else:
                return False
        else:
            if entry in self.agitations:
                del self.agitations[entry]
                app.write_json(entryType)
                return True
            else:
                return False

    def check_dependencies(self, agitation):
        conflicts = []
        
        for recipe in self.recipes:
            if self.recipes[recipe]["agitation"] == agitation:
                conflicts.append(recipe)
                
        return conflicts
        
class PyLabApp (Tk):
    
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        
        self.dataController = DataController()
        self.pController = peripherals.PeripheralsController()
        
        self.tanks = []
        
        global titleFont
        titleFont = font.Font(size=10, weight="bold")

        self.title("Layout Prototype")
        self.geometry("320x240")
        self.container = Frame(self)#, width=320, height=240)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.container.grid()
    
    def check_files(self):
        directory = os.path.dirname(defaultDir)
        if not os.path.exists(directory):
            os.mkdir(directory)
                                
    def write_json(self, dataType):#, info):
        app.check_files()
        
        if dataType == "recipe":
            directory = recipesFile
            data = app.dataController.recipes

        else: 
            directory = agitationFile
            data = app.dataController.agitations
            
        with open(directory, 'w') as jsonFile:
            if data:
                json.dump(data, jsonFile, sort_keys=False, indent=4)
            jsonFile.close()
            
    def read_json(self, dataType):
        app.check_files()

        if dataType == "recipe":
            directory = recipesFile
        else: 
            directory = agitationFile
        
        if os.stat(directory).st_size != 0:
            with open(directory, 'r') as jsonFile:
                data = json.load(jsonFile)
                jsonFile.close()
                                
                return data

    def show_frame(self, page_name):
            '''Show a frame for the given page name'''
            frame = self.frames[page_name]
            frame.tkraise()
            
    def SetParam(self, widget, param, value):
        widget[param]=value
        widget.grid()
        
    def AllChildren (self, wid) :
        _list = wid.winfo_children()

        for item in _list :
            if item.winfo_children() :
                _list.extend(item.winfo_children())

        return _list
    
    def build_app(self):
        self.frames = {}
        for F in (MainPage, GetTemperatures, SetTemperature, RunEditRecipe, Agitation, NewAgitationCheck, RecipesWindow):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainPage")
        
    def SetupApp(self):
        tanksConf = [("Tank1", 11), ("Tank2", 13)]
        
        for tankConf in tanksConf:
            self.pController.AddTank(tankConf[0], tankConf[1])
            self.tanks.append(tankConf[0])
                
        self.pController.RegisterTherms()
		
class GUIButton:
    def __init__(self, buttonType, master, **kwargs):
        #self.button = tkButton

        if "textvariable" not in kwargs:
            self.buttonTextVar = StringVar()
            kwargs.update({'textvariable': self.buttonTextVar})
            #self.button = Button(master, kwargs, textvariable=self.buttonTextVar)
        if "command" not in kwargs:
            kwargs.update({'command': lambda: self.ToggleText()})
            
        self.button = Button(master, kwargs)
            
        self.buttonToggle = True
        self.buttonType = buttonType

        if buttonType == "scale":
            self.buttonText = scaleText
        elif buttonType == "measureTemp":
            self.buttonText = onOffText
        else:
            self.buttonText = runText
            
        self.buttonTextVar.set(self.buttonText[0])

    def ToggleText(self):
				
        if self.buttonToggle:
            self.buttonTextVar.set(self.buttonText[1])
        else:
            self.buttonTextVar.set(self.buttonText[0])
        
        if self.buttonType == "measureTemp":
            if self.buttonToggle:
                app.frames["GetTemperatures"].start_reading(self)
            else:
                app.frames["GetTemperatures"].stop_reading(self)
                
        self.buttonToggle = not self.buttonToggle

    def SetText(self, newText):
        self.buttonTextVar.set(newText)

    def GetText(self):
        return self.buttonTextVar.get()

    def GetButton(self):
        return self.button

class GUIWarningWindow:
    
    def __init__(self, warningText, warningTitle="Attention!", twoButton=True):                    
        self.warning = Tk()
        self.warning.title(warningTitle)
        self.warning.geometry("320x160+%d+%d" % (app.winfo_x(), app.winfo_y()+app.winfo_height()/10))
        self.warning.lift()
        self.warning.grid_columnconfigure(0, weight=1)
        self.warning.grid_rowconfigure(0, weight=2)
        self.warning.grid_rowconfigure(1, weight=1)
        
        self.buttonFrame = Frame(self.warning)
        self.buttonFrame.grid(row=1, column=0, sticky="news", padx=10, pady=(0, 5))
        self.buttonFrame.grid_columnconfigure(0, weight=1)
        self.buttonFrame.grid_rowconfigure(0, weight=1)
                    
        self.label = Label(self.warning, text=warningText,\
                width=220, font=font.Font(weight="bold", size=10), wraplength=320, anchor=CENTER, justify=CENTER)
        self.label.grid(row=0, column=0, sticky="news", padx=10, pady=(5, 0))
        
        if twoButton:
            self.buttonFrame.grid_columnconfigure(1, weight=1)
            self.yesButton = Button(self.buttonFrame, text="Yes")
            self.yesButton.grid(row=0, column=0, sticky="news")
            
            self.noButton = Button(self.buttonFrame, text="No")
            self.noButton.grid(row=0, column=1, sticky="news")
            
        else:
            self.okButton = Button(self.buttonFrame, text="Ok", \
                            command = lambda: self.Destroy(), width=10, height=2)
            self.okButton.grid(row=0, column=0, sticky="ns", pady=0)
        
    def GetWidgets(self):
        return {"root": self.warning, "label": self.label, \
                "yesButton": self.yesButton, "noButton": self.noButton, \
                "buttonFrame": self.buttonFrame}
                
    def GetWidget(self, widget):
        widgets = self.GetWidgets()
        return widgets[widget]
        
    def Destroy(self):
        self.warning.destroy()
        
    def Hide(self):
        self.warning.withdraw()
        
    def Show(self):
        self.warning.deiconify()

class MainPage(Frame):
 
    def ScaleButtonClick(self, button):
        if button.buttonToggle:
            button.ToggleText()
            buttonText = button.GetText()

            #ler sensor da balanca aqui

            app.SetParam(button.GetButton(), "anchor", 'n')

            buttonText += scaleReadingText
            button.SetText(buttonText)
            
        else:
            button.ToggleText()
            app.SetParam(button.GetButton(), "anchor", 'center')

    def UpdateScale(self, button):
        #funcao que faz a leitura do sensor aqui!!
        pass

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        #define quatro frames iniciais
        scaleFrame = Frame (self, width=150, height=110)#, bg='cyan')
        recipesFrame = Frame (self, width=150, height=110)#, bg='red')
        temperatureFrame = Frame (self, width=150, height=110)#, bg='green')
        allFrame = Frame (self, width=150, height=110)#, bg='yellow')

        #configura comportamento dos frames
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        scaleFrame.grid_rowconfigure(0, weight=1)
        scaleFrame.grid_columnconfigure(0, weight=1)
        temperatureFrame.grid_rowconfigure(0, weight=1)
        temperatureFrame.grid_columnconfigure(1, weight=1)
        temperatureFrame.grid_columnconfigure(0, weight=1)
        allFrame.grid_rowconfigure(0, weight=1)
        allFrame.grid_columnconfigure(0, weight=1)
        recipesFrame.grid_columnconfigure(0, weight=1)
        recipesFrame.grid_columnconfigure(1, weight=1)
        recipesFrame.grid_rowconfigure(0, weight=1)

        scaleFrame.grid_propagate(False)
        temperatureFrame.grid_propagate(False)
        allFrame.grid_propagate(False)
        recipesFrame.grid_propagate(False)

        #coloca as frames no GRID
        scaleFrame.grid(row=0, column=0, pady=(7.5,2.5), padx=(7.5,2.5))
        recipesFrame.grid(row=0, column=1, pady=(7.5,2.5), padx=(2.5,7.5))
        temperatureFrame.grid(row=1, column=0, pady=(2.5,7.5), padx=(7.5,2.5))
        allFrame.grid(row=1, column=1, pady=(2.5,7.5), padx=(2.5,7.5))

        #cria estrutura de dados dos botoes
        scaleButtonGUI = GUIButton("scale", scaleFrame, command=lambda: self.ScaleButtonClick(scaleButtonGUI))

        #declara os botoes dos frames
        scaleButton = scaleButtonGUI.GetButton()
        newRecipeButton = Button(recipesFrame, text="Criar\nReceita", width=5, command=lambda: controller.show_frame("NewAgitationCheck"))
        useRecipeButton = Button(recipesFrame, text="Executar\nou\nEditar\nReceita", width=5, command=lambda: controller.show_frame("RunEditRecipe"))
        adjustTempButton = Button(temperatureFrame, text="Ajustar\nTemp.", width=5, command=lambda: controller.show_frame("SetTemperature"))
        measureTempButton = Button(temperatureFrame, text="Medir\nTemp.", width=5, command=lambda: controller.show_frame("GetTemperatures"))
        allButton = Button(allFrame, text="Rotina Completa")

        #coloca os botoes no grid do frame
        newRecipeButton.grid(column=0, row=0, sticky='news')
        useRecipeButton.grid(column=1, row=0, sticky='news')
        scaleButton.grid(column=0, row=0, sticky='news')
        adjustTempButton.grid(column=0, row=0, sticky='news')
        measureTempButton.grid(column=1, row=0, sticky='news')
        allButton.grid(row=0, column=0, sticky='news')

class GetTemperatures(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        self.activeTanks = []

        self.isCelsius = BooleanVar()
        self.isCelsius.set(True)

        tempFrame1 = Frame(self, width=305, height= 54)#, bg='green')
        tempFrame2 = Frame(self, width=305, height= 54)#, bg='red')
        tempFrame3 = Frame(self, width=305, height= 54)#, bg='yellow')
        bottomFrame = Frame(self, width=305, height= 54)#, bg='cyan')
        unitsFrame = Frame(bottomFrame, borderwidth=1, bg="black", width=225, height=54)

        tempFrame1.grid(column=0, row=0, pady=(7.5,1.5), padx=(7.5,7.5), sticky="news")
        tempFrame2.grid(column=0, row=1, pady=(1.5,1.5), padx=(7.5,7.5))
        tempFrame3.grid(column=0, row=2, pady=(1.5,1.5), padx=(7.5,7.5))
        bottomFrame.grid(column=0, row=3, pady=(1.5,7.5), padx=(7.5,7.5))
        unitsFrame.grid(column=0, row=0, padx=(0,5), sticky="news")

        #configura comportamento dos frames
        tempFrame1.grid_rowconfigure(0, weight=1)
        tempFrame2.grid_rowconfigure(0, weight=1)
        tempFrame3.grid_rowconfigure(0, weight=1)
        tempFrame1.grid_columnconfigure(1, weight=1)
        tempFrame2.grid_columnconfigure(1, weight=1)
        tempFrame3.grid_columnconfigure(1, weight=1)
        bottomFrame.grid_rowconfigure(0, weight=1)
        bottomFrame.grid_columnconfigure(0, weight=1)
        bottomFrame.grid_columnconfigure(1, weight=1)
        unitsFrame.grid_rowconfigure(0, weight=1)
        unitsFrame.grid_columnconfigure(0, weight=1)
        unitsFrame.grid_columnconfigure(1, weight=1)
        unitsFrame.grid_columnconfigure(2, weight=1)

        bottomFrame.grid_propagate(False)
        tempFrame1.grid_propagate(False)
        tempFrame2.grid_propagate(False)
        tempFrame3.grid_propagate(False)
        unitsFrame.grid_propagate(False)

        toggleTempButtonGUI1 = GUIButton("measureTemp", tempFrame1, width=5)
        toggleTempButtonGUI2 = GUIButton("measureTemp", tempFrame2, width=5)
        toggleTempButtonGUI3 = GUIButton("measureTemp", tempFrame3, width=5)
        
        tempLabel1Var = StringVar()
        tempLabel2Var = StringVar()
        tempLabel3Var = StringVar()
                
        guiButtons = [toggleTempButtonGUI1, toggleTempButtonGUI2, toggleTempButtonGUI3]
        tempVars = [tempLabel1Var, tempLabel2Var, tempLabel3Var]
        self.buttonBlobs = {}
        
        i=0
        
        for guiButton in guiButtons:
            #pdb.set_trace()
            tankName = app.tanks[i%len(app.tanks)]
            tempVar = tempVars[i]
            self.buttonBlobs[guiButton] = tankName
            app.pController.UpdateTank(tankName, textVar=tempVar)
            i+=1
        
        toggleTempButton1 = toggleTempButtonGUI1.GetButton()
        toggleTempButton2 = toggleTempButtonGUI2.GetButton()
        toggleTempButton3 = toggleTempButtonGUI3.GetButton()

        toggleTempButton1.grid(row=0, column=0, sticky='news')
        toggleTempButton2.grid(row=0, column=0, sticky='news')
        toggleTempButton3.grid(row=0, column=0, sticky='news')

        tempLabel1 = Label(tempFrame1, textvariable=tempLabel1Var)
        tempLabel2 = Label(tempFrame2, textvariable=tempLabel2Var)
        tempLabel3 = Label(tempFrame3, textvariable=tempLabel3Var)

        tempLabel1.grid(row=0, column=1, columnspan=6, sticky='news')
        tempLabel2.grid(row=0, column=1, columnspan=6, sticky='news')
        tempLabel3.grid(row=0, column=1, columnspan=6, sticky='news')

        unitsLabel = Label(unitsFrame, text="Temp.\nUnit:")
        unitsLabel.grid(row=0,column=0, sticky="news")

        celsiusRadio = Radiobutton(unitsFrame, text="Celsius\n[°C]", width=6, variable=self.isCelsius, value=True, padx=3, pady=3, indicatoron=0, command=lambda:self.change_temp_unit())
        fahrRadio = Radiobutton(unitsFrame, text="Fahrenheit\n[°F]", width=6, variable=self.isCelsius, value=False, padx=3, pady=3, indicatoron=0, command=lambda:self.change_temp_unit())

        celsiusRadio.grid(row=0, column=1, sticky="news")
        fahrRadio.grid(row=0, column=2, sticky="news")

        celsiusRadio.select()

        backButton = Button(bottomFrame, text="Voltar", width=6, command=lambda: controller.show_frame("MainPage"))
        backButton.grid(row=0, column=1, sticky='news')

    def start_reading(self, guiButton):
        app.pController.ActivateTank(self.buttonBlobs[guiButton])

    def stop_reading(self, guiButton):
        app.pController.DeactivateTank(self.buttonBlobs[guiButton])
        
    def change_temp_unit(self):
        if self.isCelsius.get():
            tempUnit = W1ThermSensor.DEGREES_C
        else:
            tempUnit = W1ThermSensor.DEGREES_F
            
        for tankName in app.tanks:
            app.pController.UpdateTank(tankName, tempUnit=tempUnit)

class SetTemperature(Frame):
    
    isRunning = False
    controller = None
    warningOut = None
        
    def CheckBeforeReturn(self, buttonGUI):
        if self.isRunning:
            
            app.SetParam(self.nametowidget('bottomFrame.returnButton'), "state", 'disabled')
            if self.warningOut is None:
                self.warningOut = GUIWarningWindow("Routine is running and you should\n"\
                "stop it before going back.\nDo you want to stop it now?")
                
                widgets = self.warningOut.GetWidgets()
                
                app.SetParam(widgets["yesButton"], "command", lambda: self.HaltAndDestroy(buttonGUI, True))
                app.SetParam(widgets["noButton"], "command", lambda: self.HaltAndDestroy(buttonGUI, False))
            else:
                self.warningOut.Show()
        else:
            if self.warningOut is not None:
                self.warningOut.Destroy()
                self.warningOut = None
                
            self.controller.show_frame("MainPage")
            
    def HaltAndDestroy(self, buttonGUI, halt):
        if halt:
            self.StopRoutine(buttonGUI)
            self.warningOut.Destroy()
            self.warningOut = None
        else:
            self.warningOut.Hide()
        
        app.SetParam(self.nametowidget('bottomFrame.returnButton'), "state", 'normal')
        self.controller.show_frame("MainPage")             
        
    def ChangeLabelUnit(self, textVar, unit):
        textVar.set(unit)
        
    def RunRoutine(self, buttonGUI):
        #Update botão
        buttonGUI.ToggleText()
        app.SetParam(buttonGUI.GetButton(), "state",  "disabled")
        app.SetParam(self.nametowidget('setTempFrame.entryField'), "state", 'disabled')
        app.SetParam(self.nametowidget('bottomFrame.unitsFrame.celsiusRadio'), "state", 'disabled')
        app.SetParam(self.nametowidget('bottomFrame.unitsFrame.fahrRadio'), "state", 'disabled')
        self.isRunning = True
        
    def StopRoutine(self, buttonGUI):
        #Update botão
        
        if self.isRunning:
            app.SetParam(self.nametowidget('setTempFrame.entryField'), "state", 'normal')
            app.SetParam(self.nametowidget('bottomFrame.unitsFrame.celsiusRadio'), "state", 'normal')
            app.SetParam(self.nametowidget('bottomFrame.unitsFrame.fahrRadio'), "state", 'normal')
            buttonGUI.ToggleText()
            app.SetParam(buttonGUI.GetButton(), "state",  "normal")
            self.isRunning = False
        
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.isCelsius = BooleanVar()
        self.isCelsius.set(True)

        targetTempFrame = Frame(self, width=305, height= 54)
        reservTempsFrame = Frame(self, width=305, height= 54)
        setTempFrame = Frame(self, width=305, height= 54, name="setTempFrame")
        bottomFrame = Frame(self, width=305, height= 54, name="bottomFrame")
        
        unitsFrame = Frame(bottomFrame, borderwidth=1, bg="black", \
                     width=225, height=54, name="unitsFrame")
        tempFrame1 = Frame(reservTempsFrame, width=150, height=54)
        tempFrame2 = Frame(reservTempsFrame, width=150, height=54)

        setTempFrame.grid(column=0, row=0, pady=(7.5,1.5), padx=(7.5,7.5))
        targetTempFrame.grid(column=0, row=1, pady=(1.5,1.5), padx=(7.5,7.5))
        reservTempsFrame.grid(column=0, row=2, pady=(1.5,1.5), padx=(7.5,7.5))
        bottomFrame.grid(column=0, row=3, pady=(1.5,7.5), padx=(7.5,7.5))
        
        unitsFrame.grid(column=0, row=0, padx=(0,5), sticky="news")
        tempFrame1.grid(column=0, row=0, padx=(0,2.5), sticky="news")
        tempFrame2.grid(column=1, row=0, padx=(2.5,0), sticky="news")

        #configura comportamento dos frames
        targetTempFrame.grid_rowconfigure(0, weight=1)
        reservTempsFrame.grid_rowconfigure(0, weight=1)
        setTempFrame.grid_rowconfigure(0, weight=1)
        
        reservTempsFrame.grid_columnconfigure(0, weight=1)
        reservTempsFrame.grid_columnconfigure(1, weight=1)
        targetTempFrame.grid_columnconfigure(0, weight=1)
        setTempFrame.grid_columnconfigure(0, weight=1)
        setTempFrame.grid_columnconfigure(1, weight=1)
        
        bottomFrame.grid_rowconfigure(0, weight=1)
        bottomFrame.grid_columnconfigure(0, weight=1)
        bottomFrame.grid_columnconfigure(1, weight=1)
        unitsFrame.grid_rowconfigure(0, weight=1)
        unitsFrame.grid_columnconfigure(0, weight=1)
        unitsFrame.grid_columnconfigure(1, weight=1)
        unitsFrame.grid_columnconfigure(2, weight=1)

        bottomFrame.grid_propagate(False)
        targetTempFrame.grid_propagate(False)
        reservTempsFrame.grid_propagate(False)
        setTempFrame.grid_propagate(False)
        unitsFrame.grid_propagate(False)
        tempFrame1.grid_propagate(False)
        tempFrame2.grid_propagate(False)
                
        entryField = Entry(setTempFrame, width=3, name="entryField", \
                     font=font.Font(size=20), justify="right")
        runButtonGUI = GUIButton("runButton", setTempFrame, text="Run", \
                       width=5, name="runButton", \
                       command=lambda: self.RunRoutine(runButtonGUI))
        runButton = runButtonGUI.GetButton()
        stopButton = Button(setTempFrame, text="Stop", width=5, \
                     command=lambda: self.StopRoutine(runButtonGUI), \
                     name="stopButton")
        
        unitVar = StringVar()
        unitVar.set("°C")
        
        unitLabel = Label(setTempFrame, textvariable=unitVar, width=2)
        targetText = Label(setTempFrame, text="Target\nTemperature", width=10)
        
        targetLabel1 = Label(targetTempFrame, text="Target Tank: asd")
        tempLabel2 = Label(reservTempsFrame, text="Tank 1: asd")
        tempLabel1 = Label(reservTempsFrame, text="Tank 2: asd")

        targetText.grid(row=0, column=0, sticky='news')
        entryField.grid(row=0, column=1, sticky='news')
        unitLabel.grid(row=0, column=2, sticky='news')
        runButton.grid(row=0, column=3, sticky='news')
        stopButton.grid(row=0, column=4, sticky='news')

        targetLabel1.grid(row=0, column=0, sticky='news')
        tempLabel2.grid(row=0, column=0, sticky='news')
        tempLabel1.grid(row=0, column=1, sticky='news')

        unitsLabel = Label(unitsFrame, text="Temp.\nUnit:")
        unitsLabel.grid(row=0,column=0, sticky="news")

        celsiusRadio = Radiobutton(unitsFrame, text="Celsius\n[°C]",\
                       name="celsiusRadio", width=6, \
                       command=lambda: self.ChangeLabelUnit(unitVar, "°C"),\
                       variable=self.isCelsius, value=True, padx=3,\
                       pady=3, indicatoron=0)
        fahrRadio = Radiobutton(unitsFrame, text="Fahrenheit\n[°F]",\
                    name="fahrRadio", width=6, \
                    command=lambda: self.ChangeLabelUnit(unitVar, "°F"),\
                    variable=self.isCelsius, value=False, padx=3, pady=3,\
                    indicatoron=0)

        celsiusRadio.grid(row=0, column=1, sticky="news")
        fahrRadio.grid(row=0, column=2, sticky="news")

        celsiusRadio.select()

        backButton = Button(bottomFrame, text="Voltar", width=6, \
                     command=lambda: self.CheckBeforeReturn(runButtonGUI),\
                     name="returnButton")
        backButton.grid(row=0, column=1, sticky='news')

class RunEditRecipe(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        rowWidth = [50, 110, 55]

        #define quatro frames iniciais
        rowFrame1 = Frame (self, width=300, height=rowWidth[0])#, bg='cyan')
        rowFrame2 = Frame (self, width=300, height=rowWidth[1])#, bg='red')
        rowFrame3 = Frame (self, width=300, height=rowWidth[2])#, bg='green')
        sortFrame = Frame (rowFrame2, width=200, height=rowWidth[1])#, bd=5)#\
                           #borderwidth=1, bg="black")
        filterFrame = Frame(rowFrame2, width=100, height=rowWidth[1])
        filmFrame = Frame(filterFrame, width=100, height=rowWidth[1]/2)
        catFrame = Frame(filterFrame, width=100, height=rowWidth[1]/2)
        recipeFrame = Frame(rowFrame1, width=300, height=rowWidth[0])
        sortButtonsFrame = Frame(sortFrame, width=200, height=rowWidth[1]-25)

        #configura comportamento dos frames
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        rowFrame1.grid_rowconfigure(0, weight=1)
        rowFrame1.grid_columnconfigure(0, weight=1)
        
        rowFrame2.grid_rowconfigure(0, weight=1)
        rowFrame2.grid_columnconfigure(0, weight=1)
        rowFrame2.grid_columnconfigure(1, weight=1)

        rowFrame3.grid_rowconfigure(0, weight=1)
        rowFrame3.grid_columnconfigure(0, weight=1)
        rowFrame3.grid_columnconfigure(1, weight=1)
        rowFrame3.grid_columnconfigure(2, weight=1)
        
        sortFrame.grid_columnconfigure(0, weight=1)
        sortFrame.grid_rowconfigure(0, weight=1)
        sortFrame.grid_rowconfigure(1, weight=1)
        
        filterFrame.grid_columnconfigure(0, weight=1)
        filterFrame.grid_rowconfigure(0, weight=1)
        filterFrame.grid_rowconfigure(1, weight=1)
        
        sortButtonsFrame.grid_columnconfigure(0, weight=1)
        sortButtonsFrame.grid_columnconfigure(1, weight=1)
        sortButtonsFrame.grid_rowconfigure(0, weight=1)
        
        catFrame.grid_columnconfigure(0, weight=1)
        catFrame.grid_rowconfigure(0, weight=1)
        catFrame.grid_rowconfigure(1, weight=1)
        
        filmFrame.grid_columnconfigure(0, weight=1)
        filmFrame.grid_rowconfigure(0, weight=1)
        filmFrame.grid_rowconfigure(1, weight=1)
        
        recipeFrame.grid_columnconfigure(0, weight=1)
        recipeFrame.grid_rowconfigure(0, weight=1)
        recipeFrame.grid_rowconfigure(1, weight=1)

        sortFrame.grid_propagate(False)
        filterFrame.grid_propagate(False)
        sortButtonsFrame.grid_propagate(False)
        recipeFrame.grid_propagate(False)
        filmFrame.grid_propagate(False)
        catFrame.grid_propagate(False)
        rowFrame1.grid_propagate(False)
        rowFrame2.grid_propagate(False)
        rowFrame3.grid_propagate(False)

        #coloca as frames no GRID
        rowFrame1.grid(row=0, column=0, pady=(7.5,2.5), padx=7.5)
        rowFrame2.grid(row=1, column=0, pady=(2.5,2.5), padx=7.5)
        rowFrame3.grid(row=2, column=0, pady=(2.5,7.5), padx=7.5)
        
        recipeFrame.grid(row=0, column=0)#, pady=(2.25,7.5), padx=7.5)
        
        filterFrame.grid(row=0, column=0)
        catFrame.grid(row=1, column=0)#, pady=(2.25,7.5), padx=7.5)
        filmFrame.grid(row=0, column=0)#, pady=(2.25,7.5), padx=7.5)
        
        sortFrame.grid(row=0, column=1)#, pady=(2.25,7.5), padx=7.5)
        sortButtonsFrame.grid(row=1, column=0)#, pady=(2.25,7.5), padx=7.5)
        
        listFont = font.Font(size=11)
        
        catLabel = Label(catFrame, text="Category:", font=titleFont)
        filmLabel = Label(filmFrame, text="Film:", font=titleFont)
        recipeLabel = Label(recipeFrame, text="Recipe:", font=titleFont)
        sortLabel = Label(sortFrame, text="Sort Recipes:", font=titleFont)
        
        catLabel.grid(row=0, column=0, sticky="news")
        filmLabel.grid(row=0, column=0, sticky="news")
        recipeLabel.grid(row=0, column=0, sticky="news")
        sortLabel.grid(row=0, column=0, sticky="news")
        
        categories = ["All", "B&W", "C41", "E6"]
        
        films = ["All", "Tri-X", "Velvia", "All", "Tri-X", "Velvia", "All", "Tri-X", "Velvia", "All", "Tri-X", "Velvia", "All", "Tri-X", "Velvia"]

        recipes = ["Caffenol Stand", "Pa-Rodinal 1:50", "Xtol 1:10"]

        catVar = StringVar()
        catVar.set(categories[0])
        filmVar = StringVar()
        filmVar.set(films[0])
        recipeVar = StringVar()
        recipeVar.set(recipes[0])
        
        recipeList = Combobox(recipeFrame, values=recipes, textvariable = recipeVar, font=listFont)
        
        filmList = Combobox(filmFrame, values=films, textvariable = filmVar, height=7, font=listFont)
        catList = Combobox(catFrame, values=categories, textvariable = catVar, height=4, font=listFont)
        #catList = OptionMenu(catFrame, catVar, *categories)
        #recipeList = OptionMenu(recipeFrame, recipeVar, *recipes)
        #filmList = OptionMenu(filmFrame, filmVar, *films)
        
        catList.grid(row=1, column=0, sticky="nsew")
        recipeList.grid(row=1, column=0, sticky="nsew")
        filmList.grid(row=1, column=0, sticky="nsew")
        
        backButton = Button(rowFrame3, text="Voltar", width=1, \
                     command=lambda: self.controller.show_frame("MainPage"))
        backButton.grid(row=0, column=2, sticky='news')
        runButton = Button(rowFrame3, text="Run Recipe", width=1)
        runButton.grid(row=0, column=0, sticky='news')
        editButton = Button(rowFrame3, text="Edit Recipe", width=1)
        editButton.grid(row=0, column=1, sticky='news')
        
        azButton = Button(sortButtonsFrame, text="A to Z", width=1)
        azButton.grid(row=0, column=0, sticky='nsew')
        zaButton = Button(sortButtonsFrame, text="Z to A", width=1)
        zaButton.grid(row=0, column=1, sticky='nsew')

class Agitation(Frame):
    def __init__(self, parent, controller):
        
        Frame.__init__(self, parent)
        self.controller = controller
        
        rowHeight = [43, 43, 133]

        #define quatro frames iniciais
        rowFrame1 = Frame (self, width=305, height=rowHeight[0])#, bg='cyan')
        rowFrame2 = Frame (self, width=305, height=rowHeight[1])#, bg='red')
        rowFrame3 = Frame (self, width=305, height=rowHeight[2])#, bg='green')
         
        patternsFrame = Frame(rowFrame3, width=244, height=rowHeight[2])
        buttonsFrame = Frame(rowFrame3, width=61, height=rowHeight[2])
        nameFrame = Frame(patternsFrame, width=244, height=rowHeight[1])
        pBoxFrame = Frame(patternsFrame, width=244, height=rowHeight[2]-rowHeight[1])

        #configura comportamento dos frames
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        rowFrame1.grid_rowconfigure(0, weight=1)
        rowFrame1.grid_rowconfigure(1, weight=1)
        rowFrame1.grid_columnconfigure(0, weight=1)
        rowFrame1.grid_columnconfigure(1, weight=1)
        
        rowFrame2.grid_rowconfigure(0, weight=1)
        rowFrame2.grid_rowconfigure(1, weight=1)
        rowFrame2.grid_columnconfigure(0, weight=1)
        rowFrame2.grid_columnconfigure(1, weight=1)

        rowFrame3.grid_rowconfigure(0, weight=1)
        rowFrame3.grid_columnconfigure(0, weight=1)
        rowFrame3.grid_columnconfigure(1, weight=1)
        
        patternsFrame.grid_columnconfigure(0, weight=1)
        patternsFrame.grid_columnconfigure(1, weight=1)
        patternsFrame.grid_rowconfigure(0, weight=1)
        patternsFrame.grid_rowconfigure(1, weight=1)
        #patternsFrame.grid_rowconfigure(2, weight=1)
        
        buttonsFrame.grid_columnconfigure(0, weight=1)
        buttonsFrame.grid_rowconfigure(0, weight=1)
        buttonsFrame.grid_rowconfigure(1, weight=1)
        buttonsFrame.grid_rowconfigure(2, weight=1)
        buttonsFrame.grid_rowconfigure(3, weight=1)
        
        nameFrame.grid_rowconfigure(1, weight=1)
        nameFrame.grid_rowconfigure(0, weight=1)
        nameFrame.grid_columnconfigure(0, weight=1)
        
        #pBoxFrame.grid_rowconfigure(1, weight=1)
        pBoxFrame.grid_rowconfigure(0, weight=1)
        pBoxFrame.grid_columnconfigure(0, weight=1)

        buttonsFrame.grid_propagate(False)
        patternsFrame.grid_propagate(False)
        nameFrame.grid_propagate(False)
        pBoxFrame.grid_propagate(False)
        rowFrame3.grid_propagate(False)
        rowFrame2.grid_propagate(False)
        rowFrame1.grid_propagate(False)
        
        rowFrame1.grid(column=0, row=0, sticky="news", pady=(7.5, 1.5), padx=7.5)
        rowFrame2.grid(column=0, row=1, sticky="news", pady=(1.5, 1.5), padx=7.5)
        rowFrame3.grid(column=0, row=2, sticky="news", pady=(1.5, 7.5), padx=7.5)
        
        self.duration = StringVar()
        self.interval = StringVar()
        self.repetitions = StringVar()
        self.totalTime = StringVar()
        self.name = StringVar()
        
        durationEntry = Entry(rowFrame1, textvar = self.duration)
        intervalEntry = Entry(rowFrame1, textvar = self.interval)
        repetitionsEntry = Entry(rowFrame2, textvar = self.repetitions)
        totalTimeEntry = Entry(rowFrame2, textvar = self.totalTime)
        
        durationEntry.grid(row=1, column=0, sticky="news")
        intervalEntry.grid(row=1, column=1, sticky="news")
        repetitionsEntry.grid(row=1, column=0, sticky="news")
        totalTimeEntry.grid(row=1, column=1, sticky="news")
        
        durationLabel = Label(rowFrame1, text="Duration [s]", font=titleFont)
        intervalLabel = Label(rowFrame1, text="Interval [s]", font=titleFont)
        repetitionsLabel = Label(rowFrame2, text="Repetitions", font=titleFont)
        totalTimeLabel = Label(rowFrame2, text="Total Time [s]", font=titleFont)
        
        durationLabel.grid(row=0, column=0, sticky="news")
        intervalLabel.grid(row=0, column=1, sticky="news")
        repetitionsLabel.grid(row=0, column=0, sticky="news")
        totalTimeLabel.grid(row=0, column=1, sticky="news")
        
        buttonsFrame.grid(column=1, row=0, sticky="news")
        
        backButton = Button(buttonsFrame, text="Voltar", height=1, \
                     command=lambda: controller.show_frame("NewAgitationCheck"))
        backButton.grid(row=3, column=0, sticky='news')
        saveButton = Button(buttonsFrame, text="Save", height=1, \
                     command=lambda: self.save_data())
        saveButton.grid(row=1, column=0, sticky='news')
        self.continueButton = Button(buttonsFrame, text="Continue", height=1, state="disabled")
        self.continueButton.grid(row=0, column=0, sticky='news')
        self.deleteButton = Button(buttonsFrame, text="Delete", height=1, \
                       command=lambda: self.confirm_delete(), state="disabled")
        self.deleteButton.grid(row=2, column=0, sticky='news')
        
        patternsFrame.grid(row=0, column=0, sticky="news")
        nameFrame.grid(row=0, column=0, sticky="news")
        pBoxFrame.grid(row=1, column=0, sticky="news")
        
        nameLabel = Label(nameFrame, text="Agitation Name", font=titleFont)
        nameEntry = Entry(nameFrame, textvar = self.name)
        
        #controller.dataController.add_widget(nameEntry, "agitation")
        
        nameLabel.grid(row=0, column=0, sticky="news", padx=(0,3))
        nameEntry.grid(row=1, column=0, sticky="news", padx=(0,3))
        
        self.patternsBox = Listbox(pBoxFrame, width=15)
        self.patternsBox.grid(row=0, column=0, sticky="news", padx=0)
        self.patternsBox.bind('<<ListboxSelect>>', self.listbox_select)
        
        controller.dataController.add_widget(self.patternsBox, "agitation", "listBox")
            
        scrollbar = Scrollbar(pBoxFrame, width=40)
        scrollbar.grid(row=0, column=1, sticky="news", padx=(0,5))
            
        self.patternsBox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.patternsBox.yview)

    def save_data(self, isUpdate=False, warning=None):
        newAgitation = {
                        self.name.get(): {
                                    "duration": self.duration.get(),
                                    "interval": self.interval.get(),
                                    "repetitions": self.repetitions.get(),
                                    "totalTime": self.totalTime.get()
                                }
                        }
                            
        if not isUpdate:
            if app.dataController.validate_data(newAgitation, "agitation", self):
                            
                app.dataController.add_agitation(newAgitation, self.name.get())
            
                self.clear_data()
            
                app.write_json("agitation")
        else:
            app.dataController.add_agitation(newAgitation, self.name.get())
            
            self.clear_data()
            
            app.write_json("agitation")
            
            warning.Destroy()
    
    def listbox_select(self, event):
        listBox = event.widget
        selection = listBox.curselection()
        agitation = listBox.get(selection)
        
        data = app.dataController.agitations[agitation]
        
        self.duration.set(data["duration"])
        self.interval.set(data["interval"])
        self.repetitions.set(data["repetitions"])
        self.totalTime.set(data["totalTime"])
        self.name.set(agitation)
        
        self.deleteButton.configure(state="normal")
        self.continueButton.configure(state="normal")
    
    def clear_data(self):
        self.duration.set("")
        self.name.set("")
        self.interval.set("")
        self.repetitions.set("")
        self.totalTime.set("")
        
        self.deleteButton.configure(state="disabled")
        self.continueButton.configure(state="disabled")
    
    def load_data(self):
        self.controller.read_json("agitation")
    
    def confirm_delete(self):
        
        item = self.patternsBox.get(self.patternsBox.curselection())

        conflicts = app.dataController.check_dependencies(item)
                        
        if conflicts:
            errorText = ["Not allowed.\nThe following recipes depend on this pattern:"]
            errorText.extend(conflicts)
            errorText = " ".join(errorText)
            GUIWarningWindow(errorText, twoButton=False)
        else:
            
            warningText = "You're about to delete an item and it cannot be undone.\nAre you sure you want to do it?"
                           
            warning = GUIWarningWindow(warningText)
            
            warning.yesButton.configure(command=lambda: self.delete_entry(warning))
            warning.noButton.configure(command=lambda: warning.Destroy())
    
    def delete_entry(self, warning=None):

        selection = self.patternsBox.curselection()

        if selection == ():
            print("No item selected!")
        else:
            if app.dataController.delete_entry(self.patternsBox.get(selection), "agitation"):
                app.dataController.update_widgets("agitation", selection, False)
        
        self.clear_data()
        
        if warning is not None:
            warning.Destroy()
    
class NewAgitationCheck(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        #define quatro frames iniciais
        rowFrame1 = Frame (self, width=305, height=225)#, bg='cyan')

        #configura comportamento dos frames
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        rowFrame1.grid_columnconfigure(0, weight=1)
        rowFrame1.grid_rowconfigure(0, weight=1)
        rowFrame1.grid_rowconfigure(1, weight=1)
        rowFrame1.grid_rowconfigure(2, weight=1)

        rowFrame1.grid_propagate(False)
        
        rowFrame1.grid(column=0, row=0, sticky="news", pady=(7.5, 7.5), padx=7.5)
        
        backButton = Button(rowFrame1, text="Voltar", height=1, \
                     command=lambda: self.controller.show_frame("MainPage"))
        backButton.grid(row=2, column=0, sticky='news')
        agitationButton = Button(rowFrame1, text="Create or Edit Agitation Patterns", height=1, \
                     command=lambda: controller.show_frame("Agitation"))
        agitationButton.grid(row=0, column=0, sticky='news')
        recipeButton = Button(rowFrame1, text="Create New Recipe", height=1, \
                     command=lambda: controller.show_frame("RecipesWindow"))
        recipeButton.grid(row=1, column=0, sticky='news')

class RecipesWindow(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        rowHeight = [43, 43, 133]

        #define quatro frames iniciais
        rowFrame1 = Frame (self, width=305, height=rowHeight[0])#, bg='cyan')
        rowFrame2 = Frame (self, width=305, height=rowHeight[1])#, bg='red')
        rowFrame3 = Frame (self, width=305, height=rowHeight[2])#, bg='green')
         
        patternsFrame = Frame(rowFrame3, width=244, height=rowHeight[2])
        buttonsFrame = Frame(rowFrame3, width=61, height=rowHeight[2])
        agitationFrame = Frame(patternsFrame, width=244, height=rowHeight[1])
        pBoxFrame = Frame(patternsFrame, width=244, height=rowHeight[2]-rowHeight[1])

        #configura comportamento dos frames
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        rowFrame1.grid_rowconfigure(0, weight=1)
        rowFrame1.grid_rowconfigure(1, weight=1)
        rowFrame1.grid_columnconfigure(0, weight=1)
        rowFrame1.grid_columnconfigure(1, weight=1)
        
        rowFrame2.grid_rowconfigure(0, weight=1)
        rowFrame2.grid_rowconfigure(1, weight=1)
        rowFrame2.grid_columnconfigure(0, weight=1)
        rowFrame2.grid_columnconfigure(1, weight=1)
        rowFrame2.grid_columnconfigure(2, weight=1)

        rowFrame3.grid_rowconfigure(0, weight=1)
        rowFrame3.grid_columnconfigure(0, weight=1)
        rowFrame3.grid_columnconfigure(1, weight=1)
        
        patternsFrame.grid_columnconfigure(0, weight=1)
        patternsFrame.grid_rowconfigure(0, weight=1)
        patternsFrame.grid_rowconfigure(1, weight=1)
        
        buttonsFrame.grid_columnconfigure(0, weight=1)
        buttonsFrame.grid_rowconfigure(0, weight=1)
        buttonsFrame.grid_rowconfigure(1, weight=1)
        buttonsFrame.grid_rowconfigure(2, weight=1)
        buttonsFrame.grid_rowconfigure(3, weight=1)
        
        agitationFrame.grid_rowconfigure(0, weight=1)
        agitationFrame.grid_rowconfigure(1, weight=1)
        agitationFrame.grid_columnconfigure(0, weight=1)
        
        pBoxFrame.grid_rowconfigure(0, weight=1)
        pBoxFrame.grid_columnconfigure(0, weight=1)
        pBoxFrame.grid_columnconfigure(1, weight=1)

        buttonsFrame.grid_propagate(False)
        patternsFrame.grid_propagate(False)
        agitationFrame.grid_propagate(False)
        pBoxFrame.grid_propagate(False)
        rowFrame3.grid_propagate(False)
        rowFrame2.grid_propagate(False)
        rowFrame1.grid_propagate(False)
        
        rowFrame1.grid(column=0, row=0, sticky="news", pady=(7.5, 1.5), padx=7.5)
        rowFrame2.grid(column=0, row=1, sticky="news", pady=(1.5, 1.5), padx=7.5)
        rowFrame3.grid(column=0, row=2, sticky="news", pady=(1.5, 7.5), padx=7.5)
        
        self.duration = StringVar()
        self.temp = StringVar()
        self.cat = StringVar()
        self.film = StringVar()
        self.name = StringVar()
        
        durationEntry = Entry(rowFrame1, textvar = self.duration)
        tempEntry = Entry(rowFrame1, textvar = self.temp)
        catEntry = Combobox(rowFrame2, textvar = self.cat, values=controller.dataController.categories)
        filmEntry = Combobox(rowFrame2, textvar = self.film, values=controller.dataController.films)
        nameEntry = Combobox(rowFrame2, textvar = self.name)#, values=list(controller.dataController.agitations.keys()))
        
        durationEntry.grid(row=1, column=0, sticky="news")
        tempEntry.grid(row=1, column=1, sticky="news")
        catEntry.grid(row=1, column=0, sticky="news")
        filmEntry.grid(row=1, column=1, sticky="news")
        nameEntry.grid(row=1, column=2, sticky="news")
        
        nameEntry.bind("<<ComboboxSelected>>", self.recipe_select)
        
        controller.dataController.add_widget(catEntry, "recipe", "categoryBox")
        controller.dataController.add_widget(filmEntry, "recipe", "filmBox")
        controller.dataController.add_widget(nameEntry, "recipe", "nameBox")
                
        durationLabel = Label(rowFrame1, text="Duration [m]", font=titleFont)
        tempLabel = Label(rowFrame1, text="Temperature [C]", font=titleFont)
        catLabel = Label(rowFrame2, text="Category", font=titleFont)
        filmLabel = Label(rowFrame2, text="Film", font=titleFont)
        nameLabel = Label(rowFrame2, text="Name", font=titleFont)
        
        durationLabel.grid(row=0, column=0, sticky="news")
        tempLabel.grid(row=0, column=1, sticky="news")
        catLabel.grid(row=0, column=0, sticky="news")
        filmLabel.grid(row=0, column=1, sticky="news")
        nameLabel.grid(row=0, column=2, sticky="news")
        
        buttonsFrame.grid(column=1, row=0, sticky="news")
        
        backButton = Button(buttonsFrame, text="Voltar", height=1, \
                     command=lambda: controller.show_frame("NewAgitationCheck"))
        backButton.grid(row=3, column=0, sticky='news')
        saveButton = Button(buttonsFrame, text="Save", height=1, \
                     command=lambda: self.save_data())
        saveButton.grid(row=1, column=0, sticky='news')
        self.continueButton = Button(buttonsFrame, text="Continue", height=1, state="normal")
        self.continueButton.grid(row=0, column=0, sticky='news')
        self.deleteButton = Button(buttonsFrame, text="Delete", height=1, \
                       command=lambda: self.delete_entry(), state="disabled")
        self.deleteButton.grid(row=2, column=0, sticky='news')
        
        patternsFrame.grid(row=0, column=0, sticky="news")
        agitationFrame.grid(row=0, column=0, sticky="news")
        pBoxFrame.grid(row=1, column=0, sticky="news")
        
        agitationLabel = Label(agitationFrame, text="Agitations", font=titleFont)
        agitationLabel.grid(row=0, column=0, sticky="news")#, padx=(0,3))
        
        self.agitation = StringVar()
        
        self.agitationEntry = Combobox(agitationFrame, textvar = self.agitation, \
                    values=list(controller.dataController.agitations.keys()))
        self.agitationEntry.bind("<<ComboboxSelected>>", self.add_pattern_to_recipe)
        self.agitationEntry.grid(row=1, column=0, sticky="news")#, padx=(0,3))
        
        controller.dataController.add_widget(self.agitationEntry, "agitation", "agitationBox")
        
        self.patternsBox = Listbox(pBoxFrame)
        self.patternsBox.grid(row=0, column=0, sticky="news", padx=0)
        self.patternsBox.bind('<<ListboxSelect>>', self.agitation_select)

        controller.dataController.add_widget(self.patternsBox, "recipe", "agitationsBox")
            
        scrollbar = Scrollbar(pBoxFrame)
        scrollbar.grid(row=0, column=1, sticky="news", padx=(0,3))
            
        self.patternsBox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.patternsBox.yview)
    
    def save_data(self, isUpdate=False, warning=None):
        newRecipe = {   
                        self.name.get(): {
                                    "category": self.cat.get(),
                                    "duration": self.duration.get(),
                                    "film": self.film.get(),
                                    "temperature": self.temp.get(),
                                    "agitations": self.patternsBox.get(0, END)
                                }
                    }
                
        if not isUpdate:
            if app.dataController.validate_data(newRecipe, "recipe", self):               
                app.dataController.add_recipe(newRecipe)
            
                self.clear_data()
            
                app.write_json("recipe")
        else:
            app.dataController.add_recipe(newRecipe, isUpdate=True)
            
            self.clear_data()
            
            app.write_json("recipe")
            
            warning.Destroy()
        
    def clear_data(self):
        self.cat.set("")
        self.name.set("")
        self.film.set("")
        self.temp.set("")
        self.duration.set("")
        self.agitation.set("")
        
        self.deleteButton.configure(state="disabled")
        self.continueButton.configure(state="disabled")
        
        self.selection = ""
    
    def load_data(self):
        self.controller.read_json("recipe")
    
    def delete_entry(self, warning=None):
        
        pdb.set_trace()
        
        selection = self.patternsBox.curselection()
        
        if self.selection == "":
            print("No item selected!")
        else:
            self.patternsBox.delete(self.patternsBox.get(0, "end").index(self.selection))
            #if app.dataController.delete_entry(self.selection, "recipe"):
            #    app.dataController.update_widgets("recipe", selection, False)
        
        #self.clear_data()
        
        if warning is not None:
            warning.Destroy()

    def recipe_select(self, event):
        #selection = self.agitationEntry.get()
        recipe = event.widget.get()
        
        data = app.dataController.recipes[recipe]
                
        self.duration.set(data["duration"])
        self.temp.set(data["temperature"])
        self.cat.set(data["category"])
        self.film.set(data["film"])
        self.name.set(recipe)
                
        if self.patternsBox.get(0, END) != ():
            self.patternsBox.delete(0, END)
                
        for agitation in data["agitation"]:
            #self.agitation.set(data["agitation"])
            self.patternsBox.insert(END, agitation)
                
        
        self.deleteButton.configure(state="normal")
        self.continueButton.configure(state="normal")
        
    def confirm_delete(self):
        warningText = "You're about to delete an recipe and it cannot be undone.\nAre you sure you want to do it?"
                       
        warning = GUIWarningWindow(warningText)
        
        warning.yesButton.configure(command=lambda: self.delete_entry(warning))
        warning.noButton.configure(command=lambda: warning.Destroy())

    def add_pattern_to_recipe(self, event):
        chosenPattern = self.agitationEntry.get()
        self.agitationEntry.set("")
        self.patternsBox.insert(END, chosenPattern)

    def agitation_select(self, event):
        pdb.set_trace()
        self.selection = self.patternsBox.get(ACTIVE)
        self.deleteButton.configure(state="normal")

if __name__ == "__main__":
    app = PyLabApp()
    
    app.SetupApp() 
    
    app.check_files()
    app.build_app()
    
    if os.path.isfile(agitationFile):
        data = app.read_json("agitation")
        if data:
            app.dataController.import_data(data, "agitation")
            
    if os.path.isfile(recipesFile):
        data = app.read_json("recipe")
        if data:
            app.dataController.import_data(data, "recipe")

    app.mainloop()

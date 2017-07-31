# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import font
from tkinter.ttk import Combobox, Notebook, Style, Labelframe
from w1thermsensor import W1ThermSensor

import os
import json
import configparser
import peripherals

import pdb

class DataController:
    def __init__(self):
        valuesText = app.interfaceText["RunRecipe"]["Values"]
        
        self.agitations = {}
        self.recipes = {}
        self.categories = [valuesText["AllCategories"]]
        self.films = [valuesText["AllFilms"]]
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
            
            recipes = list(self.recipes.keys())
            
            #for crete/edit window
            widgets["categoryBox"].configure(value=self.categories)
            widgets["filmBox"].configure(value=self.films)
            widgets["nameBox"].configure(value=recipes)
            
            #run window
            widgets["catList"].configure(value=self.categories)
            widgets["catList"].current(0)
            widgets["filmList"].configure(value=self.films)
            widgets["filmList"].current(0)
            widgets["recipeList"].configure(value=recipes)
            
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
        
        errorTexts = app.interfaceText["WarningWindow"]["Validation"]
         
        defaultText = errorText = "".join([errorTexts["DefaultError"], list(data.keys())[0], "\n"]) 
                
        if dataType == "recipe":
            updateText = errorTexts["RecipeUpdate"]#["You're about to replace recipe", "\nand it cannot be undone. Continue?"]
            warningTitle = errorTexts["RecipeTitle"]#"Recipe error: "
        else:
            updateText = errorTexts["AgitationUpdate"]#["You are replacing agitation pattern\n", "and it cannot be undone.\nContinue?"]
            warningTitle = errorTexts["AgitationTitle"]#"Agitation error: "
         
        for item in data:
            
            warningTitle = "".join([warningTitle, item])
            
            updateText.insert(1, item)
            updateText = " ".join(updateText)
            
            checkedAgitations = []
            
            if item == "":
                errorText = "".join([errorText, errorTexts["BlankName"]])
            elif item in self.recipes and dataType == "recipe":
                willUpdate = True
            elif item in self.agitations and dataType == "agitation":
                willUpdate = True
                
            for info in data[item]:
                if info == "duration":
                    if data[item][info] == "":
                        errorText = "".join([errorText, errorTexts["BlankDuration"]])
                    elif not self.check_float(data[item][info]):
                        if ',' in data[item][info]:
                            errorText = "".join([errorText, errorTexts["DurationDecimal"]])
                        else:
                            errorText = "".join([errorText, errorTexts["DurationNumeric"]])
                    elif float(data[item][info]) <= 0:
                        errorText = "".join([errorText, errorTexts["DurationZero"]])
                    continue
                    
                elif dataType == "recipe":
                    if info == "film":
                        if data[item][info] == "":
                            data[item][info] = app.interfaceText["RunRecipes"]["Values"]["AllFilms"]
                        continue
                    elif info == "category":
                        if  data[item][info] == "":
                            data[item][info] = app.interfaceText["RunRecipes"]["Values"]["AllFilms"]
                        continue
                    elif info == "temperature":
                        if not self.check_float(data[item][info]):
                            if ',' in data[item][info]:
                                errorText = "".join([errorText, errorTexts["TemperatureDecimal"]])
                            else:
                                if data[item][info] != "":
                                    errorText = "".join([errorText, errorTexts["TemperatureNumeric"]])
                        elif float(data[item][info]) <= 0:
                            errorText = "".join([errorText, errorTexts["TemperatureZero"]])
                        continue
                        
                    if info == "agitations":
                        if data[item][info] == []:
                                errorText = "".join([errorText, errorTexts["AgitationEmpty"]])
                        for agitation in data[item][info]:
                            if agitation not in self.agitations and agitation not in checkedAgitations:
                                text = errorTexts["AgitationNotFound"]
                                text.insert(1, agitation)
                                text = " ".join(text)
                                errorText = "".join([errorText, text])
                                checkedAgitations.append(agitation)
                        continue
                else:
                    if info == "interval":
                        if data[item][info] == "":
                            errorText = "".join([errorText, errorTexts["BlankInterval"]])
                        elif not self.check_float(data[item][info]):
                            if ',' in data[item][info]:
                                errorText = "".join([errorText, errorTexts["IntervalDecimal"]])
                            else:
                                errorText = "".join([errorText, errorTexts["IntervalNumeric"]])
                        elif float(data[item][info]) <= 0:
                            errorText = "".join([errorText, errorTexts["IntervalZero"]])
                        continue
                    elif info == "repetitions":
                        if not data[item][info].isdigit():
                            if data[item][info] != "":
                                errorText = "".join([errorText, errorTexts["RepetitionsZero"]])
                        continue
                    elif info == "totalTime":
                        if not self.check_float(data[item][info]):
                            if ',' in data[item][info]:
                                errorText = "".join([errorText, errorTexts["TotalTimeDecimal"]])
                            elif data[item][info] != "":
                                errorText = "".join([errorText, errorTexts["TotalTimeNumeric"]])
                        elif float(data[item][info]) <= 0:
                            errorText = "".join([errorText, errorTexts["TotalTimeZero"]])
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
        
        i=0
        
        for recipe in self.recipes:
            if i > 2:
                conflicts.append("\n")
                i=0
                
            if agitation in self.recipes[recipe]["agitations"]:
                conflicts.append(recipe)
                i+=1
                
        return conflicts
     
    def filter_data(self, dataType, param, pValue, dataIn=[]):
        filteredData = []
        dataToFilter = {}
        
        if dataType == "recipes":
            if dataIn:
                for key, value in self.recipes.items():
                    if key in dataIn:
                        dataToFilter[key] = self.recipes[key]
            else:
                dataToFilter = self.recipes
                
        else:
            if dataIn:
                for key, value in self.agitations.items():
                    if key in dataIn:
                        dataToFilter[key] = self.recipes[key]
            else:
                dataToFilter = self.recipes
            
        for key, value in dataToFilter.items():
            if dataToFilter[key][param] == pValue:
                filteredData.append(key)
                    
        return filteredData
         
class PyLabApp (Tk):
    
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        
        self.pController = peripherals.PeripheralsController(self)
        
        self.languages = []
                
        self.defaultConfigDir = "./ConfigFiles/"

        self.recipesFile = self.defaultConfigDir + "recipes.conf"
        self.agitationFile = self.defaultConfigDir + "agitation.conf"
        self.configFile = self.defaultConfigDir + "config.ini"
        self.languagesFile = self.defaultConfigDir + "supported_languages.conf"
        
        self.sections = ["Scale", "Temperature", "Interface"]
            
        self.scaleSubSections = ["ReferenceUnit", "DecimalPlaces", "WeightUnit"]
        self.tempSubSections = ["TemperatureUnit", "DecimalPlaces"]
        self.interfaceSubSections = ["Language"]

        self.tanks = []
        
        self.config = {
                        self.sections[0]: {
                                        self.scaleSubSections[0]: "",
                                        self.scaleSubSections[1]: "1",
                                        self.scaleSubSections[2]: "metric"                                        
                                     },
                        self.sections[1]: { 
                                        self.tempSubSections[0]: "celsius",
                                        self.tempSubSections[1]: "2"
                                     },
                        self.sections[2]: {
                                        self.interfaceSubSections[0]: "en-US"
                                     }
                      } 
                
        global titleFont
        titleFont = font.Font(size=10, weight="bold")

        self.title("Layout Prototype")
        self.geometry("320x240")
        self.container = Frame(self)#, width=320, height=240)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.container.grid()
        
        self.interfaceText = {
                            "MainPage": {
                                "Buttons": {
                                    "ScaleButtonOn": "Turn on\n scale",
                                    "ScaleButtonOff": "Turn off scale\n\n",
                                    "SettingUpScale": "Setting up scale...",
                                    "CreateRecipe": "Create\nor\nEdit\nRecipe",
                                    "RunRecipe": "Run\nRecipe",
                                    "SetTemperature": "Control\nTemp.",
                                    "GetTemperature": "Read\nTemp.",
                                    "Preferences": "Preferences"
                                    }
                                }
                            }
    
    def check_files(self):
        directory = os.path.dirname(self.defaultConfigDir)
        if not os.path.exists(directory):
            os.mkdir(directory)
                                
    def write_json(self, dataType):#, info):
        app.check_files()
        
        if dataType == "recipe":
            directory = self.recipesFile
            data = app.dataController.recipes

        else: 
            directory = self.agitationFile
            data = app.dataController.agitations
            
        with open(directory, 'w') as jsonFile:
            if data:
                json.dump(data, jsonFile, sort_keys=False, indent=4)
            jsonFile.close()
            
    def read_json(self, dataType):
        app.check_files()

        if dataType == "recipe":
            directory = self.recipesFile
        elif dataType == "agitation": 
            directory = self.agitationFile
        elif dataType == "language":
            directory = self.languagesFile
        else:
            raise TypeError("Unkown type of file to read")
            
        if os.stat(directory).st_size != 0:
            with open(directory, 'r') as jsonFile:
                data = json.load(jsonFile)
                jsonFile.close()
                                
                return data

    def show_frame(self, page_name, carryData = None):
            '''Show a frame for the given page name'''
            frame = self.frames[page_name]
            
            if carryData is not None:
                frame.load_carry_data(carryData)
                
            frame.tkraise()
            
    def set_param(self, widget, param, value):
        widget[param]=value
        widget.grid()
        
    def all_children (self, wid) :
        _list = wid.winfo_children()

        for item in _list :
            if item.winfo_children() :
                _list.extend(item.winfo_children())

        return _list
    
    def build_app(self): 
        self.dataController = DataController()
               
        self.frames = {}
        for F in (MainPage, GetTemperatures, SetTemperature, RunRecipe, AgitationsWindow, NewAgitationCheck, RecipesWindow, PreferencesPane):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainPage")
        
    def setup_app(self):
        tanksConf = [("Tank1", 11), ("Tank2", 13)]
        
        for tankConf in tanksConf:
            self.pController.AddTank(tankConf[0], tankConf[1])
            self.tanks.append(tankConf[0])
                
        self.pController.RegisterTherms()
        
        if not self.config[self.sections[0]][self.scaleSubSections[0]]:
            reference = self.pController.calibrate_scale()
            self.config[self.sections[0]][self.scaleSubSections[0]] = reference
            
            self.write_config(self.config)
            
        self.pController.set_scale_reference(float(self.config[self.sections[0]][self.scaleSubSections[0]]))
    
    def on_closing(self):
        print ("Fechando ça'porra")
        self.pController.cleanup()
        self.pController.stop_all()
        print ("Saionara, bitches!")
        self.destroy()
        sys.exit()
        
    def read_config(self):
        config = configparser.ConfigParser()
        config.read(self.configFile)
                
        try:
            for section, subsections in self.config.items():
                for subsection, value in subsections.items():
                    self.config[section][subsection] = config[section][subsection]

        except KeyError:
            print("INI file error at Scale section")
        
    def write_config(self, data):
        config = configparser.ConfigParser()
        
        if isinstance (data, configparser.ConfigParser):
            config = data
        elif isinstance (data, dict):
            config.read_dict(data)
        else:
            for i in range(len(self.config)):
                config[self.sections[i]] = self.config[self.sections[i]]
        
        with open(self.configFile, 'w') as confFile:
            config.write(confFile)
    
    def parse_language(self):
        if os.path.isfile(app.languagesFile):
            
            languages = self.read_json("language")
            
            self.languages = list(languages.keys())
            
            language = self.config["Interface"]["Language"] or "en-US"
            
            if language in languages:
                self.interfaceText = languages[language]
            elif "en-US" in languages:
                self.interfaceText = languages["en-US"]
            else:
                print("Due to lack of valid options, choosing the default language")
     
    def test_warnings(self):
        oneButton = self.interfaceText["WarningWindow"]["Validation"]
        twoButton = self.interfaceText["WarningWindow"]["Warns"]
                
        for text in oneButton:
            GUIWarningWindow(oneButton[text], warningTitle="One Button Test", twoButton=False)
            input("Press [Enter] to continue...")
        
        for text in twoButton:
            GUIWarningWindow(twoButton[text], warningTitle="Two Button Test")
            input("Press [Enter] to continue...")

class GUIButton:
    def __init__(self, buttonType, master, **kwargs):
        #self.button = tkButton
        
        scaleButtonsText = app.interfaceText["MainPage"]["Buttons"]
        tempButtonsText = app.interfaceText["GetTemperatures"]["Buttons"]
        
        self.scaleText = [scaleButtonsText["ScaleButtonOn"], scaleButtonsText["ScaleButtonOff"]]
        #self.scaleText = ["Ligar\nBalança", "Desligar\nBalança"]
        #self.scaleReadingText = "\n\n Leitura atual:\n"
        #self.onOffText = ["Turn\nOn", "Turn\nOff"]
        self.onOffText = [tempButtonsText["TempButtonOn"], tempButtonsText["TempButtonOff"]]
        self.runText = ["Run", "Running"]

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
            self.buttonText = self.scaleText
            #self.readingText = scaleReadingText
        elif buttonType == "measureTemp":
            self.buttonText = self.onOffText
        else:
            self.buttonText = self.runText
            
        self.buttonTextVar.set(self.buttonText[0])

    def ToggleText(self, inText=None):
                
        if self.buttonToggle:
            self.buttonTextVar.set(inText or self.buttonText[1])
        else:
            self.buttonTextVar.set(inText or self.buttonText[0])
        
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
    
    def __init__(self, warningText, warningTitle=None, twoButton=True):                    
        self.warning = Tk()
        self.warning.title(warningTitle)
        self.warning.geometry("320x160+%d+%d" % (app.winfo_x(), app.winfo_y()+app.winfo_height()/10))
        self.warning.lift()
        self.warning.grid_columnconfigure(0, weight=1)
        self.warning.grid_rowconfigure(0, weight=2)
        self.warning.grid_rowconfigure(1, weight=1)
        
        warningTitle = warningTitle or app.interfaceText["WarningWindow"]["Title"]
        
        self.buttonFrame = Frame(self.warning)
        self.buttonFrame.grid(row=1, column=0, sticky="news", padx=10, pady=(0, 5))
        self.buttonFrame.grid_columnconfigure(0, weight=1)
        self.buttonFrame.grid_rowconfigure(0, weight=1)
        
        buttonsText = app.interfaceText["WarningWindow"]["Buttons"]
                    
        self.label = Label(self.warning, text=warningText,\
                width=220, font=font.Font(weight="bold", size=10), wraplength=320, anchor=CENTER, justify=CENTER)
        self.label.grid(row=0, column=0, sticky="news", padx=10, pady=(5, 0))
        
        if twoButton:
            self.buttonFrame.grid_columnconfigure(1, weight=1)
            self.yesButton = Button(self.buttonFrame, text=buttonsText["YesButton"])
            self.yesButton.grid(row=0, column=0, sticky="news")
            
            self.noButton = Button(self.buttonFrame, text=buttonsText["NoButton"])
            self.noButton.grid(row=0, column=1, sticky="news")
            
        else:
            self.okButton = Button(self.buttonFrame, text=buttonsText["OkButton"], \
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
        app.pController.set_scale_out(scaleButtonGUI)        
        
        buttonsText = self.controller.interfaceText["MainPage"]["Buttons"]
        
        #declara os botoes dos frames
        scaleButton = scaleButtonGUI.GetButton()
        newRecipeButton = Button(recipesFrame, text=buttonsText["CreateRecipe"], width=5, command=lambda: controller.show_frame("NewAgitationCheck"))
        useRecipeButton = Button(recipesFrame, text=buttonsText["RunRecipe"], width=5, command=lambda: controller.show_frame("RunRecipe"))
        adjustTempButton = Button(temperatureFrame, text=buttonsText["SetTemperature"], width=5, command=lambda: controller.show_frame("SetTemperature"))
        measureTempButton = Button(temperatureFrame, text=buttonsText["GetTemperature"], width=5, command=lambda: controller.show_frame("GetTemperatures"))
        preferencesButton = Button(allFrame, text=buttonsText["Preferences"], command=lambda: controller.show_frame("PreferencesPane"))

        #coloca os botoes no grid do frame
        newRecipeButton.grid(column=0, row=0, sticky='news')
        useRecipeButton.grid(column=1, row=0, sticky='news')
        scaleButton.grid(column=0, row=0, sticky='news')
        adjustTempButton.grid(column=0, row=0, sticky='news')
        measureTempButton.grid(column=1, row=0, sticky='news')
        preferencesButton.grid(row=0, column=0, sticky='news')
 
    def ScaleButtonClick(self, button):
        if button.buttonToggle:
            #turn on scale reading
            button.ToggleText(app.interfaceText["MainPage"]["Buttons"]["SettingUpScale"]) 
            app.pController.activate_scale()
                       
        else:
            #turn off scale reading
            app.pController.deactivate_scale()

            button.ToggleText()
            app.set_param(button.GetButton(), "anchor", 'center')

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
        
        labelsText = app.interfaceText["GetTemperatures"]["Labels"]
        buttonsText = app.interfaceText["GetTemperatures"]["Buttons"]

        unitsLabel = Label(unitsFrame, text=labelsText["TempUnit"])
        unitsLabel.grid(row=0,column=0, sticky="news")

        celsiusRadio = Radiobutton(unitsFrame, text="Celsius\n[°C]", width=6, variable=self.isCelsius, value=True, padx=3, pady=3, indicatoron=0, command=lambda:self.change_temp_unit())
        fahrRadio = Radiobutton(unitsFrame, text="Fahrenheit\n[°F]", width=6, variable=self.isCelsius, value=False, padx=3, pady=3, indicatoron=0, command=lambda:self.change_temp_unit())

        celsiusRadio.grid(row=0, column=1, sticky="news")
        fahrRadio.grid(row=0, column=2, sticky="news")

        celsiusRadio.select()

        backButton = Button(bottomFrame, text=buttonsText["Back"], width=6, command=lambda: controller.show_frame("MainPage"))
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
            warnText = app.interfaceText["WarningWindow"]["Warns"]
            app.set_param(self.nametowidget('bottomFrame.returnButton'), "state", 'disabled')
            if self.warningOut is None:
                self.warningOut = GUIWarningWindow(warnText["RoutineRunning"])
                
                widgets = self.warningOut.GetWidgets()
                
                app.set_param(widgets["yesButton"], "command", lambda: self.HaltAndDestroy(buttonGUI, True))
                app.set_param(widgets["noButton"], "command", lambda: self.HaltAndDestroy(buttonGUI, False))
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
        
        app.set_param(self.nametowidget('bottomFrame.returnButton'), "state", 'normal')
        self.controller.show_frame("MainPage")             
        
    def ChangeLabelUnit(self, textVar, unit):
        textVar.set(unit)
        
    def RunRoutine(self, buttonGUI):
        #Update botão
        buttonGUI.ToggleText()
        app.set_param(buttonGUI.GetButton(), "state",  "disabled")
        app.set_param(self.nametowidget('setTempFrame.entryField'), "state", 'disabled')
        app.set_param(self.nametowidget('bottomFrame.unitsFrame.celsiusRadio'), "state", 'disabled')
        app.set_param(self.nametowidget('bottomFrame.unitsFrame.fahrRadio'), "state", 'disabled')
        self.isRunning = True
        
    def StopRoutine(self, buttonGUI):
        #Update botão
        
        if self.isRunning:
            app.set_param(self.nametowidget('setTempFrame.entryField'), "state", 'normal')
            app.set_param(self.nametowidget('bottomFrame.unitsFrame.celsiusRadio'), "state", 'normal')
            app.set_param(self.nametowidget('bottomFrame.unitsFrame.fahrRadio'), "state", 'normal')
            buttonGUI.ToggleText()
            app.set_param(buttonGUI.GetButton(), "state",  "normal")
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

class RunRecipe(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        self.activeFilters = {
                                "category": "All",
                                "film": "All"
                             }
        self.filteredRecipes = None
        
        rowWidth = [50, 115, 50]

        #define quatro frames iniciais
        rowFrame1 = Frame (self, width=300, height=rowWidth[0])#, bg='cyan')
        rowFrame2 = Frame (self, width=300, height=rowWidth[1])#, bg='red')
        rowFrame3 = Frame (self, width=300, height=rowWidth[2])#, bg='green')
        sortFrame = Frame (rowFrame2, width=200, height=rowWidth[1])#, bd=5)#\
                           #borderwidth=1, bg="black")
                           
        filterParentFrame = Frame(rowFrame2, width=100, height=rowWidth[1])
        filterFrame = Frame(filterParentFrame, width=100, height=rowWidth[1]-25, bd=1, bg='black')
        
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
        
        filterParentFrame.grid_columnconfigure(0, weight=1)
        filterParentFrame.grid_rowconfigure(0, weight=1)
        filterParentFrame.grid_rowconfigure(1, weight=1)
        
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
        filterParentFrame.grid_propagate(False)
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
        
        filterParentFrame.grid(column=1, row=0)
        filterFrame.grid(row=1, column=0)
        
        catFrame.grid(row=1, column=0)#, pady=(2.25,7.5), padx=7.5)
        filmFrame.grid(row=0, column=0)#, pady=(2.25,7.5), padx=7.5)
        
        sortFrame.grid(row=0, column=0)#, pady=(2.25,7.5), padx=7.5)
        sortButtonsFrame.grid(row=1, column=0)#, pady=(2.25,7.5), padx=7.5)
        
        listFont = font.Font(size=10)
        
        labelsText = app.interfaceText["RunRecipe"]["Labels"]
        buttonsText = app.interfaceText["RunRecipe"]["Buttons"]
        self.valuesText = app.interfaceText["RunRecipe"]["Values"]
        
        filterLabel = Label(filterParentFrame, text=labelsText["FilterBy"], font=titleFont)
        filterLabel.grid(row=0, column=0)
        
        catLabel = Label(catFrame, text=labelsText["Category"], font=titleFont)
        filmLabel = Label(filmFrame, text=labelsText["Film"], font=titleFont)
        recipeLabel = Label(recipeFrame, text=labelsText["Recipe"], font=titleFont)
        sortLabel = Label(sortFrame, text=labelsText["Sort"], font=titleFont)
        
        catLabel.grid(row=0, column=0, sticky="news")
        filmLabel.grid(row=0, column=0, sticky="news")
        recipeLabel.grid(row=0, column=0, sticky="news")
        sortLabel.grid(row=0, column=0, sticky="news")
        
        self.recipeList = Combobox(recipeFrame, font=listFont)
        
        self.filmList = Combobox(filmFrame, height=7, font=listFont)
        self.catList = Combobox(catFrame, height=4, font=listFont)
        
        self.filmList.set(self.valuesText["AllFilms"])
        self.catList.set(self.valuesText["AllCategories"])
        
        controller.dataController.add_widget(self.filmList, "recipe", "filmList")
        controller.dataController.add_widget(self.catList, "recipe", "catList")
        controller.dataController.add_widget(self.recipeList, "recipe", "recipeList")
        
        self.catList.bind("<<ComboboxSelected>>", self.filter_recipes)
        self.filmList.bind("<<ComboboxSelected>>", self.filter_recipes)
        
        self.catList.grid(row=1, column=0, sticky="nsew")
        self.recipeList.grid(row=1, column=0, sticky="nsew")
        self.filmList.grid(row=1, column=0, sticky="nsew")
        
        backButton = Button(rowFrame3, text=buttonsText["Back"], width=1, \
                     command=lambda: self.controller.show_frame("MainPage"))
        backButton.grid(row=0, column=2, sticky='news')
        runButton = Button(rowFrame3, text=buttonsText["Run"], width=1)
        runButton.grid(row=0, column=0, sticky='news')
        clearButton = Button(rowFrame3, text=buttonsText["Clear"], width=1, \
                      command=lambda: self.clear_all())
        clearButton.grid(row=0, column=1, sticky='news')
        
        azButton = Button(sortButtonsFrame, text=buttonsText["SortAZ"], width=1, \
                   command=lambda: self.sort_recipes())
        azButton.grid(row=0, column=0, sticky='nsew')
        zaButton = Button(sortButtonsFrame, text=buttonsText["SortZA"], width=1, \
                   command=lambda: self.sort_recipes(reverse=True))
        zaButton.grid(row=0, column=1, sticky='nsew')

    def filter_recipes(self, event):
        fValue = event.widget.get()
        filteredRecipes = []
        cats = [self.valuesText["AllCategories"]]
        films = [self.valuesText["AllFilms"]]
        changed = False
        
        self.recipeList.set("")
        
        if event.widget is self.catList:
            isCat = True

            if fValue != self.activeFilters["category"]:
                changed = True
                self.activeFilters.update({"category": fValue})
                
        else:
            isCat = False
            
            if fValue != self.activeFilters["film"]:
                changed = True
                self.activeFilters.update({"film": fValue})
                
        if changed:
            if self.activeFilters["category"] == self.valuesText["AllCategories"] and  self.activeFilters["film"] == self.valuesText["AllFilms"]:
                filteredRecipes = list(self.controller.dataController.recipes.keys())
                self.catList.config(value=self.controller.dataController.categories)
                self.filmList.config(value=self.controller.dataController.films)
                
            elif changed:
                for key, value in self.activeFilters.items():
                    #if (key == "category" and value != self.valuesText["AllCategories"]) \
                    #        or (key == "film" and value != self.valuesText["AllFilms"]):
                    if value != self.valuesText["AllCategories"] or value != self.valuesText["AllFilms"]:
                        filteredRecipes = self.controller.dataController.filter_data("recipes", key, value, filteredRecipes)
                    
                    if key == "category" and isCat:
                        listToAppend = films
                        recipeKey = "film"
                        widgetToUpdate = self.filmList
                    
                    elif key == "film" and not isCat:
                        listToAppend = cats
                        recipeKey = "category"
                        widgetToUpdate = self.catList
                        
                    else:
                        continue
                        
                    #if value == "All":
                    if value == self.valuesText["AllCategories"] or value == self.valuesText["AllFilms"]:
                        lookupList = list(self.controller.dataController.recipes.keys())
                    else:
                        lookupList = filteredRecipes
                        
                    for recipe in lookupList:
                        item = self.controller.dataController.recipes[recipe][recipeKey]
                        
                        if item not in listToAppend:
                            listToAppend.append(item)
                        
                    widgetToUpdate.config(value=listToAppend)
                
                self.recipeList.config(values=filteredRecipes)        
                    
                self.filteredRecipes = filteredRecipes
            
    def clear_all(self):
        self.recipeList.config(values=list(self.controller.dataController.recipes.keys()))
        self.filmList.config(value=self.controller.dataController.films)
        self.catList.config(value=self.controller.dataController.categories)
        
        self.activeFilters = {
                                "category": self.valuesText["AllCategories"],
                                "film": self.valuesText["AllFilms"]
                             }
                             
        self.filmList.current(0)
        self.catList.current(0)
        self.filteredRecipes = None
        
    def sort_recipes(self, reverse=False):
        try:
            if  len(self.filteredRecipes) == 0:
                recipesToSort = list(self.controller.dataController.recipes.keys())
            else:
                recipesToSort = self.filteredRecipes
            
            #recipesToSort.sort(reverse=reverse)
            #self.recipeList.config(values=recipesToSort)
        except:
            recipesToSort = list(self.controller.dataController.recipes.keys())
            
        recipesToSort.sort(reverse=reverse)
        self.recipeList.config(values=recipesToSort)
    
    def load_carry_data(self, carryData):
        if carryData in self.controller.dataController.recipes:
            self.recipeList.set(carryData)
            
class AgitationsWindow(Frame):
    def __init__(self, parent, controller):
        
        Frame.__init__(self, parent)
        self.controller = controller
        
        rowHeight = [43, 43, 133]

        #define quatro frames iniciais
        rowFrame1 = Frame (self, width=305, height=rowHeight[0])#, bg='cyan')
        rowFrame2 = Frame (self, width=305, height=rowHeight[1])#, bg='red')
        rowFrame3 = Frame (self, width=305, height=rowHeight[2])#, bg='green')
         
        patternsFrame = Frame(rowFrame3, width=181, height=rowHeight[2])
        buttonsFrame = Frame(rowFrame3, width=124, height=rowHeight[2])
        nameFrame = Frame(patternsFrame, width=181, height=rowHeight[1])
        pBoxFrame = Frame(patternsFrame, width=181, height=rowHeight[2]-rowHeight[1])

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
        buttonsFrame.grid_columnconfigure(1, weight=1)
        buttonsFrame.grid_rowconfigure(0, weight=1)
        buttonsFrame.grid_rowconfigure(1, weight=1)
        buttonsFrame.grid_rowconfigure(2, weight=1)
        #buttonsFrame.grid_rowconfigure(3, weight=1)
        
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
        
        labelsText = app.interfaceText["AgitationsWindow"]["Labels"]
        buttonsText = app.interfaceText["AgitationsWindow"]["Buttons"]
        
        durationLabel = Label(rowFrame1, text=labelsText["Duration"], font=titleFont)
        intervalLabel = Label(rowFrame1, text=labelsText["Interval"], font=titleFont)
        repetitionsLabel = Label(rowFrame2, text=labelsText["Repetitions"], font=titleFont)
        totalTimeLabel = Label(rowFrame2, text=labelsText["TotalTime"], font=titleFont)
        
        durationLabel.grid(row=0, column=0, sticky="news")
        intervalLabel.grid(row=0, column=1, sticky="news")
        repetitionsLabel.grid(row=0, column=0, sticky="news")
        totalTimeLabel.grid(row=0, column=1, sticky="news")
        
        buttonsFrame.grid(column=1, row=0, sticky="news")
        
        backButton = Button(buttonsFrame, text=buttonsText["Back"], height=1, \
                     width=1, command=lambda: controller.show_frame("NewAgitationCheck"))
        backButton.grid(row=2, column=1, sticky='news')
        saveButton = Button(buttonsFrame, text=buttonsText["Save"], height=1, \
                     width=1, command=lambda: self.save_data())
        saveButton.grid(row=1, column=1, sticky='news')
        self.continueButton = Button(buttonsFrame, text=buttonsText["Continue"], \
                     height=1, command=lambda: self.change_page())
        self.continueButton.grid(row=0, column=0, columnspan=2, sticky='news')
        self.deleteButton = Button(buttonsFrame, text=buttonsText["Delete"], height=1, \
                       width=1, command=lambda: self.confirm_delete(), state="disabled")
        self.deleteButton.grid(row=2, column=0, sticky='news')
        self.clearButton = Button(buttonsFrame, text=buttonsText["Clear"], height=1, \
                       width=1, command=lambda: self.clear_data())
        self.clearButton.grid(row=1, column=0, sticky='news')
        
        patternsFrame.grid(row=0, column=0, sticky="news")
        nameFrame.grid(row=0, column=0, sticky="news")
        pBoxFrame.grid(row=1, column=0, sticky="news")
        
        nameLabel = Label(nameFrame, text=labelsText["Name"], font=titleFont)
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
        #print(selection)
        self.agitation = listBox.get(selection)
        
        data = app.dataController.agitations[self.agitation]
        
        self.duration.set(data["duration"])
        self.interval.set(data["interval"])
        self.repetitions.set(data["repetitions"])
        self.totalTime.set(data["totalTime"])
        self.name.set(self.agitation)
        
        if len(selection) > 0:
            self.deleteButton.configure(state="normal")
            self.continueButton.configure(state="normal")
    
    def clear_data(self):
        self.duration.set("")
        self.name.set("")
        self.interval.set("")
        self.repetitions.set("")
        self.totalTime.set("")
        
        self.deleteButton.configure(state="disabled")
        #self.continueButton.configure(state="disabled")
    
    def load_data(self):
        self.controller.read_json("agitation")
    
    def confirm_delete(self):
        
        item = self.patternsBox.get(self.patternsBox.curselection())

        conflicts = app.dataController.check_dependencies(item)
                        
        if conflicts:
            errorText = [app.interfaceText["WarnWindow"]["Warns"]["AgitationDependency"]]
            errorText.extend(conflicts)
            errorText = " ".join(errorText)
            GUIWarningWindow(errorText, twoButton=False)
        else:
            
            warningText = app.interfaceText["WarnWindow"]["Warns"]["DeleteItem"]
                           
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
        
        self.deleteButton.configure(state="disabled")
        
        if warning is not None:
            warning.Destroy()
    
    def change_page(self):
        try:
            carryData = self.agitation
            self.controller.show_frame("RecipesWindow", carryData)
        except:
            self.controller.show_frame("RecipesWindow")
            
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
        
        buttonsText = app.interfaceText["NewAgitationCheck"]["Buttons"]
        
        rowFrame1.grid(column=0, row=0, sticky="news", pady=(7.5, 7.5), padx=7.5)
        
        backButton = Button(rowFrame1, text=buttonsText["Back"], height=1, \
                     command=lambda: self.controller.show_frame("MainPage"))
        backButton.grid(row=2, column=0, sticky='news')
        agitationButton = Button(rowFrame1, text=buttonsText["Agitations"], height=1, \
                     command=lambda: controller.show_frame("AgitationsWindow"))
        agitationButton.grid(row=0, column=0, sticky='news')
        recipeButton = Button(rowFrame1, text=buttonsText["Recipes"], height=1, \
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
         
        patternsFrame = Frame(rowFrame3, width=181, height=rowHeight[2])
        buttonsFrame = Frame(rowFrame3, width=124, height=rowHeight[2])
        agitationFrame = Frame(patternsFrame, width=181, height=rowHeight[1])
        pBoxFrame = Frame(patternsFrame, width=181, height=rowHeight[2]-rowHeight[1])

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
        buttonsFrame.grid_columnconfigure(1, weight=1)
        buttonsFrame.grid_rowconfigure(0, weight=1)
        buttonsFrame.grid_rowconfigure(1, weight=1)
        buttonsFrame.grid_rowconfigure(2, weight=1)
        #buttonsFrame.grid_rowconfigure(3, weight=1)
        
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
        self.nameEntry = Combobox(rowFrame2, textvar = self.name)#, values=list(controller.dataController.agitations.keys()))
        
        durationEntry.grid(row=1, column=0, sticky="news")
        tempEntry.grid(row=1, column=1, sticky="news")
        catEntry.grid(row=1, column=0, sticky="news")
        filmEntry.grid(row=1, column=1, sticky="news")
        self.nameEntry.grid(row=1, column=2, sticky="news")
        
        self.nameEntry.bind("<<ComboboxSelected>>", self.recipe_select)
        
        controller.dataController.add_widget(catEntry, "recipe", "categoryBox")
        controller.dataController.add_widget(filmEntry, "recipe", "filmBox")
        controller.dataController.add_widget(self.nameEntry, "recipe", "nameBox")
        
        labelsText = app.interfaceText["RecipesWindow"]["Labels"]
        buttonsText = app.interfaceText["RecipesWindow"]["Buttons"]
                
        durationLabel = Label(rowFrame1, text=labelsText["Duration"], font=titleFont)
        tempLabel = Label(rowFrame1, text=labelsText["Temperature"], font=titleFont)
        catLabel = Label(rowFrame2, text=labelsText["Category"], font=titleFont)
        filmLabel = Label(rowFrame2, text=labelsText["Film"], font=titleFont)
        nameLabel = Label(rowFrame2, text=labelsText["Name"], font=titleFont)
        
        durationLabel.grid(row=0, column=0, sticky="news")
        tempLabel.grid(row=0, column=1, sticky="news")
        catLabel.grid(row=0, column=0, sticky="news")
        filmLabel.grid(row=0, column=1, sticky="news")
        nameLabel.grid(row=0, column=2, sticky="news")
        
        buttonsFrame.grid(column=1, row=0, sticky="news")
        
        backButton = Button(buttonsFrame, text=buttonsText["Back"], height=1, \
                     width=1, command=lambda: controller.show_frame("NewAgitationCheck"))
        backButton.grid(row=2, column=1, sticky='news')
        saveButton = Button(buttonsFrame, text=buttonsText["Save"], height=1, \
                     width=1, command=lambda: self.save_data())
        saveButton.grid(row=1, column=1, sticky='news')
        self.continueButton = Button(buttonsFrame, text=buttonsText["Continue"], height=1, \
                              command=lambda: self.change_page(), state="normal")
        self.continueButton.grid(row=0, column=0, columnspan=2, sticky='news')
        self.deleteButton = Button(buttonsFrame, text=buttonsText["Delete"], height=1, \
                       width=1, command=lambda: self.delete_entry(), state="disabled")
        self.deleteButton.grid(row=2, column=0, sticky='news')
        self.clearButton = Button(buttonsFrame, text=buttonsText["Clear"], height=1, \
                       width=1, command=lambda: self.delete_entry())
        self.clearButton.grid(row=1, column=0, sticky='news')
        
        patternsFrame.grid(row=0, column=0, sticky="news", padx=(0,3))
        agitationFrame.grid(row=0, column=0, sticky="news")
        pBoxFrame.grid(row=1, column=0, sticky="news")
        
        agitationLabel = Label(agitationFrame, text=labelsText["Agitations"], font=titleFont)
        agitationLabel.grid(row=0, column=0, sticky="news")#, padx=(0,3))
        
        self.agitationEntry = Combobox(agitationFrame, \
                    values=list(controller.dataController.agitations.keys()))
        self.agitationEntry.bind("<<ComboboxSelected>>", self.add_pattern_to_recipe)
        self.agitationEntry.grid(row=1, column=0, sticky="news", padx=(1,0))
        
        controller.dataController.add_widget(self.agitationEntry, "agitation", "agitationBox")
        
        self.patternsBox = Listbox(pBoxFrame)
        self.patternsBox.grid(row=0, column=0, sticky="news")
        self.patternsBox.bind('<<ListboxSelect>>', self.agitation_select)

        controller.dataController.add_widget(self.patternsBox, "recipe", "agitationsBox")
            
        scrollbar = Scrollbar(pBoxFrame, width=73)
        scrollbar.grid(row=0, column=1, sticky="news", pady=1)
            
        self.patternsBox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.patternsBox.yview)
    
    def save_data(self, isUpdate=False, warning=None):
        newRecipe = {   
                        self.name.get(): {
                                    "category": self.cat.get(),
                                    "duration": self.duration.get(),
                                    "film": self.film.get(),
                                    "temperature": self.temp.get(),
                                    "agitations": list(self.patternsBox.get(0, END))
                                }
                    }
        if not isUpdate:
            if app.dataController.validate_data(newRecipe, "recipe", self):               
                app.dataController.add_recipe(newRecipe)
                app.dataController.update_widgets("recipe")
            
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
        
        self.patternsBox.delete(0, END)
        
        self.deleteButton.configure(state="disabled")
        #self.continueButton.configure(state="disabled")
        
        self.selection = ()
    
    def load_data(self):
        self.controller.read_json("recipe")
    
    def delete_entry(self, warning=None):
        if len(self.selection) == 0:
            print("No item selected!")
        else:
            for item in self.selection:
                self.patternsBox.delete(item)#self.patternsBox.get(0, "end").index(self.selection))
            
        #self.clear_data()
        self.deleteButton.configure(state="disabled")
        
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
                
        for agitation in data["agitations"]:
            #self.agitation.set(data["agitation"])
            self.patternsBox.insert(END, agitation)
                
        
        self.deleteButton.configure(state="normal")
        self.continueButton.configure(state="normal")
        
    def confirm_delete(self):
        warningText = app.interfaceText["WarnWindow"]["Warns"]["DeleteRecipe"]
                       
        warning = GUIWarningWindow(warningText)
        
        warning.yesButton.configure(command=lambda: self.delete_entry(warning))
        warning.noButton.configure(command=lambda: warning.Destroy())

    def add_pattern_to_recipe(self, event):
        chosenPattern = self.agitationEntry.get()
        self.agitationEntry.set("")
        self.patternsBox.insert(END, chosenPattern)

    def agitation_select(self, event):
        listBox = event.widget
        self.selection = listBox.curselection()
        
        if len(self.selection) > 0:
            self.deleteButton.configure(state="normal")

    def load_carry_data(self, carryData):
        if carryData in self.controller.dataController.agitations:
            self.patternsBox.delete(0, END)
            self.patternsBox.insert(END, carryData)
    
    def change_page(self):
        try:
            carryData = self.nameEntry.get()
            self.controller.show_frame("RunRecipe", carryData)
        except:
            self.controller.show_frame("RunRecipe")

class PreferencesPane(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        noteStyle = Style()
        noteStyle.theme_create( "NoteStyle", parent="alt", settings={
        "TNotebook.Tab": {"configure": {"padding": [5, 12, 5, 12] }}})
        
        noteStyle.theme_use("NoteStyle")
        
        rowHeight = [190, 40]
        rowWidth = 310
        
        entryFont = font.Font(size=20)
                
        noteFrame = Frame(self, height=rowHeight[0], width=rowWidth)
        buttonsFrame = Frame(self, height=rowHeight[1], width=rowWidth)
        
        buttonsFrame.grid_rowconfigure(0, weight=1)
        buttonsFrame.grid_columnconfigure(0, weight=1)
        buttonsFrame.grid_columnconfigure(1, weight=1)
        buttonsFrame.grid_columnconfigure(2, weight=1)
        
        noteFrame.grid_rowconfigure(0, weight=1)
        noteFrame.grid_columnconfigure(0, weight=1)

        buttonsFrame.grid_propagate(False)
        noteFrame.grid_propagate(False)
        
        noteFrame.grid(column=0, row=0, sticky="news", padx=5, pady=(5,0))
        buttonsFrame.grid(column=0, row=1, sticky="news", padx=5, pady=(0,5))
        
        backButton = Button(buttonsFrame, text="Cancel", width=1, \
                     command=lambda: controller.show_frame("MainPage"))
        backButton.grid(row=0, column=2, sticky='news')
        okButton = Button(buttonsFrame, text="Ok", width=1, \
                     command=lambda: self.save_prefs(True))
        okButton.grid(row=0, column=0, sticky='news')
        applyButton = Button(buttonsFrame, text="Apply", width=1, \
                     command=lambda: self.save_prefs())
        applyButton.grid(row=0, column=1, sticky='news')
        
        notebook = Notebook(noteFrame)
        
        tempFrame = Frame(notebook, width=rowWidth, height=rowHeight[0])
        scaleFrame = Frame(notebook, width=rowWidth, height=rowHeight[0])
        interfaceFrame = Frame(notebook, width=rowWidth, height=rowHeight[0])
        
        tempFrame.grid_propagate(False)
        scaleFrame.grid_propagate(False)
        interfaceFrame.grid_propagate(False)
        
        tempFrame.grid_rowconfigure(0, weight=1)
        tempFrame.grid_rowconfigure(1, weight=1)
        tempFrame.grid_columnconfigure(0, weight=1)
        tempFrame.grid_columnconfigure(1, weight=1)
        
        scaleFrame.grid_rowconfigure(0, weight=1)
        scaleFrame.grid_rowconfigure(1, weight=1)
        scaleFrame.grid_columnconfigure(0, weight=1)
        scaleFrame.grid_columnconfigure(1, weight=1)
        
        interfaceFrame.grid_rowconfigure(0, weight=1)
        interfaceFrame.grid_rowconfigure(1, weight=1)
        interfaceFrame.grid_columnconfigure(0, weight=1)
        interfaceFrame.grid_columnconfigure(1, weight=1)
        
        labelsText = app.interfaceText["PreferencesPane"]["Labels"]
        buttonsText = app.interfaceText["PreferencesPane"]["Buttons"]
        
        notebook.add(tempFrame, text=labelsText["TempFrame"], sticky="news")
        notebook.add(scaleFrame, text=labelsText["ScaleFrame"], sticky="news")
        notebook.add(interfaceFrame, text=labelsText["InterFrame"], sticky="news")
        
        notebook.grid(column=0, row=0, sticky="news")
        
        ## Temperature Unity Section ##
        
        tempUnitLabelFrame = Labelframe(tempFrame, text=labelsText["TempUnit"], borderwidth=2, relief="groove", width=(rowWidth)/2, height=(rowHeight[0]-3)/2)
        tempUnitLabelFrame.grid(column=0, row=0, sticky="news", padx=(2,1), pady=(2,1))
                
        self.isCelsius = BooleanVar()
        
        self.celsiusRadio = Radiobutton(tempUnitLabelFrame, text="Celsius\n[°C]", width=8, variable=self.isCelsius, value=True, padx=3, pady=3, indicatoron=0)
        self.fahrRadio = Radiobutton(tempUnitLabelFrame, text="Fahrenheit\n[°F]", width=8, variable=self.isCelsius, value=False, padx=3, pady=3, indicatoron=0)
        
        self.celsiusRadio.grid(column=0, row=0, sticky="news")
        self.fahrRadio.grid(column=1, row=0, sticky="news")
        
        self.tempDecimals = StringVar()
        
        tempPlacesLabelFrame = Labelframe(tempFrame, text=labelsText["TempDecimals"], borderwidth=2, relief="groove", width=(rowWidth-6)/2, height=(rowHeight[0]-3)/2)
        tempPlacesLabelFrame.grid(column=1, row=0, sticky="news", padx=(1,2), pady=(2,1))

        tempDecimalsEntry = Entry(tempPlacesLabelFrame, font=entryFont, width=8, textvar=self.tempDecimals, justify="right")
        tempDecimalsEntry.grid(column=0, row=0, sticky="news")
        
        tempPlacesLabelFrame.grid_propagate(False)
        tempUnitLabelFrame.grid_propagate(False)
        
        ## Weigh Scale Section ##
        
        scaleUnitLabelFrame = Labelframe(scaleFrame, text=labelsText["ScaleUnit"], borderwidth=2, relief="groove", width=(rowWidth)/2, height=(rowHeight[0]-3)/2)
        scaleUnitLabelFrame.grid(column=0, row=0, sticky="news", padx=(2,1), pady=(2,1))
                
        self.isMetric = BooleanVar()
        
        self.metricRadio = Radiobutton(scaleUnitLabelFrame, text=buttonsText["Metric"], width=8, variable=self.isMetric, value=True, padx=3, pady=3, indicatoron=0)
        self.imperialRadio = Radiobutton(scaleUnitLabelFrame, text=buttonsText["Imperial"], width=8, variable=self.isMetric, value=False, padx=3, pady=3, indicatoron=0)
        
        self.metricRadio.grid(column=0, row=0, sticky="news")
        self.imperialRadio.grid(column=1, row=0, sticky="news")
        
        scalePlacesLabelFrame = Labelframe(scaleFrame, text=labelsText["ScaleDecimals"], borderwidth=2, relief="groove", width=(rowWidth-6)/2, height=(rowHeight[0]-3)/2)
        scalePlacesLabelFrame.grid(column=1, row=0, sticky="news", padx=(1,2), pady=(2,1))

        self.scaleDecimals = StringVar()

        scaleDecimalsEntry = Entry(scalePlacesLabelFrame, font=entryFont, width=8, textvar=self.scaleDecimals, justify="right")
        scaleDecimalsEntry.grid(column=0, row=0, sticky="news")
        
        scaleReferenceLabelFrame = Labelframe(scaleFrame, text=labelsText["ScaleReference"], borderwidth=2, relief="groove", width=(rowWidth-4), height=(rowHeight[0]-3)/2)
        scaleReferenceLabelFrame.grid(column=0, row=1, sticky="news", columnspan=2, padx=2, pady=(1,2))
        
        self.referenceUnit = StringVar()
        
        scaleReferenceEntry = Entry(scaleReferenceLabelFrame, font=entryFont, width=10, textvar=self.referenceUnit, justify="right")
        scaleReferenceEntry.grid(column=0, row=0, sticky="news")
        
        calibrateScaleButton = Button(scaleReferenceLabelFrame, text=buttonsText["CalibrateScale"])#, \
                     #command=lambda: controller.show_frame("MainPage"))
        calibrateScaleButton.grid(row=0, column=1, sticky='news')
        
        scalePlacesLabelFrame.grid_propagate(False)
        scaleUnitLabelFrame.grid_propagate(False)
        scaleReferenceLabelFrame.grid_propagate(False)
        
        ## General Section ##
        
        languageLabelFrame = Labelframe(interfaceFrame, text=labelsText["Language"], borderwidth=2, relief="groove", width=(rowWidth-4), height=(rowHeight[0])/2)
        languageLabelFrame.grid(column=0, row=0, sticky="news", padx=(2,1), pady=(2,1))
        languageLabelFrame.grid_propagate(False)
                
        languageLabelFrame.option_add("*TCombobox*Listbox*Font", entryFont)
        languageLabelFrame.option_add("*TCombobox*Font", entryFont)
        
        self.languageBox = Combobox(languageLabelFrame, values=app.languages, width=16)
        self.languageBox.grid(column=0, row=0, sticky="news", padx=5)

        ## Finally, loads the preferences ##
        self.load_prefs()

    def load_prefs(self):
        
        scalePrefs = self.controller.config[self.controller.sections[0]]
        tempPrefs = self.controller.config[self.controller.sections[1]]
        generalPrefs = self.controller.config[self.controller.sections[2]]
        
        ## Parses temperature prefs
        self.tempDecimals.set(tempPrefs[self.controller.tempSubSections[1]])
        
        if tempPrefs[self.controller.tempSubSections[0]].lower() == "celsius":
            self.isCelsius.set(True)
            self.celsiusRadio.select()
        else:
            self.isCelsius.set(False)
            self.fahrRadio.select()
        
        ## Parses scale prefs
        self.referenceUnit.set(scalePrefs[self.controller.scaleSubSections[0]])
        self.scaleDecimals.set(scalePrefs[self.controller.scaleSubSections[1]])
        
        if scalePrefs[self.controller.scaleSubSections[2]].lower() == "metric":
            self.isMetric.set(True)
            self.metricRadio.select()
        else:
            self.isMetric.set(False)
            self.imperialRadio.select()
        
        ## Parses general prefs
        self.languageBox.set(generalPrefs[self.controller.interfaceSubSections[0]])

    def save_prefs(self, goBack=False):
        newConfig = {}
        config = configparser.ConfigParser(allow_no_value=True)
        
        scaleComments = "\n\
## decimalplaces: number of decimal places for scale readings.\n\
##                Must be an integer greater or equal to zero.\n\
##\n\
## referenceunit: users are highly disencouraged to change it manually.\n\
##                Do it at your own risk (might change scale readings).\n\
##                To re-calibrate at startup, leave it blank.\n\
##\n\
## weightunit: can be either metric (grams) or imperial (ounces)."
                         
        tempComments = "\n\
## decimalplaces: number of decimal places for temperature readings.\n\
##                 Must be an integer greater or equal to zero.\n\
##\n\
## temperatureunit can be either celsius or fahrenheit."
        
        interfaceComments = "\n\
## language: must be one of the available languages in supported_languages.conf.\n\
##           default language is en-US."
        
        scalePrefs = self.controller.sections[0]
        tempPrefs = self.controller.sections[1]
        interfacePrefs = self.controller.sections[2]
        
        newConfig.update({
                          scalePrefs: {},
                          tempPrefs: {},
                          interfacePrefs: {}
                         })
        
        ## Gets temperature prefs
        if self.isCelsius.get():
            tempUnit = "celsius"
        else:
            tempUnit = "fahrenheit"
            
        newConfig[tempPrefs].update({
                                        self.controller.tempSubSections[1]: self.tempDecimals.get(),
                                        self.controller.tempSubSections[0]: tempUnit
                                    })

        ## Gets scale prefs
        
        if self.isMetric.get():
            scaleUnit = "metric"
        else:
            scaleUnit = "imperial"
            
        newConfig[scalePrefs].update({
                                        self.controller.scaleSubSections[0]: self.referenceUnit.get(),
                                        self.controller.scaleSubSections[1]: self.scaleDecimals.get(),
                                        self.controller.scaleSubSections[2]: scaleUnit
                                     })
        
        ## Parses general prefs
        newConfig[interfacePrefs].update({self.controller.interfaceSubSections[0]: self.languageBox.get()})
                
        config.read_dict(newConfig)
        
        config.set(scalePrefs, scaleComments)
        config.set(tempPrefs, tempComments)
        config.set(interfacePrefs, interfaceComments)        
        
        self.controller.write_config(config)
        
        saveText = self.controller.interfaceText["PreferencesPane"]["Warns"]
        
        GUIWarningWindow(saveText["Done"], warningTitle=saveText["Title"], twoButton=False)
                
        if goBack:
            self.controller.show_frame("MainPage")

if __name__ == "__main__":
    app = PyLabApp()
    
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    if os.path.isfile(app.configFile):
        app.read_config()
        
    app.parse_language()
    
    app.setup_app() 
    
    app.check_files()
    app.build_app()
    
    if os.path.isfile(app.agitationFile):
        data = app.read_json("agitation")
        if data:
            app.dataController.import_data(data, "agitation")
            
    if os.path.isfile(app.recipesFile):
        data = app.read_json("recipe")
        if data:
            app.dataController.import_data(data, "recipe")

    #app.test_warnings()

    app.mainloop()

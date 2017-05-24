# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import font
from tkinter import messagebox

import pdb

scaleText = ["Ligar\nBalança", "Desligar\nBalança"]
scaleReadingText = "\n\n Leitura atual:\nMUITOS KGs"
onOffText = ["Turn\nOn", "Turn\nOff"]
runText = ["Run", "Running"]

class PyLabApp (Tk):

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

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.title("Layout Prototype")
        self.geometry("320x240")
        container = Frame(self)#, width=320, height=240)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        container.grid()

        self.frames = {}
        for F in (MainPage, GetTemperatures, SetTemperature, RunEditRecipe):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainPage")

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
            
        self.buttonToggle = not self.buttonToggle        

    def SetText(self, newText):
        self.buttonTextVar.set(newText)

    def GetText(self):
        return self.buttonTextVar.get()

    def GetButton(self):
        return self.button

class GUIWarningWindow:
    
    def __init__(self, warningText, warningTitle="Attention!"):                    
        self.warning = Tk()
        self.warning.title(warningTitle)
        self.warning.geometry("320x120+%d+%d" % (app.winfo_x(), app.winfo_y()+app.winfo_height()/5))
        self.warning.lift()
        self.warning.grid_columnconfigure(0, weight=1)
        self.warning.grid_rowconfigure(0, weight=1)
        self.warning.grid_rowconfigure(1, weight=1)
        
        self.buttonFrame = Frame(self.warning)
        self.buttonFrame.grid(row=1, column=0, sticky="news")
        self.buttonFrame.grid_columnconfigure(0, weight=1)
        self.buttonFrame.grid_columnconfigure(1, weight=1)
        self.buttonFrame.grid_rowconfigure(0, weight=1)
                    
        self.label = Label(self.warning, text=warningText,\
                width=220, font=font.Font(weight="bold", size=10))
        self.label.grid(row=0, column=0, sticky="news", padx=10, pady=10)
        self.yesButton = Button(self.buttonFrame, text="Yes")
        self.yesButton.grid(row=0, column=0, sticky="news")
        self.noButton = Button(self.buttonFrame, text="No")
        self.noButton.grid(row=0, column=1, sticky="news")
        
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
        newRecipeButton = Button(recipesFrame, text="Criar\nReceita", width=5)
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

        toggleTempButton1 = toggleTempButtonGUI1.GetButton()
        toggleTempButton2 = toggleTempButtonGUI2.GetButton()
        toggleTempButton3 = toggleTempButtonGUI3.GetButton()

        toggleTempButton1.grid(row=0, column=0, sticky='news')
        toggleTempButton2.grid(row=0, column=0, sticky='news')
        toggleTempButton3.grid(row=0, column=0, sticky='news')

        tempLabel1 = Label(tempFrame1, text="asd")
        tempLabel2 = Label(tempFrame2, text="asd")
        tempLabel3 = Label(tempFrame3, text="asd")

        tempLabel1.grid(row=0, column=1, columnspan=6, sticky='news')
        tempLabel2.grid(row=0, column=1, columnspan=6, sticky='news')
        tempLabel3.grid(row=0, column=1, columnspan=6, sticky='news')

        unitsLabel = Label(unitsFrame, text="Temp.\nUnit:")
        unitsLabel.grid(row=0,column=0, sticky="news")

        celsiusRadio = Radiobutton(unitsFrame, text="Celsius\n[°C]", width=6, variable=self.isCelsius, value=True, padx=3, pady=3, indicatoron=0)
        fahrRadio = Radiobutton(unitsFrame, text="Fahrenheit\n[°F]", width=6, variable=self.isCelsius, value=False, padx=3, pady=3, indicatoron=0)

        celsiusRadio.grid(row=0, column=1, sticky="news")
        fahrRadio.grid(row=0, column=2, sticky="news")

        celsiusRadio.select()

        backButton = Button(bottomFrame, text="Voltar", width=6, command=lambda: controller.show_frame("MainPage"))
        backButton.grid(row=0, column=1, sticky='news')

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

        #define quatro frames iniciais
        rowFrame1 = Frame (self, width=300, height=43)#, bg='cyan')
        rowFrame2 = Frame (self, width=300, height=86)#, bg='red')
        rowFrame3 = Frame (self, width=300, height=86)#, bg='green')
        sortFrame = Frame (rowFrame2, width=200, height=86, \
                           borderwidth=2, bg="black")
        filterFrame = Frame(rowFrame2, width=100, height=86)
        filmFrame = Frame(filterFrame, width=100, height=43)
        catFrame = Frame(filterFrame, width=100, height=43)
        recipeFrame = Frame(rowFrame1, width=300, height=43)
        sortButtonsFrame = Frame(sortFrame, width=200, height=73)

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
        catFrame.grid(row=0, column=0)#, pady=(2.25,7.5), padx=7.5)
        filmFrame.grid(row=1, column=0)#, pady=(2.25,7.5), padx=7.5)
        
        sortFrame.grid(row=0, column=1)#, pady=(2.25,7.5), padx=7.5)
        sortButtonsFrame.grid(row=1, column=0)#, pady=(2.25,7.5), padx=7.5)
        
        catLabel = Label(catFrame, text="Category:")
        filmLabel = Label(filmFrame, text="Film:")
        recipeLabel = Label(recipeFrame, text="Recipe:")
        sortLabel = Label(sortFrame, text="Sort Recipes:")
        
        catLabel.grid(row=0, column=0, sticky="news")
        filmLabel.grid(row=0, column=0, sticky="news")
        recipeLabel.grid(row=0, column=0, sticky="news")
        sortLabel.grid(row=0, column=0, sticky="news")
        
        categories = ["All", "B&W", "C41", "E6"]
        
        films = ["All", "Tri-X", "Velvia"]

        recipes = ["Caffenol Stand", "Pa-Rodinal 1:50", "Xtol 1:10"]

        catVar = StringVar()
        catVar.set(categories[0])
        filmVar = StringVar()
        filmVar.set(films[0])
        recipeVar = StringVar()
        recipeVar.set(recipes[0])

        catList = OptionMenu(catFrame, catVar, *categories)
        recipeList = OptionMenu(recipeFrame, recipeVar, *recipes)
        filmList = OptionMenu(filmFrame, filmVar, *films)
        
        catList.grid(row=1, column=0, sticky="ew")
        recipeList.grid(row=1, column=0, sticky="ew")
        filmList.grid(row=1, column=0, sticky="ew")
        
        backButton = Button(rowFrame3, text="Voltar", width=6, \
                     command=lambda: self.controller.show_frame("MainPage"))
        backButton.grid(row=0, column=2, sticky='news')
        runButton = Button(rowFrame3, text="Run Recipe", width=6)
        runButton.grid(row=0, column=0, sticky='news')
        editButton = Button(rowFrame3, text="Edit Recipe", width=6)
        editButton.grid(row=0, column=1, sticky='news')
        
        azButton = Button(sortButtonsFrame, text="A to Z", width=6)
        azButton.grid(row=0, column=0, sticky='nsew')
        zaButton = Button(sortButtonsFrame, text="Z to A", width=6)
        zaButton.grid(row=0, column=1, sticky='nsew')

if __name__ == "__main__":
    app = PyLabApp()
    app.mainloop()

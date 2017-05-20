# -*- coding: utf-8 -*-
from tkinter import *

scaleText = ["Ligar\nBalança", "Desligar\nBalança"]
scaleReadingText = "\n\n Leitura atual:\nMUITOS KGs"
onOffText = ["Turn\nOn", "Turn\nOff"]

class PyLabApp (Tk):

    def show_frame(self, page_name):
            '''Show a frame for the given page name'''
            frame = self.frames[page_name]
            frame.tkraise()

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
        for F in (MainPage, GetTemperatures):
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

    def SetParam(self, param, value):
        self.button[param]=value
        self.button.grid()

    def GetButton(self):
        return self.button

class MainPage(Frame):
 
    def ScaleButtonClick(self, button):
        if button.buttonToggle:
            button.ToggleText()
            buttonText = button.GetText()

            #ler sensor da balanca aqui

            button.SetParam("anchor", 'n')

            buttonText += scaleReadingText
            button.SetText(buttonText)
            
        else:
            button.ToggleText()
            button.SetParam("anchor", 'center')


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
        newRecipeButton = Button(recipesFrame, text="Editar\nReceita", width=5)
        useRecipeButton = Button(recipesFrame, text="Executar\nReceita", width=5)
        adjustTempButton = Button(temperatureFrame, text="Ajustar\nTemp.", width=5)
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

class PageTwo(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        label = Label(self, text="This is page 1")
        label.pack(side="top", fill="x", pady=10)
        button = Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("MainPage"))
        button1 = Button(self, text="Go to page two",
                           command=lambda: controller.show_frame("PageTwo"))
        button.pack()
        button1.pack()

if __name__ == "__main__":
    app = PyLabApp()
    app.mainloop()

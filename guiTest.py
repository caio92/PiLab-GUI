# -*- coding: utf-8 -*-
from tkinter import *

scaleText = ["Ligar\nBalança", "Desligar\nBalança"]
scaleReadingText = "\n\n Leitura atual:\nMUITOS KGs"

class PyLabApp (Tk):

    def show_frame(self, page_name):
            '''Show a frame for the given page name'''
            frame = self.frames[page_name]
            frame.tkraise()

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        container = Frame(self, width=320, height=240)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        container.grid()

        self.frames = {}
        for F in (MainPage, PageOne, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainPage")

class GUIButton:
    def __init__(self, tkButton, buttonType, buttonTextVar):
        self.button = tkButton
        self.buttonTextVar = buttonTextVar
        self.buttonToggle = True
        self.buttonType = buttonType

        if buttonType == "scale":
            self.buttonText = scaleText

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
    
    #root = Tk()
    #root.title('Layout Prototype')
    #root.geometry("320x240")

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        #define quatro frames iniciais
        self.scaleFrame = Frame (self, width=150, height=110)#, bg='cyan')
        self.recipesFrame = Frame (self, width=150, height=110)#, bg='red')
        self.temperatureFrame = Frame (self, width=150, height=110)#, bg='green')
        self.allFrame = Frame (self, width=150, height=110)#, bg='yellow')

        #configura comportamento dos frames
        self.grid_rowconfigure( 1, weight=1)
        self.grid_columnconfigure( 1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.scaleFrame.grid_rowconfigure( 0, weight=1)
        self.scaleFrame.grid_columnconfigure( 0, weight=1)
        self.temperatureFrame.grid_rowconfigure( 0, weight=1)
        self.temperatureFrame.grid_columnconfigure( 1, weight=1)
        self.temperatureFrame.grid_columnconfigure( 0, weight=1)
        self.allFrame.grid_rowconfigure( 0, weight=1)
        self.allFrame.grid_columnconfigure( 0, weight=1)
        self.recipesFrame.grid_columnconfigure( 0, weight=1)
        self.recipesFrame.grid_columnconfigure( 1, weight=1)
        self.recipesFrame.grid_rowconfigure( 0, weight=1)

        #coloca as frames no GRID
        self.scaleFrame.grid(row=0, column=0, pady=(7.5,2.5), padx=(7.5,2.5))
        self.recipesFrame.grid(row=0, column=1, pady=(7.5,2.5), padx=(2.5,7.5))
        self.temperatureFrame.grid(row=1, column=0, pady=(2.5,7.5), padx=(7.5,2.5))
        self.allFrame.grid(row=1, column=1, pady=(2.5,7.5), padx=(2.5,7.5))

        #configura variaveis de texto dos botoes
        self.scaleTextVar = StringVar()

        #declara os botoes dos frames
        self.scaleButton = Button(self.scaleFrame, textvariable=self.scaleTextVar, command=lambda: self.ScaleButtonClick(self.scaleButtonGUI), height=7, width=16)
        self.newRecipeButton = Button(self.recipesFrame, height=7, width=6, text="Editar\nReceita")
        self.useRecipeButton = Button(self.recipesFrame, height=7, width=6, text="Executar\nReceita")
        self.adjustTempButton = Button(self.temperatureFrame, height=7, width=6, text="Ajustar\nTemp.")
        self.measureTempButton = Button(self.temperatureFrame, height=7, width=6, text="Medir\nTemp.")
        self.allButton = Button(self.allFrame, height=7, width=16, text="Rotina Completa")

        #coloca os botoes no grid do frame
        self.newRecipeButton.grid(column=0, row=0, sticky=N+S+E+W)
        self.useRecipeButton.grid(column=1, row=0, sticky=N+S+E+W)
        self.scaleButton.grid(sticky=N+S+E+W)
        self.adjustTempButton.grid(column=0, row=0, sticky=N+S+E+W)
        self.measureTempButton.grid(column=1, row=0, sticky=N+S+E+W)
        self.allButton.grid(sticky=N+S+E+W)

        #cria estrutura de dados dos botoes
        self.scaleButtonGUI = GUIButton(self.scaleButton, "scale", self.scaleTextVar)

class PageOne(Frame):

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

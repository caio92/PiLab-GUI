from tkinter import *

#class Application:
#    def __init__(self, master=None):


scaleText = ["Ligar\nBalança", "Desligar\nBalança"]


class GUIButton:
    def __init__(self, tkButton, buttonType):
        self.button = tkButton
        self.labelTextVar = StringVar()
        self.buttonLabel = Label(tkButton, textvariable=self.labelTextVar)
        self.buttonLabel.pack(fill=BOTH, expand=1)
        self.buttonToggle = True
        self.buttonType = buttonType

        if buttonType == "scale":
            self.buttonText = scaleText

        self.labelTextVar.set(self.buttonText[0])

    def ToggleText(self):
        if self.buttonToggle:
            self.labelTextVar.set(self.buttonText[1])
        else:
            self.labelTextVar.set(self.buttonText[0])
            
        self.buttonToggle = not self.buttonToggle        

    def SetText(self, newText):
        self.labelTextVar.set(newText)

    def GetText(self):
        self.labelTextVar.get()
        

def ScaleButtonClick(button):
    if button.buttonToggle:
        button.ToggleText()
        buttonText = button.GetText()

        #ler sensor da balanca aqui
        
    else:
        button.ToggleText()


def UpdateScale(button):
    #funcao que faz a leitura do sensor aqui!!
    pass   

root = Tk()
root.title('Layout Prototype')
root.geometry("320x240")

#define quatro frames iniciais
scaleFrame = Frame (root, width=150, height=110)#, bg='cyan')
recipesFrame = Frame (root, width=150, height=110)#, bg='red')
temperatureFrame = Frame (root, width=150, height=110)#, bg='green')
allFrame = Frame (root, width=150, height=110)#, bg='yellow')

#configura comportamento dos frames
root.grid_rowconfigure( 1, weight=1)
root.grid_columnconfigure( 1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)


scaleFrame.grid_rowconfigure( 0, weight=1)
scaleFrame.grid_columnconfigure( 0, weight=1)
temperatureFrame.grid_rowconfigure( 0, weight=1)
temperatureFrame.grid_columnconfigure( 1, weight=1)
temperatureFrame.grid_columnconfigure( 0, weight=1)
allFrame.grid_rowconfigure( 0, weight=1)
allFrame.grid_columnconfigure( 0, weight=1)
recipesFrame.grid_columnconfigure( 0, weight=1)
recipesFrame.grid_columnconfigure( 1, weight=1)
recipesFrame.grid_rowconfigure( 0, weight=1)

#coloca as frames no GRID
scaleFrame.grid(row=0, column=0, pady=(7.5,2.5), padx=(7.5,2.5))
recipesFrame.grid(row=0, column=1, pady=(7.5,2.5), padx=(2.5,7.5))
temperatureFrame.grid(row=1, column=0, pady=(2.5,7.5), padx=(7.5,2.5))
allFrame.grid(row=1, column=1, pady=(2.5,7.5), padx=(2.5,7.5))

#declara os botoes dos frames
scaleButton = Button(scaleFrame, command= lambda: ScaleButtonClick(scaleButtonGUI), height=7, width=16)
newRecipeButton = Button(recipesFrame, height=7, width=6, text="Editar\nReceita")
useRecipeButton = Button(recipesFrame, height=7, width=6, text="Executar\nReceita")
adjustTempButton = Button(temperatureFrame, height=7, width=6, text="Ajustar\nTemp.")
measureTempButton = Button(temperatureFrame, height=7, width=6, text="Medir\nTemp.")
allButton = Button(allFrame, height=7, width=16, text="Rotina Completa")

#coloca os botoes no grid do frame
newRecipeButton.grid(column=0, row=0, sticky=N+S+E+W)
useRecipeButton.grid(column=1, row=0, sticky=N+S+E+W)
scaleButton.grid(sticky=N+S+E+W)
adjustTempButton.grid(column=0, row=0, sticky=N+S+E+W)
measureTempButton.grid(column=1, row=0, sticky=N+S+E+W)
allButton.grid(sticky=N+S+E+W)

#cria estrutura de dados dos botoes
scaleButtonGUI = GUIButton(scaleButton, "scale")

root.mainloop()

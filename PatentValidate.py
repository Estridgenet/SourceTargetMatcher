import Validator
import tkinter
from tkinter import filedialog
import webbrowser  # will open text editor despite name
import BatchProcess


# TODO: FIX THIS TERRIBLE THING


root = tkinter.Tk()
root.title("Patent Validator")
root.geometry("600x300")

baseFrame = tkinter.Frame(width=600, height=300)
baseFrame.grid(column=0,row=0,columnspan=4,rowspan=4)
# Create Greeting top Frame
topFrame = tkinter.Frame(baseFrame)
topFrame.grid(row=0, column=0, columnspan=4)

greeting = tkinter.Label(topFrame, text="Patent Validation Tool\nBy Eli Estridge")
greeting.grid(row=0, sticky="n")

# Create L-hand single file processing frame and subsidiary buttons
######################################################################
fromFileFrame = tkinter.Frame(baseFrame, width=300, height=300)
fromFileFrame.grid(row=0, column=0, rowspan=4, columnspan=2)


def openFile():
    k = filedialog.askopenfilename()


entry1 = tkinter.Label(fromFileFrame, text="Terms File:")
entry2 = tkinter.Label(fromFileFrame, text="XLF File:")


# To save the terms file and update the GUI
termsfile = ""


def openTerms():
    global termsfile
    termsfile = filedialog.askopenfilename()
    entry1.config(text=termsfile)


# To save the file path and update the GUI
xlfFile = ""


def openFile():
    global xlfFile
    xlfFile = filedialog.askopenfilename()
    entry2.config(text=xlfFile)


button1 = tkinter.Button(fromFileFrame, text="Import Terms", command=openTerms)

button2 = tkinter.Button(fromFileFrame, text="Import SDLXLF", command=openFile)


def startFileValidate():
    print("Using this as terms file:%s" % termsfile)
    print("Using this as source document:%s" % xlfFile)
    if termsfile != "" and xlfFile != "":
        Validator.main(termsfile, xlfFile)

        root.destroy()


button3 = tkinter.Button(
    fromFileFrame, text="Start Individual Validation", command=startFileValidate
)
button1.grid(row=1, column=0)
button2.grid(row=1, column=1)
entry1.grid(row=2, column=0)
entry2.grid(row=3, column=0)
button3.grid(row=4, column=0, columnspan=2)


######################################################################


######################################################################
# Create R-hand Batch frame

batchFrame = tkinter.Frame(baseFrame,width=300,height=300)
batchFrame.grid(row=0, column=2, rowspan=4, columnspan=2)
entry3 = tkinter.Label(batchFrame, text="Project directory: ")

dirpath = ""


def openDirectory():
    """opens the root directory of a projects folder"""
    global dirpath
    dirpath = filedialog.askdirectory()
    entry3.config(text=dirpath)


def runBatchProcess():
    if dirpath != "":
        print("Looking through %s" % dirpath)
        for termBase, xlfFile in BatchProcess.walkShallowDir(dirpath):
            Validator.main(termBase, xlfFile)
        root.destroy()


button4 = tkinter.Button(batchFrame, text="Batch Process", command=openDirectory)
entry4 = tkinter.Label(batchFrame)
button5 = tkinter.Button(
    batchFrame, text="Start Batch Validation", command=runBatchProcess
)

button4.grid(row=1, column=0, columnspan=2)
entry3.grid(row=2)
entry4.grid(row=3)
button5.grid(row=4, column=0, columnspan=2)

######################################################################

root.mainloop()

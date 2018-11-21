import json
from tkinter import messagebox
import utility
import tkinter as tk

class RawDataParserGui(tk.Frame):
	pass

class RawDataParser:
    pass

class JSONParser:

	@classmethod
	def loadJSONFile(cls, file):
		""" Reads the JSON data from a file into memory and returns it as a dictionary """
		# TODO: Do I need these error checkings?
		try:
			if file == '':
				raise AttributeError
		except AttributeError:
			messagebox.showinfo("Error", "Keine Datei ausgewählt.")
			return
		except FileNotFoundError:
			messagebox.showinfo("Error", "Die Datei konnte nicht gefunden werden")
			return
		except Exception as e:
			raise e

		with open(file, "r") as file_obj:
			dataDict = json.load(file_obj)

		return dataDict

	@classmethod
	def writeJSONFile(cls, outFile, dataDict):
		""" write a data dictionary to the output file as JSON """

		with open(outFile, "w") as f:
			json.dump(dataDict, f)

# TODO: Refactor class Parser

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import progressBar
import json
import utility

class Parser(tk.Frame):
	def __init__(self, master=None, mainApp=None):
		super().__init__(master)

		self.mainApp = mainApp

		self.grid()
		self.master.minsize(500, 300)
		self.master.title("Parser data logger")

		self.createGui()

	def close(self):
		self.master.destroy()
		self.mainApp.parser = None

	def createGui(self):
		""" Menu bar """
		self.menubar = tk.Menu(self)
		self.master.config(menu=self.menubar)

		self.filemenu = tk.Menu(self.menubar, tearoff=0)
		self.filemenu.add_command(label="Beenden", command=self.master.destroy)
		self.menubar.add_cascade(label="Datei", menu=self.filemenu)

		""" Frames """
		self.parserFrame = tk.LabelFrame(master=self, text="Daten einlesen", borderwidth=1,
                                   relief="sunken", width=500, height=300, padx=5, pady=5)
		self.parserFrame.grid(column=0, row=10)

		self.statusFrame = tk.Frame(master=self, borderwidth=1, padx=5, pady=5)
		self.statusFrame.grid(column=0, row=5)

		self.previewFrame = tk.Frame(master=self.parserFrame, borderwidth=1, padx=5, pady=5)
		self.previewFrame.grid(column=10, row=2)

		""" Loading bar """
		self.loadBar = progressBar.SimpleProgressBar(self.statusFrame)

		""" Buttons and Labels """
		self.openLoggerFileButton = tk.Button(self.parserFrame, text="Rohdatei öffnen",
                                        command=self.loadLoggerFile)
		self.openLoggerFileButton.grid(row=1, column=5, sticky="ew")

		self.openLoggerFileLabel = tk.Label(self.parserFrame, text="", borderwidth=0,
                                      width=40)
		self.openLoggerFileLabel.grid(row=1, column=10, sticky="w")

		self.parseLoggerFileButton = tk.Button(self.parserFrame, text="Rohdaten parsen",
                                         command=self.parseLoggerFile)
		self.parseLoggerFileButton.grid(row=2, column=5, sticky="new")

		self.jsonFileLabel = tk.Label(
			self.parserFrame, text="", borderwidth=0, width=40)
		self.jsonFileLabel.grid(row=5, column=10, columnspan=3, sticky="w")

	def loadFilePreview(self):
		self.loadPreviewValues()

		# info text
		tk.Label(self.previewFrame, text="Bitte die Spalten zum Parsen auwählen:", fg="red", borderwidth=0
           ).grid(row=1, column=1, columnspan=6, sticky="w", padx=3)

		# preview checkbuttons and headline
		self.columnSelectionVars = []
		for i in range(6):
			self.columnSelectionVars.append(tk.IntVar())
			tk.Checkbutton(
				self.previewFrame, 
				text="", 
				variable=self.columnSelectionVars[i],
                onvalue=1, 
				offvalue=0
            ).grid(row=3, column=i+2)

			tk.Label(self.previewFrame, text="U_" + str(i), borderwidth=0).grid(row=4, column=i+2, sticky="ew", padx=3)

		# preview values
		i = 0
		for date, data in self.U_preview.items():
			tk.Label(self.previewFrame, text=date[-13:-4], borderwidth=0, width=8).grid(row=5+i, column=1, sticky="ew")
			for j in range(len(data)):
				tk.Label(
					self.previewFrame,
					text=str(data[j]) + " V",
					borderwidth=0,
					width=7
				).grid(row=5+i, column=2+j, sticky="ew")
			i += 1
		tk.Label(self.previewFrame, text="...", borderwidth=0, width=3).grid(row=5+i, column=4, sticky="e")
		

	def loadLoggerFile(self):
		import os
		if not os.path.isdir("files"):
			initialDir = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
		else:
			initialDir = "files"

		# open the file dialog
		selectedFile = filedialog.askopenfilename(initialdir=initialDir, title="Select file",
                                            	  filetypes=(("txt files", "*.txt"), ("all files", "*.*")), parent=self)
		# check if a file was read in
		if selectedFile == '':  # file dialog was canceled
			return
		else:
			self.loggerFile = selectedFile

		# find the substring indicating the filename without the path
		label = utility.getFilenameSubstr(self.loggerFile)

		# set the file Label showing the selected file with the previously found substring
		try:
			self.openLoggerFileLabel['text'] = label
		except UnboundLocalError:
			raise e
		except Exception as e:
			raise e

		self.loadFilePreview()

	def parseLoggerFile(self):

		try:
			outFile = utility.FILES_LOCATION + "\\" + \
				utility.getFilenameSubstr(self.loggerFile[:-4] + '_PYOUTPUT.json')
			self.read_datalogger(self.loggerFile, outFile)
			self.jsonFileLabel['text'] = utility.getFilenameSubstr(outFile)
		except Exception as e:
			messagebox.showinfo(
				"Error", "Bitte zuerst eine Datei zum Parsen auswählen.", parent=self)
			print(e)

		self.setToLoad = tk.Button(self.parserFrame, text="|-> Zur Datenverarbeitung laden",
                             command=lambda: self.passToMainApp(outFile))
		self.setToLoad.grid(row=20, column=10, sticky="ew")
		tk.Label(self.parserFrame, text="(Schließt den Parser)",
		         fg="red").grid(row=21, column=10, sticky="ew")

	def passToMainApp(self, outFile):
		# TODO: Make sure the parsed file isn't the same as the currently loaded file
		self.mainApp.setFileToLoad(outFile, False)
		self.close()

	def loadPreviewValues(self):
		""" Loads the first three rows of the selected file"""

		self.U_preview = dict()
		self.t_preview = []

		with open(self.loggerFile, 'r') as file_obj:
			for i, line in enumerate(file_obj):

				if line[0] == ";":
					continue
				if i > 20:
					break

				newU = [None for x in range(6)]
				try:
					_date, _, newU[0], newU[1], newU[2], newU[3], newU[4], newU[5] = line.replace("\n", "").split("	")
				except ValueError as e:
					messagebox.showinfo("Error", "Beim Parsen der Datei ist ein Fehler aufgetreten.\nBitte sicherstellen, dass die richtige Datei ausgewählt wurde!\n\nDieser Fehler kann insbesondere auftreten, wenn eine von diesem Programm als Output generierte Datei versucht wird zu parsen.")
				except Exception as e:
					messagebox.showinfo("Error", "Beim Parsen der Datei ist ein Fehler aufgetreten.\nBitte die Datei auf fehlerhafte Zeilen überprüfen.\n\nIn jeder Zeile müssen 8 mit Tabstopp getrennte Werte stehen.\n(Mit ';' beginnende Zeilen werden ignoriert.)")
					raise e

				self.U_preview[_date] = newU

	def read_datalogger(self, inFile, outFile):

		num_lines = utility.file_len(inFile)
		# columns to parse are 1, the others 0
		parseColumns = [a.get() for a in self.columnSelectionVars]
		U = {"TimeStamps": list(), "DataColumns": dict(), "TimeDefinitions": dict()}
		U["DataColumns"] = {"Spalte"+str(i): {"data": list(), "Unit": "V", "convFunc": {"x1": 0, "x2": 1, "y1": 0, "y2": 1}} 
							for i in range(sum(parseColumns))}  # dictionary to store

		# open input file and parse it
		with open(inFile, "r") as file_obj:
			for progress, line in enumerate(file_obj):

				if line[0] == ";":
					continue

				newU = [None for x in range(6)]
				try:
					_date, _, newU[0], newU[1], newU[2], newU[3], newU[4], newU[5] = line.replace("\n", "").split("	")
				except ValueError as e:
					messagebox.showinfo("Error", "Beim Parsen der Datei ist ein Fehler aufgetreten.\nBitte sicherstellen, dass die richtige Datei ausgewählt wurde!\n\nDieser Fehler kann insbesondere auftreten, wenn eine von diesem Programm als Output generierte Datei versucht wird zu parsen.")
				except Exception as e:
					messagebox.showinfo("Error", "Beim Parsen der Datei ist ein Fehler aufgetreten.\nBitte die Datei auf fehlerhafte Zeilen überprüfen.\n\nIn jeder Zeile müssen 8 mit Tabstopp getrennte Werte stehen.\n(Mit ';' beginnende Zeilen werden ignoriert.)")
					raise e

				U["TimeStamps"].append(_date)

				col = 0
				for k, val in enumerate(newU):
					if parseColumns[k] == 1:
						U["DataColumns"]["Spalte"+str(col)]["data"].append(val.replace(",", "."))
						col += 1

				# update progress bar
				self.loadBar.update(progress, num_lines, msg="(Parsing Data)")

			# loop finished, fill progress bar except last %
			self.loadBar.update(99, 100, msg="(Saving Data)")

		# write the dictionary to the output file as JSON
		with open(outFile, "w") as outFile_obj:
			json.dump(U, outFile_obj)

		# output file written, fill progress bar
		self.loadBar.update(1, 1, msg="(Idle)")

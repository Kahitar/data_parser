#from tqdm import tqdm
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import time
import json

FILES_LOCATION = os.getenv('APPDATA') + "\\data_logger"
if not os.path.isdir(FILES_LOCATION):
	os.mkdir(FILES_LOCATION)

def timeit(method):
	""" This function can be used as a decorator to measure a functions execution time """
	def timed(*args, **kw):
		ts = time.time()
		result = method(*args, **kw)
		te = time.time()
		if 'log_time' in kw:
			name = kw.get('log_name', method.__name__.upper())
			kw['log_time'][name] = int((te - ts) * 1000)
		else:
			dt = (te - ts)
			if dt > 1:
				print('%r  %2.2f s' % (method.__name__, dt))
			else:
				print('%r  %2.2f ms' % (method.__name__, dt * 1000))
		return result
	return timed

def main():
	root = tk.Tk()
	app = Application(master=root)
	app.mainloop()

def findFilenameSubstr(filename):
		# find the substring indicating the filename without the path
		counter = len(filename) # counter to count the chars of the new directory or file
		for i, char in enumerate(filename):
			if char == '/' or char == '\\': # start counting the chars from zero
				counter = 0
			elif char == '.': # the substring for the filename was found.
				return filename[i-counter:i+4] # add everything from the last '/' to the substring
			else:
				counter += 1

class DataConfiguratorRow(tk.Frame):
	def __init__(self, master, isHeadline=False, rowNumber=0):
		super().__init__(master)

		# headline
		if isHeadline:
			tk.Label(self, text="Spalte").grid(row=1, column=1, sticky="ew", padx=3, pady=3)
			tk.Label(self, text="Name").grid(row=1, column=3, sticky="ew", padx=3, pady=3)
			tk.Label(self, text="Umrechnung").grid(row=1, column=5, columnspan=3, sticky="ew", padx=3, pady=3)
			tk.Label(self, text="Einheit").grid(row=1, column=8, sticky="ew", padx=3, pady=3)

		# row number label
		tk.Label(self, text=str(rowNumber)).grid(row=2, column=1, padx=20, pady=3)

		# name field
		self.nameField = tk.Entry(self)
		self.nameField.grid(row=2, column=3, padx=3, pady=3)

		# conversion Fields
		self.x1 = tk.Entry(self, width=4, justify="center")
		self.x1.grid(row=2, column=5, sticky="w", padx=3, pady=3)
		tk.Label(self, text="V = ").grid(row=2, column=6, sticky="w", pady=5)
		self.y1 = tk.Entry(self, width=4, justify="center")
		self.y1.grid(row=2, column=7, sticky="w", padx=3, pady=3)

		self.x2 = tk.Entry(self, width=4, justify="center")
		self.x2.grid(row=3, column=5, sticky="w", padx=3, pady=3)
		tk.Label(self, text="V =").grid(row=3, column=6, sticky="w", pady=5)
		self.y2 = tk.Entry(self, width=4, justify="center")
		self.y2.grid(row=3, column=7, sticky="w", padx=3, pady=3)
		self.y2_UnitLabel = tk.Label(self, text="V")
		self.y2_UnitLabel.grid(row=3, column=8, sticky="w", pady=5)

		self.Unit_y1 = tk.StringVar(self, value='V')
		tk.OptionMenu(self, self.Unit_y1, *('V', 'bar', '°C')).grid(row=2, column=8, sticky="w", pady=5)

		self.Unit_y1.trace("w", self.setConversionUnit)

	def setConversionUnit(self, *args):
		self.y2_UnitLabel['text'] = self.Unit_y1.get()

	def getConversionFunctionParams(self):
		""" Returns the conversion parameters for the data entered 
		Conversion function: y = y1 + (x-x1)*((y1-y2)/(x1-x2))"""
		try:
			x1 = int(self.x1.get())
			x2 = int(self.x2.get())
			y1 = int(self.y1.get())
			y2 = int(self.y2.get())
			return {"x1": x1, "x2": x2, "y1": y1, "y2": y2}
		except tk._tkinter.TclError:
			# This error occures when closing the app if the DataConfigurator 
			# was previously opened but closed before the app is closed.  
			pass
		except ValueError:
			print("Setting standard conversion values because: ")
			return {"x1": 0, "x2": 1, "y1": 0, "y2": 1}
		except Exception as e:
			raise e

	def setConversionFunctionParams(self, conversionDict):
		self.x1.delete(0, len(self.x1.get()))
		self.x2.delete(0, len(self.x2.get()))
		self.y1.delete(0, len(self.y1.get()))
		self.y2.delete(0, len(self.y2.get()))

		self.x1.insert(0, conversionDict["x1"])
		self.x2.insert(0, conversionDict["x2"])
		self.y1.insert(0, conversionDict["y1"])
		self.y2.insert(0, conversionDict["y2"])

class DataConfigurator(tk.Frame):
	def __init__(self, master=None, mainApp=None):
		super().__init__(master)
		master.protocol("WM_DELETE_WINDOW", self.close)

		self.mainApp = mainApp

		self.grid()
		self.master.minsize(500, 300)
		self.master.title("Daten konfigurieren")

		self.createGui()

	def createGui(self):

		""" Menu bar """
		self.menubar = tk.Menu(self)

		self.filemenu = tk.Menu(self.menubar, tearoff=0)
		self.filemenu.add_command(label="Beenden", command=self.close)

		self.master.config(menu=self.menubar)
		self.menubar.add_cascade(label="Datei", menu=self.filemenu)

		""" Frames """
		self.configColsFrame = tk.LabelFrame(master=self, text="Spalten konfigurieren", borderwidth=1,
									relief="sunken", width=500, height=400, padx=5, pady=15)
		self.configColsFrame.grid(column=0, row=10, rowspan=2)

		""" Data configurator rows """
		self.setConversionData()

	def setConversionData(self):
		self.DataConfiguratorRows = []
		headline = True
		for i in range(len(self.mainApp.dataDict)):
			# data configurator rows
			self.DataConfiguratorRows.append(DataConfiguratorRow(
				self.configColsFrame, isHeadline=headline, rowNumber=i))
			headline = False
			self.DataConfiguratorRows[i].grid(
				row=2*i+5, column=2, padx=3, pady=3, columnspan=5)

			try:
				self.DataConfiguratorRows[i].setConversionFunctionParams(
					self.mainApp.dataDict["Spalte"+str(i)]["convFunc"])
			# TODO: Why do sometimes get a typeError instead of a keyError? (NoneType object is not subscriptable)
			except TypeError:
				self.DataConfiguratorRows[i].setConversionFunctionParams(
					{"x1": 0, "x2": 1, "y1": 0, "y2": 1})
			except KeyError:
				self.DataConfiguratorRows[i].setConversionFunctionParams(
					{"x1": 0, "x2": 1, "y1": 0, "y2": 1})
			except Exception as e:
				raise e

			try:
				self.DataConfiguratorRows[i].nameField.delete(
					0, len(self.DataConfiguratorRows))
				self.DataConfiguratorRows[i].nameField.insert(
					0, self.mainApp.dataDict["Spalte"+str(i)]["name"])
			except KeyError:
				self.DataConfiguratorRows[i].nameField.insert(0, "Spalte"+str(i))
			except Exception as e:
				raise e

			try:
				self.DataConfiguratorRows[i].Unit_y1.set(
					self.mainApp.dataDict["Spalte"+str(i)]["Unit"])
			except KeyError:
				self.DataConfiguratorRows[i].Unit_y1.set("V")
			except Exception as e:
				raise e

	def close(self):
		self.safeConfigData()
		self.master.destroy()
		#self.mainApp.dataConfigurator = None # TODO: Why is this not working?

	def safeConfigData(self):
		i = 0
		for _, value in self.mainApp.dataDict.items():
			value["convFunc"] = self.DataConfiguratorRows[i].getConversionFunctionParams()
			value["name"] = self.DataConfiguratorRows[i].nameField.get()
			value["Unit"] = self.DataConfiguratorRows[i].Unit_y1.get()
			i += 1

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
		#self.mainApp.parser = None # TODO: Why is this not working?

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
		self.parserFrame.grid_propagate(False)

		self.statusFrame = tk.Frame(master=self, borderwidth=1, padx=5, pady=5)
		self.statusFrame.grid(column=0, row=5)

		self.previewFrame = tk.Frame(master=self.parserFrame, borderwidth=1, padx=5, pady=5)
		self.previewFrame.grid(column=10, row=2)

		""" Loading bar """
		self.loadBar = SimpleProgressBar(self.statusFrame)

		""" Buttons and Labels """
		self.openLoggerFileButton = tk.Button(self.parserFrame, text="Rohdatei öffnen",
											command=self.loadLoggerFile)
		self.openLoggerFileButton.grid(row=1, column=5, sticky="ew")

		self.openLoggerFileLabel = tk.Label(self.parserFrame, text="", borderwidth=0, 
											width=40)
		self.openLoggerFileLabel.grid(row=1, column=10, sticky="w")

		self.parseLoggerFileButton = tk.Button(self.parserFrame, text="Rohdaten parsen",
												command=self.parseLoggerFile)
		self.parseLoggerFileButton.grid(row=5, column=5, sticky="ew")

		self.loggerFileLabel = tk.Label(self.parserFrame, text="", borderwidth=0, width=40)
		self.loggerFileLabel.grid(row=5, column=10, columnspan=3, sticky="w")

	def loadFilePreview(self):
		self.loadPreviewValues()

		""" preview selection """
		tk.Label(self.previewFrame, text="Bitte die Spalten zum Parsen auwählen:", fg="red", borderwidth=0
					).grid(row=1, column=1, columnspan=6, sticky="w", padx=3)

		# preview Zeiten
		for i in range(3):
			tk.Label(self.previewFrame, text=str(i+1) + ".", borderwidth=0, width=3
					).grid(row=5+i, column=1, sticky="ew")
		ttk.Label(self.previewFrame, text="...", borderwidth=0, width=3
				).grid(row=8, column=4, sticky="e")

		# preview checkbuttons and values
		self.columnSelectionVars = []
		for i in range(6):
			self.columnSelectionVars.append(tk.IntVar())
			tk.Checkbutton(self.previewFrame, text="", variable=self.columnSelectionVars[i], 
							onvalue=1, offvalue=0
							).grid(row=3, column=i+2)

			tk.Label(self.previewFrame, text="U_" + str(i), borderwidth=0
						).grid(row=4, column=i+2, sticky="ew", padx=3)

			tk.Label(self.previewFrame, text=str(self.U_preview[i][0]) + " V", 
						borderwidth=0, width=7
						).grid(row=5, column=i+2, sticky="ew")
			tk.Label(self.previewFrame, text=str(self.U_preview[i][1]) + " V", 
						borderwidth=0, width=7
						).grid(row=6, column=i+2, sticky="ew")
			tk.Label(self.previewFrame, text=str(self.U_preview[i][2]) + " V", 
						borderwidth=0, width=7
						).grid(row=7, column=i+2, sticky="ew")

	def loadLoggerFile(self):
		# open the file dialog
		selectedFile = filedialog.askopenfilename(initialdir="files", title="Select file",
													filetypes=(("txt files","*.txt"),("all files","*.*")))
		# check if a file was read in
		if selectedFile == '': # file dialog was canceled
			return
		else:
			self.loggerFile = selectedFile
			
		self.focus_force()

		# find the substring indicating the filename without the path
		label = findFilenameSubstr(self.loggerFile)

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
			outFile = FILES_LOCATION + "\\" + findFilenameSubstr(self.loggerFile[:-4] + '_PYOUTPUT.txt')
			self.read_datalogger(self.loggerFile, outFile)
			self.loggerFileLabel['text'] = findFilenameSubstr(outFile)
		except Exception as e:
			messagebox.showinfo("Error", "Bitte zuerst eine Datei zum Parsen auswählen.")
			self.focus_force()
			raise e

		self.setToLoad = tk.Button(self.parserFrame, text="|-> Zur Datenverarbeitung laden",
												command=lambda: self.mainApp.setFileToLoad(outFile, False))
		self.setToLoad.grid(row=20, column=10, sticky="ew")
		tk.Label(self.parserFrame, text="(Schließt den Parser)", fg="red").grid(row=21,column=10, sticky="ew")

	def loadPreviewValues(self):
		""" Loads the first three rows of the selected file"""

		self.U_preview = [[] for x in range(6)]
		self.t_preview = []

		with open(self.loggerFile, 'r') as file_obj:
			for progress, line in enumerate(file_obj):

				if line[0] == ";":
					continue
				if progress > 20:
					break

				newU = [None for x in range(6)]
				try:
					newDate, counter, newU[0], newU[1], newU[2], newU[3], newU[4], newU[5] = line.replace("\n", "").split("	")
				except Exception as e:
					messagebox.showinfo("Error", "Beim Parsen der Datei ist ein Fehler aufgetreten.\nBitte die Datei auf fehlerhafte Zeilen überprüfen.\n\nIn jeder Zeile müssen 8 mit Tabstopp getrennte Werte stehen.\n(Mit ';' beginnende Zeilen werden ignoriert.)")
					print(e)

				for i in range(6):
					self.U_preview[i].append(newU[i])

	def read_datalogger(self, inFile, outFile):
		
		num_lines = file_len(inFile)
		parseColumns = [a.get() for a in self.columnSelectionVars] # columns to parse are 1, the others 0
		U = {"Spalte"+str(_): {"data": [], "Unit": "V"} for _ in range(sum(parseColumns))} # dictionary to store 

		# open input file and parse it
		with open(inFile, "r") as file_obj:
			for progress, line in enumerate(file_obj):

				if line[0] == ";":
					continue

				newU = [None for x in range(6)]
				try:
					newDate, counter, newU[0], newU[1], newU[2], newU[3], newU[4], newU[5] = line.replace("\n", "").split("	")
				except Exception as e:
					messagebox.showinfo("Error", "Beim Parsen der Datei ist ein Fehler aufgetreten.\nBitte die Datei auf fehlerhafte Zeilen überprüfen.\n\nIn jeder Zeile müssen 8 mit Tabstopp getrennte Werte stehen.\n(Mit ';' beginnende Zeilen werden ignoriert.)")
					print(e)

				i = 0
				for k, val in enumerate(newU):
					if parseColumns[k] == 1:
						U["Spalte"+str(i)]["data"].append(val.replace(",","."))
						i += 1

				# update progress bar
				self.loadBar.update(progress, num_lines, msg="(Parsing Data)")

			# loop finished, fill progress bar except last %
			self.loadBar.update(99, 100, msg="(Saving Data)")

		# write the dictionary to the output file as JSON
		with open(outFile, "w") as outFile_obj:
			json.dump(U, outFile_obj)

		# output file written, fill progress bar
		self.loadBar.update(1, 1, msg="(Idle)")

class Application(tk.Frame):
	def __init__(self, master=None):
		master.protocol("WM_DELETE_WINDOW", self.closeApp)

		super().__init__(master)

		self.grid()
		self.master.minsize(500,500)
		self.master.title("Data logger")

		self.createGui()

	def writeData(self, outFile):
		# Set the loading bar message
		self.loadBar.update(1, 1, msg="(Saving data)")

		# write the data dictionary to the output file as JSON
		with open(outFile, "w") as file:
			json.dump(self.dataDict, file)

		self.loadBar.update(1, 1, msg="(Idle)")

		try:
			print("Saved: ", self.dataDict["Spalte0"]["convFunc"], self.dataDict["Spalte0"]["unit"])
		except KeyError:
			print("No conversion values set")
		except Exception as e:
			raise e

	@timeit
	def closeApp(self):
		# Try to close the dataConfigurator via it's close function.
		# If that doesn't work, just destroy it
		try:
			self.parser.close()
		except AttributeError:
			pass
		except Exception as e:
			self.parser.master.destroy()
			print("ERROR: Couldn't close the parser nominally!")
			print(e)
		
		# Try to close the dataConfigurator via it's close function.
		# If that doesn't work, just destroy it
		try:
			self.dataConfigurator.close()
		except AttributeError:
			pass
		except Exception as e:
			self.dataConfigurator.master.destroy()
			print("ERROR: Couldn't close the data configurator nominally!")
			print(e)
		
		# Try to safe the data currently stored in the dataDict
		try:
			self.writeData(self.file)
		except AttributeError:
			pass
		except Exception as e:
			print("ERROR: Couldn't close the App nominally!")
			raise e
		finally:
			self.master.destroy()

	def histogramPotiDeviceOn(self):
		try:
			plt.hist([100+v*15 for i, v in enumerate(self.U3) if self.U2[i]>10], bins=50)
			plt.xlabel("Sollwert Druck [bar]")
			plt.ylabel("Sekunden [s]")
			plt.title("Poti Setting")
			plt.grid(True)

			plt.show()
		except AttributeError:
			messagebox.showinfo("Error", "Zur Anzeige des Histograms bitte zuerst die Zeiten berechnen.")
		except Exception as e:
			raise e

	def histogram(self):
		try:
			plt.hist([100+v*15 for i, v in enumerate(self.U3) if self.U2[i]>10], bins=50)
			plt.xlabel("Sollwert Druck [bar]")
			plt.ylabel("Sekunden [s]")
			plt.title("Poti Setting")
			plt.grid(True)

			plt.show()
		except AttributeError:
			messagebox.showinfo("Error", "Zur Anzeige des Histograms bitte zuerst die Zeiten berechnen.")
		except Exception as e:
			raise e

	def histogramPressureDeviceOn(self):
		try:
			plt.hist([v*40 for v in self.turnedOnPressure], bins=50)
			plt.xlabel("Druck [bar]")
			plt.ylabel("Sekunden [s]")
			plt.title("Histogramm des Drucks")
			plt.grid(True)

			plt.show()
		except AttributeError:
			messagebox.showinfo("Error", "Zur Anzeige des Histograms bitte zuerst die Zeiten berechnen.")
		except Exception as e:
			raise e

	def newFile(self, file):
		""" Sets a new JSON file and makes sure that data currently
		loaded is saved to the old file"""
		try:
			self.writeData(self.file)
		except:
			print("Caution: Couldn't save data file!")
		self.file = file

	def createGui(self):
		""" Menu bar """
		self.menubar = tk.Menu(self)
		self.master.config(menu=self.menubar)

		self.filemenu = tk.Menu(self.menubar, tearoff=0)
		self.filemenu.add_command(label="Parser öffnen", command=self.initParser)
		self.filemenu.add_command(label="Daten konfigurieren", command=self.initDataConfigurator)
		self.filemenu.add_command(label="Beenden", command=self.closeApp)
		self.menubar.add_cascade(label="Datei", menu=self.filemenu)

		""" Frames """
		self.statusFrame = tk.Frame(master=self, borderwidth=1, padx=5, pady=5)
		self.statusFrame.grid(column=0, row=5)

		self.dataFrame = tk.LabelFrame(master=self, text="Daten verarbeiten", borderwidth=1, relief="sunken", width=500, height=300, padx=5, pady=5)
		self.dataFrame.grid(column=0, row=15)
		self.dataFrame.grid_propagate(False)

		self.diagrammFrame = tk.LabelFrame(master=self, text="Diagramme", borderwidth=1, relief="sunken", padx=5, pady=15)
		self.diagrammFrame.grid(column=0, row=25, sticky="nsew")

		""" Loading bar """
		self.loadBar = SimpleProgressBar(self.statusFrame)

		""" Buttons and Labels """
		self.openFileButton = tk.Button(self.dataFrame, text="Datei öffnen", command=self.loadFile)
		self.openFileButton.grid(row=3, column=5, sticky="ew")

		self.fileLabel = tk.Label(self.dataFrame, text="", borderwidth=0, width=40)
		self.fileLabel.grid(row=3, column=10, sticky="w")

		self.configDataButton = tk.Button(self.dataFrame, text="Daten konfigurieren", command=self.initDataConfigurator)
		self.configDataButton.grid(row=4, column=5, sticky="ew")

		self.configDataLabel = tk.Label(self.dataFrame, text="", borderwidth=0, width=40)
		self.configDataLabel.grid(row=4, column=10, sticky="w")

		self.ZeitenButton = tk.Button(self.dataFrame, text="Laufzeiten berechnen", command=self.showTimes)
		self.ZeitenButton.grid(row=6, column=5, sticky="ew")

		self.U2_plotButton = tk.Button(self.diagrammFrame, text="Zustand über Zeit", command=self.plot_U2)
		self.U2_plotButton.grid(row=0, column=2, padx=3)

		self.U3_plotButton = tk.Button(self.diagrammFrame, text="Poti über Zeit", command=self.plot_U3)
		self.U3_plotButton.grid(row=0, column=3, padx=3)
		
		self.U1_plotButton = tk.Button(self.diagrammFrame, text="Druck über Zeit", command=self.plot_U1)
		self.U1_plotButton.grid(row=0, column=4, padx=3)

		""" Table """ 
		self.table = SimpleTable(self.dataFrame, 8, 2)
		self.table.grid(row=6, column=10, rowspan=9, padx=10)
		self.updateTimeTable()
	
		# test button
		tk.Button(self, text="Testbutton", command=self.histogramPotiDeviceOn).grid(column=0, row=1)

	def initParser(self):
		# start the parser as a toplevel widget
		self.parser = Parser(tk.Toplevel(), self)
		self.parser.mainloop()

	def initDataConfigurator(self):
		# start the data configurator window as a toplevel widget
		try:
			if not self.dataDict:
				raise AttributeError
		except AttributeError:
			messagebox.showinfo("Error", "Bitte zuerst eine Datei einlesen.")
		else:
			self.dataConfigurator = DataConfigurator(tk.Toplevel(), self)
			self.dataConfigurator.mainloop()

	def setFileLabel(self, file):
		# find the substring indicating the filename without the path
		labelText = findFilenameSubstr(file)

		# set the file Label showing the selected file with the previously found substring
		try:
			self.fileLabel['text'] = labelText
		except UnboundLocalError:
			raise e
		except Exception as e:
			raise e

	def setFileToLoad(self, file, deleteOldData=False):
		""" loads a new file into memory """

		# if the deleteOldData flag was not set, 
		# save the data currently in memory to its file
		if not deleteOldData:
			self.newFile(file)
		else: # otherwise just set the new file as current file
			self.file = file

		# change the file label
		self.setFileLabel(self.file)

		# close the parser
		self.parser.close()
		
		# parse the file
		self.loadData()
	

	def loadFile(self):
		""" Opens the file dialog to ask for a new file to load
		and loads the data from the file"""

		# open the file dialog
		selectedFile = filedialog.askopenfilename(initialdir=FILES_LOCATION, title="Select file", 
													filetypes=(("txt files","*_PYOUTPUT.txt"),))
		# check if a file was read in
		if selectedFile == '': # file dialog was canceled
			return
		else:
			self.newFile(selectedFile)

		# change the file label
		self.setFileLabel(self.file)

		# parse the file
		self.loadData()

	# aktualisiert die Zeiten-Tabelle und zeigt diese an. Ausführen über Button.
	def showTimes(self): 
		try:
			self.calculateTimes()
		except AttributeError:
			messagebox.showinfo("Error", "Bitte zuerst Daten einlesen!")
		except Exception as e:
			print(e)
		else:
			try:
				self.updateTimeTable()
			except Exception as e:	
				self.table = SimpleTable(self.dataFrame, 8, 2)
				self.table.grid()
				self.updateTimeTable()
				print(e)

	def updateTimeTable(self):
		self.table.set(0,0,"Zeit")
		self.table.set(0,1,"Wert")

		self.table.set(1,0,"Gerät an")
		try:
			self.table.set(1,1,"{0:.2f} h".format(self.t_on/60/60))
		except:
			self.table.set(1,1,"{0:} h".format('----'))
		self.table.set(2,0,"p > 240bar")
		try:
			self.table.set(2,1,"{0:.2f} h".format(self.t_240bar/60/60))
		except:
			self.table.set(2,1,"{0:} h".format('----'))
		self.table.set(3,0,"Schwemm")
		try:
			self.table.set(3,1,"{0:.2f} h".format(self.t_schwemm/60/60))
		except:
			self.table.set(3,1,"{0:} h".format('----'))
		self.table.set(4,0,"Poti 100V")
		try:
			self.table.set(4,1,"{0:.2f} h".format(self.t_poti_lowest/60/60))
		except:
			self.table.set(4,1,"{0:} h".format('----'))
		self.table.set(5,0,"Poti 250V")
		try:
			self.table.set(5,1,"{0:.2f} h".format(self.t_poti_highest/60/60))
		except:
			self.table.set(5,1,"{0:} h".format('----'))
		self.table.set(6,0,"Poti mitte")
		try:
			self.table.set(6,1,"{0:.2f} h".format(self.t_poti_between/60/60))
		except:
			self.table.set(6,1,"{0:} h".format('----'))
		self.table.set(7,0,"N Poti")
		try:
			if self.n_poti == None:
				self.table.set(7,1,'----')
			else:
				self.table.set(7,1,self.n_poti)
		except:
			self.table.set(7,1,'----')

		self.update_idletasks()

	def loadData(self):
		""" Reads the data from a JSON file into memory """
		try:
			if self.file == '':
				raise AttributeError
		except AttributeError:
			messagebox.showinfo("Error", "Bitte zuerst eine Datei öffnen.")
			return
		except FileNotFoundError:
			messagebox.showinfo("Error", "Bitte eine korrekte Datei öffnen.")
			return
		except Exception as e:
			raise e

		self.U = []

		with open(self.file, "r") as file_obj:
			self.dataDict = json.load(file_obj)

		i = 0
		dicLen = len(self.dataDict) # for progress bar
		for _, values in self.dataDict.items():
			self.U.append(list(map(float, values["data"])))

			# progress bar
			self.loadBar.update(i, dicLen, msg="(Loading Data)")
			i+=1

		# fill progress bar
		self.loadBar.update(1, 1, msg="(Idle)")

		# <========== temp ==========
		self.U1 = self.U[0]
		self.U2 = self.U[1]
		self.U3 = self.U[2]
		#  ========== temp ==========>

	@timeit
	def calculateTimes(self):

		valid_lines = len(self.U1)

		limit_schwemm = 2.0
		# variables to evaluate data
		time_on = []
		time_highest_pressure = []
		time_poti_lowest = []
		time_poti_highest = []
		time_poti_between = []
		time_schwemm = []
		poti_schaltungen = 0
		potiSwitching = False
		sumPressureOn = 0
		sumPressureOnCount = 0

		self.turnedOnPressure = []

		# constants
		U1_volts_per_Bar = 10 / 400 # [V/bar]

		# evaluate data
		for i in range(len(self.U1)):

			turnedOn = False
			# count time device on
			if self.U2[i] > 20:
				turnedOn = True
				time_on.append(i)

			# values when the device is turned on
			if turnedOn:

				# device on and highest pressure
				if self.U1[i] > 6.0:
					time_highest_pressure.append(i)

				# calculate sum for average pressure when turned on
				sumPressureOn += self.U1[i]
				sumPressureOnCount += 1
				self.turnedOnPressure.append(self.U1[i])

				# find schwemmbetrieb
				if i > 0:
					if self.U1[i] < limit_schwemm and self.U1[i] == self.U1[i-1]:
						time_schwemm.append(i)

				# evaluate poti position
				if self.U3[i] < 0.5: # poti on lowest setting when turned on
					time_poti_lowest.append(i)
				elif self.U3[i] > 9.5: # poti on highest setting when turned on
					time_poti_highest.append(i)
				else: # poti in between the highest and lowest setting
					time_poti_between.append(i)

				# find all times the poti was changed even when turned off
				if i > 0:
					if self.U3[i] != self.U3[i-1]:
						potiSwitching = True
					elif potiSwitching:
						poti_schaltungen += 1
						potiSwitching = False

			# write progress bar
			self.loadBar.update(i, len(self.U1), msg="(Calculating)")
		
		# loop finished, fill progress bar
		self.loadBar.update(1, 1, msg="(Idle)")

		self.t_ges = valid_lines
		self.t_on = len(time_on)
		self.t_240bar = len(time_highest_pressure)
		self.t_poti_lowest = len(time_poti_lowest)
		self.t_poti_highest = len(time_poti_highest)
		self.t_poti_between = len(time_poti_between)
		self.t_schwemm = len(time_schwemm)
		self.n_poti = poti_schaltungen
		self.p_OnAvg = sumPressureOn / sumPressureOnCount / U1_volts_per_Bar

	def plot_U1(self):
		try:
			p1_bar = [u * 400 / 10 for u in self.U1]

			plt.figure(figsize=(2, 1))
			plt.subplot(211)
			plt.plot(p1_bar)
			plt.xlabel("Zeit [sec]")
			plt.ylabel("Druck [bar]")
			plt.title("Drucksensor")

			plt.subplot(212)
			self.plot_U2()

		except AttributeError:
			messagebox.showinfo("Error", "Bitte zuerst eine Datei öffnen!")
		except Exception as e:
			raise e

	def plot_U2(self):
		try:
			isOn = [1 if x > 15 else 0 for x in self.U2]

			plt.plot(isOn)
			plt.xlabel("Zeit [sec]")
			plt.ylabel("Ein/Aus [-]")
			plt.title("Gerät an/aus")
			plt.show()
		except AttributeError:
			messagebox.showinfo("Error", "Bitte zuerst eine Datei öffnen!")
		except Exception as e:
			raise e

	def plot_U3(self):
		try:
			p3_bar = [100 + u * 15 for u in self.U3]

			plt.figure(figsize=(2, 1))
			plt.subplot(211)
			plt.plot(p3_bar[0:1100000])
			plt.xlabel("Zeit [sec]")
			plt.ylabel("Poti setting [bar]")
			plt.title("Schiebepotentiometer, 100-250 bar")
			plt.subplot(212)
			
			isOn = [1 if x > 15 else 0 for x in self.U2]

			plt.plot(isOn[0:1100000])
			plt.xlabel("Zeit [sec]")
			plt.ylabel("Ein/Aus [-]")
			plt.title("Gerät an/aus")
			
			plt.show()
		except AttributeError:
			messagebox.showinfo("Error", "Bitte zuerst eine Datei öffnen!")
		except Exception as e:
			raise e


class SimpleTable(tk.Frame):
    def __init__(self, parent, rows=10, columns=2):
        # use black background so it "peeks through" to 
        # form grid lines
        tk.Frame.__init__(self, parent, background="black")
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = tk.Label(self, text="%s/%s" % (row, column), 
                                 borderwidth=0, width=10)
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)


    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)


class SimpleProgressBar(tk.Frame):

	def __init__(self, parent, total=100, msg="(Idle)"):
		tk.Frame.__init__(self, parent)

		self.progressbar = ttk.Progressbar(master=parent, length=200, 
											mode='determinate', maximum=total)
		self.progressbar.grid(column=0, row=0)
		
		self.progressLabel = tk.Label(parent, text="0%", width=5)
		self.progressLabel.grid(column=1, row=0)

		self.messageLabel = tk.Label(parent, text=msg)
		self.messageLabel.grid(column=2, row=0)

		self.updateTime = 0.005 # ms
		self.lastUpdate = time.time()

	def update(self, count, total=None, msg=""):
		if count == total:
			self.progressbar['maximum'] = total
			self.progressbar['value'] = count
			self.progressLabel['text'] = "100%"
			self.messageLabel['text'] = msg
		elif time.time() - self.lastUpdate > self.updateTime:
			if total != None:
				self.progressbar['maximum'] = total
			
			percents = round(100.0 * count / float(self.progressbar['maximum']), 1)
	    	
			self.progressbar['value'] = count
			self.progressLabel['text'] = str(percents) + '%'
			self.messageLabel['text'] = msg
			self.progressbar.update_idletasks()

			self.lastUpdate = time.time()

# length of a file
def file_len(fname):
    with open(fname) as f:
        for i, _ in enumerate(f):
            pass
    return i + 1

if __name__ == '__main__': main()

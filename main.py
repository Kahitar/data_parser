import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import dataConfigurator
import dataLoggerParser
import progressBar
import utility

def main():
	root = tk.Tk()
	app = Application(master=root)
	app.mainloop()

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
			print("Saved: ", self.dataDict["DataColumns"]["Spalte0"]["convFunc"], self.dataDict["DataColumns"]["Spalte0"]["Unit"])
		except KeyError:
			print("No conversion values set")
		except Exception as e:
			raise e

	@utility.timeit
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
			if self.dataConfigurator != None: # the dataConfigurator is still open
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

	def newFile(self, file):
		""" Sets a new JSON file and makes sure that data currently
		loaded is saved to the old file"""
		try:
			self.writeData(self.file)
		except AttributeError:
			# self.file does not exist yet. Therefore there exists no data to save and nothing will be lost.
			pass
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
		self.loadBar = progressBar.SimpleProgressBar(self.statusFrame)

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
		self.table = SimpleTable(self.dataFrame)
		self.table.grid(row=6, column=10, rowspan=9, padx=10)
		self.table.set(0,0,"Zeit")
		self.table.set(0,1,"Sekunden")
	
		# test button
		tk.Button(self, text="Testbutton", command=self.histogramPotiDeviceOn).grid(column=0, row=1)

	def initParser(self):
		# start the parser as a toplevel widget
		self.parser = dataLoggerParser.Parser(master=tk.Toplevel(), mainApp=self)
		self.parser.mainloop()

	def initDataConfigurator(self):
		# start the data configurator window as a toplevel widget
		try:
			if not self.dataDict:
				raise AttributeError
		except AttributeError:
			messagebox.showinfo("Error", "Bitte zuerst eine Datei einlesen.")
		else:
			self.dataConfigurator = dataConfigurator.DataConfigurator(tk.Toplevel(), self)
			self.dataConfigurator.mainloop()

	def setFileLabel(self, file):
		# find the substring indicating the filename without the path
		labelText = utility.findFilenameSubstr(file)

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

		# close the parser # TODO: Let the parser handle this
		try:
			self.parser.close()
		except:
			pass
		
		# parse the file
		self.loadData()

	def loadFile(self):
		""" Opens the file dialog to ask for a new file to load
		and loads the data from the file"""

		# open the file dialog
		selectedFile = filedialog.askopenfilename(initialdir=utility.FILES_LOCATION, title="Select file", 
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

	def showTimes(self):
		""" Refreshes the time-table (or renders it). Function run through button """
		try:
			self.calculateTimes()
		except AttributeError:
			messagebox.showinfo("Error", "Bitte zuerst Daten einlesen!")
		except Exception as e:
			raise e
		else:
			self.updateTimeTable()

	def updateTimeTable(self):
		""" times = {"Gerät an/aus": {"occurence": [], "sum": 0}} """

		self.table.emptyTable()

		self.table.set(0,0,"Zeit")
		self.table.set(0,1,"Wert")

		i = 0
		for key, value in self.times.items():
			self.table.set(i+1,0,key)
			self.table.set(i+1,1,"{:.3} h".format(value["sum"]/60/60))
			i += 1

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

		self.data = []

		with open(self.file, "r") as file_obj:
			self.dataDict = json.load(file_obj)

		try:
			 # for progress bar
			dicLen = len(self.dataDict["DataColumns"])
		except KeyError:
			self.dataDict["DataColumns"] = dict()
		i = 0
		for _, values in self.dataDict["DataColumns"].items():
			self.data.append(list(map(float, values["data"])))

			# progress bar
			self.loadBar.update(i, dicLen, msg="(Loading Data)")
			i+=1

		# fill progress bar
		self.loadBar.update(1, 1, msg="(Idle)")

	def evaluateExpression(self, expression):
		""" {"columnData": 1, "operator": ">", "comparator": 0.1} """

		d = expression
		d["columnData"] = float(d["columnData"])
		d["comparator"] = float(d["comparator"])
		
		return eval("columnData" + d["operator"] + "comparator", d)

	@utility.timeit
	def calculateTimes(self):

		try:
			self.times = {name: {"occurence": [], "sum": 0} for name,_ in self.dataDict["TimeDefinitions"].items()}
		except KeyError:
			self.dataDict["TimeDefinitions"] = dict()
			self.calculateTimes()
			return
		
		# evaluate data
		for i in range(len(self.data[0])):

			# iterate through the time definitions
			for timeDef, conditions in self.dataDict["TimeDefinitions"].items():
				conditionsSatisfied = True
				# iterate through the conditions for the current time
				for condition in conditions:
					# iterate through data columns and find the data needed for the current condition
					for colKey, dataColumn in self.dataDict["DataColumns"].items():

						# create the conversion function
						params = dataColumn["convFunc"]
						conversion = lambda x, params: params["y1"] + (x-params["x1"])*((params["y1"]-params["y2"])/(params["x1"]-params["x2"]))

						# check if the current column matches the column needed for a condition
						if dataColumn["name"] == condition["column"]:
							# the data needed for the condition
							dataPoint = conversion(float(dataColumn["data"][i]), params)
							operator = condition["operator"]
							try:
								comparator = float(condition["comparator"])
							except ValueError:
								comparator = 0.0
								condition["comparator"] = 0.0 # TODO: give a warning instead

							# construct expression
							expression = {"columnData": dataPoint, "operator": operator, "comparator": comparator}

							# check if the data fullfills the condition
							conditionsSatisfied = conditionsSatisfied and self.evaluateExpression(expression)
							
					if not conditionsSatisfied:
						break
				if conditionsSatisfied:
					self.times[timeDef]["occurence"].append(i+1)
					self.times[timeDef]["sum"] += 1

			# write progress bar
			self.loadBar.update(i, len(self.data[0]), msg="(Calculating)")

		# loop finished, fill progress bar
		self.loadBar.update(1, 1, msg="(Idle)")

	def plot_U1(self):
		try:
			p1_bar = [u * 400 / 10 for u in self.data[0]]

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
			isOn = [1 if x > 15 else 0 for x in self.data[1]]

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
			p3_bar = [100 + u * 15 for u in self.data[2]]

			plt.figure(figsize=(2, 1))
			plt.subplot(211)
			plt.plot(p3_bar[0:1100000])
			plt.xlabel("Zeit [sec]")
			plt.ylabel("Poti setting [bar]")
			plt.title("Schiebepotentiometer, 100-250 bar")
			plt.subplot(212)
			
			isOn = [1 if x > 15 else 0 for x in self.data[1]]

			plt.plot(isOn[0:1100000])
			plt.xlabel("Zeit [sec]")
			plt.ylabel("Ein/Aus [-]")
			plt.title("Gerät an/aus")
			
			plt.show()
		except AttributeError:
			messagebox.showinfo("Error", "Bitte zuerst eine Datei öffnen!")
		except Exception as e:
			raise e
	
	def histogramPotiDeviceOn(self):
		try:
			plt.hist([100+v*15 for i, v in enumerate(self.data[2]) if self.data[1][i]>10], bins=50)
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
			plt.hist([100+v*15 for i, v in enumerate(self.data[2]) if self.data[1][i]>10], bins=50)
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

class SimpleTable(tk.Frame):
	def __init__(self, parent):
		# use black background so it "peeks through" to 
		# form grid lines
		tk.Frame.__init__(self, parent, background="black")
		self._widgets = []

	def addRow(self):
		current_row = []
		numRows = len(self._widgets)
		try:
			numCols = len(self._widgets[0])
		except:
			numCols = 1

		for column in range(numCols):
			label = tk.Label(self, text="", borderwidth=0, width=10)
			label.grid(row=numRows, column=column, sticky="nsew", padx=1, pady=1)
			current_row.append(label)
		self._widgets.append(current_row)

	def addColumn(self):
		numRows = len(self._widgets)
		try:
			numCols = len(self._widgets[0])
		except:
			numCols = 1

		for row in range(numRows):
			label = tk.Label(self, text="", borderwidth=0, width=10)
			label.grid(row=row, column=numCols, sticky="nsew", padx=1, pady=1)
			self._widgets[row].append(label)

	def emptyTable(self):
		for row in range(len(self._widgets)):
			for column in range(len(self._widgets[row])):
				self._widgets[row][column].grid_forget()
		self._widgets = []

	def set(self, row, column, value):

		# check if the cell already exists
		if len(self._widgets) > row:
			if len(self._widgets[0]) > column:
				# cell exists, change text
				widget = self._widgets[row][column]
				widget["text"] = value
				widget.config(width=len(str(value)))
			else:
				self.addColumn()
				self.set(row, column, value)
		else:
			self.addRow()
			self.set(row, column, value)

if __name__ == '__main__': main()

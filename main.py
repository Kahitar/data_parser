import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import dataCache
import dataConfigurator
import dataLoggerParser
import progressBar
import tkTable
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
		self.statusFrame.grid(row=5, column=0)

		self.dataFrame = tk.LabelFrame(master=self, text="Daten", borderwidth=1, relief="sunken", width=500, height=85, padx=5, pady=5)
		self.dataFrame.grid(row=15, column=0)
		self.dataFrame.grid_propagate(False)

		self.timesFrame = tk.LabelFrame(master=self, text="Laufzeiten", borderwidth=1, relief="sunken", width=500, height=200, padx=5, pady=5)
		self.timesFrame.grid(row=20, column=0, sticky='ew')
		#self.timesFrame.grid_propagate(False)

		self.diagrammFrame = tk.LabelFrame(master=self, text="Diagramme", borderwidth=1, relief="sunken", padx=5, pady=15)
		self.diagrammFrame.grid(row=25, column=0, sticky="nsew")

		""" Loading bar """
		self.loadBar = progressBar.SimpleProgressBar(self.statusFrame)

		""" Data Frame """
		self.openFileButton = tk.Button(self.dataFrame, text="Datei öffnen", command=self.loadFile)
		self.fileLabel = tk.Label(self.dataFrame, text="", borderwidth=0, width=40)
		self.configDataButton = tk.Button(self.dataFrame, text="Daten auswählen", command=self.initDataConfigurator)
		self.configDataLabel = tk.Label(self.dataFrame, text="", borderwidth=0, width=40)

		self.openFileButton.grid(row=3, column=5, sticky="ew")
		self.fileLabel.grid(row=3, column=10, sticky="w")
		self.configDataButton.grid(row=4, column=5, sticky="ew")
		self.configDataLabel.grid(row=4, column=10, sticky="w")

		""" Times Frame """

		self.ZeitenButton = tk.Button(self.timesFrame, text="Laufzeiten berechnen", command=self.showTimes)
		self.timeRangeFrame = tk.Frame(self.timesFrame)
		self.table = tkTable.TkTable(self.timesFrame)

		self.ZeitenButton.grid(row=5, column=5, padx=5, sticky='w')
		self.timeRangeFrame.grid(row=6, column=0, rowspan=2, sticky='n')
		self.table.grid(row=6, column=5, pady=5, padx=5)

		self.timeRangeLabel = tk.Label(self.timeRangeFrame, text="Berechnungszeitraum")
		self.fromTimeLabel = tk.Label(self.timeRangeFrame, text="Von: ")
		self.fromTimeEntry = tk.Entry(self.timeRangeFrame, width=15)
		self.toTimeLabel = tk.Label(self.timeRangeFrame, text="Bis: ")
		self.toTimeEntry = tk.Entry(self.timeRangeFrame, width=15)
		self.formatLabel = tk.Label(self.timeRangeFrame, text="Format: yyyy-mm-dd")

		self.timeRangeLabel.grid(row=0, column=0, columnspan=2, sticky='w')
		self.fromTimeLabel.grid(row=1, column=0, sticky='e')
		self.fromTimeEntry.grid(row=1, column=1)
		self.toTimeLabel.grid(row=2, column=0, sticky='e')
		self.toTimeEntry.grid(row=2, column=1)
		self.formatLabel.grid(row=3, column=0, columnspan=2, sticky='w')

		self.table.set(0,0,"Name")
		self.table.set(0,1,"Zeit")
	
	def initParser(self):
		# start the parser as a toplevel widget
		self.parser = dataLoggerParser.Parser(master=tk.Toplevel(), mainApp=self)
		self.parser.mainloop()

	def initDataConfigurator(self):
		# start the data configurator window as a toplevel widget
		try:
			if not dataCache.dataDict:
				raise AttributeError
		except AttributeError:
			messagebox.showinfo("Error", "Bitte zuerst eine Datei einlesen.")
		else:
			self.dataConfigurator = dataConfigurator.DataConfigurator(tk.Toplevel(), self)
			self.dataConfigurator.mainloop()

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
			self.saveData()
		except AttributeError:
			pass
		except Exception as e:
			print("ERROR: Couldn't close the App nominally!")
			raise e
		finally:
			self.master.destroy()

	def saveData(self):
		# Set the loading bar message
		self.loadBar.update(1, 1, msg="(Saving data)")

		# write the data dictionary to the output file as JSON
		dataCache.saveDataToFile()

		self.loadBar.update(1, 1, msg="(Idle)")

	def loadFile(self):
		""" Opens the file dialog to ask for a new file to load
		and loads the data from the file
		"""

		# open the file dialog
		selectedFile = filedialog.askopenfilename(initialdir=utility.FILES_LOCATION, title="Select file", 
													filetypes=(("json files","*.json"),))
		# check if a file was read in
		if selectedFile == '': # file dialog was canceled
			return
		else:
			self.setFileToLoad(selectedFile)
	
	def setFileToLoad(self, file, deleteOldData=False):
		""" loads a new file into memory """

		# load the data
		self.loadBar.update(1, 1, msg="(Loading new File)")
		dataCache.loadDataFromFile(file, deleteOldData)
		self.loadBar.update(1, 1, msg="(Idle)")

		# change the file label
		self.setFileLabel(file)

		# reset the table
		self.resetTimeTable()

	def setFileLabel(self, file):
		# find the substring indicating the filename without the path
		labelText = utility.findFilenameSubstr(file, 4) # the file is a .json file

		# set the file Label showing the selected file with the previously found substring
		try:
			self.fileLabel['text'] = labelText
		except UnboundLocalError:
			raise e
		except Exception as e:
			raise e

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

		self.table.set(0,0,"Name")
		self.table.set(0,1,"Zeit")

		try:
			i = 0
			for key, value in self.times.items():
				self.table.set(i+1,0,key)
				self.table.set(i+1,1,"{:.3} h".format(value["sum"]/60/60))
				i += 1
		except AttributeError:
			# Times not calculated yet
			pass

		self.update_idletasks()

	def resetTimeTable(self):
		try:
			self.table.emptyTable()
		except AttributeError:
			pass
		self.table.set(0,0,"Name")
		self.table.set(0,1,"Zeit")

	@utility.timeit
	def calculateTimes(self):

		try:
			self.times = {name: {"occurence": [], "sum": 0} for name,_ in dataCache.dataDict["TimeDefinitions"].items()}
		except KeyError:
			dataCache.dataDict["TimeDefinitions"] = dict()
			self.calculateTimes()
			return
		
		# evaluate data
		for i in range(len(dataCache.dataDict["DataColumns"]["Spalte0"]["data"])):

			# iterate through the time definitions
			for timeDef, conditions in dataCache.dataDict["TimeDefinitions"].items():
				conditionsSatisfied = True
				# iterate through the conditions for the current time
				for condition in conditions:
					# iterate through data columns and find the data needed for the current condition
					for _colKey, dataColumn in dataCache.dataDict["DataColumns"].items():

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
			self.loadBar.update(i, len(dataCache.dataDict["DataColumns"]["Spalte0"]["data"]), msg="(Calculating)")

		# loop finished, fill progress bar
		self.loadBar.update(1, 1, msg="(Idle)")
	
	def evaluateExpression(self, expression):
		""" {"columnData": 1, "operator": ">", "comparator": 0.1} """

		d = expression
		d["columnData"] = float(d["columnData"])
		d["comparator"] = float(d["comparator"])
		
		return eval("columnData" + d["operator"] + "comparator", d)

if __name__ == '__main__': 
	main()

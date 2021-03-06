import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import utility
import dataCache

class TimeDefinition(tk.Frame):

	def __init__(self, master, name, conditions, dataColumnDefinitions):
		super().__init__(master)
		self.dataColumnDefinitions = dataColumnDefinitions

		self.conditions = dict()

		# time name
		self.name = tk.Entry(self, justify="center")
		self.name.insert(0, name)
		self.name.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=(15,0))

		# placeholder label
		tk.Label(self, width=5).grid(row=3, column=0)

		# add condition Button
		self.addConditionButton = tk.Button(self, text="Bedingung hinzufügen", command=self.addCondition)
		self.addConditionButton.grid(row=2, column=2, columnspan=3, pady=(15,0))

		# time delete Button
		self.timeDeleteButton = tk.Button(self, fg="red", text="X", command=lambda: self.master.deleteTimeDefinition(self))
		self.timeDeleteButton.grid(row=2, column=5, padx=5, pady=(15,0))

		# add all specified conditions
		if conditions:
			for condition in conditions:
				self.addCondition(condition)
		else:
			self.addCondition()

	def __eq__(self, other):
		return self.__dict__ == other.__dict__


	def addCondition(self, condition=False):
		""" param condition: {"column": "Spannung", "operator": ">", "comparator": ""} """
		
		dataColumnNames = tuple(col["name"] for col in self.dataColumnDefinitions)

		self.conditions[len(self.conditions)] = dict()
		currIndex = len(self.conditions)-1

		# column name
		self.conditions[currIndex]['column'] = tk.StringVar(self, value=condition["column"] if condition else dataColumnNames[0])
		self.conditions[currIndex]['column'].trace_add('write', callback=lambda name, index, mode: self.changeConditionUnit(currIndex))
		self.conditions[currIndex]['columnMenu'] = tk.OptionMenu(self, self.conditions[currIndex]['column'], *dataColumnNames)
		self.conditions[currIndex]['columnMenu'].grid(row=len(self.conditions)+2, column=1)

		# column comparison
		self.conditions[currIndex]['operator'] = tk.StringVar(self, value=condition["operator"] if condition else '>')
		self.conditions[currIndex]['operatorMenu'] = tk.OptionMenu(self, self.conditions[currIndex]['operator'], *('>', '>=', '==', '<=', '<'))
		self.conditions[currIndex]['operatorMenu'].grid(row=len(self.conditions)+2, column=2)

		self.conditions[currIndex]['comparator'] = tk.Entry(self, width=10, justify="center")
		self.conditions[currIndex]['comparator'].insert(0, condition["comparator"] if condition else '0.0')
		self.conditions[currIndex]['comparator'].grid(row=len(self.conditions)+2, column=3)
		self.conditions[currIndex]['unitLabel'] = tk.Label(self, text="")
		self.changeConditionUnit(currIndex)
		self.conditions[currIndex]['unitLabel'].grid(row=len(self.conditions)+2, column=4, padx=5)
		
		self.conditions[currIndex]['deleteRowButton'] = tk.Button(self, text="X", command=lambda: self.deleteRow(currIndex))
		self.conditions[currIndex]['deleteRowButton'].grid(row=currIndex+3, column=5)

	def refreshConditions(self, dataColumnDefinitions):
		# refresh option menu options
		dataColumnNames = tuple(col["name"] for col in dataColumnDefinitions)
		for _key, condition in self.conditions.items():
			condition['columnMenu']['menu'].delete(0, 'end')
			for _idx, dataColumnName in enumerate(dataColumnNames):
				condition['columnMenu']['menu'].add_command(label=dataColumnName,
															command=tk._setit(condition['column'], dataColumnName))

			optionMenuOptions = [condition['columnMenu']['menu'].entrycget(i, 'label') for i in range(3)]
			if condition['column'].get() not in optionMenuOptions:
				condition['column'].set(optionMenuOptions[0])
		
	def changeConditionUnit(self, index):
		currName = self.conditions[index]['column'].get()

		for col in self.dataColumnDefinitions:
			if col["name"] == currName:
				self.conditions[index]['unitLabel']['text'] = col["unit"]

	def deleteRow(self, rowNum):
		# remove the specified row from the row list
		for _, value in self.conditions[rowNum].items():
			try:
				value.grid_forget()
			except AttributeError:
				# value is not a tk widget
				pass
		del self.conditions[rowNum]

class TimesCalculationFrame(tk.LabelFrame):
	def __init__(self, master, **kw):
		super().__init__(master, kw)

		tk.Button(self, text="Neue Zeit", command=self.addTimeDefinition).grid(column=1)
		self.timeFrames = list()

	def setTimeDefinitions(self, timeDefinitions):
		""" sets the time definition from the main data dict 
		timeDefinitions format: {"<name>": [{"column": "Spannung", "operator": ">", "comparator": ""}]}
		"""

		# iterate through time definitions
		for timeName, timeDef in timeDefinitions.items():
			# add a time frame for the current time definition
			self.addTimeDefinition(name=timeName, conditions=timeDef)

	def getTimeDefinitions(self):
		""" returns the time definition as a list of dicts describing the calculation inside a dictionary with the time name
		format: <TODO: update this> {"name", [{"column": <columnName>, "operator": <operator>, "comparator": <comparator>}, {<...>}]} possibly repeated and 
		connected with a comparison operator 
		"""

		returnValue = dict()
		for time in self.timeFrames:
			returnValue[time.name.get()] = list()
			for _, value in time.conditions.items():
				returnValue[time.name.get()].append({'column': 	value['column'].get(),
											'operator': value['operator'].get(),
											'comparator': value['comparator'].get()
											})
		return returnValue

	def addTimeDefinition(self, name="", conditions=None):
		newRow = TimeDefinition(self, name, conditions, self.master.getDataColumnDefinitions())
		newRow.grid(column=1)
		self.timeFrames.append(newRow)

	def deleteTimeDefinition(self, delObj):
		for i, obj in enumerate(self.timeFrames):
			if obj == delObj:
				obj.grid_forget()
				del self.timeFrames[i]
				return
		
class DataConfiguratorRow(tk.Frame):
	def __init__(self, master, isHeadline=False, rowNumber=0):
		super().__init__(master)

		# headline
		if isHeadline:
			tk.Label(self, text="Spalte").grid(
				row=1, column=1, padx=3, pady=3)
			tk.Label(self, text="Name").grid(
				row=1, column=3, padx=3, pady=3)
			tk.Label(self, text="Umrechnung").grid(
				row=1, column=5, columnspan=3, padx=3, pady=3)
			tk.Label(self, text="Einheit").grid(
				row=1, column=8, padx=3, pady=3)

		# row number label
		tk.Label(self, text=str(rowNumber+1)).grid(row=2, column=1, padx=20)

		# name field
		self.nameFieldString = tk.StringVar()
		self.nameFieldString.trace_add(mode="write", 
					callback=lambda name, index, mode: master.master.refresh())
		self.nameField = tk.Entry(self, textvariable=self.nameFieldString)
		self.nameField.grid(row=2, column=3, padx=3)

		# conversion Fields
		self.x1 = tk.Entry(self, width=4, justify="center")
		self.x1.grid(row=2, column=5, padx=3)
		tk.Label(self, text="V = ").grid(row=2, column=6)
		self.y1 = tk.Entry(self, width=4, justify="center")
		self.y1.grid(row=2, column=7, padx=3)

		self.x2 = tk.Entry(self, width=4, justify="center")
		self.x2.grid(row=3, column=5, padx=3)
		tk.Label(self, text="V =").grid(row=3, column=6)
		self.y2 = tk.Entry(self, width=4, justify="center")
		self.y2.grid(row=3, column=7, padx=3)
		self.y2_UnitLabel = tk.Label(self, text="V", width=8, anchor="w") # The width of this label is important to keep the gui aligned
		self.y2_UnitLabel.grid(row=3, column=8)

		self.Unit_y1 = tk.StringVar(self, value='V')
		tk.OptionMenu(self, self.Unit_y1, *('V', 'A', 'bar', 'l/h', '°C', '--')).grid(row=2, column=8, sticky="w")

		self.Unit_y1.trace_add("write", self.setConversionUnit)

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
			# This means it was never necessary call this function since the 
			# conversion params didn't change
			pass
		except ValueError:
			print("Setting standard conversion values because: ")
			return {"x1": 0, "x2": 1, "y1": 0, "y2": 1}
		except Exception as e:
			raise e

	def setConversionFunctionParams(self, conversionDict):
		self.x1.delete(0, 'end')
		self.x2.delete(0, 'end')
		self.y1.delete(0, 'end')
		self.y2.delete(0, 'end')

		self.x1.insert(0, conversionDict["x1"])
		self.x2.insert(0, conversionDict["x2"])
		self.y1.insert(0, conversionDict["y1"])
		self.y2.insert(0, conversionDict["y2"])

class DataConfigurator(tk.Frame):
	def __init__(self, master=None, mainApp=None):
		super().__init__(master)
		master.protocol("WM_DELETE_WINDOW", self.close)

		self.mainApp = mainApp # TODO: Remove mainApp

		self.grid()
		self.master.minsize(500, 300)
		self.master.title("Daten konfigurieren")

		self.createGui()

	def refresh(self):
		""" Refreshs all fields of the data configurator """

		#for dataConfiguratorRow in self.dataConfiguratorRows:
		#		for timeDefinitionFrame in dataConfiguratorRow:
		#			pass
		try:
			for timeFrame in self.timesCalculationFrame.timeFrames:
				timeFrame.refreshConditions(self.getDataColumnDefinitions())
		except AttributeError:
			pass

	def getDataColumnDefinitions(self):
		""" Returns a list with dicts holding name and unit of each data column """

		result = list()

		for row in self.dataConfiguratorRows:
			result.append({'name': row.nameField.get(), 'unit': row.Unit_y1.get()})
		
		return result

	def createGui(self):
		""" Menu bar """
		self.menubar = tk.Menu(self)

		self.filemenu = tk.Menu(self.menubar, tearoff=0)
		self.filemenu.add_command(label="Daten exportieren", command=self.exportConfigData)
		self.filemenu.add_command(label="Daten importieren", command=self.importConfigData)
		self.filemenu.add_command(label="Beenden", command=self.close)

		self.master.config(menu=self.menubar)
		self.menubar.add_cascade(label="Datei", menu=self.filemenu)

		""" Frames """
		self.configColsFrame = tk.LabelFrame(master=self, text="Spalten konfigurieren", borderwidth=1,
                                       relief="sunken", width=500, height=400, padx=5, pady=15)
		self.configColsFrame.grid(row=10, column=0, sticky="NW")

		""" Data configurator rows """
		self.constructDataConversionGui()

		""" Time calculations frame """
		self.constructTimeCalculationFrame()

	def constructTimeCalculationFrame(self):
		self.timesCalculationFrame = TimesCalculationFrame(master=self, text="Zeitenberechnung konfigurieren", borderwidth=1,
                                        relief="sunken", width=500, height=400, padx=5, pady=15)
		self.timesCalculationFrame.grid(row=10, column=1, sticky="NW")
		self.timesCalculationFrame.setTimeDefinitions(dataCache.dataDict["TimeDefinitions"])

	def constructDataConversionGui(self):
		self.dataConfiguratorRows = []
		headline = True
		for i in range(len(dataCache.dataDict["DataColumns"])):
			# data configurator rows
			self.dataConfiguratorRows.append(DataConfiguratorRow(
				self.configColsFrame, isHeadline=headline, rowNumber=i))
			headline = False
			self.dataConfiguratorRows[i].grid(
				row=2*i+5, column=2, padx=3, pady=3, columnspan=5)

			try:
				self.dataConfiguratorRows[i].setConversionFunctionParams(
					dataCache.dataDict["DataColumns"]["Spalte"+str(i)]["convFunc"])
			except TypeError:
				self.dataConfiguratorRows[i].setConversionFunctionParams(
					{"x1": 0, "x2": 1, "y1": 0, "y2": 1})
			except KeyError:
				self.dataConfiguratorRows[i].setConversionFunctionParams(
					{"x1": 0, "x2": 1, "y1": 0, "y2": 1})
			except Exception as e:
				raise e

			try:
				self.dataConfiguratorRows[i].nameField.delete(
					0, len(self.dataConfiguratorRows))
				self.dataConfiguratorRows[i].nameField.insert(
					0, dataCache.dataDict["DataColumns"]["Spalte"+str(i)]["name"])
			except KeyError:
				self.dataConfiguratorRows[i].nameField.insert(0, "Spalte"+str(i+1))
			except Exception as e:
				raise e

			try:
				self.dataConfiguratorRows[i].Unit_y1.set(
					dataCache.dataDict["DataColumns"]["Spalte"+str(i)]["Unit"])
			except KeyError:
				self.dataConfiguratorRows[i].Unit_y1.set("V")
			except Exception as e:
				raise e

	def close(self):
		self.safeConfigData()
		self.master.destroy()
		self.mainApp.dataConfigurator = None

	def exportConfigData(self):
		data = {"DataColumns": dict(), "TimeDefinitions": self.timesCalculationFrame.getTimeDefinitions()}
		i = 0
		for _key, _value in dataCache.dataDict["DataColumns"].items():
			# safe conversion data
			data["DataColumns"]['Spalte'+str(i)] = dict()
			data["DataColumns"]['Spalte'+str(i)]["convFunc"] = self.dataConfiguratorRows[i].getConversionFunctionParams()
			data["DataColumns"]['Spalte'+str(i)]["name"] = self.dataConfiguratorRows[i].nameField.get()
			data["DataColumns"]['Spalte'+str(i)]["Unit"] = self.dataConfiguratorRows[i].Unit_y1.get()
			i += 1

		fileObj = filedialog.asksaveasfile(
									title="Select a folder",
									defaultextension='.json',
									filetypes=(("json files", "*.json"), ("all files", "*.*")), 
									parent=self
								)
		filename = fileObj.name
		fileObj.close()

		# save the data to the file
		from dataLoggerParser import JSONParser
		JSONParser.writeJSONFile(filename, data)

	def importConfigData(self):
		# TODO: Implement warning, that current config data will be overriden

		# open the file dialog
		filename = filedialog.askopenfilename(
									title="Select file",
									filetypes=(("jsonX files", "*.json"), ("all files", "*.*")), 
									parent=self
								)

		# load json from file
		from dataLoggerParser import JSONParser
		data = JSONParser.loadJSONFile(filename)

		# override the current dataCache config data with the imported config data
		# The actual (voltage) data is not changed by this
		try:
			for column, value in dataCache.dataDict["DataColumns"].items():
				# safe conversion data
				value["convFunc"] = data['DataColumns'][column]['convFunc']
				value["name"] = data['DataColumns'][column]['name']
				value["Unit"] = data['DataColumns'][column]['Unit']
		except KeyError:
			# If the config data doesn't have all the rows, just leave the additional rows unchanged
			print("The imported config data has less rows than that of the currently loaded file.")

		# safe time definition data
		dataCache.dataDict["TimeDefinitions"] = data['TimeDefinitions']

		# remove the old frames
		for row in self.dataConfiguratorRows:
			row.grid_forget()
		self.timesCalculationFrame.grid_forget()
		
		# reconstruct the frames
		self.constructDataConversionGui()
		self.constructTimeCalculationFrame()

	def safeConfigData(self):
		i = 0
		try:
			for _, value in dataCache.dataDict["DataColumns"].items():
				# safe conversion data
				value["convFunc"] = self.dataConfiguratorRows[i].getConversionFunctionParams()
				value["name"] = self.dataConfiguratorRows[i].nameField.get()
				value["Unit"] = self.dataConfiguratorRows[i].Unit_y1.get()
				i += 1
		except KeyError:
			dataCache.dataDict["DataColumns"] = dict()
			self.safeConfigData()

		# safe time definition data
		dataCache.dataDict["TimeDefinitions"] = self.timesCalculationFrame.getTimeDefinitions()

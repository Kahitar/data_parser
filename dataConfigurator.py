import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class TimeDefinition(tk.Frame):

	def __init__(self, master):
		super().__init__(master)

		self.conditions = dict()

		# time name
		self.name = tk.Entry(self, justify="center")
		self.name.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=(15,0))
		# placeholder label
		tk.Label(self, width=5).grid(row=3, column=0)

		# add condition Button
		self.addConditionButton = tk.Button(self, text="Bedingung hinzufügen", command=self.addCondition)
		self.addConditionButton.grid(row=2, column=2, columnspan=3, pady=(15,0))

		# time delete Button
		self.timeDeleteButton = tk.Button(self, fg="red", text="X", command=lambda: self.master.deleteTimeFrame(self))
		self.timeDeleteButton.grid(row=2, column=5, padx=5, pady=(15,0))

		self.addCondition()

		tk.Button(self, text="test", command=lambda: print(self.getTimeDefinition())).grid()

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	def getTimeDefinition(self):
		""" returns the time definition as a list of dicts describing the calculation inside a dictionary with the time name
		format: {"name", [{"column": <columnName>, "operator": <operator>, "comparator": <compareValue>}, {<...>}]} possibly repeated and 
		connected with a comparison operator """

		returnValue = {self.name.get(): list()}
		for _, value in self.conditions.items():
			returnValue[self.name.get()].append({'column': 	value['fromColumn'].get(),
                        						 'operator': value['logicOperator'].get(),
                        						 'comparator': value['compareValue'].get()
                       							 })
		return returnValue

	def addCondition(self):
		self.conditions[len(self.conditions)] = dict()

		# column name
		self.conditions[len(self.conditions)-1]['fromColumn'] = tk.StringVar(self, value='Spannung')
		self.conditions[len(self.conditions)-1]['fromColumnMenu'] = tk.OptionMenu(
			self, self.conditions[len(self.conditions)-1]['fromColumn'], *('Spannung', 'Spalte1', 'Spalte2'))
		self.conditions[len(self.conditions)-1]['fromColumnMenu'].grid(row=len(self.conditions)+2, column=1)

		# column comparison
		self.conditions[len(self.conditions)-1]['logicOperator'] = tk.StringVar(self, value='>')
		self.conditions[len(self.conditions)-1]['operatorMenu'] = tk.OptionMenu(
			self, self.conditions[len(self.conditions)-1]['logicOperator'], *('>', '≥', '=', '<', '≤'))
		self.conditions[len(self.conditions)-1]['operatorMenu'].grid(row=len(self.conditions)+2, column=2)

		self.conditions[len(self.conditions)-1]['compareValue'] = tk.Entry(self, width=10, justify="center")
		self.conditions[len(self.conditions)-1]['compareValue'].grid(row=len(self.conditions)+2, column=3)
		self.conditions[len(self.conditions)-1]['compareValueLabel'] = tk.Label(self, text="V")
		self.conditions[len(self.conditions)-1]['compareValueLabel'].grid(row=len(self.conditions)+2, column=4, padx=5)
		
		delIdx = len(self.conditions)-1
		self.conditions[len(self.conditions)-1]['deleteRowButton'] = tk.Button(self, text="X", command=lambda: self.deleteRow(delIdx))
		self.conditions[len(self.conditions)-1]['deleteRowButton'].grid(row=len(self.conditions)+2, column=5)

	def deleteRow(self, rowNum):
		# remove the specified row from the row list
		for _, value in self.conditions[rowNum].items():
			try:
				value.grid_forget()
			except AttributeError:
				# value is not a tk widget
				pass
		del self.conditions[rowNum]

class TimesCalculationFrame(tk.Frame):
	def __init__(self, master):
		super().__init__(master)

		tk.Button(self, text="Neue Zeit", command=self.addTimeFrame).grid(column=1)
		self.timeFrames = list()
		self.addTimeFrame()

	def moveTimeDown(self):
		pass

	def addTimeFrame(self):
		newRow = TimeDefinition(self)
		newRow.grid(column=1)
		self.timeFrames.append(newRow)

	def deleteTimeFrame(self, delObj):
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
		tk.Label(self, text=str(rowNumber)).grid(row=2, column=1, padx=20)

		# name field
		self.nameField = tk.Entry(self)
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
		tk.OptionMenu(self, self.Unit_y1, *('V', 'bar', '°C')).grid(row=2, column=8, sticky="w")

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
			# This means it was never necessary call this function since the 
			# conversion params didn't change
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
		self.configColsFrame.grid(row=10, column=0, sticky="NW")
		self.timesCalculationFrame = tk.LabelFrame(master=self, text="Zeitenberechnung konfigurieren", borderwidth=1,
                                        relief="sunken", width=500, height=400, padx=5, pady=15)
		self.timesCalculationFrame.grid(row=10, column=1, sticky="NW")

		""" Data configurator rows """
		self.dataConversionGui()

		""" Time calculations frame """
		TimesCalculationFrame(self.timesCalculationFrame).grid(
				row = 1, column = 2, padx = 3, pady = 3, columnspan = 5)

	def dataConversionGui(self):
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
		self.mainApp.dataConfigurator = None

	def safeConfigData(self):
		i = 0
		for _, value in self.mainApp.dataDict.items():
			value["convFunc"] = self.DataConfiguratorRows[i].getConversionFunctionParams()
			value["name"] = self.DataConfiguratorRows[i].nameField.get()
			value["Unit"] = self.DataConfiguratorRows[i].Unit_y1.get()
			i += 1

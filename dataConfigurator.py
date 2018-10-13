import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class TimeDefinitionRow(tk.Frame):
	_firstInstance = True

	def __init__(self, master):
		super().__init__(master)

		self.numRows=0

		if TimeDefinitionRow._firstInstance:
			TimeDefinitionRow._firstInstance = False

			# make headline
			tk.Label(self, text="Name").grid(
				row=1, column=1, sticky="ew", pady=1)
			tk.Label(self, text="Spalte").grid(
				row=1, column=2, sticky="ew", pady=1)
			tk.Label(self, text="Bedingung").grid(
				row=1, column=3, columnspan=3, sticky="ew", pady=1)

		# time name
		self.name = tk.Entry(self, justify="center", width=15)
		self.name.grid(row=2, column=1, sticky="w")

		self.addRow()

	def setLogic(self):
		pass

	def addRow(self):
		self.numRows += 1

		# column name
		self.fromColumn = tk.StringVar(self, value='Spannung')
		self.fromColumn.trace("w", self.setLogic)
		tk.OptionMenu(self, self.fromColumn, *('Spannung', 'Spalte1', 'Spalte2')
		              ).grid(row=self.numRows+1, column=2, sticky="w")

		# column comparison
		self.logic = tk.StringVar(self, value='>')
		self.logic.trace("w", self.setLogic)
		tk.OptionMenu(self, self.logic, *('>', '≥', '=', '<', '≤')
		              ).grid(row=self.numRows+1, column=3, sticky="w")

		self.condition = tk.Entry(self, width=4, justify="center")
		self.condition.grid(row=self.numRows+1, column=5, sticky="w")
		tk.Label(self, text="V").grid(row=self.numRows+1, column=6, sticky="w", padx=5)

		# column options # TODO: Add option to change row order
		#self.moveButton = tk.Button(self, text="md", command=self.moveRowDown)
		#self.moveButton.grid(row=self.numRows+1, column=7)

		self.addRowButton = tk.Button(self, text="+", command=self.addRow)
		self.addRowButton.grid(row=self.numRows+1, column=8)

		self.deleteRowButton = tk.Button(self, text="X", command=self.deleteRow)
		self.deleteRowButton.grid(row=self.numRows+1, column=9)
		

	def deleteRow(self):
		pass

class TimesCalculationFrame(tk.Frame):
	def __init__(self, master):
		super().__init__(master)

		tk.Button(self, text="Neue Zeit", command=self.addTimeFrame).grid(column=1)
		self.addTimeFrame()

	def moveTimeDown(self):
		pass

	def addTimeFrame(self):
		TimeDefinitionRow(self).grid(column=1)
		
class DataConfiguratorRow(tk.Frame):
	def __init__(self, master, isHeadline=False, rowNumber=0):
		super().__init__(master)

		# headline
		if isHeadline:
			tk.Label(self, text="Spalte").grid(
				row=1, column=1, sticky="ew", padx=3, pady=3)
			tk.Label(self, text="Name").grid(
				row=1, column=3, sticky="ew", padx=3, pady=3)
			tk.Label(self, text="Umrechnung").grid(
				row=1, column=5, columnspan=3, sticky="ew", padx=3, pady=3)
			tk.Label(self, text="Einheit").grid(
				row=1, column=8, sticky="ew", padx=3, pady=3)

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
		tk.OptionMenu(self, self.Unit_y1, *('V', 'bar', '°C')
		              ).grid(row=2, column=8, sticky="w", pady=5)

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
		self.configColsFrame.grid(row=10, column=0)
		self.timesCalculationFrame = tk.LabelFrame(master=self, text="Zeitenberechnung konfigurieren", borderwidth=1,
                                        relief="sunken", width=500, height=400, padx=5, pady=15)
		self.timesCalculationFrame.grid(row=10, column=1)

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

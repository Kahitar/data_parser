#from tqdm import tqdm
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import time

FILES_LOCATION = os.getenv('APPDATA') + "\\data_logger"
if not os.path.isdir(FILES_LOCATION):
	os.mkdir(FILES_LOCATION)

def main():
	root = tk.Tk()
	app = Application(master=root)
	app.mainloop()

def findFilenameSubstr(filename):
		# find the substring indicating the filename without the path
		counter = len(filename) # counter to count the chars of the new directory or file
		for i in range(len(filename)):
			char = filename[i]
			if char == '/' or char == '\\': # start counting the chars from zero
				counter = 0
			elif char == '.': # the substring for the filename was found.
				return filename[i-counter:i+4] # add everything from the last '/' to the substring
				break
			else:
				counter += 1

class Parser(tk.Frame):
	def __init__(self, master=None, mainApp=None):
		super().__init__(master)

		self.mainApp = mainApp

		self.grid()
		self.master.minsize(500, 300)
		self.master.title("Parser data logger")

		self.createGui()

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
		self.load_bar = SimpleProgressBar(self.statusFrame)

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
			msg = messagebox.showinfo("Error", "Bitte zuerst eine Datei zum Parsen auswählen.")
			self.focus_force()
			raise e

		self.setToLoad = tk.Button(self.parserFrame, text="|-> Zur Datenverarbeitung laden",
												command=lambda: self.mainApp.setFileToLoad(outFile))
		self.setToLoad.grid(row=20, column=10, sticky="ew")
		tk.Label(self.parserFrame, text="(Schließt den Parser)", fg="red").grid(row=21,column=10, sticky="ew")

	def loadPreviewValues(self):
		""" Loads the first three rows of the selected file"""
		num_lines = file_len(self.loggerFile)

		self.U_preview = [[] for x in range(6)]

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
					msg = messagebox.showinfo("Error", "Beim Parsen der Datei ist ein Fehler aufgetreten.\nBitte die Datei auf fehlerhafte Zeilen überprüfen.\n\nIn jeder Zeile müssen 8 mit Tabstopp getrennte Werte stehen.\n(Mit ';' beginnende Zeilen werden ignoriert.)")
					print(e)

				for i in range(6):
					self.U_preview[i].append(newU[i])

				# update progress bar
				self.load_bar.update(progress, num_lines)

			# loop finished, fill progress bar
			self.load_bar.update(1, 1)

	def read_datalogger(self, inFile, outFile):
		
		num_lines = file_len(inFile)
		valid_lines = 0
		parseColumns = [a.get() for a in self.columnSelectionVars] # columns to parse are 1, the others 0
		self.U = [[] for x in range(sum(parseColumns))]

		# open input file and parse it
		with open(inFile, "r") as file_obj:
			for progress, line in enumerate(file_obj):

				if line[0] == ";":
					continue

				newU = [None for x in range(6)]
				try:
					newDate, counter, newU[0], newU[1], newU[2], newU[3], newU[4], newU[5] = line.replace("\n", "").split("	")
				except Exception as e:
					msg = messagebox.showinfo("Error", "Beim Parsen der Datei ist ein Fehler aufgetreten.\nBitte die Datei auf fehlerhafte Zeilen überprüfen.\n\nIn jeder Zeile müssen 8 mit Tabstopp getrennte Werte stehen.\n(Mit ';' beginnende Zeilen werden ignoriert.)")
					print(e)

				j = 0
				for k, val in enumerate(newU):
					if parseColumns[k] == 1:
						self.U[j].append(val)
						j += 1

				# update progress bar
				self.load_bar.update(progress, num_lines)

			# loop finished, fill progress bar
			self.load_bar.update(1, 1)

		# open output file and save voltages
		with open(outFile, "w") as outFile_obj:
			for j in range(len(self.U[0])):
				for i in range(len(self.U)):
					outFile_obj.write("{} ".format(self.U[i][j]))
				outFile_obj.write("\n")


class Application(tk.Frame):
	def __init__(self, master=None):
		master.protocol("WM_DELETE_WINDOW", self.closeApp)

		super().__init__(master)

		self.grid()
		self.master.minsize(500,500)
		self.master.title("Data logger")

		self.createGui()

	def closeApp(self):
		try:
			self.parser.master.destroy()
		except:
			pass
		self.master.destroy()

	def createGui(self):
		""" Menu bar """
		self.menubar = tk.Menu(self)
		self.master.config(menu=self.menubar)

		self.filemenu = tk.Menu(self.menubar, tearoff=0)
		self.filemenu.add_command(label="Parser öffnen", command=self.initParser)
		self.filemenu.add_command(label="Beenden", command=self.closeApp)
		self.menubar.add_cascade(label="Datei", menu=self.filemenu)

		""" Frames """
		self.statusFrame = tk.Frame(master=self, borderwidth=1, padx=5, pady=5)
		self.statusFrame.grid(column=0, row=5)

		self.dataFrame = tk.LabelFrame(master=self, text="Daten verarbeiten", borderwidth=1, relief="sunken", width=500, height=200, padx=5, pady=5)
		self.dataFrame.grid(column=0, row=15)
		self.dataFrame.grid_propagate(False)

		self.diagrammFrame = tk.LabelFrame(master=self, text="Diagramme", borderwidth=1, relief="sunken", padx=5, pady=15)
		self.diagrammFrame.grid(column=0, row=25, sticky="nsew")

		""" Loading bar """
		self.load_bar = SimpleProgressBar(self.statusFrame)

		""" Buttons and Labels """
		self.openFileButton = tk.Button(self.dataFrame, text="Datei öffnen", command=self.loadFile)
		self.openFileButton.grid(row=3, column=5, sticky="ew")

		self.fileLabel = tk.Label(self.dataFrame, text="", borderwidth=0, width=40)
		self.fileLabel.grid(row=3, column=10, sticky="w")

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
	
	def initParser(self):
		# start the parser as a toplevel widget
		self.parser = Parser(tk.Toplevel(), self)
		self.parser.mainloop()

	def setFileToLoad(self, file):
		self.file = file

		# find the substring indicating the filename without the path
		label = findFilenameSubstr(self.file)

		# set the file Label showing the selected file with the previously found substring
		try:
			self.fileLabel['text'] = label
		except UnboundLocalError:
			raise e
		except Exception as e:
			raise e

		# kill the parser
		self.parser.master.destroy()
		
		# parse the file
		self.readVoltages()
	

	def loadFile(self):
		# open the file dialog
		selectedFile = filedialog.askopenfilename(initialdir=FILES_LOCATION, title="Select file", 
													filetypes=(("txt files","*_PYOUTPUT.txt"),))
		# check if a file was read in
		if selectedFile == '': # file dialog was canceled
			return
		else:
			self.file = selectedFile

		# find the substring indicating the filename without the path
		label = findFilenameSubstr(self.file)

		# set the file Label showing the selected file with the previously found substring
		try:
			self.fileLabel['text'] = label
		except UnboundLocalError:
			raise e
		except Exception as e:
			raise e

		# parse the file
		self.readVoltages()

	# aktualisiert die Zeiten-Tabelle und zeigt diese an. Ausführen über Button.
	def showTimes(self): 
		try:
			self.calculateTimes()
		except AttributeError:
			msg = messagebox.showinfo("Error", "Bitte zuerst Daten einlesen!")
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

	def readVoltages(self):
		try:
			file = self.file

			if file == '':
				raise AttributeError
		except AttributeError:
			msg = messagebox.showinfo("Error", "Bitte zuerst eine Datei öffnen.")
			return
		except FileNotFoundError:
			msg = messagebox.showinfo("Error", "Bitte eine korrekte Datei öffnen.")
			return
		except Exception as e:
			raise e

		num_lines = file_len(file)

		self.U = [[] for x in range(6)]

		with open(file, "r") as file_obj:
			# read the voltages from the previously created pyoutput file
			for progress, line in enumerate(file_obj):

				try:
					new_U1, new_U2, new_U3 = line.rstrip().split(" ")
				except ValueError:
					msg = messagebox.showinfo("Error", "Die ausgewählte Datei hat nicht das richtige Format.\nBitte andere Datei auswählen.")
					return
				except Exception as e:
					raise e

				self.U[0].append(float(new_U1.replace(",", ".")))
				self.U[1].append(float(new_U2.replace(",", ".")))
				self.U[2].append(float(new_U3.replace(",", ".")))

				# write progress bar
				self.load_bar.update(progress, num_lines)

		# loop finished, fill progress bar
		self.load_bar.update(1, 1)

		# <========== temp ==========
		self.U1 = self.U[0]
		self.U2 = self.U[1]
		self.U3 = self.U[2]
		#  ========== temp ==========>

		self.t_ges = None
		self.t_on = None
		self.t_240bar = None
		self.t_poti_lowest = None
		self.t_poti_highest = None
		self.t_poti_between = None
		self.t_schwemm = None
		self.n_poti = None
		self.p_OnAvg = None

		self.updateTimeTable()

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

		# constants
		max_Possible_Pressure = 250 # [bar]
		U1_volts_per_Bar = 10 / 400 # [V/bar]

		# evaluate data
		for i in range(len(self.U1)):

			turnedOn = False
			# count time device on
			if self.U2[i] > 20:
				turnedOn = True
				time_on.append(i)

			# device on and highest pressure
			if turnedOn and self.U1[i] > 6.0:
				time_highest_pressure.append(i)

			# values when the device is turned on
			if turnedOn:
				# calculate sum for average pressure when turned on
				sumPressureOn += self.U1[i]
				sumPressureOnCount += 1

				# find schwemmbetrieb
				if i > 0:
					if self.U2[i] < limit_schwemm and self.U2[i] == self.U2[i-1]:
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
			self.load_bar.update(i, len(self.U1))
		
		# loop finished, fill progress bar
		self.load_bar.update(1, 1)

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
			plt.title("Drucksensor, 0-250 bar")

			plt.subplot(212)
			self.plot_U2()

		except AttributeError:
			msg = messagebox.showinfo("Error", "Bitte zuerst eine Datei öffnen!")
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
			msg = messagebox.showinfo("Error", "Bitte zuerst eine Datei öffnen!")
		except Exception as e:
			raise e

	def plot_U3(self):
		try:
			p3_bar = [100 + u * 150 / 10 for u in self.U3]

			plt.figure(figsize=(2, 1))
			plt.subplot(211)
			plt.plot(p3_bar[0:80000])
			plt.xlabel("Zeit [sec]")
			plt.ylabel("Poti setting [bar]")
			plt.title("Schiebepotentiometer, 100-250 bar")
			plt.subplot(212)
			
			isOn = [1 if x > 15 else 0 for x in self.U2]

			plt.plot(isOn[0:80000])
			plt.xlabel("Zeit [sec]")
			plt.ylabel("Ein/Aus [-]")
			plt.title("Gerät an/aus")
			
			plt.show()
		except AttributeError:
			msg = messagebox.showinfo("Error", "Bitte zuerst eine Datei öffnen!")
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

	def __init__(self, parent, total=100):
		tk.Frame.__init__(self, parent)

		self.progressbar = ttk.Progressbar(master=parent, length=200, 
											mode='determinate', maximum=total)
		self.progressbar.grid(column=0, row=0)
		
		self.progressLabel = tk.Label(parent, text="0%", width=5)
		self.progressLabel.grid(column=1, row=0)

		self.updateTime = 0.005 # ms
		self.lastUpdate = time.time()

	def update(self, count, total=None):
		if count == total:
			self.progressbar['maximum'] = total
			self.progressbar['value'] = count
			self.progressLabel['text'] = "100%"
		elif time.time() - self.lastUpdate > self.updateTime:
			if total != None:
				self.progressbar['maximum'] = total
			
			percents = round(100.0 * count / float(self.progressbar['maximum']), 1)
	    	
			self.progressbar['value'] = count
			self.progressLabel['text'] = str(percents) + '%'
			self.progressbar.update_idletasks()

			self.lastUpdate = time.time()

# length of a file
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def plot_voltages(voltages, indices):
	voltages_to_plot = []
	for i in indices:
		voltages_to_plot.append(voltages[i])

	plt.plot(indices,voltages_to_plot)
	plt.show()

if __name__ == '__main__': main()

#from tqdm import tqdm
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sys

def main():
	root = tk.Tk()
	app = Application(master=root)
	app.mainloop()

class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.grid()
		self.master.minsize(500,500)
		#self.master.geometry("1000x700")
		self.master.title("Application")

		self.menuFrame = tk.Frame(master=self, padx=5, pady=5)
		self.menuFrame.grid(column=0, row=5)

		self.dataFrame = tk.LabelFrame(master=self, text="Fetching data", borderwidth=1, relief="sunken", width=500, height=250, padx=5, pady=5)
		self.dataFrame.grid(column=0, row=15)
		self.dataFrame.grid_propagate(False)

		self.diagrammFrame = tk.LabelFrame(master=self, text="Diagramms", borderwidth=1, relief="sunken", padx=5, pady=15)
		self.diagrammFrame.grid(column=0, row=25, sticky="nsew")

		self.statusFrame = tk.Frame(master=self, borderwidth=1, padx=5, pady=5)
		self.statusFrame.grid(column=0, row=10)

		self.load_bar = SimpleProgressBar(self.statusFrame)

		self.createGui()

	def createGui(self):
		self.read_file = tk.Button(self.dataFrame, text="Daten einlesen", command=self.readVoltages)
		self.read_file.grid(row=5, column=5, sticky="ew")

		self.ZeitenButton = tk.Button(self.dataFrame, text="Laufzeiten berechnen", command=self.showTimes)
		self.ZeitenButton.grid(row=6, column=5, sticky="ew")

		self.table = SimpleTable(self.dataFrame, 8, 2)
		self.table.grid(row=6, column=10, rowspan=9, padx=10)
		self.updateTimeTable()

		self.U2_plot = tk.Button(self.diagrammFrame, text="Zustand über Zeit", command=self.plot_U2)
		self.U2_plot.grid(row=0, column=2)

		self.U3_plot = tk.Button(self.diagrammFrame, text="Poti über Zeit", command=self.plot_U3)
		self.U3_plot.grid(row=0, column=3)
		
		self.U1_plot = tk.Button(self.diagrammFrame, text="Druck über Zeit", command=self.plot_U1)
		self.U1_plot.grid(row=0, column=4)

		self.quit = tk.Button(self.menuFrame, text="QUIT", fg="red", command=self.master.destroy)
		self.quit.grid(row=0, column=0, padx=10)

	def showTimes(self):
		try:
			self.calculateTimes()
		except Exception as e:
			msg = messagebox.showinfo("Error", "Fehler: Bitte zuerst Daten einlesen!")
			raise e
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
			self.table.set(1,1,"{0:.2f} h".format(0))
		self.table.set(2,0,"p > 240bar")
		try:
			self.table.set(2,1,"{0:.2f} h".format(self.t_240bar/60/60))
		except:
			self.table.set(2,1,"{0:.2f} h".format(0))
		self.table.set(3,0,"Schwemm")
		try:
			self.table.set(3,1,"{0:.2f} h".format(self.t_schwemm/60/60))
		except:
			self.table.set(3,1,"{0:.2f} h".format(0))
		self.table.set(4,0,"Poti 100V")
		try:
			self.table.set(4,1,"{0:.2f} h".format(self.t_poti_lowest/60/60))
		except:
			self.table.set(4,1,"{0:.2f} h".format(0))
		self.table.set(5,0,"Poti 250V")
		try:
			self.table.set(5,1,"{0:.2f} h".format(self.t_poti_highest/60/60))
		except:
			self.table.set(5,1,"{0:.2f} h".format(0))
		self.table.set(6,0,"Poti mitte")
		try:
			self.table.set(6,1,"{0:.2f} h".format(self.t_poti_between/60/60))
		except:
			self.table.set(6,1,"{0:.2f} h".format(0))
		self.table.set(7,0,"N Poti")
		try:
			self.table.set(7,1,self.n_poti)
		except:
			self.table.set(7,1,0)
		self.update_idletasks()

	def readVoltages(self):
		file_folder = "files/"
		file = file_folder + "gerät1_voltages_after_test_PYOUTPUT.txt"

		num_lines = file_len(file)

		file_obj = open(file, "r")

		self.U1 = [] # pressure: 0-400bar (0-10V)
		self.U2 = [] # <1V: on, >23V: off
		self.U3 = [] # Schiebepoti: 100-250bar (0-10V)

		# read the voltages from the previously created pyoutput file
		print("\n")
		print("Parsing file {}...".format(file))
		i = 0
		for line in file_obj:

			# write progress bar
			if i / num_lines * 1000 % 1 >= 0.999:
				self.load_bar.update(i, num_lines)
			i += 1

			new_U1, new_U2, new_U3 = line.replace("\n", "").split(" ")

			self.U1.append(float(new_U1.replace(",", ".")))
			self.U2.append(float(new_U2.replace(",", ".")))
			self.U3.append(float(new_U3.replace(",", ".")))

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

			# write progress bar
			if i / len(self.U1) * 1000 % 1 >= 0.99:
				self.load_bar.update(i, len(self.U1))

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

		except Exception as e:
			msg = messagebox.showinfo("Error", "Fehler: Bitte zuerst Daten einlesen!")
			print(e)

	def plot_U2(self):
		try:
			isOn = [1 if x > 15 else 0 for x in self.U2]

			plt.plot(isOn)
			plt.xlabel("Zeit [sec]")
			plt.ylabel("Ein/Aus [-]")
			plt.title("Gerät an/aus")
			plt.show()
		except Exception as e:
			msg = messagebox.showinfo("Error", "Fehler: Bitte zuerst Daten einlesen!")
			print(e)

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
		except Exception as e:
			msg = messagebox.showinfo("Error", "Error: Bitte zuerst Daten einlesen!")
			print(e)

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

		self.progressbar = ttk.Progressbar(master=parent, length=200, mode='determinate', maximum=total)
		self.progressbar.grid(column=0, row=0)
		
		self.progressLabel = tk.Label(parent, text="0%", width=5)
		self.progressLabel.grid(column=1, row=0)

	def update(self, count, total=None):
		if total != None:
			self.progressbar['maximum'] = total
		
		self.progressbar['value'] = count
		self.progressbar.update_idletasks()

		percents = round(100.0 * count / float(self.progressbar['maximum']), 1)
    	
		self.progressLabel['text'] = str(percents) + '%'

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
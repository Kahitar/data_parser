import tkinter as tk

class TkTable(tk.Frame):
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

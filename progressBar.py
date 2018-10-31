import tkinter as tk
from tkinter import ttk
import time

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

		self.updateTime = 0.005  # ms
		self.lastUpdate = time.time()

	def update(self, count, total=None, msg=""):
		if count == total:
			self.progressbar['maximum'] = total
			self.progressbar['value'] = count
			self.progressLabel['text'] = ""
			self.messageLabel['text'] = msg
			self.progressbar.update_idletasks()
		elif time.time() - self.lastUpdate > self.updateTime:
			if total != None:
				self.progressbar['maximum'] = total

			percents = round(100.0 * count / float(self.progressbar['maximum']), 1)

			self.progressbar['value'] = count
			self.progressLabel['text'] = str(percents) + '%'
			self.messageLabel['text'] = msg
			self.progressbar.update_idletasks()

			self.lastUpdate = time.time()

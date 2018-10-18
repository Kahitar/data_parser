import time
import os

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

def findFilenameSubstr(filename):
	""" find the substring indicating the filename without the path
	counter to count the chars of the new directory or file """

	counter = len(filename)
	for i, char in enumerate(filename):
		if char == '/' or char == '\\':  # start counting the chars from zero
			counter = 0
		elif char == '.':  # the substring for the filename was found.
			# add everything from the last '/' to the substring
			return filename[i-counter:i+4]
		else:
			counter += 1

def file_len(fname):
	""" returns the length (number of lines) of a file """

	with open(fname) as f:
		for i, _ in enumerate(f):
			pass
	return i + 1

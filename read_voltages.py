# progress bar
import sys
def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def read_datalogger(inFile, outFile):
	file_folder = "files/"
	file = file_folder + inFile

	num_lines = file_len(file)

	file_obj = open(file, "r")

	valid_lines = 0

	U1 = [] # pressure: 0-400bar (0-10V)
	U2 = [] # <1V: on, >23V: off
	U3 = [] # Schiebepoti: 100-250bar (0-10V)

	i = 0
	print("\n")
	print("Parsing file {}...".format(file))
	for line in file_obj:

		# write progress bar
		if i / num_lines * 1000 % 1 >= 0.999:
			progress(i, num_lines)
		i += 1

		line = line.rstrip("\n")

		if line[0] == ";":
			continue

		valid_lines += 1

		tab_counter = 0
		new_U1 = ""
		new_U2 = ""
		new_U3 = ""
		for char in line:

			if char == "	":
				tab_counter += 1
				continue

			if tab_counter == 5:
				new_U1 = new_U1 + char

			if tab_counter == 6:
				new_U2 = new_U2 + char

			if tab_counter == 7:
				new_U3 = new_U3 + char

		U1.append(float(new_U1.replace(",", ".")))
		U2.append(float(new_U2.replace(",", ".")))
		U3.append(float(new_U3.replace(",", ".")))

	print("\n")
	outFile = file_folder + outFile
	outFile_obj = open(outFile, "w")

	for i in range(len(U1)):
		outFile_obj.write("{} {} {}\n".format(U1[i], U2[i], U3[i]))

	outFile_obj.close()

if __name__ == "__main__": read_datalogger("Gerät1_nach_Feldtest.txt", "gerät1_voltages_after_test_PYOUTPUT.txt")
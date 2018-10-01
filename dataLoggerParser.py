import json
from tkinter import messagebox

class RawDataParser:
    pass

class JSONParser:

    def loadJSONFile(self, file):
        """ Reads the JSON data from a file into memory and returns it as a dictionary """
        # TODO: Do I need these error checkings?
        try:
            if file == '':
                raise AttributeError
        except AttributeError:
            messagebox.showinfo("Error", "Keine Datei ausgewählt.")
            return
        except FileNotFoundError:
            messagebox.showinfo("Error", "Die Datei konnte nicht gefunden werden")
            return
        except Exception as e:
            raise e

        with open(file, "r") as file_obj:
            dataDict = json.load(file_obj)

        return dataDict

    def writeJSONFile(self, outFile, dataDict):
        """ write a data dictionary to the output file as JSON """

        with open(outFile, "w") as f:
            json.dump(dataDict, f)

def file_len(fname):
    """ Returns the length of the file """
    with open(fname) as f:
        for i, _ in enumerate(f):
            pass
    return i + 1
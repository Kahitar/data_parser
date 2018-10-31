import json
from dataLoggerParser import JSONParser

currFile = ""
dataDict = dict()

def loadDataFromFile(file, deleteOldData=False):
    """ Saves the data currently loaded to the current file 
    and loads the data from the new file
    """

    global currFile
    global dataDict

    # make sure the curerntly loaded data doesn't get lost (save it to its file)
    if dataDict and not deleteOldData: # the dataDict is not empty 
                                            # and it's data should be saved
        try:
            saveDataToFile(currFile)
        except NoFileSpecifiedError: # no file loaded yet
            # save the data to a temporary file
            tempFile = "unsaved_Data.json"
            saveDataToFile(tempFile)

            # print warnings
            print("Data was cached when trying to load a new file.\nThe data was saved to the temporary file " + tempFile)
            print("The file will be overriden if this error happens again!")
        except Exception as e:
            print("Couldn't save data. Data is now lost...")
            print(e)
    
    # load data from new file
    dataDict = JSONParser.loadJSONFile(file)

    # save the file as current file
    currFile = file

def saveDataToFile(file=None):
    """ Saves the currently loaded data to a file. 
    If no file was specified, the currently loaded file will be used as destination
    """

    global dataDict
    global currFile

    # check wether a file was specified
    if file == None:
        # if no fiel was specified, save the data to the currently loaded file
        if currFile != "":
            file = currFile
        else:
            raise NoFileSpecifiedError("Keine Datei zum Speichern der Daten verfügbar.")
    
    # save the data to the file
    JSONParser.writeJSONFile(file, dataDict)

class NoFileSpecifiedError(AttributeError):
    def __init__(self, message):
        super().__init__(message)
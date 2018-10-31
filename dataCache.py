import json

class DataCache:

    def __init__(self):
        self.currFile = ""
        self.dataDict = dict()

    def loadDataFromFile(self, file, deleteOldData=False):
        """ Saves the data currently loaded to the current file 
        and loads the data from the new file
        """

        # make sure the curerntly loaded data doesn't get lost (save it to its file)
        if self.dataDict and not deleteOldData: # the dataDict is not empty 
                                                # and it's data should be saved
            try:
                self.saveDataToFile(self.currFile)
            except NoFileSpecifiedError: # no file loaded yet
                # save the data to a temporary file
                tempFile = "unsaved_Data.json"
                self.saveDataToFile(tempFile)

                # print warnings
                print("Data was cached when trying to load a new file.\nThe data was saved to the temporary file " + tempFile)
                print("The file will be overriden if this error happens again!")
            except Exception as e:
                print("Couldn't save data. Data is now lost...")
                print(e)
        
        # load data from new file
        with open(file, "r") as f:
            self.dataDict = json.load(f)

        # save the file as current file
        self.currFile = file

    def saveDataToFile(self, file=None):
        """ Saves the currently loaded data to a file. 
        If no file was specified, the currently loaded file will be used as destination
        """

        # check wether a file was specified
        if file == None:
            # if no fiel was specified, save the data to the currently loaded file
            if self.currFile != "":
                file = self.currFile
            else:
                raise NoFileSpecifiedError("Keine Datei zum Speichern der Daten verfügbar.")
        
        # save the data to the file
        with open(file, "w") as f:
            json.dump(self.dataDict, f)

class NoFileSpecifiedError(AttributeError):
    def __init__(self, message):
        super().__init__(message)
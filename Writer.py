class FileWriter:
    def writeDataToFile(self, data, outputFileName):
        f = open(outputFileName, "wb")
        f.write(data)

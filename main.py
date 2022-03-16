from Reader import FileReader
from InstrParser import InstructionParser
from Utils import writeDataToFile
from InstrParser import opcodeForInstruction
from Instr import *

def main():
	reader = FileReader()
	reader.loadFile("example.asm")

	lineTokens = reader.getLineTokens()

	parser = InstructionParser()
	parser.parseLines(lineTokens)

	romData = parser.getBinaryData()
	if romData == None:
		print("There was an error with getting output data")
		return

	writeDataToFile(romData, "output.bin")

if __name__ == "__main__":
	main()
from Reader import FileReader
from InstrParser import InstructionParser
from Utils import writeDataToFile
from InstrParser import opcodeForInstruction
from Instr import *
"""
def testInstruction(name, params):
    testInstruction = Instruction(name, params, 0, INSTR_ADDRESSING_MODES[matchInstruction(name)[1]], 0, False)
    testInstruction = instructionValidAndAddressingMode
    return opcodeForInstruction(testInstruction, 0, [None], testInstruction.address)

def runTests():
    addWithCarry = "adc"
    addWithCarryHexImmediate = ["#$43"]
    addWithCarryBinaryAbsoluteX = ["$72f3", "x"]
    
    if testInstruction(addWithCarry, addWithCarryHexImmediate) != 0x6943:
        print("ADC test failed")
    print("%04x" % testInstruction(addWithCarry, addWithCarryBinaryAbsoluteX))
"""
def main():
    reader = FileReader()
    reader.loadFile("example.asm")

    lineTokens = reader.getLineTokens()

    parser = InstructionParser()
    parser.parseLines(lineTokens)

    romData = parser.getBinaryData()
    if romData == None:
        print("There was an error with getting the data")
        return

    writeDataToFile(romData, "output.bin")




if __name__ == "__main__":
    main()
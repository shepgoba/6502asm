from Instr import *
from Label import *
from array import array

def addressingModeIndex(addressingMode):
    idx = 0

    while addressingMode != 0:
        addressingMode >>= 1
        idx += 1

    return idx

def parseInstruction(addressingModes, instrParams, lineNumber):
    paramCount = len(instrParams)
    if paramCount == 0:
        exitWithError("Line %i: Invalid parameters", lineNumber)

    if paramCount == 1:
        firstParam = instrParams[0]

        if firstParam == "A" and addressingModes & ACCUMULATOR_ENCODING:
            return (True, ACCUMULATOR_ENCODING, 1, False)

        if firstParam[0] == "[" and firstParam[-1] == "]" and addressingModes & INDIRECT_ENCODING:
            resultSuccess, resultNumber = numForString(firstParam[1:-1], None)
            if resultNumber > 0xffff:
                print("Line %i: Value is beyond instruction encoding" % lineNumber)
            return (resultSuccess, INDIRECT_ENCODING, 3, False)

        # has immediate
        if firstParam[0] == '#' and len(firstParam) > 1:
            if addressingModes & IMMEDIATE_ENCODING:
                result = numForString(firstParam[1::], None)
                resultSuccess = result[0]

                if not resultSuccess:
                    exitWithError("Line %i: Invalid token %s", lineNumber, firstParam)
                return (True, IMMEDIATE_ENCODING, 2, False)
        elif addressingModes & ABSOLUTE_ENCODING or addressingModes & ZEROPAGE_ENCODING or addressingModes & RELATIVE_ENCODING:

            firstParam = instrParams[0]

            resultSuccess, resultNumber = numForString(firstParam, None)

            usesLabel = isLabel(firstParam)

            if not usesLabel and not resultSuccess:
                print("rip")
                exitWithError("Line %i: Invalid token %s", lineNumber, firstParam)



            if addressingModes & ZEROPAGE_ENCODING and not usesLabel and resultNumber <= 0xFF:

                return (True, ZEROPAGE_ENCODING, 2, False)
            elif addressingModes & RELATIVE_ENCODING:
                return (True, RELATIVE_ENCODING, 2, usesLabel)
            elif addressingModes & ABSOLUTE_ENCODING:
                return (True, ABSOLUTE_ENCODING, 3, usesLabel)
                
    elif (addressingModes & ABSOLUTE_ENCODING or addressingModes & ABSOLUTE_X_ENCODING 
         or addressingModes & ABSOLUTE_Y_ENCODING or addressingModes & ZEROPAGE_X_ENCODING 
         or addressingMode & ZEROPAGE_Y_ENCODING or addressingModes & INDIRECT_Y_ENCODING):

         
        firstParam = instrParams[0]
        result = numForString(firstParam, None)
        resultSuccess = result[0]
        resultNumber = result[1]

        usesLabel = isLabel(firstParam) and not resultSuccess
        if firstParam[0] == "[" and firstParam[-1] == "]" and addressingModes & INDIRECT_Y_ENCODING:
            if instrParams[1].lower() == "y":
                resultSuccess, num = numForString(firstParam[1:-1], None)
                if resultNumber > 0xff:
                    print("Line %i: Value is beyond instruction encoding" % lineNumber)
                return (resultSuccess, INDIRECT_Y_ENCODING, 2, usesLabel)
            else:
                exitWithError("Line %i: Invalid parameter \"%s\" (must be register y)", lineNumber, instrParams[1])
 
        if firstParam[0] == "[" and instrParams[1][-1] == "]" and addressingModes & INDIRECT_X_ENCODING:
            if instrParams[1].lower() == "x]":
                resultSuccess, num = numForString(firstParam[1:], None)
                if resultNumber > 0xff:
                    print("Line %i: Value is beyond instruction encoding" % lineNumber)
                return (resultSuccess, INDIRECT_X_ENCODING, 2, usesLabel)

        if (resultSuccess or isLabel(firstParam)) and paramCount == 2:

            if instrParams[1].lower() == 'x':
                
                if resultNumber > 0xFF or not addressingModes & ZEROPAGE_X_ENCODING:
                    if addressingModes & ABSOLUTE_X_ENCODING:
                        return (True, ABSOLUTE_X_ENCODING, 3, usesLabel)
                else:
                    if addressingModes & ZEROPAGE_X_ENCODING:
                        return (True, ZEROPAGE_X_ENCODING, 2, usesLabel)
            elif instrParams[1].lower() == 'y':
                if resultNumber > 0xFF:
                    if addressingModes & ABSOLUTE_Y_ENCODING:
                        return (True, ABSOLUTE_Y_ENCODING, 3, usesLabel)
                else:
                    if addressingModes & ZEROPAGE_Y_ENCODING:
                        return (True, ZEROPAGE_Y_ENCODING, 2, usesLabel)
            else:
                #print("addrMode: %i" % addressingModes)
                exitWithError("Line %i: Invalid parameter \"%s\" (must be register X or Y)", lineNumber, instrParams[1])


    exitWithError("Line %i: Invalid token %s", lineNumber, firstParam)


def opcodeForInstruction(instr, lineNumber, validLabels, address):

    instrName = instr.mnemonic.lower()
    addrModeIndex = addressingModeIndex(instr.addressingMode) - 1
    wasFound, instrIndex = matchInstruction(instrName)
    
    print("instr.name: %s, address: %s, addrModeIndex: %i" % (instrName, address, addrModeIndex))

    if instr.addressingMode == ADDRESSINGMODENONE:
        return IMPLIED_OPCODE_TABLE[instrIndex](instr, lineNumber)
    return PARSER_FOR_ADDRESSING_MODE[addrModeIndex](instr, INSTRUCTION_ENCODINGS[instrIndex][addrModeIndex], validLabels, address)

class InstructionParser: 
    currentAddress = 0
    maxAddress = 0
    instructions = []
    labels = []
    hasReadFile = False
    finalbinary = [0]*0xffff

    def isInstructionNameValid(self, instrName):
        return matchInstruction(instrName)[0]

    def getInstructionInformation(self, addressingModes, instrParams, lineNumber):
        if addressingModes == ADDRESSINGMODENONE and len(instrParams) == 0:
            return (True, ADDRESSINGMODENONE, 1, False)


        return parseInstruction(addressingModes, instrParams, lineNumber)

    
    def parseLines(self, tokens):
        linesToRemove = []
        for lineIndex, line in enumerate(tokens):
            if line == None:
                continue

            opcodeOffset = 0
            lineNumber = lineIndex + 1

            firstToken = line[0]
            
            # is label
            if firstToken.endswith(":"):
                newLabel = Label(firstToken[:-1], self.currentAddress)
                self.labels.append(newLabel)
                if len(line) < 2:
                    continue

                opcodeOffset += 1
            nextToken = line[opcodeOffset]
            # is directive
            if nextToken.startswith("."):
                directiveName = nextToken[1:]
                if directiveName == "db":
                    for tokenIdx in range(opcodeOffset + 1, len(line)):
                        success, number = numForString(line[tokenIdx], None)
                        if not success:
                            print("Line %i: Invalid number" % lineNumber)
                        if number > 0xFF:
                            exitWithError("Line %i: Can't fit value in a byte." % lineNumber)
                            #number &= 0xff

                        self.finalbinary[self.currentAddress] = number
                        self.currentAddress += 1

                elif directiveName == "org":
                    success, number = numForString(line[opcodeOffset + 1], None)
                    if not success:
                        exitWithError("Line %i: Invalid number" % lineNumber)
                    if number > 0xffff:
                        exitWithError("Line %i: Too large!" % lineNumber)
                        
                    self.currentAddress = number
                    
                if self.currentAddress > self.maxAddress:
                    self.maxAddress = self.currentAddress
                continue

            instrName = line[opcodeOffset]

            if not self.isInstructionNameValid(line[opcodeOffset]):
                exitWithError("Invalid instruction \"%s\" on line %i" % (instrName, lineNumber))
                return
   
            paramsSlice = line[(opcodeOffset + 1)::]

            parametersValid, addressingModeUsed, instrSize, usesLabel = self.getInstructionInformation(INSTR_ADDRESSING_MODES[matchInstruction(instrName)[1]], paramsSlice, lineNumber)
            if not parametersValid:
                exitWithError("Invalid parameters for instruction \"%s\" on line %i" % (instrName, lineNumber))
                return

            newInstruction = Instruction(instrName, paramsSlice, self.currentAddress, addressingModeUsed, instrSize, usesLabel)
            self.instructions.append(newInstruction)

            print("%04x: %s with addressing mode %s" % (self.currentAddress, newInstruction.mnemonic, addressingModeUsed))


            self.currentAddress += instrSize

            if self.currentAddress > self.maxAddress:
                self.maxAddress = self.currentAddress

        self.currentAddress = 0
        for instr in self.instructions:
            opcode = opcodeForInstruction(instr, lineNumber, self.labels, instr.address)

            print("%06x: %06x" % (self.currentAddress, opcode))

            if opcode > 0xFFFF:
                self.finalbinary[instr.address] = (opcode & 0xff0000) >> 16
                self.finalbinary[instr.address + 1] = (opcode & 0x00ff00) >> 8
                self.finalbinary[instr.address + 2] = (opcode & 0xff)
            elif opcode > 0xFF:
                self.finalbinary[instr.address] = (opcode & 0xff00) >> 8
                self.finalbinary[instr.address + 1] = (opcode & 0x00ff)
            else:
                self.finalbinary[instr.address] = opcode

            self.currentAddress += instr.size

        self.hasReadFile = True

    def getBinaryData(self):
        if self.hasReadFile:
            f = open("output.bin", "wb")
            bytes = bytearray(self.finalbinary)
            return bytes[:self.maxAddress]


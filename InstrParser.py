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

			usesLabel = Label.isValid(firstParam)

			if not usesLabel and not resultSuccess:
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

		usesLabel = Label.isValid(firstParam) and not resultSuccess
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

		if (resultSuccess or Label.isValid(firstParam)) and paramCount == 2:

			if instrParams[1].lower() == 'x':
				if addressingModes & ZEROPAGE_X_ENCODING and not usesLabel and resultNumber <= 0xFF:
					return (True, ZEROPAGE_X_ENCODING, 2, False)
				elif addressingModes & ABSOLUTE_X_ENCODING:
					return (True, ABSOLUTE_X_ENCODING, 3, usesLabel)
			elif instrParams[1].lower() == 'y':
				if addressingModes & ZEROPAGE_Y_ENCODING and not usesLabel and resultNumber <= 0xFF:
					return (True, ZEROPAGE_Y_ENCODING, 2, False)
				elif addressingModes & ABSOLUTE_Y_ENCODING:
					return (True, ABSOLUTE_Y_ENCODING, 3, usesLabel)
			else:
				exitWithError("Line %i: Invalid parameter \"%s\" (must be register X or Y)", lineNumber, instrParams[1])


	exitWithError("Line %i: Invalid tokenss %s", lineNumber, firstParam)


def opcodeForInstruction(instr, lineNumber, validLabels, address):

	instrName = instr.mnemonic.lower()
	addrModeIndex = addressingModeIndex(instr.addressingMode) - 1
	wasFound, instrIndex = matchInstruction(instrName)
	
	if instr.addressingMode == ADDRESSINGMODENONE:
		return IMPLIED_OPCODE_TABLE[instrIndex](instr, lineNumber)
	return PARSER_FOR_ADDRESSING_MODE[addrModeIndex](instr, INSTRUCTION_ENCODINGS[instrIndex][addrModeIndex], validLabels, address)
class Macro:
	name = ""
	value = ""

	def __init__(self, name, value):
		self.name = name
		self.value = value

class InstructionParser:
	def __init__(self):
		self.currentAddress = 0
		self.maxAddress = 0
		self.instructions = []
		self.labels = []
		self.macros = []
		self.hasParsedTokens = False
		self.finalbinary = [0xff]*0xffff


	def isInstructionNameValid(self, instrName):
		return matchInstruction(instrName)[0]

	def getInstructionInformation(self, addressingModes, instrParams, lineNumber):
		if addressingModes == ADDRESSINGMODENONE and len(instrParams) == 0:
			return (True, ADDRESSINGMODENONE, 1, False)


		return parseInstruction(addressingModes, instrParams, lineNumber)

	def parseLines(self, tokens):
		for lineIndex, line in enumerate(tokens):
			if line == None:
				continue
			
			for tokenIdx, token in enumerate(line):
				for macro in self.macros:
					if token == macro.name:
						line[tokenIdx] = macro.value


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
				if directiveName == "byte":
					for tokenIdx in range(opcodeOffset + 1, len(line)):
						success, number = numForString(line[tokenIdx], None)
						if not success:
							exitWithError("Line %i: Invalid number" % lineNumber)
						if number > 0xFF:
							exitWithError("Line %i: Can't fit value in a byte." % lineNumber)

						self.finalbinary[self.currentAddress] = number
						self.currentAddress += 1

				elif directiveName == "word":
					for tokenIdx in range(opcodeOffset + 1, len(line)):
						success, number = numForString(line[tokenIdx], None)
						foundLabel = False

						if not success:
							for lbl in self.labels:
								if lbl.name == line[tokenIdx]:
									addr = lbl.address
									foundLabel = True
									number = addr + 0x1000
									break
							if not foundLabel:
								exitWithError("Label \"%s\" not found.", line[tokenIdx])                           
						
						
							
						if number > 0xFFFF:
							exitWithError("Line %i: Can't fit value in a word." % lineNumber)

						self.finalbinary[self.currentAddress] = number & 0xff
						self.finalbinary[self.currentAddress + 1] = (number & 0xff00) >> 8
						
						self.currentAddress += 2
				elif directiveName == "org":
					success, number = numForString(line[opcodeOffset + 1], None)
					if not success:
						exitWithError("Line %i: Invalid number" % lineNumber)
					if number > 0xffff:
						exitWithError("Line %i: Too large!" % lineNumber)
						
					self.currentAddress = number

				elif directiveName == "define":
					name = line[opcodeOffset + 1]
					value = line[opcodeOffset + 2]
					self.macros.append(Macro(name, value))
				else:
					exitWithError("Unknown directive \"%s\" on line %i" % (directiveName, lineNumber))
					
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


			self.currentAddress += instrSize

			if self.currentAddress > self.maxAddress:
				self.maxAddress = self.currentAddress

		self.currentAddress = 0
		for instr in self.instructions:
			opcode = opcodeForInstruction(instr, lineNumber, self.labels, instr.address)


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

		self.hasParsedTokens = True

	def getBinaryData(self):
		if self.hasParsedTokens:
			f = open("output.bin", "wb")
			bytes = bytearray(self.finalbinary)

			cappedAddress = self.maxAddress
			if cappedAddress < 0x1000:
				cappedAddress = 0x1000
			return bytes[:cappedAddress]
		return None

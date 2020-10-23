import re

def separateTokens(line):
	tokens = []
	lastIndex = 0
	foundComment = False

	for i in range(len(line)):
		if line[i] == ';':
			slicedLine = line[lastIndex:i]
			if slicedLine.strip():
				tokens.append(slicedLine)
			#lastIndex = i + 1
			foundComment = True
			break
		if line[i] == ' ' or line[i] == ',':
			slicedLine = line[lastIndex:i]
			if slicedLine:
				tokens.append(slicedLine)
			lastIndex = i + 1

	if not foundComment:
		tokens.append(line[lastIndex:len(line)])
	if tokens == [] or tokens == ['']:
		return None
	return tokens

class FileReader:
	file = None
	fileLines = []
	fileLineCount = 0

	def loadFile(self, fileName):
		self.file = open(fileName, "r")
		self.__readFile()

	def __readFile(self):		
		line = self.file.readline()
		lineCount = 1
		while line:
			lineStripped = line.strip()
			self.fileLines.append(lineStripped)

			line = self.file.readline()
			lineCount += 1
		
		self.fileLineCount = lineCount

	def getLineTokens(self):
		tokens = []
		for line in self.fileLines:
			strippedLine = separateTokens(line)
			#if strippedLine:
			tokens.append(strippedLine)

		print(tokens)
		return tokens
from enum import Enum

def _alphaNumericWithUnderscore(name):
		return not name[0].isdigit() and all(c.isalnum() or c == '_' for c in name)

class Label:
	@staticmethod
	def isValid(tokenName):
		return tokenName[0].isalpha() and _alphaNumericWithUnderscore(tokenName[1:])
	
	def __init__(self, name, address):
		self.name = name
		self.address = address



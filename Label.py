from enum import Enum

def alphaNumericWithUnderscore(name):
    return not name[0].isdigit() and all(c.isalnum() or c == '_' for c in name)

def isLabel(tokenName):
    return tokenName[0].isalpha() and alphaNumericWithUnderscore(tokenName[1:])
    
class Label:
    name = ""
    address = 0

    def __init__(self, name, address):
        self.name = name
        self.address = address



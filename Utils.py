import sys

addressingModeNames = ["INDIRECT_Y_ENCODING", "INDIRECT_X_ENCODING", "ABSOLUTE_Y_ENCODING", "ABSOLUTE_X_ENCODING",
                       "ABSOLUTE_ENCODING", "ZEROPAGE_X_ENCODING", "ZEROPAGE_ENCODING", "IMMEDIATE_ENCODING", 
                       "RELATIVE_ENCODING", "ACCUMULATOR_ENCODING", "INDIRECT_ENCODING", "ZEROPAGE_Y_ENCODING" ]



def writeDataToFile(data, outputFileName):
    f = open(outputFileName, "wb")
    f.write(data)

def exitWithError(fmt, *error):
    print(fmt % error)
    sys.exit()

def addressingModeString(addressingMode):
    if addressingMode == 0:
        return "IMPLIED_ENCODING"

    return addressingModeNames[addressingModeIndex(addressingMode) - 1]

# expects a string number with the format $<hex number>. examples: $FF, $80, $C87F
def numForString(numStr, enforceType):

    # must be explicit about number
    if (numStr[0] == '$' or enforceType == "hex") and enforceType != "binary":
        try:
            value = int(numStr[1::], 16)
            return (True, value)
        except ValueError as verr:
            return (False, 0)
    elif numStr[0] == '%' or enforceType == "binary":
        try:
            value = int(numStr[1::], 2)
            return (True, value)
        except ValueError as verr:
            return (False, 0)
    else:
        try:
            value = int(numStr, 10)
            return (True, value)
        except ValueError as verr:
            return (False, 0)
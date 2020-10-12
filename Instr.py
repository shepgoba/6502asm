from Utils import numForString
from Utils import exitWithError

ADDRESSINGMODENONE = 0
ZEROPAGE_Y_ENCODING  = 1 << 11 #0b100000000000
INDIRECT_ENCODING    = 1 << 10 #0b010000000000
ACCUMULATOR_ENCODING = 1 << 9  #0b001000000000
RELATIVE_ENCODING    = 1 << 8  #0b000100000000
IMMEDIATE_ENCODING   = 1 << 7  #0b000010000000
ZEROPAGE_ENCODING    = 1 << 6  #0b000001000000
ZEROPAGE_X_ENCODING  = 1 << 5  #0b000000100000
ABSOLUTE_ENCODING    = 1 << 4  #0b000000010000
ABSOLUTE_X_ENCODING  = 1 << 3  #0b000000001000
ABSOLUTE_Y_ENCODING  = 1 << 2  #0b000000000100
INDIRECT_X_ENCODING  = 1 << 1  #0b000000000010
INDIRECT_Y_ENCODING  = 1       #0b000000000001

# Returns if instruction was a valid one, and what index it has in the instruction table
def matchInstruction(instrName):
    for (idx, currentInstrName) in enumerate(VALID_INSTR_NAMES):
        if instrName.lower() == currentInstrName.lower():
            return (True, idx)
    return (False, 0)

def byteswap(num):
    return ((num & 0xff00) >> 8) | ((num & 0xff) << 8)


def singleParameterOpcode(opcode, instr, lineNumber):
    instr.size = 1
    return opcode

def opcodeDEX(instr, lineNumber):
    return singleParameterOpcode(0xCA, instr, lineNumber)

def opcodeDEY(instr, lineNumber):
    return singleParameterOpcode(0x88, instr, lineNumber)

def opcodeINX(instr, lineNumber):
    return singleParameterOpcode(0xE8, instr, lineNumber)

def opcodeINY(instr, lineNumber):
    return singleParameterOpcode(0xC8, instr, lineNumber)

def opcodeNOP(instr, lineNumber):
    return singleParameterOpcode(0xEA, instr, lineNumber)

def opcodePHA(instr, lineNumber):
    return singleParameterOpcode(0x48, instr, lineNumber)

def opcodePHP(instr, lineNumber):
    return singleParameterOpcode(0x08, instr, lineNumber)

def opcodePLA(instr, lineNumber):
    return singleParameterOpcode(0x68, instr, lineNumber)

def opcodePLP(instr, lineNumber):
    return singleParameterOpcode(0x28, instr, lineNumber)

def opcodeRTI(instr, lineNumber):
    return singleParameterOpcode(0x40, instr, lineNumber)

def opcodeRTS(instr, lineNumber):
    return singleParameterOpcode(0x60, instr, lineNumber)

def opcodeSEC(instr, lineNumber):
    return singleParameterOpcode(0x38, instr, lineNumber)

def opcodeSEI(instr, lineNumber):
    return singleParameterOpcode(0x78, instr, lineNumber)

def opcodeSED(instr, lineNumber):
    return singleParameterOpcode(0xF8, instr, lineNumber)

def opcodeTAX(instr, lineNumber):
    return singleParameterOpcode(0xAA, instr, lineNumber)

def opcodeTAY(instr, lineNumber):
    return singleParameterOpcode(0xA8, instr, lineNumber)

def opcodeTSX(instr, lineNumber):
    return singleParameterOpcode(0xBA, instr, lineNumber)

def opcodeTXA(instr, lineNumber):
    return singleParameterOpcode(0x8A, instr, lineNumber)

def opcodeTXS(instr, lineNumber):
    return singleParameterOpcode(0x9A, instr, lineNumber)

def opcodeTYA(instr, lineNumber):
    return singleParameterOpcode(0x98, instr, lineNumber)

def opcodeCLC(instr, lineNumber):
    return singleParameterOpcode(0x18, instr, lineNumber)

def opcodeCLD(instr, lineNumber):
    return singleParameterOpcode(0xD8, instr, lineNumber)

def opcodeCLI(instr, lineNumber):
    return singleParameterOpcode(0x58, instr, lineNumber)
    
def opcodeCLV(instr, lineNumber):
    return singleParameterOpcode(0xB8, instr, lineNumber)

def opcodeBRK(instr, lineNumber):
    return singleParameterOpcode(0x00, instr, lineNumber)

def opcodeDEX(instr, lineNumber):
    return singleParameterOpcode(0xCA, instr, lineNumber)

def opcodeDEY(instr, lineNumber):
    return singleParameterOpcode(0x88, instr, lineNumber)

IMPLIED_OPCODE_TABLE = [None, None, None, None, None, None, None, None, None, None, opcodeBRK, None, None, opcodeCLC,
                opcodeCLD, opcodeCLI, opcodeCLV, None, None, None, None, opcodeDEX, opcodeDEY, None, None, opcodeINX, opcodeINY, None,
                None, None, None, None, None, opcodeNOP, None, opcodePHA, opcodePHP, opcodePLA, opcodePLP, None, None, opcodeRTI,
                opcodeRTS, None, opcodeSEC, opcodeSED, opcodeSEI, None, None, None, opcodeTAX, opcodeTAY, opcodeTXS, opcodeTXA, opcodeTXS, opcodeTYA]

VALID_INSTR_NAMES = ["ADC", "AND", "ASL", "BCC", "BCS", "BEQ", "BIT", "BMI", "BNE", "BPL", "BRK", "BVC", "BVS", "CLC", 
                     "CLD", "CLI", "CLV", "CMP", "CPX", "CPY", "DEC", "DEX", "DEY", "EOR", "INC", "INX", "INY", "JMP", 
                     "JSR", "LDA", "LDX", "LDY", "LSR", "NOP", "ORA", "PHA", "PHP", "PLA", "PLP", "ROL", "ROR", "RTI", 
                     "RTS", "SBC", "SEC", "SED", "SEI", "STA", "STX", "STY", "TAX", "TAY", "TSX", "TXA", "TXS", "TYA"]

# addressing modes are as follows: 
# high byte: zeropage Y, indirect, accumulator, relative, 
# low byte: immediate, zeropage, zeropage X, absolute, absolute X, absolute Y, indirect X, indirect Y
INSTR_ADDRESSING_MODES = [0b0000000011111111, 0b0000000011111111, 0b0000001001111000, 0b0000000100000000, 0b0000000100000000, 0b0000000100000000, # ADC - BEQ
                          0b0000000001010000, 0b0000000100000000, 0b0000000100000000, 0b0000000100000000, ADDRESSINGMODENONE, 0b0000000100000000, # BIT - BVC
                          0b0000000100000000, ADDRESSINGMODENONE, ADDRESSINGMODENONE, ADDRESSINGMODENONE, ADDRESSINGMODENONE, 0b0000000011111111, # BVS - CMP
                          0b0000000011010000, 0b0000000011010000, 0b0000000001111000, ADDRESSINGMODENONE, ADDRESSINGMODENONE, 0b0000000011111111, # CPX - EOR
                          0b0000000001111000, ADDRESSINGMODENONE, ADDRESSINGMODENONE, 0b0000010000010000, 0b0000000000010000, 0b0000000011111111, # INC - LDA
                          0b0000100011010100, 0b0000000011111000, 0b0000001001111000, ADDRESSINGMODENONE, 0b0000000011111111, ADDRESSINGMODENONE, # LDX - PHA
                          ADDRESSINGMODENONE, ADDRESSINGMODENONE, ADDRESSINGMODENONE, 0b0000001001111000, 0b0000001001111000, ADDRESSINGMODENONE, # PHP - RTI
                          ADDRESSINGMODENONE, 0b0000000011111111, ADDRESSINGMODENONE, ADDRESSINGMODENONE, ADDRESSINGMODENONE, 0b0000000001111111, # RTS - STA
                          0b0000100001010000, 0b0000000001110000, ADDRESSINGMODENONE, ADDRESSINGMODENONE, ADDRESSINGMODENONE, ADDRESSINGMODENONE, # STX - TXA
                          ADDRESSINGMODENONE, ADDRESSINGMODENONE] # TXS - TYA

def accumulatorOpcodeForInstruction(instr, opcodeBase, validLabels, address):
    return opcodeBase

def immediateOpcodeForInstruction(instr, opcodeBase, validLabels, address):
    resultSuccess, num = numForString(instr.params[0][1::], None)
    return opcodeBase << 8 | num

def zeropageOpcodeForInstruction(instr, opcodeBase, validLabels, address):
    resultSuccess, num = numForString(instr.params[0], None)
    return opcodeBase << 8 | num

# TODO: - make this better
def encodeTwosComplement(num):
    if num < 0:
        return 0xff + num - 1
    else:
        return num

def relativeOpcodeForInstruction(instr, opcodeBase, validLabels, address):
    if instr.usesLabel:
        for lbl in validLabels:
            if lbl.name == instr.params[0]:
                #if address - lbl.address >= 0:
                addr = encodeTwosComplement(lbl.address - address)
                #else:
                #addr = encodeTwosComplement(address - lbl.address)

                #print("instr address: %04x, lbl address: %04x" % (address & 0xff, lbl.address & 0xff))
                return opcodeBase << 8 | addr
        exitWithError("Label \"%s\" not found.", instr.params[0])
    resultSuccess, num = numForString(instr.params[0], None)
    return opcodeBase << 8 | (num & 0xff)

def absoluteOpcodeForInstruction(instr, opcodeBase, validLabels, address):
    #print("nice")
    if instr.usesLabel:
        for lbl in validLabels:
            if lbl.name == instr.params[0]:
                addr = lbl.address
                return opcodeBase << 16 | byteswap(addr)

        exitWithError("Label \"%s\" not found.", instr.params[0])
    resultSuccess, num = numForString(instr.params[0], None)

    result = opcodeBase << 16 | byteswap(num)

    return result


def indirectOpcodeForInstruction(instr, opcodeBase, validLabels, address):
    firstParam = instr.params[0]
    resultSuccess, num = numForString(firstParam[1:-1], None)
    result = opcodeBase << 16 | byteswap(num)
    return result

def indirectYOpcodeForInstruction(instr, opcodeBase, validLabels, address):
    firstParam = instr.params[0]
    resultSuccess, num = numForString(firstParam[1:-1], None)
    result = opcodeBase << 8 | num
    return result

def indirectXOpcodeForInstruction(instr, opcodeBase, validLabels, address):
    firstParam = instr.params[0]
    resultSuccess, num = numForString(firstParam[1:], None)

    result = opcodeBase << 8 | num
    return result

ADC_ENCODINGS = [0x71, 0x61, 0x79, 0x7D, 0x6D, 0x75, 0x65, 0x69]
AND_ENCODINGS = [0x31, 0x21, 0x39, 0x3D, 0x2D, 0x35, 0x25, 0x29]
ASL_ENCODINGS = [0x00, 0x00, 0x00, 0x1E, 0x0E, 0x16, 0x06, 0x00, 0x00, 0x0A]
BCC_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x90]
BCS_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xB0]
BEQ_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0]
BIT_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0x2C, 0x00, 0x24, 0x00, 0x90]
BMI_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x30]
BNE_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xD0]
BPL_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10]
BRK_ENCODINGS = []
BVC_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x50]
BVS_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x70]
CLC_ENCODINGS = []
CLD_ENCODINGS = []
CLI_ENCODINGS = []
CLV_ENCODINGS = []
CMP_ENCODINGS = [0xD1, 0xC1, 0xD9, 0xDD, 0xCD, 0xD5, 0xC5, 0xC9]
CPX_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0xEC, 0x00, 0xE4, 0xE0]
CPY_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0xCC, 0x00, 0xC4, 0xC0]
DEC_ENCODINGS = [0x00, 0x00, 0x00, 0xDE, 0xCE, 0xD6, 0xC6, 0x00]
DEX_ENCODINGS = []
DEY_ENCODINGS = []
EOR_ENCODINGS = [0x49, 0x45, 0x55, 0x4D, 0x5D, 0x59, 0x41, 0x51]
INC_ENCODINGS = [0x00, 0x00, 0x00, 0xFE, 0xEE, 0xF6, 0xE6, 0x00]
INX_ENCODINGS = []
INY_ENCODINGS = []
JMP_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0x4C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x6C]
JSR_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00, 0x00]
LDA_ENCODINGS = [0xB1, 0xA1, 0xB9, 0xBD, 0xAD, 0xB5, 0xA5, 0xA9]
LDX_ENCODINGS = [0x00, 0x00, 0xBE, 0x00, 0xAE, 0x00, 0xA6, 0xA2, 0x00, 0x00, 0x00, 0xB6]
LDY_ENCODINGS = [0x00, 0x00, 0x00, 0xBC, 0xAC, 0xB4, 0xA4, 0xA0]
LSR_ENCODINGS = [0x00, 0x00, 0x00, 0x5E, 0x4E, 0x56, 0x46, 0x00, 0x00, 0x4A]
NOP_ENCODINGS = []
ORA_ENCODINGS = [0x11, 0x01, 0x19, 0x1D, 0x0D, 0x15, 0x05, 0x09]
PHA_ENCODINGS = []
PHP_ENCODINGS = []
PLA_ENCODINGS = []
PLP_ENCODINGS = []
ROL_ENCODINGS = [0x00, 0x00, 0x00, 0x3E, 0x2E, 0x36, 0x26, 0x00, 0x00, 0x2A]
ROR_ENCODINGS = [0x00, 0x00, 0x00, 0x7E, 0x6E, 0x76, 0x66, 0x00, 0x00, 0x6A]
RTI_ENCODINGS = []
RTS_ENCODINGS = []
SBC_ENCODINGS = [0xE1, 0xE1, 0xF9, 0xFD, 0xED, 0xF5, 0xE5, 0xE9]
SEC_ENCODINGS = []
SED_ENCODINGS = []
SEI_ENCODINGS = []
STA_ENCODINGS = [0x91, 0x81, 0x99, 0x9D, 0x8D, 0x95, 0x85, 0x00]
STX_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0x8E, 0x00, 0x86, 0x00, 0x00, 0x00, 0x00, 0x96]
STY_ENCODINGS = [0x00, 0x00, 0x00, 0x00, 0x8C, 0x94, 0x84, 0x00]
TAX_ENCODINGS = []
TAY_ENCODINGS = []
TSX_ENCODINGS = []
TXA_ENCODINGS = []
TXS_ENCODINGS = []
TYA_ENCODINGS = []


INSTRUCTION_ENCODINGS = [ADC_ENCODINGS, AND_ENCODINGS, ASL_ENCODINGS, BCC_ENCODINGS, BCS_ENCODINGS, BEQ_ENCODINGS, BIT_ENCODINGS, BMI_ENCODINGS, BNE_ENCODINGS, BPL_ENCODINGS, BRK_ENCODINGS, BVC_ENCODINGS, BVS_ENCODINGS, CLC_ENCODINGS, CLD_ENCODINGS, CLI_ENCODINGS, CLV_ENCODINGS, CMP_ENCODINGS, CPX_ENCODINGS, CPY_ENCODINGS, DEC_ENCODINGS, DEX_ENCODINGS, DEY_ENCODINGS, EOR_ENCODINGS, INC_ENCODINGS, INX_ENCODINGS, INY_ENCODINGS, JMP_ENCODINGS, JSR_ENCODINGS, LDA_ENCODINGS, LDX_ENCODINGS, LDY_ENCODINGS, LSR_ENCODINGS, NOP_ENCODINGS, ORA_ENCODINGS, PHA_ENCODINGS, PHP_ENCODINGS, PLA_ENCODINGS, PLP_ENCODINGS, ROL_ENCODINGS, ROR_ENCODINGS, RTI_ENCODINGS, RTS_ENCODINGS, SBC_ENCODINGS, SEC_ENCODINGS, SED_ENCODINGS, SEI_ENCODINGS, STA_ENCODINGS, STX_ENCODINGS, STY_ENCODINGS, TAX_ENCODINGS, TAY_ENCODINGS, TSX_ENCODINGS, TXA_ENCODINGS, TXS_ENCODINGS, TYA_ENCODINGS]
PARSER_FOR_ADDRESSING_MODE = [indirectYOpcodeForInstruction, indirectXOpcodeForInstruction, absoluteOpcodeForInstruction, absoluteOpcodeForInstruction, absoluteOpcodeForInstruction, zeropageOpcodeForInstruction, zeropageOpcodeForInstruction, immediateOpcodeForInstruction, relativeOpcodeForInstruction, accumulatorOpcodeForInstruction, indirectOpcodeForInstruction, zeropageOpcodeForInstruction]

class Instruction:
    mnemonic = ""
    params = []
    size = 0
    address = 0
    addressingMode = None
    usesLabel = 0


    def __init__(self, mnemonic, params, address, addressingModeUsed, size, usesLabel):
        self.mnemonic = mnemonic
        self.params = params
        self.address = address
        self.addressingMode = addressingModeUsed
        self.size = size
        self.usesLabel = usesLabel

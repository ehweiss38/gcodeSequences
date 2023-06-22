from math import sqrt, floor, isnan
from io import TextIOWrapper
from os import path


class GCodeDoc:
    file: TextIOWrapper = None

    def __init__(self, fileName: str):
        if len(fileName) == 0: fileName = "testGcode"
        fileName += '.txt'
        if path.isfile(fileName):
            self.file = open(fileName, "w")
        else:
            self.file = open(fileName, "x")

        self.file.write("G21\n")
        # absolute mode
        self.file.write("G90\n")
        # feed speed, possibly redundant
        self.file.write("F100")
        # assumes center start position
        self.file.write("G28.3 X0 Y0 Z0 \n")

    def close(self):
        self.file.close()

    def g0(self, x: int = None, y: int = None, z: int = None):
        self.file.write(
            f"G0 {f'X{x} ' if x != None else ''}{f'Y{y} ' if y != None else ''}{f'Z{z}' if z != None else ''}\n")

    def g1(self, x: int = None, y: int = None, z: int = None):
        self.file.write(
            f"G1 {f'X{x} ' if x != None else ''}{f'Y{y} ' if y != None else ''}{f'Z{z} ' if z != None else ''}(chilipeppr_pause)\n")


class LineBoundaries:
    def __init__(self, y):
        self.y = y
        self.end = 0


def calcEndpoint(radius: float, y: float, increment: float, buffer: float = 10, inner: bool = True,
                 raw_val: bool = False):
    raw = sqrt(abs(radius ** 2 - y ** 2))
    val = floor(raw)
    # add
    if raw_val:
        return val
    while (val % increment != 0 and abs(raw - val) <= buffer):
        # print(radius-val)
        val = val - 1 if inner else val + 1
        # print(val)
    return val


def modFloor(number, divisor):
    # good question of what to do in event they will never be divisible by one another
    # 17.25 1 1
    number = floor(number / 10)
    while number % (divisor / 10) != 0:
        print(number)
        --number
    return number * 10


def setValues(name: str, maximum: bool, default: float, min: float = None, absV=False):
    inpVal = input(f"Enter {'maximum' if maximum else 'minimum'} {name}-value (cm)")
    print('iv', inpVal)
    if len(inpVal) == 0 or isnan(float(inpVal)):
        print('def', default)
        return default
    val = abs(float(inpVal) * 10) if absV else float(inpVal) * 10
    # if min!=None and val<min:return None
    return val


def setIncrement(name: str, default: float):
    inpVal = input(f"Enter {name}-increment (cm)")
    if len(inpVal) == 0 or isnan(float(inpVal)): return default
    val = float(inpVal) * 10
    return val


def setCircleVals(name: str, default: float):
    inpVal = input(f"Enter {name} (cm)")
    if len(inpVal) == 0 or isnan(float(inpVal)): return default
    val = abs(float(inpVal) * 10)
    return val


# need to calculate at which point coord is equal to ~20 of length

# assumes symmetry along x=axis
def calcChordSpace(radius: float, width: float):
    x = .8 * width
    return -floor(sqrt(radius ** 2 - x ** 2))


def effective_val(base: float, increment: float):
    return base - (base % increment) * (-1 if base < 0 else 1)


def relativeMin(val1: float, val2: float):
    if abs(val1) < abs(val2):
        return val1
    else:
        return val2


def relativeMax(val1: float, val2: float):
    if abs(val1) > abs(val2):
        return val1
    else:
        return val2


def customerInfo(value, doc: TextIOWrapper):
    entered = input(f"{value}?")
    if (entered.length):
        doc.write(f";{value}:{entered}\n")


def movement(num, increment):
    if num % increment == 0:
        # print(num,'return 1')
        return '1'
    else:
        # print(num,'return 0')
        return '0'

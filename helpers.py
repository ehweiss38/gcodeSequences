from math import sqrt,floor,isnan
        
class LineBoundaries:
    def __init__(self,y):
        self.y=y
        self.end=0


def calcEndpoint(radius:float,y:float,increment:float,buffer:float,inner:bool=True):
    raw=sqrt(abs(radius**2-y**2))
    val=floor(raw)
    #not radius-val actually 
    while (val%increment!=0 and abs(raw-val)<buffer) :
        #print(radius-val)
        val=val-1 if inner else val+1
        #print(val)
    return val

def modFloor(number,divisor):
    #good question of what to do in event they will never be divisible by one another
    #17.25 1 1 
    number=floor(number/10)
    while number%(divisor/10)!=0:
        print(number)
        --number
    return number*10

def setValues(name:str,maximum:bool,default:float,min:float=None,absV=False):
    inpVal=input(f"Enter {'maximum' if maximum else 'minimum'} {name}-value (cm)")
    if len(inpVal)==0 or isnan(float(inpVal)):return default
    val=abs(float(inpVal)*10) if absV else float(inpVal)*10
    #if min!=None and val<min:return None
    return val
def setIncrement(name:str,default:float):
    inpVal=input(f"Enter {name}-increment (cm)")
    if len(inpVal)==0 or isnan(float(inpVal)):return default
    val=float(inpVal)*10
    return val
def setCircleVals(name:str,default:float):
    inpVal=input(f"Enter {name} (cm)")
    if len(inpVal)==0 or isnan(float(inpVal)):return default
    val=abs(float(inpVal)*10)
    return val

#need to calculate at which point coord is equal to ~20 of length

#assumes symmetry along x=axis
def calcChordSpace(radius:float,width:float):
    x=.8*width
    return -floor(sqrt(radius**2-x**2))

def effectiveVal(divisor:float,bound:float):
    if divisor==None:return None
    elif divisor!=None and bound%divisor==0:return bound
    running=0
    while running+divisor<bound:running+=divisor
    return running

def relativeMin(val1:float,val2:float):
    if abs(val1)<abs(val2):
        return val1
    else:
        return val2
def relativeMax(val1:float,val2:float):
    if abs(val1)>abs(val2):
        return val1
    else:
        return val2
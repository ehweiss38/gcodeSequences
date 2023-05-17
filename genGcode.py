from os import path
from math import isnan


fileName=input('Enter file name')
if len(fileName)==0:fileName="testGcode"
fileName+='.txt'
f=None 


if path.isfile(fileName):f=open(fileName,"w")
else: f=open(fileName,"x")

#Type dimensions here (#mm):

inch=25.4
#total length of x axis
def setValues(name:str,maximum:bool,default:float):
    inpVal=input(f"Enter {'maximum' if maximum else 'minimum'} {name}-value (cm)")
    if len(inpVal)==0 or isnan(float(inpVal)):return default
    val=float(inpVal)*10
    return val
def setIncrement(name:str,default:float):
    inpVal=input(f"Enter {name}-increment (cm)")
    if len(inpVal)==0 or isnan(float(inpVal)):return default
    val=float(inpVal)*10
    return val

xMax=setValues('x',True,120)
xMin=-1*setValues('x',False,120)
yMax=setValues('y',True,120)
yMin=-1*setValues('y',False,120)
zMax=setValues('z',True,150)

print(xMax,xMin,yMax,yMin)

#distance to move between measurements
xIncrement=setIncrement('x',10) 
yIncrement=setIncrement('y',10) 
zIncrement=setIncrement('z',50) 

#metric units
f.write("G21\n")
#absolute mode
f.write("G90\n")
4
#feed speed, possibly redundant
f.write("F100\n")

#assumes center start position 
f.write("G28.3 X0 Y0 Z0 \n")
	


f.write(f"G0 X{xMin} Y{yMax} Z0 (chilipeppr_pause)\n\n")

downwards=True
x=0
y=0
z=0
rightwards=True
while(z<=zMax):
#a little connfusing but low meaninng start, high finish, irrespective of actual values
    lowY=yMax if downwards else yMin
    highY=yMin if downwards else yMax
    y=lowY
    while((downwards and y>=highY) or (downwards==False and y<=highY)):
        lowX=xMin if rightwards else xMax
        highX=xMax if rightwards else xMin
        x=lowX
        while (x!=highX):
            x+=xIncrement if rightwards else -1*xIncrement
            f.write(f"G1 X{x} (chilipeppr pause)\n")
    
        #end behavior
        rightwards=False if rightwards else True
        if y!=highY:y+=-1*yIncrement if downwards else yIncrement
        else: break
        f.write(f"G1 X{x} Y{y} Z{z} (chilipeppr_pause)\n")
        print(f"{y}-y {z}-z level complete\n")
    if z!=zMax:z+=zIncrement
    else:break
    
    f.write(f"G1 X{x} Y{y} Z{z} (chilipeppr_pause)\n")
    downwards=False if downwards else True
    print(f"{z} z level complete\n")

f.write(f"G0 X0 Y0")
f.write(f"G X0 Y0 Z0")
print('closing')
f.close()
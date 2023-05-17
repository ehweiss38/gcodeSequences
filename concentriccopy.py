#important changes 
#need to cosndier coil

#nhanna270@gmail.com

from helpers import modFloor,calcEndpoint,LineBoundaries,setCircleVals,setValues,effectiveVal,relativeMin
from math import ceil
from os import path


fileName=input('Enter file name')
if len(fileName)==0:fileName="testGcode"
fileName+='.txt'
f=None 


if path.isfile(fileName):f=open(fileName,"w")
else: f=open(fileName,"x")


thickness=setCircleVals('thickness',50)
radius=setCircleVals('radius',170)
buffer=setCircleVals('buffer',10)
increment=setCircleVals('increment',10)

#important to remember you need actual values not just decimals

#the main improvement that is needed is that when it is above the circle, it no longer needs to follow the outline and can do the whole square




f.write("G21\n")
#absolute mode
f.write("G90\n")
4
#feed speed, possibly redundant
f.write("F100")

#assumes center start position 
f.write("G28.3 X0 Y0 Z0 \n")


oRadius=radius+thickness
xMax=None
#need to further consider negative cases
while xMax==None:
    xMax=effectiveVal(increment,setValues('x',True,250,oRadius))
    if xMax==None:print(f"Value must be greater than outer-radius({oRadius})")
xMin=None
while xMin==None:
    xMin=-effectiveVal(increment,setValues('x',False,250,oRadius))
    if xMax==None:print(f"Value must be greater than outer-radius({oRadius})")
yMax=None
while yMax==None:
    yMax=effectiveVal(increment,setValues('y',True,250,oRadius))
    if yMax==None:print(f"Value must be greater than outer-radius({oRadius})")
yMin=None
while yMin==None:
    yMin=-effectiveVal(increment,setValues('y',False,250,oRadius))
    if yMax==None:print(f"Value must be greater than outer-radius({oRadius})")

y=0
tail=True if yMin!=0 and xMin!=0 else False

# if i cut off on top, doesnt work overshoots where it shouldnt and undershjoots too


pathRadius=modFloor(radius-buffer,increment)
xTargH=min(pathRadius,xMax-increment)
hBarrier=True if xTargH!=pathRadius else False
#offset by 1 more at start
x=xTargH
if hBarrier==False:x+=increment
xTargL=relativeMin(-pathRadius,xMin+increment)
lBarrier=True if xTargL!=-pathRadius else False
#not sure if this is ideal
# f.write(f"G0 X{x} Y{y} Z0\n\n")

#can still do it otherwise, just only go as far as if it divisible
#deciding to work from center, even though it takes longer
#reason being is other wise, there could be some combinations of buffers and increments that wouldnt be centered a 0
xStart=xTargH
xFinish=xTargL
downwards=True
rightwards=True
zIncrement=setCircleVals('z-increment',30)
zMin=-1*effectiveVal(zIncrement,setCircleVals('z-min',60))
z=zMin
zTarg=effectiveVal(zIncrement,setCircleVals('z-max',60))
#doesnt really work in practice, as need to align min to be compatible with divisor, in the sense that divisor overrides min

f.write(f"G0 X0 Y0 Z{z} \n\n")
#CIRCLE
if(xMax!=0):
    f.write(f"G0 X{x +increment if hBarrier else x} Y{y} Z{z} \n\n")
#seems to overshoot on some, under on others

#think it messes up if it starts wrong because it starts counting as if it is in right place, so ends up short




if hBarrier:x+=increment
zLimit=thickness
while z<zLimit:
    #redundant reading here...
    
    f.write(f"G1 X{x} Y{y} Z{z} (chilipeppr_pause);layer {z}\n\n")
    #technically the singular point is overshooting
    #need to consider endpoint, returning to that center spot
    #you do want this, however, that means it should offset by -1 at start
    partialEdgeCheck=True
    while(x>=xFinish if downwards else x<=xFinish):
        #overshoots to get the 0, but doesnt work if not full trip
        #this is one of the issues, it needs to do the line firs
        # Not sure how to best phrase this
        if ((x>=xTargH and hBarrier) or (x<=xTargL and lBarrier)) and partialEdgeCheck:
            partialEdgeCheck=False
        else: x+=-increment if downwards else increment
        lineEnd=calcEndpoint(radius,x,increment,buffer)
        
        #error is xTarg when going left
        y=relativeMin(-lineEnd if rightwards else lineEnd,yMin if rightwards else yMax)
        #xTarg 
        yTarg=relativeMin(lineEnd if rightwards else -lineEnd,yMax if rightwards else yMin)
        #the issue is if it is full you want the extra point (only 1 x), but otherwise you want it to stop

        #not yTarg cuz its always tgat
        #almost made it worse
        #its not the equals that is probelmatic, it is the next one that should only happen if it matxhes
        f.write(f"G1 X{x} Y{y} (chilipeppr_pause)\n")
        while y<yTarg if rightwards else x>yTarg:
            y+=increment if rightwards else -increment
            #if y==yFinish:x=0
            f.write(f"G1 X{x} Y{y} (chilipeppr_pause)\n")
        rightwards=False if rightwards else True
    downwards=False if downwards else True
    z+=zIncrement
    xFinish=xTargL if downwards else xTargH
    if z<=zLimit:f.write(f"G1 X{x} Y{y} Z{z};layer {z} \n\n")
#above by some measure
f.write(f"G0 X0 Y0 Z{z};layer {z}\n")

#deprecated feature
tailCoord=0

x=xMax
#still above
print(y)
f.write(f"G1 X{x} Y{y} (chilipeppr_pause)\n")
z-=zIncrement
#moves down
f.write(f"G0 X{x} Y{y} Z{z} (chilipeppr_pause);layer {z}\n")

#clearance so i

#




#assuming it is round tube, lower bounds will always be equal to -thickness if 0 is between two tubes
#should it start this below level with top or with level?
# also raises question of base collission
while(z>=-thickness):
    #print('Z',z)
    f.write(f"G1 X{xMax} Y{y} Z{z} (chilipeppr_pause);layer {z}\n")
    for i in range(0,2):
        tailSpace=False
        rightwards=True if i==1 else False
        yTarg=yMax if rightwards else yMin
        #tecnically overshoots a little and goes back
        while x>=xMin:
            #still need to put line switch in 
            #also need to consider before where circle starts
                #logic would be if(abs(y)>oRadius)
            while y<yTarg if rightwards else y>yTarg:
                y+=increment if rightwards else -increment
                f.write(f"G1 X{x} Y{y} (chilipeppr_pause)\n")
            x-=increment
            rightwards=False if rightwards else True
            line=LineBoundaries(x)
            #print(y,oRadius)
            #best way is to adjust for widest point in circle before it closes
            #more specifically wide enough to fit thickness and buffer
            #when it reaches that width on bottom 
            line.end=(calcEndpoint(oRadius,y,increment,buffer,False) * (-1 if i==0 else 1)) if abs(y)<oRadius else (0 if tailSpace==False else (-tailCoord if i==0 else tailCoord))
            #just adding extra line for clarity
            line.end=relativeMin(line.end,yMin if i==0 else yMax)
            if tailCoord==0 and line.end!=yMax and line.end!=yMin and abs(line.end*2)>thickness+buffer:
                tailCoord=abs(line.end)
                print("tailcoord",tailCoord)
            
            if abs(line.end)<=tailCoord and x<0:
                tailSpace=True

            yTarg=(line.end if rightwards else yMin) if i==0 else ((yMax if rightwards else line.end))
            #print(x,line.end,rightwards)
            y=(y if rightwards else line.end) if i==0 else ((line.end if rightwards else y))
            if x>=xMin:f.write(f"G1 X{x} Y{y} (chilipeppr_pause)\n")
            #add cable gap later 
        if y!=(yMin if i==0 else yMax):
            #this is a major logic error, and it is causing the error
            y=yMin if i==0 else yMax
        #f.write(f"G0 X{x} Y{y}\n")
        #i am a little confused about the little tails but it is not a huge deal
        x=xMax
        f.write(f"G0 X{x} Y{y}\n")
        y=0
        f.write(f"G0 X{x} Y{y}\n")
    z-=zIncrement
    print(x,y)
y=yMax
f.write(f"G0 X{xMax} Y{y} Z{0};layer {z}\n")
downwards=True
#few issues, need seperate variables for coil height and total height, so know when to switch to others, because 0 is in center of coil


#cant do these moves, need to really consider possibilities
#f.write(f"G0 X0 Y0 Z0")
#f.write(f"G0 X{xMin} Y{xMin} Z0")

#square here

#more precise way
z= ceil(thickness/zIncrement)*zIncrement

f.write(f"G1 X{xMax} Y{y}Z{z} (chilipeppr_pause);layer {z}\n")

#seems to cross too much right here

#print('z',z,'ztarg',zTarg)
while(z<=zTarg):
#a little connfusing but low meaninng start, high finish, irrespective of actual values
    lowX=xMax if downwards else xMin
    highX=xMin if downwards else xMax
    x=lowX
    while((downwards and x>=highX) or (downwards==False and x<=highX)):
       # print(x,y)
        lowY=yMin if rightwards else yMax
        highY=yMax if rightwards else yMin
        y=lowY
        while (y!=highY):
            y+=increment if rightwards else -1*increment
            f.write(f"G1 Y{y} (chilipeppr_pause)\n")
    
        #end behavior
        rightwards=False if rightwards else True
        if x!=highY:x+=-1*increment if downwards else increment
        else: break
        f.write(f"G1 X{x} Y{y} Z{z} (chilipeppr_pause);layer {z}\n")
        #print(f"{y}-y {z}-z level complete\n")
    if z!=zTarg:z+=zIncrement
    else:break
    
    f.write(f"G1 X{x} Y{y} Z{z} (chilipeppr_pause);layer {z}\n")
    downwards=False if downwards else True
    #print(f"{z} z level complete\n")

f.write(f"G0 X0 Y0 Z{zTarg};layer {z}\n")
f.write(f"G0 X0 Y0 Z0\n")
print('closing')
f.close()

f.close()
print('complete')
    
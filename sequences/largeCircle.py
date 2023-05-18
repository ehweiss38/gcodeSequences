#important changes 
#different increments
    #messes up inner circle( malformed, too close, overshoots y)
    #weird polygons elsewhere

# one of the prevailing issues is trying to accomodate both partial and full readings. Switching to quadrant would make this more manageable 


from helpers.helpers import modFloor,calcEndpoint,LineBoundaries,setCircleVals,setValues,effectiveVal,relativeMin
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

#also looks like it may offset to different lines



f.write("G21\n")
#absolute mode
f.write("G90\n")
4
#feed speed, possibly redundant
f.write("F100")

#assumes center start position 
f.write("G28.3 X0 Y0 Z0 \n")


oRadius=radius+thickness
xInput=None
yInput=None

#change to dimensions, assigns to min or max
#need to further consider negative cases
while xInput==None:
    xInput=effectiveVal(increment,setValues('x',True,280,oRadius,False))
    if xInput==None:print(f"Value must be greater than outer-radius({oRadius})")
while yInput==None:
    yInput=effectiveVal(increment,setValues('y',True,280,oRadius,False))
    if yInput==None:print(f"Value must be greater than outer-radius({oRadius})")

xMin=min(0,xInput)
xMax=max(0,xInput)

yMin=min(0,yInput)
yMax=max(0,yInput)


x=0

# if i cut off on top, doesnt work overshoots where it shouldnt and undershjoots too

print('y',yMin)
#why minus buffer, seems to work elsewhere (it is to set inner edge)
pathRadius=modFloor(radius-buffer,increment)
print('pathr',pathRadius)
#not sure why dropping the increment here, but minus plus is to reflect opposite valss
# i think it does it because it does <= so it equals that on final iteration
yTargH=min(pathRadius,yMax-increment)

#relative barriers, I think this logic is a little convoluted, not the issue though
hBarrier=True if yTargH!=pathRadius else False
#offset by 1 more at start

y=yTargH
#sets it back so that it gets the point. If i change to the assumption that
if hBarrier==False:y+=increment
print(radius,yTargH)
yTargL=relativeMin(-pathRadius,yMin+increment)
lBarrier=True if yTargL!=-pathRadius else False
print('h',yTargH,'l',yTargL)
#not sure if this is ideal
# f.write(f"G0 X{x} Y{y} Z0\n\n")

#can still do it otherwise, just only go as far as if it divisible
#deciding to work from center, even though it takes longer
#reason being is other wise, there could be some combinations of buffers and increments that wouldnt be centered a 0
yStart=yTargH
yFinish=yTargL
downwards=True
#for first circle, this is always true
rightwards=True


zIncrement=setCircleVals('z-increment',20)
zMin=-1*effectiveVal(zIncrement,setCircleVals('z-min',40))
print('zmin',zMin)
z=zMin
zTarg=effectiveVal(zIncrement,setCircleVals('z-max',60))
print (yTargH, y,yFinish)
#doesnt really work in practice, as need to align min to be compatible with divisor, in the sense that divisor overrides min

f.write(f"G0 X0 Y0 Z{z} \n\n")
#CIRCLE
if(yMax!=0):
    f.write(f"G0 X{x} Y{y+increment if hBarrier else y} Z{z} \n\n")
#seems to overshoot on some, under on others

#think it messes up if it starts wrong because it starts counting as if it is in right place, so ends up short

#need to move at right angles inwards



if hBarrier:y+=increment
print (yTargH, y,yFinish)
zLimit=0
while z<zLimit:
    #redundant reading here...
    
    f.write(f"G1 X{x} Y{y} Z{z} (chilipeppr_pause)\n\n")
    #technically the singular point is overshooting
    print (yTargH, y,yFinish)
    #need to consider endpoint, returning to that center spot
    #you do want this, however, that means it should offset by -1 at start
    partialEdgeCheck=True
    while(y>=yFinish if downwards else y<=yFinish):
        #overshoots to get the 0, but doesnt work if not full trip
        #this is one of the issues, it needs to do the line firs
        # Not sure how to best phrase this
        if ((y>=yTargH and hBarrier) or (y<=yTargL and lBarrier)) and partialEdgeCheck:
            partialEdgeCheck=False
        else: y+=-increment if downwards else increment
        lineEnd=calcEndpoint(radius,y,increment,buffer)
        
        #error is xTarg when going left
        x=relativeMin(-lineEnd if rightwards else lineEnd,xMin if rightwards else xMax)
        #xTarg 
        xTarg=relativeMin(lineEnd if rightwards else -lineEnd,xMax if rightwards else xMin)
        #the issue is if it is full you want the extra point (only 1 x), but otherwise you want it to stop

        #not yTarg cuz its always tgat
        #almost made it worse
        #its not the equals that is probelmatic, it is the next one that should only happen if it matxhes
        f.write(f"G1 X{x} Y{y} (chilipeppr_pause)\n")
        while x<xTarg if rightwards else x>xTarg:
            x+=increment if rightwards else -increment
            #if y==yFinish:x=0
            f.write(f"G1 X{x} Y{y} (chilipeppr_pause)\n")
        rightwards=False if rightwards else True
    downwards=False if downwards else True
    z+=zIncrement
    yFinish=yTargL if downwards else yTargH
    if z<=zLimit:f.write(f"G1 X{x} Y{y} Z{z} \n\n")
#above by some measure
f.write(f"G0 X0 Y0 Z{z}\n")

#deprecated feature
tailCoord=0

y=yMax
#still above
f.write(f"G1 X{x} Y{y} (chilipeppr_pause)\n")
z-=zIncrement
#moves down
f.write(f"G1 Z{z} (chilipeppr_pause)\n")

#clearance so i



xPositive=True if xMax!=0 else False
#main source of issue
while(z>=relativeMin(-thickness,zMin)):
    #print('Z',z)
    f.write(f"G1 X{x} Y{yMax} Z{z} (chilipeppr_pause)\n")
    #needs to go
    #can broadly be replaced by representing overall direction of reading relative to center
    tailSpace=False
    rightwards=True if xPositive else False
    xTarg=xMax if rightwards else xMin
    #tecnically overshoots a little and goes back
    while y>=yMin:
        #still need to put line switch in 
        #also need to consider before where circle starts
            #logic would be if(abs(y)>oRadius)
        while x<xTarg if rightwards else x>xTarg:
            x+=increment if rightwards else -increment
            f.write(f"G1 X{x} Y{y} (chilipeppr_pause)\n")
        y-=increment
        rightwards=False if rightwards else True
        line=LineBoundaries(y)
            

        # i think solution might be to maintain movement of single increment while only measuring if %2=0  
        #needs to change
        line.end=(calcEndpoint(oRadius,y,increment,buffer,False) * (1 if xPositive else -1)) if abs(y)<oRadius else (0 if tailSpace==False else (tailCoord if xPositive else -tailCoord))
        #tail coord will only be relevant for 1 quadrant
        if tailCoord==0 and line.end!=xMax and line.end!=xMin and abs(line.end*2)>thickness+buffer:
            tailCoord=abs(line.end)
            #print("tailcoord",tailCoord)
            
        #if abs(line.end)<=tailCoord and y<0:
            #tailSpace=True

        #change
        xTarg=(xMax if rightwards else line.end) if xPositive else (line.end if rightwards else xMin)
        #print(x,line.end,rightwards)
        x=(line.end if rightwards else x) if xPositive else (xMax if rightwards else line.end)
        if y>=yMin:f.write(f"G1 X{x} Y{y} (chilipeppr_pause)\n")
        #add cable gap later 
    if x!=(xMax if xPositive else xMin):
        #doesnt need to redeclare but i feel like it majkes it more clear/ easier to trace flow & errorss
        x=xMax if xPositive else xMin
    #f.write(f"G0 X{x} Y{y}\n")
    #i am a little confused about the little tails but it is not a huge deal
    y=yMax
    f.write(f"G0 X{x} Y{yMax}\n")
    x=0
    f.write(f"G0 X{x} Y{yMax}\n")

    z-=zIncrement
f.write(f"G0 X{xMin} Y{yMax} Z{0}\n")
downwards=True
#few issues, need seperate variables for coil height and total height, so know when to switch to others, because 0 is in center of coil




#cant do these moves, need to really consider possibilities
#f.write(f"G0 X0 Y0 Z0")
#f.write(f"G0 X{xMin} Y{xMin} Z0")

#square here

#more precise way
z=0
print('z',z)
f.write(f"G1 Z{z} (chilipeppr_pause)")

#seems to cross too much right here

while(z<=zTarg):
#a little connfusing but low meaninng start, high finish, irrespective of actual values
    lowY=yMax if downwards else yMin
    highY=yMin if downwards else yMax
    y=lowY
    while((downwards and y>=highY) or (downwards==False and y<=highY)):
        lowX=xMin if rightwards else xMax
        highX=xMax if rightwards else xMin
        x=lowX
        while (x!=highX):
            x+=increment if rightwards else -1*increment
            f.write(f"G1 X{x} (chilipeppr_pause)\n")
    
        #end behavior
        rightwards=False if rightwards else True
        if y!=highY:y+=-1*increment if downwards else increment
        else: break
        f.write(f"G1 X{x} Y{y} Z{z} (chilipeppr_pause)\n")
        #print(f"{y}-y {z}-z level complete\n")
    if z!=zTarg:z+=zIncrement
    else:break
    
    f.write(f"G1 X{x} Y{y} Z{z} (chilipeppr_pause)\n")
    downwards=False if downwards else True
    #print(f"{z} z level complete\n")

f.write(f"G0 X0 Y0 Z{z}")
f.write(f"G0 X0 Y0 Z0")
print('closing')
f.close()

f.close()
print('complete')
    
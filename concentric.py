#wider tail slot...

#-14->14 x -14->14
#7 radius, 1 inch increment both directions, 


#1 thickness from center
#iteration 1: <outer radius and negative regular
    #=outer radius->thickness: -thickness
    #after all the way to the end
#iteration 2:
    #stop at oradius-buffer



from helpers.helpers import modFloor,calcEndpoint,LineBoundaries,setCircleVals,setValues,effectiveVal,relativeMin,relativeMax
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

x=0
tail=True if yMin!=0 and xMin!=0 else False
tailWidth=2*thickness

# if i cut off on top, doesnt work overshoots where it shouldnt and undershjoots too


pathRadius=modFloor(radius-buffer,increment)
yTargH=min(pathRadius,yMax-increment)
hBarrier=True if yTargH!=pathRadius else False
#offset by 1 more at start
yStart=yTargH-increment
y=yTargH
if hBarrier==False:y+=increment
yTargL=relativeMin(-pathRadius,yMin+increment)
lBarrier=True if yTargL!=-pathRadius else False
#not sure if this is ideal
# f.write(f"G0 X{x} Y{y} Z0\n\n")

#can still do it otherwise, just only go as far as if it divisible
#deciding to work from center, even though it takes longer
#reason being is other wise, there could be some combinations of buffers and increments that wouldnt be centered a 0
yStart=yTargH-increment
yFinish=yTargL
x=calcEndpoint(radius,yStart,increment, buffer)
downwards=True
rightwards=False
zIncrement=setCircleVals('z-increment',30)
#zMin=-1*effectiveVal(zIncrement,setCircleVals('z-min',60))
z=0
zTarg=effectiveVal(zIncrement,setCircleVals('z-max',60))
#doesnt really work in practice, as need to align min to be compatible with divisor, in the sense that divisor overrides min

f.write(f"G0 X0 Y0 Z{z} \n\n")
#CIRCLE
if(yMax!=0):
    f.write(f"G0 X{x} Y{y+increment if hBarrier else y} Z{z} \n\n")
#seems to overshoot on some, under on others

#think it messes up if it starts wrong because it starts counting as if it is in right place, so ends up short




if hBarrier:y+=increment
zLimit=thickness
while z<zLimit:
    #redundant reading here...
    
    f.write(f"G1 X{x} Y{y} Z{z} (chilipeppr_pause);layer {z}\n\n")
    
    while(y>=yFinish if downwards else y<=yFinish):
        
        lineEnd=calcEndpoint(radius,y,increment,buffer)
        
        #Pretty sure this is no longer needed
        if(y!=0):
            x=relativeMin(-lineEnd if rightwards else lineEnd,xMin if rightwards else xMax)
            #xTarg 
            xTarg=relativeMin(lineEnd if rightwards else -lineEnd,xMax if rightwards else xMin)
        else:
            xTarg=-x
        #the issue is if it is full you want the extra point (only 1 x), but otherwise you want it to stop

        if y!=yStart:
            f.write(f"G1 X{x} Y{y} (chilipeppr_pause)\n")
        while x<xTarg if rightwards else x>xTarg:
            x+=increment if rightwards else -increment
            #if y==yFinish:x=0
            f.write(f"G1 X{x} Y{y} (chilipeppr_pause)\n")
        y+=-increment if downwards else increment
        rightwards=False if rightwards else True
    y+=increment if downwards else -increment
    downwards=False if downwards else True
    z+=zIncrement
    yFinish=yTargL if downwards else yTargH
    if z<=zLimit:f.write(f"G1 X{x} Y{y} Z{z};layer {z} \n\n")
#above by some measure
f.write(f"G0 X0 Y0 Z{z};layer {z}\n")

#deprecated feature
tailCoord=0

y=yMax
#still above
x=0
print(x)
f.write(f"G0 X{x} Y{y} (chilipeppr_pause)\n")
z-=zIncrement
#moves down
f.write(f"G0 X{x} Y{y} Z{z} (chilipeppr_pause);layer {z}\n")

#clearance so i

#




#assuming it is round tube, lower bounds will always be equal to -thickness if 0 is between two tubes
#should it start this below level with top or with level?
# also raises question of base collission
thicknessBuffer=(ceil(thickness/10)+ceil(buffer/10))*10
tempYmin=yMin
while(z>=0):
    yMin=tempYmin
    #print('Z',z)
    f.write(f"G1 X{x} Y{yMax} Z{z} (chilipeppr_pause);layer {z}\n")
    for i in range(0,2):
        tailZone=False
        tailSpace=False
        softLim=False
        rightwards=True if i==1 else False
        xTarg=xMax if rightwards else xMin
        if i==0 and y<0:
            softLim=True
        if i==1:
            yMin=-oRadius+thickness
        #tecnically overshoots a little and goes back
        while y>=yMin:
            #still need to put line switch in 
            #also need to consider before where circle starts
                #logic would be if(abs(y)>oRadius)
            while x<xTarg if rightwards else x>xTarg:
                x+=increment if rightwards else -increment
                f.write(f"G1 X{x} Y{y} (chilipeppr_pause)\n")
            y-=increment
            if y<=-oRadius+increment:
                    tailZone=True
            rightwards=False if rightwards else True
            line=LineBoundaries(y)
            #print(y,oRadius)
            #best way is to adjust for widest point in circle before it closes
            #more specifically wide enough to fit thickness and buffer
            #when it reaches that width on bottom 
            if softLim==True:
                line.end=relativeMax(-calcEndpoint(oRadius,y,increment,buffer,False),-thicknessBuffer)
            elif tailZone==True:
                if y>=-oRadius-thickness:
                    line.end=-thicknessBuffer
                else:
                    line.end=xMax
            else:
                line.end=(calcEndpoint(oRadius,y,increment,buffer,False) * (-1 if i==0 else 1)) if abs(y)<oRadius else (0 if tailSpace==False else (-tailCoord if i==0 else tailCoord))
                #just adding extra line for clarity
                #line.end=relativeMin(line.end,xMin if i==0 else xMax)
                if tailCoord==0 and line.end!=xMax and line.end!=xMin and abs(line.end*2)>thickness+buffer:
                    tailCoord=abs(line.end)
                    print("tailcoord",tailCoord)
            xTarg=(line.end if rightwards else xMin) if i==0 else ((xMax if rightwards else line.end))
            #print(x,line.end,rightwards)
            x=(x if rightwards else line.end) if i==0 else ((line.end if rightwards else x))
            if y>=yMin:f.write(f"G1 X{x} Y{y} (chilipeppr_pause)\n")
            #add cable gap later 
        if x!=(xMin if i==0 else xMax):
            #this is a major logic error, and it is causing the error
            x=xMin if i==0 else xMax
            f.write(f"G0 X{x} Y{yMin}\n") 
        #f.write(f"G0 X{x} Y{y}\n")
        #i am a little confused about the little tails but it is not a huge deal    
        y=yMax
        f.write(f"G0 X{x} Y{y}\n")
        x=0
        f.write(f"G0 X{x} Y{y}\n")
    z-=zIncrement
    print(x,y)

yMin=tempYmin
x=xMax
f.write(f"G0 X{x} Y{yMax} Z{0};layer {z}\n")
downwards=True
#few issues, need seperate variables for coil height and total height, so know when to switch to others, because 0 is in center of coil


#cant do these moves, need to really consider possibilities
#f.write(f"G0 X0 Y0 Z0")
#f.write(f"G0 X{xMin} Y{xMin} Z0")

#square here

#more precise way
z= ceil(thickness/zIncrement)*zIncrement

print("xmax",xMax)
f.write(f"G0 X{x} Y{yMax}Z{z} (chilipeppr_pause);layer {z}\n")

#seems to cross too much right here

#print('z',z,'ztarg',zTarg)
while(z<=zTarg):
#a little connfusing but low meaninng start, high finish, irrespective of actual values
    lowY=yMax if downwards else yMin
    highY=yMin if downwards else yMax
    y=lowY
    while((downwards and y>=highY) or (downwards==False and y<=highY)):
       # print(x,y)
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
    
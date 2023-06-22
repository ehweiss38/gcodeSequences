from helpers.helpers import modFloor, calcEndpoint, LineBoundaries, setCircleVals, setValues, effective_val, \
    relativeMin, \
    relativeMax, customerInfo, GCodeDoc
from math import ceil

'''
Can be thought of as three sequences

1. Up from bottom inside the circle
    This retains a lot from the previous iteration
2. Work down around edges, similar to previous, but needs to avoid corners

3. Work way up from the face
    a. tricky part is dealing with the circle, need to move forward and back, or in and out
    

'''

gcode = GCodeDoc(input('Enter file name'))

thickness = setCircleVals('thickness', 25)
radius = setCircleVals('radius', 70)
buffer = setCircleVals('buffer', 10)
increment = setCircleVals('increment', 10)

oRadius = radius + thickness
xMax = None
# need to further consider negative cases
while xMax is None:
    xMax = effective_val(setValues('x', True, 140, oRadius), increment)
    if xMax is None:
        print(f"Value must be greater than outer-radius({oRadius})")
xMin = None
print(xMax)
while xMin is None:
    xMin = effective_val(setValues('x', False, -140, oRadius), increment)
    if xMax is None:
        print(f"Value must be greater than outer-radius({oRadius})")
yMax = None
while yMax is None:
    yMax = effective_val(setValues('y', True, 140, oRadius), increment)
    if yMax is None:
        print(f"Value must be greater than outer-radius({oRadius})")
yMin = None
while yMin is None:
    yMin = effective_val(setValues('y', False, radius, radius), increment)
    if yMax is None:
        print(f"Value must be greater than outer-radius({oRadius})")

x = 0

effective_radius = modFloor(radius - buffer, increment)
y_targ_high = min(effective_radius, yMax - increment)
# remove offset
print(y_targ_high)
y = y_targ_high - increment
y_targ_low = relativeMin(-effective_radius, yMin + increment)
print(y_targ_low)
y_start = y_targ_high
y_finish = y_targ_low

x = calcEndpoint(radius, y_start, increment, buffer)

downwards = True
rightwards = False
zIncrement = setCircleVals('z-increment', 10)
zMin = effective_val(-thickness, zIncrement)
print(zMin, zIncrement)
z = effective_val(zMin, zIncrement)
z_targ = effective_val(setCircleVals('z-max', 60), zIncrement)

# wholly redundant
# gcode.g0(0, 0, z)
# CIRCLE

first_move = True

# if hBarrier:y+=increment
z_limit = 0
print('z', )
y += increment

if yMax != 0:
    gcode.g0(x, y, z)

gcode.g1(x, y, z)
while z <= z_limit:
    print(z, y)
    # redundant reading here...

    while y > y_finish if downwards else y < y_finish:

        if first_move is False:
            y += -increment if downwards else increment

        # issue
        lineEnd = calcEndpoint(radius, y, increment, buffer)
        print(y, lineEnd, x)
        # Pretty sure this is no longer needed

        if y != 0:
            # remove relative min

            x = relativeMin(-lineEnd if rightwards else lineEnd, xMin if rightwards else xMax)
            x_targ = relativeMin(lineEnd if rightwards else -lineEnd, xMax if rightwards else xMin)
            print(x_targ)
        else:
            x_targ = -x
        # the issue is if it is full you want the extra point (only 1 x), but otherwise you want it to stop

        if first_move:
            first_move = False
        else:
            gcode.g1(x, y)
        while x < x_targ if rightwards else x > x_targ:
            x += increment if rightwards else -increment
            # if y==yFinish:x=0
            gcode.g1(x, y)
        rightwards = False if rightwards else True
    # this is different from before, but it is very simple albeit potentially misnamed
    first_move = True

    downwards = False if downwards else True
    z += zIncrement
    y_finish = y_targ_low if downwards else y_targ_high
    if z <= z_limit:
        gcode.g1(x, y, int(z))
# above by some measure
x = y = 0
gcode.g0(x, y, int(z))

# dump
y = yMax
gcode.g0(x, y, z)
z = zMin

thicknessBuffer = (ceil(thickness / 10) + ceil(buffer / 10)) * 10

while z <= 0:
    # print('Z',z)
    gcode.g1(x, yMax, int(z))
    for i in range(0, 2):

        rightwards = True if i == 1 else False
        x_targ = xMax if rightwards else xMin
        if i == 0:
            yMin = -oRadius + thickness
        # tecnically overshoots a little and goes back
        while y >= yMin:
            # still need to put line switch in
            # also need to consider before where circle starts
            # logic would be if(abs(y)>oRadius)
            while x < x_targ if rightwards else x > x_targ:
                x += increment if rightwards else -increment
                gcode.g1(x, y)
            y -= increment
            rightwards = False if rightwards else True
            # semispurrious
            line = LineBoundaries(y)
            # print(y,oRadius)
            # best way is to adjust for widest point in circle before it closes
            # more specifically wide enough to fit thickness and buffer
            # when it reaches that width on bottom
            line.end = (calcEndpoint(oRadius, y, increment, buffer, False) * (-1 if i == 0 else 1)) if abs(
                y) < oRadius else 0
            # just adding extra line for clarity
            x_targ = (line.end if rightwards else xMin) if i == 0 else ((xMax if rightwards else line.end))
            # print(x,line.end,rightwards)
            x = (x if rightwards else line.end) if i == 0 else ((line.end if rightwards else x))
            if y >= yMin:
                gcode.g1(x, y)
            # add cable gap later
        if x != (xMin if i == 0 else xMax):
            # this is a major logic error, and it is causing the error
            x = xMin if i == 0 else xMax
            gcode.g0(x, yMin)
            # f.write(f"G0 X{x} Y{y}\n")
        y = yMax
        gcode.g0(x, y)
        x = 0
        gcode.g0(x, y)
    z += zIncrement
    print(x, y)

x = xMin
y = yMax

gcode.g0(x, y, z)
gcode.g1(x, y, z)

downwards = True
rightwards = True

print(z_targ)

while z < z_targ:
    inner_lims = None
    if thickness < z < radius:
        inner_lims = calcEndpoint(radius, oRadius - z, 10) if z < oRadius else calcEndpoint(radius, radius - (z + 10),
                                                                                            10, inner=True)
    outer_lims = calcEndpoint(oRadius, oRadius - (z + 10), 10) if z < oRadius else calcEndpoint(radius, oRadius - z, 10)
    # so it will never have to backtrack
    # the issue is x is way overshooting the bounds, so it loops infinitely
    x_targ = xMax if rightwards else xMin
    while x < x_targ if rightwards else x > x_targ:
        # issue only going up to inner radius, just variable declaration i think
        y_targ = y_targ_low if downwards else y_targ_high
        if downwards and (abs(x) > outer_lims or (inner_lims is not None and abs(x) < inner_lims)):
            y_targ -= effective_val(thickness, increment)
        while y > y_targ if downwards else y < y_targ:
            y += -increment if downwards else increment
            gcode.g1(x, y)
        x += increment if rightwards else increment
        downwards = False if downwards else True
        gcode.g1(x, y)
    rightwards = False if rightwards else True
    z += zIncrement
    gcode.g1(x, y, z)

'''
Third section will go up and down, in and out
Assuming that outer radius starts at 0
Need to add buffer for height, feed x for z limits, z for y limits


'''

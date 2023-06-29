from helpers.helpers import modFloor, calcEndpoint, LineBoundaries, setCircleVals, setValues, effective_val, \
    relativeMin, GCodeDoc, display_options, EndValue
from math import ceil

# One thing i will need to consider as I adapt this to the broader application is flexbility
# this can only produce orthogonal, so improving the algorithms so that they dont necessarilly each require own function


# Not perfect, but good enough for now

'''
Can be thought of as three sequences

1. Up from bottom inside the circle
    This retains a lot from the previous iteration
2. Work down around edges, similar to previous, but needs to avoid corners

3. Work way up from the face
    a. tricky part is dealing with the circle, need to move forward and back, or in and out


'''
# i think best way to go is dynamic x max that adjusts based on y and brace
# where it gets tricky is how you want to approach flexibility of this
# for that issue, i think all of the end values should be classes, calculates based on coordinate obstructions.
# Some degree of felxibility, also curious how it will interact with thickness. Does lend itself nicely to c# version


gcode = GCodeDoc(input('Enter file name'))

thickness = setCircleVals('thickness', 25)
radius = setCircleVals('radius', 70)
buffer = setCircleVals('buffer', 10)
increment = setCircleVals('increment', 10)
brace_plane = {1: False, 2: False, 3: False, 4: False}

brace = setCircleVals('brace', 0)
if brace != 0:
    brace_plane[
        display_options(
            "Which plane is brace on?\n1. Right-most\n2. Left-most\n3. Back-most\n4. Front-most ", 1, 4)] = True

outer_radius = radius + thickness
x_max = None
# need to further consider negative cases
while x_max is None:
    x_max = EndValue(effective_val(setValues('x', True, radius if brace_plane[2] else 140, outer_radius), increment),
                     brace if brace_plane[1] else 0, -thickness)
    if x_max is None:
        print(f"Value must be greater than outer-radius({outer_radius})")
x_min = None
while x_min is None:
    x_min = EndValue(effective_val(setValues('x', False, radius if brace_plane[2] else -140, outer_radius), increment),
                     brace if brace_plane[2] else 0, -thickness)
    if x_min is None:
        print(f"Value must be greater than outer-radius({outer_radius})")
y_max = None
while y_max is None:
    y_max = EndValue(effective_val(setValues('y', True, radius if brace_plane[3] else 140, outer_radius), increment),
                     brace if brace_plane[3] else 0, -thickness)
    if y_max is None:
        print(f"Value must be greater than outer-radius({outer_radius})")
y_min = None
while y_min is None:
    # this probably should not be hardcoded as such
    y_min = EndValue(effective_val(setValues('y', False, -radius if brace_plane[4] else -140, radius), increment),
                     brace if brace_plane[4] else 0, -thickness)
    if y_max is None:
        print(f"Value must be greater than outer-radius({outer_radius})")

x = 0

zIncrement = setCircleVals('z-increment', 10)
z_min = effective_val(-thickness, zIncrement)
# print(zMin, zIncrement)
z = 0
z_targ = effective_val(setCircleVals('z-max', outer_radius), zIncrement)

effective_radius = modFloor(radius - buffer, increment)
y_targ_high = min(effective_radius, y_max.calc_end(z, True) - increment)
# remove offset
# print(y_targ_high)
y = y_targ_high - increment
y_targ_low = relativeMin(-effective_radius, y_min.calc_end(z, True) + increment)
# print(y_targ_low)
y_start = y_targ_high
y_finish = y_targ_low

x = calcEndpoint(radius, y_start, increment, buffer)

downwards = True
rightwards = False

# wholly redundant
# gcode.g0(0, 0, z)
# CIRCLE

first_move = True

# if hBarrier:y+=increment
z_limit = 0
# print('z', )
y += increment

if y_max.calc_end(z) != 0:
    gcode.g0(x, y, z)

gcode.g1(x, y, z)
while z >= z_min:
    # print(z, y)
    # redundant reading here...

    while y > y_finish if downwards else y < y_finish:

        if first_move is False:
            y += -increment if downwards else increment

        # issue
        line_end = calcEndpoint(radius, y, increment, buffer)
        # print(y, lineEnd, x)
        # Pretty sure this is no longer needed

        if y != 0:
            # remove relative min

            x = relativeMin(-line_end if rightwards else line_end,
                            x_min.calc_end(z, True) if rightwards else x_max.calc_end(z, True))
            x_targ = relativeMin(line_end if rightwards else -line_end,
                                 x_max.calc_end(z, True) if rightwards else x_min.calc_end(z, True))
            # print(x_targ)
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
    z -= zIncrement
    print(z, z_limit)
    y_finish = y_targ_low if downwards else y_targ_high
    if z >= z_min:
        print('z', z)
        gcode.g1(x, y, int(z))
# above by some measure
x = y = 0
if z < z_min:
    z += zIncrement
gcode.g0(x, y, int(z))
gcode.g0(x, y, zIncrement)

# dump
# need to make this rotatable

y = y_max.calc_end(z)
gcode.g0(x, y, zIncrement)
z = z_min
gcode.g0(x, y, z)
# think this might be useless
thickness_buffer = (ceil(thickness / 10) + ceil(buffer / 10)) * 10

# on xmax edge, it goes up without first completing the row

# top half behavior is a little bit off..., edges dont close like they should, inner doesnt extend as it should

while z <= 0:
    # print('Z',z)
    gcode.g1(x, y_max.calc_end(z), int(z))
    for i in range(0, 2):

        rightwards = True if i == 1 else False
        x_targ = x_max.calc_end(z) if rightwards else x_min.calc_end(z)
        while y >= y_min.calc_end(z):
            # still need to put line switch in
            # also need to consider before where circle starts
            # logic would be if(abs(y)>oRadius)
            while x < x_targ if rightwards else x > x_targ:
                x += increment if rightwards else -increment
                gcode.g1(x, y)
            y -= increment
            rightwards = False if rightwards else True
            # semispurrious
            # print(y,oRadius)
            # best way is to adjust for widest point in circle before it closes
            # more specifically wide enough to fit thickness and buffer
            # when it reaches that width on bottom
            line_end = (calcEndpoint(outer_radius, y, increment, buffer, False) * (-1 if i == 0 else 1)) if abs(
                y) < outer_radius else 0
            # just adding extra line for clarity
            x_targ = (line_end if rightwards else x_min.calc_end(z)) if i == 0 else (
                x_max.calc_end(z) if rightwards else line_end)
            # print(x,line.end,rightwards)
            x = (x if rightwards else line_end) if i == 0 else (line_end if rightwards else x)
            if y >= y_min.calc_end(z):
                gcode.g1(x, y)
            # add cable gap later
        if x != (x_min.calc_end(z) if i == 0 else x_max.calc_end(z)):
            # this is a major logic error, and it is causing the error
            x = x_min.calc_end(z) if i == 0 else x_max.calc_end(z)
            gcode.g0(x, y_min.calc_end(z))
            # f.write(f"G0 X{x} Y{y}\n")
        y = y_max.calc_end(z)
        gcode.g0(x, y)
        x = 0
        gcode.g0(x, y)
    z += zIncrement
    # print(x, y)

x = x_min.calc_end(z)
y = y_max.calc_end(z)

gcode.g0(x, y, z)
gcode.g1(x, y, z)

downwards = True
rightwards = True

# print(z_targ)

# didnt properly consider height of probe
# worth also considering length of probe


while z <= z_targ:
    inner_lims = None

    # has trouble with the handoff here

    if thickness < z < radius * 2:
        inner_lims = calcEndpoint(radius, outer_radius - z, 10) if z < outer_radius else calcEndpoint(radius,
                                                                                                      radius - (
                                                                                                              z + 10), )
    outer_lims = calcEndpoint(outer_radius, outer_radius - (z + 10), 10) if z < outer_radius else calcEndpoint(radius,
                                                                                                               outer_radius - z,
                                                                                                               inner=False)
    # so it will never have to backtrack
    x_targ = x_max.calc_end(z) if rightwards else x_min.calc_end(z)
    while (x < x_targ) if rightwards else (x > x_targ):
        # issue only going up to inner radius, just variable declaration i think
        y_targ = y_min.calc_end(z) if downwards else y_max.calc_end(z)
        if downwards and (abs(x) > outer_lims or (inner_lims is not None and abs(x) < inner_lims)):
            y_targ -= effective_val(thickness, increment)
        while y > y_targ if downwards else y < y_targ:
            y += -increment if downwards else increment
            gcode.g1(x, y)
        x += increment if rightwards else -increment
        downwards = False if downwards else True
        gcode.g1(x, y)
    rightwards = False if rightwards else True
    z += zIncrement
    if z == z_targ:
        gcode.g0(0, 0)
        gcode.g0(0, 0, 0)
    gcode.g1(x, y, z)

'''
Third section will go up and down, in and out
Assuming that outer radius starts at 0
Need to add buffer for height, feed x for z limits, z for y limits


'''

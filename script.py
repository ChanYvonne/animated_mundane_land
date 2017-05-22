import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """

def first_pass( commands ):
    basename = "giffy"
    num_frames = 1
    yes_frames = False
    yes_basename = False
    yes_vary = False
    
    for line in commands:
        if line[0] == "frames":
            num_frames = int(line[1])
            yes_frames = True
        if line[0] == "basename":
            basename = line[0]
            yes_basename = True
        if line[0] == "vary":
            yes_vary = True

    if yes_vary and not yes_frames:
        print "Has vary but does not set frames"
        exit(0)
    if yes_frames and not yes_basename:
        print basename + "is being used and frames are set"

    return num_frames, basename

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands, num_frames ):
    knobs = []

    for x in range(num_frames):
        knobs.append({})
    for i in range(num_frames):
        for line in commands:
            if line[0] == "vary":
                word = line[1]
                start_frame = line[2]
                end_frame = line[3]
                start_val = line[4]
                end_val = line[5]
                if i >= start_frame and i <= end_frame:
                    mod = float((end_val-start_val)/(end_frame-start_frame+1))
                    val = start_val
                    for f in range(start_frame, end_frame+1):
                        knobs[f][word] = val
                        val += mod                
                
    return knobs

def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    num_frames, basename = first_pass(commands)
    knobs = second_pass(commands, num_frames)
    
    for frame in range(num_frames):
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        tmp = []
        step = 0.1
        knob_val = 1.0
        for command in commands:
            #print command
            c = command[0]
            args = command[1:]
            
            if c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                if num_frames > 1 and args[3] != None:
                    knob_val = knobs[frame][args[3]]
                tmp = make_translate(args[0] * knob_val,
                                     args[1] * knob_val,
                                     args[2] * knob_val)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if num_frames > 1 and args[3] != None:
                   knob_val = knobs[frame][args[3]]
                tmp = make_scale(args[0] * knob_val,
                                 args[1] * knob_val,
                                 args[2] * knob_val)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                if num_frames > 1 and args[2] != None:
                   knob_val = knobs[frame][args[2]]
                theta = args[1] * (math.pi/180) * knob_val
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                save_ppm(screen, 'pic.ppm')
            elif c == 'save':
                save_ppm(screen, args[0])

        if num_frames > 1:
            save_ppm(screen, 'anim/%s%03d.ppm'%('anim', frame))
        clear_screen(screen)
            

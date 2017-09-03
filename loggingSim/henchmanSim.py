from OpenGL.GL   import *
from OpenGL.GLUT import *
from OpenGL.GLU  import *
import numpy as np
import time
import random


def web23f( val, cache={} ):
    if val in cache:
        return cache[val]
    
    v = ""
    if( len( val ) > 6 ):
        if( val[0] == "#" ):
            v = val[1:7]
        else:
            v = val[:6]
    elif( len( val ) < 6 ):
        # some web colours are #123 -> #112233
        if( val[0] == "#" ):
            v = val[1]*2 + val[2]*2 + val[3]*2
        else:
            # can't untangle input
            v = "FFDEAD" # default to 'Navajo White'
    else:
        v = val
    r = float( int( v[0:2], 16 ) ) / 255.
    g = float( int( v[2:4], 16 ) ) / 255.
    b = float( int( v[4:6], 16 ) ) / 255.
    ret = (r, g, b)
    cache[val] = ret
    return ret

        
class KeyMan( object ):
    DOWN = 0
    UP   = 1
    
    SPECIAL_OS = 128
    LEFT_SHIFT = 112 + SPECIAL_OS
    RIGHT_SHIFT= 113 + SPECIAL_OS
    LEFT_CTRL  = 114 + SPECIAL_OS
    RIGHT_CTRL = 115 + SPECIAL_OS
    LEFT_ALT   = 116 + SPECIAL_OS
    
    
    def __init__( self ):
        self.history    = {}
        self.taps       = {}
        self.active     = set()
        self._boot      = time.time()
        self.tap_window = 0.255 # ms
        self.acumulate  = True
        self.last_time  = 0
        # registry
        self._rises    = {}
        self._falls    = {}
        self._taps     = {}
        
    def push( self, key_idx, action ):
        ''' deal with keypressess, keyholds, and keytaps.
            TODO:   work out packing sceme so all keys & modifiers fit
                    in flat contigious arrays (SoA)
        '''
        self.last_time = time.time()
        last_action = None
        if action==KeyMan.DOWN:
            self.active.add( key_idx )
            last_action = KeyMan.UP
        else:
            self.active.remove( key_idx )
            last_action = KeyMan.DOWN
            
        if key_idx not in self.history:
            self.history[ key_idx ] = [ 0, 0 ]
            self.taps[ key_idx ] = 0
        
        key_stats = self.history[ key_idx ]
        key_taps  = self.taps[ key_idx ]
        
        # log some data
        key_stats[ action ] = self.last_time
        delta = self.last_time - key_stats[last_action]
        
        # detect multi-taps
        if (delta < self.tap_window):
            # tapped
            if action==KeyMan.DOWN:
                key_taps += 1
        else:
            # out of tap window - tap count only cleared on subsequent press!
            if self.acumulate and action==KeyMan.DOWN:
                key_taps = 0

        # scan registered key events for 'key_idx' and emit CB
        if action==KeyMan.DOWN:
            if key_idx in self._falls:
                self._falls[key_idx]()
        else:
            if key_idx in self._rises:
                self._rises[key_idx]()
                
        if key_taps>1:
            if key_idx in self._taps:
                self._taps[key_idx]()
        # done
        
    def registerFallingCB( self, key_idx, fcall ):
        self._falls[key_idx] = fcall
        
    def registerRisingCB( self, key_idx, fcall ):
        self._rises[key_idx] = fcall
        
    def registerTapsCB( self, key_idx, fcall ):
        self._taps[key_idx] = fcall
        
        
class GLtoast( object ):

    def __init__( self ):
        self.g_wind = None
        self._glut_opts = None
        self._title = None
        self._wh = (640,480)
        self._native_wh = (1920,1280)
        self._pos = (0,0)
        self._center = False
        self._ratio_lock = True
        self._ratio = float(self._wh[0]) / float(self._wh[1])
        self._fov = 45.0
        self._z_clip = ( 0.1, 100.0 )
        self._key_man = KeyMan()
     
       
    def _reSize( self, width, height ):
        new_h = 2 if(height<2) else height
        new_w = 2 if(width<2)  else width
        ''' not quite right yet
        if self._ratio_lock:
            fw, fh = float( new_w ), float( new_h )
            ratio = fw/fh
            print ratio
            if( ratio > self._ratio ):
                # width wrong
                fw = fh / self._ratio
            elif( ratio < self._ratio ):
                # wrong height
                fh = fw * self._ratio
            new_w, new_h = int( fw ), int( fh )
            print new_w, new_h, (fw/fh)
        '''
        self._wh = ( new_w, new_h )
        
        
    def _idle( self ):
        glutPostRedisplay()
        #self._draw()
        
    def _draw( self ):
        pass

    def _keyDn( self, key, x, y ):
        self._action_pos = (x, y)
        self._key_man.push( ord(key.lower()), KeyMan.DOWN )
    
    def _keyUp( self, key, x, y ):
        self._action_pos = (x, y)
        self._key_man.push( ord(key.lower()), KeyMan.UP )
        
    def _keyDnS( self, val, x, y ):
        self._action_pos = (x, y)
        self._key_man.push( val + KeyMan.SPECIAL_OS, KeyMan.DOWN )
        
    def _keyUpS( self, val, x, y ):
        self._action_pos = (x, y)
        self._key_man.push( val + KeyMan.SPECIAL_OS, KeyMan.UP )
        
    def init( self ):
        # do glut init
        glutInit()
        glutInitDisplayMode( self._glut_opts )
        
        # Get Natove res
        self._native_wh = (glutGet( GLUT_SCREEN_WIDTH ), glutGet( GLUT_SCREEN_HEIGHT ))
        # TODO: guard against requested window size > native
        
        # auto center
        if self._center:
            pos_x = (self._native_wh[0]-self._wh[0]) / 2
            pos_y = (self._native_wh[1]-self._wh[1]) / 2
            self._pos = (pos_x, pos_y)
            
        glutInitWindowSize( self._wh[0], self._wh[1] )
        glutInitWindowPosition( self._pos[0], self._pos[1] )  
        self.g_wind = glutCreateWindow( self._title )
        
        # Enable GL Options
        glShadeModel(GL_SMOOTH)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        #glEnable(GL_LIGHTING)
        glDepthFunc(GL_LESS) 
    
        # bind std CBs
        glutDisplayFunc( self._draw   )
        glutIdleFunc(    self._idle   )
        glutReshapeFunc( self._reSize )
        
        # keys
        glutIgnoreKeyRepeat( 1 )
        glutKeyboardFunc(   self._keyDn  )
        glutKeyboardUpFunc( self._keyUp  )
        glutSpecialFunc(    self._keyDnS )
        glutSpecialUpFunc(  self._keyUpS )
        
        
    def prep( self ):
        pass
        
        
    def exe( self ):
        glutMainLoop()

        
    def end( self ):
        # graceful exit cb
        pass

        
class HenchSim( GLtoast ):
    ''' Been meening to write a 'capture henchman' tool for years. Oh well, now's
        my chance
    '''
    
    def __init__(self):
        super( HenchSim, self ).__init__()

        
    def init( self ):         # Fill,    Highlight
        self.colours = {"BACK":["696969","808080"], # Dim Gray, web Gray
                        "REG" :["C0C0C0","C0C0C0"], # Silver, Gainsboro
                        "REC" :["6B8E23","9ACD32"], # Olive Drab, Yellow Green
                        "MARK":["FFFFE0","FFDEAD"]  # Light Yellow, Navajo White
        }
        
        self.rec_list = []
        self.takes = {}
        self.take_no = 1
        self.active_take = None
        self.recording = False
        self.regioning = False
        
        # timing
        self.now = 0
        
        # Register keys / Callback into the key_man
        self._key_man.registerFallingCB( ord('r'), self._startTake   )
        self._key_man.registerFallingCB( ord('o'), self._regionOut   )
        self._key_man.registerFallingCB( ord('p'), self._marker      )
        self._key_man.registerFallingCB( ord('c'), self._endTake     )
        self._key_man.registerFallingCB( ord('a'), self._advanceTake )
        self._key_man.registerRisingCB(  ord('i'), self._regionIn    )
        
        # clean exit
        self._key_man.registerFallingCB( 27, self.end)
        super( HenchSim, self ).init()
        
        
    def end( self ):
        print self.takes
        exit(0)
        
        
    def _startTake( self ):
        #print "started @ {}".format( self._key_man.last_time )
        if not self.recording:
            self.recording = True
            self.takes[ self.take_no ] = {
                "START"  : self.now,
                "END"    : -1.,
                "REGIONS": [],
                "MARKS"  : []
            }
            self.active_take = self.take_no
        else:
            self.takes[ self.take_no ]["START"] = self.now
            
            
    def _endTake( self ):
        #print "ended @ {}".format( self._key_man.last_time )
        if self.recording:
            self.takes[ self.take_no ]["END"] = self.now
            self.recording = False
        if self.regioning:
            self.takes[ self.take_no ]["REGIONS"][-1][1] = self.now
            self.regioning = False
        # TODO: move Marks into their regions, upgrade regions to dicts
        
        
    def _regionIn( self ):
        #print "IN @ {}".format( self._key_man.last_time )
        if self.recording:
            if not self.regioning:
                # new sub region
                self.takes[ self.take_no ]["REGIONS"].append( [0.,-1.] )
                self.regioning = True
            else:
                # updating in time
                pass
            self.takes[ self.take_no ]["REGIONS"][-1][0] = self.now
            
            
    def _regionOut( self ):
        #print "OUT @ {}".format( self._key_man.last_time )
        if self.recording:
            if self.regioning:
                self.takes[ self.take_no ]["REGIONS"][-1][1] = self.now
                self.regioning = False
            else:
                # closed the last region, but want to extend?
                pass
                
                
    def _marker( self ):
        #print "MARKER @ {}".format( self._key_man.last_time )
        if self.recording:
            self.takes[ self.take_no ]["MARKS"].append(self.nowe)
            
            
    def _advanceTake( self ):
        self.take_no += 1
        print "Advance to {}".format( self.take_no )
        
        
    def drawRect2D( self, x, y, w, h, col=(.5,.0,.0), mode=GL_QUADS ):
        glColor3f( col[0], col[1], col[2] )
        glBegin( mode )
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        if mode==GL_LINES:
            glVertex2f(x, y)
            glVertex2f(x, y + h)
            glVertex2f(x + w, y)
            glVertex2f(x + w, y + h)
        glEnd()
          
          
    def set2D( self ):
        glViewport( 0, 0, self._wh[0], self._wh[1] )
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        glOrtho( 0.0, self._wh[0], 0.0, self._wh[1], 0.0, 1.0 )
        #glMatrixMode( GL_MODELVIEW )
        
        
    def _computeRecs( self ):
        off_x, off_y = 20, 20 # margin
        off_m = self._wh[0]-off_x # Right limit, inc margin
        disp_h = 20 # height of display
        disp_w = off_m - off_x
        
        # build draw list
        self.rec_list=[]
        # background
        colour = self.colours["BACK"]
        self.rec_list.append( (off_x, off_y, disp_w, disp_h, colour[0], GL_QUADS ) )
        self.rec_list.append( (off_x, off_y, disp_w, disp_h, colour[1], GL_LINES ) )
        
        # Take Data
        if self.active_take != None:
            dat = self.takes[self.active_take]
            start, end = dat["START"], dat["END"]
            end = self.now if end<0. else end # rolling Vs cut take
            draw_scale = float(off_m) / (end - dat["START"]) # pixels per second
            
            # regions
            colour = self.colours["REG"]
            for reg_start, reg_end in dat["REGIONS"]: # skips if empty
                offsetl = reg_start - start
                px_x = offsetl * draw_scale
                if reg_end > 0.:
                    # out point has been set
                    offsetr = reg_end - start
                else:
                    # no out set, so recording
                    offsetr = end - start
                    colour = self.colours["REC"]
                px_m = offsetr * draw_scale
                reg_x = int(px_x)
                reg_w = int(px_m) - reg_x
                # add region to list
                self.rec_list.append( (reg_x, off_y, reg_w, disp_h, colour[0], GL_QUADS ) )
                self.rec_list.append( (reg_x, off_y, reg_w, disp_h, colour[1], GL_LINES ) )
                
            # Finally, Marks
            colour = self.colours["MARK"]
            for mark in dat["MARKS"]:
                offset = mark - start
                px_x = offset * draw_scale
                mark_x = int(px_x) - 1
                self.rec_list.append( (mark_x, off_y, 3, disp_h, colour[0], GL_QUADS ) )
                self.rec_list.append( (mark_x, off_y, 3, disp_h, colour[1], GL_LINES ) )
            
            
    def _draw( self ):
        # gl Reset
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
        # Draw Stuff
        self.set2D()
        self.now = time.time()
        self._computeRecs()
        self.rec_list.reverse() # gl wants front to back drawing order
        
        for (x, y, w, h, col, mode) in self.rec_list:
            self.drawRect2D( x, y, w, h, web23f( col ), mode )
                    
        # swap
        glutSwapBuffers()   
        
        
myApp = HenchSim()
myApp._glut_opts = GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA #| GLUT_DEPTH
myApp._title = "MoCap Henchman, test regions"
myApp._center = True
myApp._wh = ( 640, 60 )

myApp.init()
myApp.prep()
myApp.exe()

"""
What's supposed to happen in here...

Take can have multiple sub-takes:

|--------------Take "blarBlar_AA_AA_001"--------------------|
   [---Sub 1---] [---Sub 2---]    [---Sub 3---] [---Sub 4---]
     a    b        a                 a     b      a  b   c 
                                     ^
so the indicated point in the take will be called: 'blarBlar_AA_AA_001.3.a'

When tying togeather multipule resources (Cams, Data, Audio, HMC), there will
be many possibly differing in/out points for a peice of media encompassing 
these ranges.  also deal with battery changes, slow starts, or loss of data.

future improvements allow advancing the 'alphas' and auto-incrementing the take no.
possibly bind Addvance/retreat to F1,F2 for Ax_xx, F3,F4 for xA_xx and so on.

"""
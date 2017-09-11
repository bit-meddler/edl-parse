from OpenGL.GL   import *
from OpenGL.GLUT import *
from OpenGL.GLU  import *
import numpy as np
import time
import random


import chromaTool as CT


class KeyMan( object ):
    # press states
    DOWN        = 0
    UP          = 1
    
    # key ids
    SPECIAL_OS  = 128
    MAX_SLOTS   = 255 # Arbitrary, I'll fix it if there's a crash
    C_RIGHT     = 100 + SPECIAL_OS
    C_UP        = 101 + SPECIAL_OS
    C_LEFT      = 102 + SPECIAL_OS
    C_DOWN      = 103 + SPECIAL_OS
    PGUP        = 104 + SPECIAL_OS
    PGDN        = 105 + SPECIAL_OS
    HOME        = 106 + SPECIAL_OS
    END         = 107 + SPECIAL_OS
    LEFT_SHIFT  = 112 + SPECIAL_OS
    RIGHT_SHIFT = 113 + SPECIAL_OS
    LEFT_CTRL   = 114 + SPECIAL_OS
    RIGHT_CTRL  = 115 + SPECIAL_OS
    LEFT_ALT    = 116 + SPECIAL_OS
    
    
    def __init__( self ):
        self.history     = np.zeros( (KeyMan.MAX_SLOTS, 2), dtype=np.float64 )
        self.taps        = np.zeros( KeyMan.MAX_SLOTS, dtype=np.uint8 )
        self.active      = np.zeros( KeyMan.MAX_SLOTS, dtype=np.uint8 )
        self._boot       = time.time()
        self.tap_window  = 0.255 # ms
        self.acumulate   = True
        self.last_time   = 0.
        self.last_action = 0
        # registry
        self._rises      = {}
        self._falls      = {}
        self._taps       = {}
        
        
    def push( self, key_idx, action ):
        ''' deal with keypressess, keyholds, and keytaps.
        '''
        now = time.time()
        last_action = int( not action )
        self.active[ key_idx ] = last_action
        self.last_time = now
        
        # SoA data
        self.history[ key_idx ][ action ] = now
        delta = now - self.history[ key_idx ][ last_action ]
                
        # detect multi-taps
        if (delta < self.tap_window):
            # tapped
            if action==KeyMan.DOWN:
                self.taps[ key_idx ] += 1
                
        else:
            # out of tap window - tap count only cleared on subsequent press!
            if self.acumulate and action==KeyMan.DOWN:
                self.taps[ key_idx ] = 0

        # check registered key events for 'key_idx' and emit CB
        if action : # up==1==True
            if key_idx in self._rises:
                self._rises[key_idx]()
        else:
            if key_idx in self._falls:
                self._falls[key_idx]()
            self.last_action = key_idx
                
        # I might not do it this way. I think a CB expecting to be tapped
        # should check taps[idx] when called (it knows the regidtered idx)
        if self.taps[ key_idx ]>1:
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
        self.reverseDrawOrder = True
        self.nav_mode = "MAYA" # TODO: "QUAKE" mode (wasd + orbit mouse)
     
       
    def _reSize( self, width, height ):
        new_h = 2 if(height<2) else height
        new_w = 2 if(width<2)  else width
        # TODO: fix fixed ratio window
        '''
        not quite right yet
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
        # if [Alt] pressed, mouse clicks are navigation taasks
        self._navigating = (self.nav_mode=="MAYA") and \
                            self._key_man.active[KeyMan.LEFT_ALT]
        
        glutPostRedisplay()
        
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
        # TODO: refactor to freeglut
        glutInit()
        glutInitDisplayMode( self._glut_opts )
        
        # Get Natove res
        self._native_wh = (glutGet( GLUT_SCREEN_WIDTH ), glutGet( GLUT_SCREEN_HEIGHT ))
        
        # Guard against requested window size > native
        new_wh = list( self._wh )
        new_wh[0] = min( self._wh[0], self._native_wh[0] )
        new_wh[1] = min( self._wh[1], self._native_wh[1] )
        self._wh = tuple( new_wh )
        
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

        

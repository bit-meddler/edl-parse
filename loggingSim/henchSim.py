from OpenGL.GL   import *
from OpenGL.GLUT import *
from OpenGL.GLU  import *
import numpy as np
import time
import datetime as DT
import calendar as CR

import gtBase
import chromaTool as CT
import tcLite     as TC


class HenchSim( gtBase.GLtoast ):
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
        now         = time.time()
        tmp_time    = DT.datetime.fromtimestamp( now )
        log_time    = DT.datetime( tmp_time.year, tmp_time.month, tmp_time.day, 0, 0, 0, 0 )
        self._epoch = CR.timegm( log_time.timetuple() )
        del( tmp_time, log_time, now )
        self.now = time.time() - self._epoch
        
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
        # TODO: Cast ToD stamps into TC strings
        
        
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
            self.takes[ self.take_no ]["MARKS"].append( self.now )
            
            
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
        self.now = time.time() - self._epoch
        self._computeRecs()
        if self.reverseDrawOrder:
            self.rec_list.reverse() # gl wants front to back drawing order
        
        for (x, y, w, h, col, mode) in self.rec_list:
            self.drawRect2D( x, y, w, h, CT.web23f( col ), mode )
                    
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

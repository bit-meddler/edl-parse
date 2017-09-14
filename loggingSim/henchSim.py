
import time

import numpy    as np
import datetime as DT
import calendar as CR

import gtBase
import chromaTool as CT


class HenchSim( gtBase.GLtoast ):
    ''' Been meening to write a 'capture henchman' tool for years. Oh well, now's
        my chance
    '''
    
    COLOURS = {  # Fill,   Highlight
        "BACK": ["696969","808080"], # Dim Gray, web Gray
        "REG" : ["C0C0C0","C0C0C0"], # Silver, Gainsboro
        "REC" : ["6B8E23","9ACD32"]  # Olive Drab, Yellow Green
    }
    
    MARK_COLOURS = (
                ("FA8072", "FFA07A"), # 0 Red (Salmon, lightSalmon)
                ("FF6347", "FF4500"), # 1 Orange (Tomato, OrangeRed)
                ("EEE8AA", "FFD700"), # 2 Yellow (PalegoldenRod, Gold)
                ("98FB98", "00FF7F"), # 3 Green (Palegreen, SpringGreen)
                ("AFEEEE", "7FFFD4"), # 4 Teal (PaleTurquoise, AquaMarine)
                ("4682B4", "1E90FF"), # 5 Blue (SteelBlue, DogerBlue)
                ("4169E1", "0000FF"), # 6 Indigo (RoyalBlue, Blue)
                ("9966CC", "BA2BE2"), # 7 Violet (Amethist, Blueviolet)
                ("F9A460", "D2691E"), # 8 Brown (SandyBrown, Chocolate)
                ("FFFAFA", "FFFFFF")  # 9 White (Snow, White)
    )
    
    def __init__(self):
        super( HenchSim, self ).__init__()

        
    def init( self ):
        # super
        super( HenchSim, self ).init()
        self._hud_man.addMsg( "LOG", "Booting...", CT.web23f("#0000FF") )
        
        # my Vars
        self.takes          = {}    # logging info
        self.take_no        = 1     # current take
        self.active_take    = None  # Current active take
        self.recording      = False # flags
        self.regioning      = False # flags
        self.bar_h          = 20    # height of display
        
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
        
        # set up Messages
        self._hud_man.addElement( "MSG", self._wh[0]-200, self._wh[1]-10, CT.web23f("#FFFFFF"), -1 )
        self._hud_man.addMsg( "LOG", "Ready!" )
        
        
    def end( self ):
        self._endTake()
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
            # are 'hints' pressed?
            which_np = np.where( self._key_man.active[48:58]==1 )
            which = map(int, which_np[0].tolist() )
            if len(which)==0:
                which =[9] # default to white
            self.takes[ self.take_no ]["MARKS"].append( (self.now, which) )
            
            
    def _advanceTake( self ):
        if not self.recording:
            self.take_no += 1
            retort = "Take: BlarBlar_AA_AA_{:0>3}".format( self.take_no )
            self._hud_man.addMsg( "LOG", "Advance", CT.web23f("#00FF00") )
            self._hud_man.addMsg( "MSG", retort )
        else:
            self.HUD_msg = "Can't advance when recording"
       
       
    def _computeRecs( self ):
        off_x, off_y = 20, 20 # margin
        off_m = self._wh[0]-off_x # Right limit, inc margin
        disp_w = off_m - off_x
        
        # build draw list
        self.rec_list=[]
        
        # background
        colour = self.COLOURS["BACK"]
        self.rec_list.append( (off_x, off_y, disp_w, self.bar_h, colour[0], self.STYLES["QUADS"]) )
        self.rec_list.append( (off_x, off_y, disp_w, self.bar_h, colour[1], self.STYLES["LINES"]) )
        
        # Take Data
        if self.active_take != None:
            dat = self.takes[self.active_take]
            start, end = dat["START"], dat["END"]
            end = self.now if end<0. else end # rolling Vs cut take
            draw_scale = float(off_m) / (end - dat["START"]) # pixels per second
            
            # regions
            colour = self.COLOURS["REG"]
            for reg_start, reg_end in dat["REGIONS"]: # skips if empty
                offsetl = reg_start - start
                px_x = offsetl * draw_scale
                if reg_end > 0.:
                    # out point has been set
                    offsetr = reg_end - start
                else:
                    # no out set, so recording
                    offsetr = end - start
                    colour = self.COLOURS["REC"]
                px_m = offsetr * draw_scale
                reg_x = int(px_x)
                reg_w = int(px_m) - reg_x
                # add region to list
                self.rec_list.append( (reg_x, off_y, reg_w, self.bar_h, colour[0], self.STYLES["QUADS"]) )
                self.rec_list.append( (reg_x, off_y, reg_w, self.bar_h, colour[1], self.STYLES["LINES"]) )
                
            # Finally, Marks
            for (mark, group) in dat["MARKS"]:
                offset = mark - start
                px_x = offset * draw_scale
                mark_x = int(px_x)
                colour = self.MARK_COLOURS[group[0]]
                self.rec_list.append( (mark_x, off_y, 3, self.bar_h, colour[0], self.STYLES["QUADS"]) )
                self.rec_list.append( (mark_x, off_y, 1, self.bar_h, colour[1], self.STYLES["LINES"]) )
            
            
    def _draw( self ):
        # Reset canvas
        self._clear()
    
        # Draw Stuff
        self.set2D()
        self.now = time.time() - self._epoch # I'd prefer not to do this every frame, but it's needed for drawing
        self._computeRecs()
        
        # do lists
        self.paintLists()
        
        # swap buffers & clean up
        super( HenchSim, self )._draw()
        
        
myApp = HenchSim()
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



DIGICONT_LOG = {
    "SESSION_DATA":{
        "PROJECT": NAME,
        "STAGE_ID": MAME,       # Id of stage, eg "A1", "A2", "B1"
        "STAGE_NAME": NAME,     # Name of stage (Ealing Main, Ealing ROM. Pinewood Main)
        "FRAME_RATE": NUMBER,
        "SUBJECTS_ENCOUNTERED": (NAME1,NAME2),
                                # Every subject activated ever this day
        "CAPTURE_PATH": TEXT,   # Path to where this data was captured
        "CAPTURE_HOST": TEXT,   # Hostname / IP / MAC of original capture host
        "UNIT": TEXT            # Name of Unit recording
    },
    "SCRIPT_DATA":{
        "SCENE_ID":{
            "SCENE_UUID": UUID  # UUID
            "SLATE": NAME       # slate name from production
            "SCENE": NAME       # Scene Name from production
            "SCENE_DESC": TEXT  # textual description of the scene
        }
    }
    "SESSION_TAKE_LOGS":{
        "TAKE_DISPLAY_NAME":{
            "UUID": UUID,
            "SCENE_ID"
            "TAKE_NAME_DETAIL": (BASENAME,SETUP,ACTION,TAKE) # Blar_AA_AA_0001
            "CREATION_TOD": (YYYY,MM,DD,HH,MM,SS,ZZZ), # 2017,09,12,13,50,45,GMT
            "SUBJECTS":(NAME1,NAME2),   # List of Subjects (actors)
            "IN": TIMECODE,             # Recording start timecode (NOT Action)
            "OUT": TIMECODE,            # End of recording timecode, might be 'cut' time
            "DURATION_FRAMES": NUMBER,  # Imply from end-start
            "SUBTAKES":{
                "ACTION": TIMECODE,     # action tc
                "CUT": TIMECODE,        # cut tc
                "MARKERS":{             # any markers logged, labelled [a-z]
                    "TIME": TIMECODE,   # TC
                    "NOTE": TEXT,       # Logging Notes
                    "D_NOTE": TEXT      # Director's notes
                },
                "PREFERENCE": TEXT,     # Director's Preference
                "NOTE": TEXT,           # Logging Note
                "D_NOTE": TEXT          # Director's notes
            },
            "COSTUME":( (SUBJECT1, TARGET1, TIMECODE),
                        (SUBJECT1, TARGET2, TIMECODE)
                        # Map of Subjects to 'costumes' and time they atarted wearing it
            )
        }
    },
    "SESSION_TAKE_DATA":{ # Technical date about MoCap
        "TAKE_DISPLAY_NAME":{ 
            "UUID": UUID,               # Inherited from Lag Log
            "CALIBRATION": FILENAME,    # MoCap Calibration in use
            "MASKS": FILENAME,          # Masks
            "CAMERA_SETTINGS": FILENAME,# camera data
            "DISPATCHERS_REGISTERED": (CAPTURE_SLAVE_NAME1, CAPTURE_SLAVE_NAME2)
            "DISPATCHER_LOGS":{
                CAPTURE_SLAVE_NAME:(
                    (TIMECODE,EVENT,TEXT),
                )
            }
        }
    }
}


# more like VFX set survey / Data acquisition than MoCap / Digi-Cont logging, but for extensibility, think about it...

CAM_REPORTS = {
    "KNOWN_CAMERAS": (CAMERA_NAME1, CAMERA_NAME2),
    "SESSION_DATA":{
        "PROJECT": NAME,
        "STAGE_ID": MAME,       # Id of stage, eg "A1", "A2", "B1"
        "STAGE_NAME": NAME,     # Name of stage (Ealing ROM. Pinewood Main)
        "FRAME_RATE": NUMBER,   # Project base frame-rate (can be overridden by cameras)
        "UNIT": TEXT            # Name of Unit recording
    },
    "TAKE_DATA":{
        "TAKE_DISPLAY_NAME":{
            "SETUP_ID"": ID,    # ID of the setup
            "CAMERA_LOGS":{
                "CAMERA_NAME":{
                    "ROLL": NAME,
                    "SHUTTER" NUMBER,
                    "F-STOP": NUMBER,
                    "FPS": NUMBER
                    "LENS_SN": NAME,
                    "FOCAL_LENGTH": NUMBER
                    "SYNCRONIZED": TRUE
                    "IN": TIMECODE
                    "OUT": TIMECODE
                }
            }
        }
    },
    "SETUP_DATA":{
        "SETUP_ID":{
            "ELEMENT_TYPE": TEXT,
            "ELEMENTS": (Set Extension, Chromakey ),
            "RECORDED": (IBC, Macbeth, Balls, Clean-pass, )
        },
    }
    "CAMERA_DATA":{
        "CAMERA_NAME":{
            "BODY_SN":NUMBER,
            "TYPE": NAME,
            "HIRE": NAME
        }
    }
    
}

VFX_SURVEY = {
    "SHOOTING_DATA":{
        "PROJECT": NAME,
        "STAGE_ID": MAME,       # Id of stage, eg "A1", "A2", "B1"
        "STAGE_NAME": NAME,     # Name of stage (Ealing ROM. Pinewood Main)
        "FRAME_RATE": NUMBER,   # Project base framerate (can be overridden by cameras)
        "UNIT": TEXT            # Name of Unit recording
        "LOCATION": GPS         # GPS location of shoot
    },
    "SETUPS":{
        "SETUP_ID":{
            "HDR":
            "SPHERICAL"
            "TRIG_SURVEY"
            "LIDAR_SCAN"
            "PHOTO_REF"
            "PHOTO_SCAN"
            "CONSTRUCTION_PLANS"
            "LIGHTING_PLOT"
        }
    }

}




































































"""

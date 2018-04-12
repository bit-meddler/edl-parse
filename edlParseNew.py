"""
EDL Parser, now with added complexity.
"""
import timecode as TC
import re

class EdEvent( object ):
    """
    An Edit event as encountered in an EDL.
    it will have an id, source and timeline Timecodes
    and then extended metadata for source clip name(s), transitions, named effects
    """
    
    def __init__( self, id ):
        self.id = id
        self.source_in = None
        self.source_out = None
        self.timeline_in = None
        self.timeline_out = None
        self.inner_name = None
        self.taking = None
        self.meta = {}
        self.extended = {}
        self.unexpected = []
        
        
class EdTransition( object  ):
    """
    A transition, which will have two events and some paramiterization of the
    transition, such as durration, speed, IN Time
    
    Expected Transitions:
        Disolve
        Wipe
        
    Transitions may additionally have Named Effect(s)
        Cross Disolve
        Cross Fade
        Constant Power
        
    """
    pass
    
    
class EdlParse( object ):
    """
    EDL parser
    """
    # Regexs
    M_EVENT = re.compile(      r"(\d{1,3})\s+" +                # 1 Cut id
                                "(\w+)\s+" +                    # 2 Inner Name
                                "([av/]+)\s+" +                 # 3 Taking
                                "(c|d|w\d+)\s+" +               # 4 Transition
                                "(\w*?)\s" +                    # 5 Optional Duration
                                "((?:(?:\d\d)[:;]?){4})\s+" +   # 6 Source In
                                "((?:(?:\d\d)[:;]?){4})\s+" +   # 7 Source Out
                                "((?:(?:\d\d)[:;]?){4})\s+" +   # 8 TL In
                                "((?:(?:\d\d)[:;]?){4})\s*",    # 9 TL Out
                                re.I )                          #   ignore case
                                
    M_CLIPNAMES = re.compile(  r"\*\s" +                        #   Start with a *
                                "(?:(from|to) clip name:)\s+" + # 1 From or to
                                "([\w\\/\-\.]+)",               # 2 the claip name
                                re.I )                          #   ignore case
                                
    M_NAMEDFX = re.compile(    r"^\*?\s?effect.*?(?:is|:)\s?" + #   Effect preamble
                                "([\w \-\\/]+)\s" +             # 1 Effect Name
                                "(\((?:[\w\d\+\-_ ]*)\))?\s*",  # 2 Optional paramiter
                                re.I )                          #   ignore case
                                
    M_TIMEWARP = re.compile(   r"m2\s+" +                       #   timewarp id
                                "(\w+)\s+" +                    # 1 inner name
                                "([-+]?[0-9]*\.?[0-9]+)\s+" +   # 2 new framerate
                                "((?:(?:\d\d)[:;]?){4})",       # 3 source_in
                                re.I )                          #   ignore case
                                
    M_DROPPING = re.compile(   r"fcm:\s+" +                     #   Rate preamble
                                "([\w\-]+)" +                   # 1 DF / NDF
                                "\s+frame", re.I )              #   Ignore Case
    
    # Special Test for corrupt timecode
    M_BAD_TC = re.compile(      r"\d{1,3}\s+" +                 #   id
                                "\w+\s+" +                      #   Inner Name
                                "[av/]+\s+" +                   #   Taking
                                "(?:c|d|w\d)+\s+" +             #   Transition
                                "\w*?\s" +                      #   Optional Duration
                                ".*?::\s*", re.I )              #   Corrupt TC!

                               
    def __init__( self, file_path=None, rate=25 ):
        self.source_file = file_path
        self.sequence_name = None
        self.events = {}
        self.event_order = []
        self.tc_drop = "NON-DROP"
        self.tc_rate = rate
        self.extended = []
        self._interuption = None
        self._fh = None
        self.unexpected = 0

        
    def _makeTC( self, tc_string ):
        tc = TC.Timecode( self.tc_rate, 1 )
        tc.setFromStringTC( tc_string )
        return tc

        
    def _makeEvent( self, id, match ):
        e = EdEvent( id )
        e.inner_name = match.group(2)
        e.taking = match.group(3)
        trans = match.group(4)
        if( trans != "C" ):
            # may have transition duration
            e.extended[ trans ] = match.group(5)
        e.source_in    = self._makeTC( match.group(6) )
        e.source_out   = self._makeTC( match.group(7) )
        e.timeline_in  = self._makeTC( match.group(8) )
        e.timeline_out = self._makeTC( match.group(9) )
        return e

        
    def _unexpected( self, line ):
        self.unexpected += 1
        print "Unrecognised EDL Line:\n'{}'".format( line )


    @staticmethod
    def _cleanLine( line ):
        line = line.replace( str(26), "" )
        return line.strip()

    
    def parse( self ):
        # open file
        fh = open( self.source_file, "rb" )
        
        cur_rate = cur_e_id = None

# Header ----------------------------------------------
        header = True
        while( header ):
            got_match = False
            line = self._cleanLine( fh.readline() )
            if( len( line ) < 3 ):
                # blank line
                continue
                
            match = re.match( r"title:\s+(.*)", line, re.I )
            if match:
                self.sequence_name = match.group( 1 ).strip()
                got_match = True
                
            match = self.M_DROPPING.match( line )
            if match:
                self.tc_drop = match.group( 1 )
                cur_rate = self.tc_drop
                got_match = True
                
            match = re.match( r"\*\s+format\s+(\d+x\d+)\s*([ip])\s*(\d+\.?\d*)fps", line, re.I )
            if match:
                # extended metadata
                self.extended.append( match.group(0) )
                if( self.tc_rate == None ):
                    self.tc_rate = int( float( match.group(3) ) )
                got_match = True
                
            # take what we can up too the first event.
            match = self.M_EVENT.match( line )
            if match:
                header = False
                got_match = True
            if not got_match:
                self._unexpected(line)
                
# Event List ---------------------------------------------------------
        cur_e_id = -1
        fails = 0
        while( len( line ) > 0 ):
            # Guard against blank line
            if( line.strip() == "" ):
                line = self._cleanLine( fh.readline() )
                fails = 0
                
            match = self.M_DROPPING.match( line )
            if match:
                # update dropping
                new_rate = match.group( 1 )
                if( new_rate != cur_rate ):
                    cur_rate = new_rate
                line = self._cleanLine( fh.readline() )
                fails = 0
            else:
                fails += 1
                
            # test for event
            match = self.M_EVENT.match( line )
            if match:
                test_id = int( match.group(1) )
                if( test_id != cur_e_id ):
                    # New Event
                    cur_e_id = test_id
                    e = self._makeEvent( cur_e_id, match )
                    e.meta[ "DROPPING" ] = cur_rate
                    # store
                    self.events[ cur_e_id ] = e
                    self.event_order.append( cur_e_id )
                else:
                    # usually a disolve transition
                    e = self._makeEvent( cur_e_id, match )
                    e.meta[ "DROPPING" ] = cur_rate
                    self.events[ cur_e_id ].extended[ "TRANSITION" ] = e
                line = self._cleanLine( fh.readline() )
                fails = 0
            else:
                fails += 1
                
            # test for expected metadata
            match = self.M_NAMEDFX.match( line )
            if match:
                line = self._cleanLine( fh.readline() )
                fails = 0
            else:
                fails += 1
                
            # test for ClipName Data
            match = self.M_CLIPNAMES.match( line )
            if match:
                line = self._cleanLine( fh.readline() )
                fails = 0
            else:
                fails += 1
                
            # test for a timewarp
            match = self.M_TIMEWARP.match( line )
            if match:
                line = self._cleanLine( fh.readline() )
                fails = 0
            else:
                fails += 1
               
            # Last resort
            if( fails > 5 ):
                # Test for corrupt TC
                match = self.M_BAD_TC.match( line )
                if match:
                    line = line.replace( "::", ":00:" )
                    # I give you back your life...
                    fails -= 1
                    continue
                # tried all Regexs, this is unknown metadata
                self.events[ cur_e_id ].unexpected.append( line )
                self._unexpected( line )
                line = self._cleanLine( fh.readline() )
                fails = 0
                
        # Done!
        if( self.unexpected > 0 ):
            print( "{} Unexpected Line{} found in this file!".format(
                self.unexpected, "s" if self.unexpected > 2 else "" ) )
            
        # END!
        
        
if __name__ == "__main__":
    # OK GO!
    import os
    tests = [ "example.edl", "RSG-BLACK-1.edl", "SCENEcombined.edl" ]
    for test in tests:
        file_name = os.path.join( "testData", test )
        print( test )
        edl = EdlParse( file_name )
        edl.parse()
        

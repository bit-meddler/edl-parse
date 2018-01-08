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
        
class EdlParse( object ):
    """
    EDL parser
    """
    # Regexs
    M_EVENT = re.compile(      r"(\d{3})\s+" +                  # Cut id
                                "(\w+)\s+" +                    # Inner Name
                                "([av/]+)\s+" +                 # Taking
                                "(c|d|w\d+)\s+(\w*?)\s" +       # Transition (Optional Duration)
                                "((?:(?:\d\d)[:;]?){4})\s+" +   # Source In
                                "((?:(?:\d\d)[:;]?){4})\s+" +   # Source Out
                                "((?:(?:\d\d)[:;]?){4})\s+" +   # TL In
                                "((?:(?:\d\d)[:;]?){4})\s*",    # TL Out
                                re.I )                          # ignore case
                                
    M_CLIPNAMES = re.compile(  r"\*\s" +                        # Start with a *
                                "(?:(from|to) clip name:)\s+" + # From or to
                                "([\w\\/\-\.]+)",               # the claip name
                                re.I )                          # ignore case
                                
    M_NAMEDFX = re.compile(    r"^\*?\s?effect.*?(?:is|:)\s?" + # Effect preamble
                                "([\w \-\\/]+)\s" +             # Effect Name
                                "(\((?:[\w\d\+\-_ ]*)\))?\s*",  # Optional paramiter
                                re.I )                          # ignore case
                                
    M_TIMEWARP = re.compile(   r"m2\s+" +                       # timewarp id
                                "(\w+)\s+" +                    # inner name
                                "([-+]?[0-9]*\.?[0-9]+)\s+" +   # new framerate
                                "((?:(?:\d\d)[:;]?){4})",       # source_in
                                re.I )                          # ignore case
                                
    def __init__( self, file_path=None ):
        self.source_file = file_path
        self.sequence_name = None
        self.events = {}
        self.event_order = []
        self.tc_rate = None
        
        self._interuption = None
        self._fh = None
        
    def parse( self ):
        # open file
        
        # read title
        
        # test for optional 'format' metadata
        
        # test for next event's Dropping standard
        
        # test for event fingerprint
        # test for metadata
        
        
if __name__ == "__main__":
    # OK GO!
    tests = [ "example.edl", "RSG-BLACK-1.edl", "SCENEcombined.edl" ]
    
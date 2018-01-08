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
    M_EDIT = re.compile(   r"(\d{3})\s+" +                # Cut id
                            "(\w+)\s+" +                  # Inner Name
                            "([av/]+)\s+" +               # Taking
                            "(c|d|w\d+)\s+(\w*?)\s" +     # Transition (Optional Duration)
                            "((?:(?:\d\d)[:;]?){4})\s+" + # Source In
                            "((?:(?:\d\d)[:;]?){4})\s+" + # Source Out
                            "((?:(?:\d\d)[:;]?){4})\s+" + # TL In
                            "((?:(?:\d\d)[:;]?){4})\s*" ) # TL Out
                            
                            
    def __init__( self, file_path=None ):
        self.source_file = file_path
        self.events = {}
        self.event_order = []
        self.tc_rate = None
        
        self._interuption = None
        self._fh = None
        
    def _fingerprint( self ):
        
        
        
if __name__ == "__main__":
    # OK GO!
    tests = [ "example.edl", "RSG-BLACK-1.edl", "SCENEcombined.edl" ]
    
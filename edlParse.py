import timecode as TC

class EDLparse( object ):

    EVENT_MAP = {
        "EVENT"      : 0,
        "AX"         : 1,
        "TAKING"     : 2,
        "TRANSITION" : 3,
        "CLIP_TC_IN" : 4,
        "CLIP_TC_OUT": 5,
        "SEQ_TC_IN"  : 6,
        "SEQ_TC_OUT" : 7
    }

    
    def __init__(self):
        self.name = None
        self.org_file = None
        self.title = None
        self.fcm = None
        self.events = []
        self._fh = None
        self.rate = TC.Timecode.TIME_RATES[ 25 ]

        
    def load( self, filename ):
        if self._fh:
            self._fh.close()

        self._fh = open( filename, "r" )

        line = self._fh.readline()
        _, self.title = line.split(":")

        line = self._fh.readline()
        _, self.fcm = line.split(":")
        
        event = {}
        start = True
        for line in self._fh.readlines():
            if len(line)<3:
                # new event
                if start:
                    # first event
                    start = False
                else:
                    self.events.append(event)
                    event = {}
            else:
                toks = line.split()
                if toks[0] == "*":
                    # asset data
                    if toks[1] == "FROM":
                        event["SOURCE_CLIP"] = toks[4]
                else:
                    # should be event line
                    event_num = -1
                    try:
                        event_num = int( toks[self.EVENT_MAP["EVENT"]] )
                    except ValueError:
                        print line
                        print "Unknown Key"
                        assert( False )
                    # OK
                    if len(self.EVENT_MAP) > len(toks):
                        print toks
                        print "unexpected"
                        assert( False )
                    for key, idx in self.EVENT_MAP.iteritems():
                        event[key] = toks[idx]
        if len(event)>0:
            self.events.append( event )
        self._fh.close()
        
        
    def toTC( self ):
        todo = ( "CLIP_TC_IN", "CLIP_TC_OUT", "SEQ_TC_IN", "SEQ_TC_OUT" )
        for e in self.events:
            for task in todo:
                if task in e:
                    tc_string = e[task]
                    e[task] = TC.Timecode( self.rate, 1 )
                    e[task].setFromStringTC( tc_string )
        #
# Bit hairy, but I only have one Example EDL to play with
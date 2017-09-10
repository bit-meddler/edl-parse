''' minimal timecode implementation for logging sim '''
import re # to split tc String

class Timecode( object ):

    def __init__( self, rate, divisor ):
        self.rate = rate
        self.divisor = divisor
        self.true_rate = rate * divisor
        self.frame_dur = 1. / self.true_rate
        self._reset()
        
    def _reset( self ):
        self.QSE = 0.
        
    def setSecs( self, secs_from_midnight=None ):
        if secs_from_midnight==None:
            return
            
        self._reset()            
        tsecs,  subsecs = divmod( secs_from_midnight,  1. )
        frames, remains = divmod( subsecs, self.frame_dur )
        hours, mins_sec = divmod( tsecs,             3600 )
        mins,      secs = divmod( mins_sec,            60 )
        self.QSE = int( (self.rate * tsecs) + frames )
        
    def setString( self, tc_str=None ):
        if tc_str == None:
            return
            
        toks = re.split(':|;|\.', tc_str)
        num = len( toks )
        parts = [0,0,0,0] # h, m, s, f
        vals = map(int, toks)
        if num>4:
            num = 4 # limit to just hmsf, ignor subframes
        for i in xrange( num ): # default to zero if secs or frames missing
            parts[i] = vals[i]
        parts[0] *= 3600
        parts[1] *=   60
        tsecs = sum( parts[:3] )
        self.QSE = int( (self.rate * tsecs) + parts[3] )
    
    def tcTuple( self ):
        secs, frames = divmod( self.QSE, self.rate )
        hours, minss = divmod( secs, 3600 )
        mins,   secs = divmod( minss,  60 )
        return (hours, mins, secs, frames)
        
    def toString( self ):
        return "{}:{}:{}:{}".format( *self.tcTuple() )
        
        
if __name__ == "__main__":
    rates = (24, 24, 25, 30, 30)
    divs = ((1./1.001),
            (1./1.000),
            (1./1.000),
            (1./1.001),
            (1./1.000)
    )
    # from secs since midnight
    x = 60732.72199988365 # 16:52:12.721
    for rate, divisor in zip( rates, divs ):
        code = Timecode( rate, divisor )
        code.setSecs( x )
        print code.toString()
        
    # from string    
    x = '20:29:38:6'
    print x
    for rate, divisor in zip( rates, divs ):
        code = Timecode( rate, divisor )
        code.setString( x )
        print code.QSE, code.toString()

"""
Some tools to help with colours in OpenGL
20/7/2017 : RichH

TYPES:

RGB8 = 3 uint8s   r,g,b
HSV8 = 3 uint8s   r,g,b
hsvf = 3 float32s h,s,l
gl3f = 3 float32s r,g,b
gl4f = 4 float32s r,g,b,a

All f assumed to be in range 0. ~ 1.

hex = web hex code

"""
import numpy as np

X11LUT_RGB8 = {"AliceBlue": (240, 248, 255),
            "AntiqueWhite": (250, 235, 215),
                    "Aqua": (  0, 255, 255),
              "Aquamarine": (127, 255, 212),
                   "Azure": (240, 255, 255),
                   "Beige": (245, 245, 220),
                  "Bisque": (255, 228, 196),
                   "Black": (  0,   0,   0),
          "BlanchedAlmond": (255, 235, 205),
                    "Blue": (  0,   0, 255),
              "BlueViolet": (138,  43, 226),
                   "Brown": (165,  42,  42),
               "Burlywood": (222, 184, 135),
               "CadetBlue": ( 95, 158, 160),
              "Chartreuse": (127, 255,   0),
               "Chocolate": (210, 105,  30),
                   "Coral": (255, 127,  80),
          "CornflowerBlue": (100, 149, 237),
                "Cornsilk": (255, 248, 220),
                 "Crimson": (220,  20,  60),
                    "Cyan": (  0, 255, 255),
                "DarkBlue": (  0,   0, 139),
                "DarkCyan": (  0, 139, 139),
           "DarkGoldenrod": (184, 134,  11),
                "DarkGray": (169, 169, 169),
               "DarkGreen": (  0, 100,   0),
                "DarkGrey": (169, 169, 169),
               "DarkKhaki": (189, 183, 107),
             "DarkMagenta": (139,   0, 139),
          "DarkOliveGreen": ( 85, 107,  47),
              "DarkOrange": (255, 140,   0),
              "DarkOrchid": (153,  50, 204),
                 "DarkRed": (139,   0,   0),
              "DarkSalmon": (233, 150, 122),
            "DarkSeaGreen": (143, 188, 143),
           "DarkSlateBlue": ( 72,  61, 139),
           "DarkSlateGray": ( 47,  79,  79),
           "DarkSlateGrey": ( 47,  79,  79),
           "DarkTurquoise": (  0, 206, 209),
              "DarkViolet": (148,   0, 211),
                "DeepPink": (255,  20, 147),
             "DeepSkyBlue": (  0, 191, 255),
                 "DimGray": (105, 105, 105),
                 "DimGrey": (105, 105, 105),
              "DodgerBlue": ( 30, 144, 255),
               "Firebrick": (178,  34,  34),
             "FloralWhite": (255, 250, 240),
             "ForestGreen": ( 34, 139,  34),
                 "Fuchsia": (255,   0, 255),
               "Gainsboro": (220, 220, 220),
              "GhostWhite": (248, 248, 255),
                    "Gold": (255, 215,   0),
               "Goldenrod": (218, 165,  32),
                    "Gray": (128, 128, 128),
                   "Green": (  0, 128,   0),
             "GreenYellow": (173, 255,  47),
                    "Grey": (128, 128, 128),
                "Honeydew": (240, 255, 240),
                 "HotPink": (255, 105, 180),
               "IndianRed": (205,  92,  92),
                  "Indigo": ( 75,   0, 130),
                   "Ivory": (255, 255, 240),
                   "Khaki": (240, 230, 140),
                "Lavender": (230, 230, 250),
           "LavenderBlush": (255, 240, 245),
               "LawnGreen": (124, 252,   0),
            "LemonChiffon": (255, 250, 205),
               "LightBlue": (173, 216, 230),
              "LightCoral": (240, 128, 128),
               "LightCyan": (224, 255, 255),
          "LightGoldenrod": (238, 221, 130),
    "LightGoldenrodYellow": (250, 250, 210),
               "LightGray": (211, 211, 211),
              "LightGreen": (144, 238, 144),
               "LightGrey": (211, 211, 211),
               "LightPink": (255, 182, 193),
             "LightSalmon": (255, 160, 122),
           "LightSeaGreen": ( 32, 178, 170),
            "LightSkyBlue": (135, 206, 250),
          "LightSlateBlue": (132, 112, 255),
          "LightSlateGray": (119, 136, 153),
          "LightSlateGrey": (119, 136, 153),
          "LightSteelBlue": (176, 196, 222),
             "LightYellow": (255, 255, 224),
                    "Lime": (  0, 255,   0),
               "LimeGreen": ( 50, 205,  50),
                   "Linen": (250, 240, 230),
                 "Magenta": (255,   0, 255),
                  "Maroon": (128,   0,   0),
        "MediumAquamarine": (102, 205, 170),
              "MediumBlue": (  0,   0, 205),
            "MediumOrchid": (186,  85, 211),
            "MediumPurple": (147, 112, 219),
          "MediumSeaGreen": ( 60, 179, 113),
         "MediumSlateBlue": (123, 104, 238),
       "MediumSpringGreen": (  0, 250, 154),
         "MediumTurquoise": ( 72, 209, 204),
         "MediumVioletRed": (199,  21, 133),
            "MidnightBlue": ( 25,  25, 112),
               "MintCream": (245, 255, 250),
               "MistyRose": (255, 228, 225),
                "Moccasin": (255, 228, 181),
             "NavajoWhite": (255, 222, 173),
                    "Navy": (  0,   0, 128),
                "NavyBlue": (  0,   0, 128),
                 "OldLace": (253, 245, 230),
                   "Olive": (128, 128,   0),
               "OliveDrab": (107, 142,  35),
                  "Orange": (255, 165,   0),
               "OrangeRed": (255,  69,   0),
                  "Orchid": (218, 112, 214),
           "PaleGoldenrod": (238, 232, 170),
               "PaleGreen": (152, 251, 152),
           "PaleTurquoise": (175, 238, 238),
           "PaleVioletRed": (219, 112, 147),
              "PapayaWhip": (255, 239, 213),
               "PeachPuff": (255, 218, 185),
                    "Peru": (205, 133,  63),
                    "Pink": (255, 192, 203),
                    "Plum": (221, 160, 221),
              "PowderBlue": (176, 224, 230),
                  "Purple": (128,   0, 128),
                     "Red": (255,   0,   0),
               "RosyBrown": (188, 143, 143),
               "RoyalBlue": ( 65, 105, 225),
             "SaddleBrown": (139,  69,  19),
                  "Salmon": (250, 128, 114),
              "SandyBrown": (244, 164,  96),
                "SeaGreen": ( 46, 139,  87),
                "Seashell": (255, 245, 238),
                  "Sienna": (160,  82,  45),
                  "Silver": (192, 192, 192),
                 "SkyBlue": (135, 206, 235),
               "SlateBlue": (106,  90, 205),
               "SlateGray": (112, 128, 144),
               "SlateGrey": (112, 128, 144),
                    "Snow": (255, 250, 250),
             "SpringGreen": (  0, 255, 127),
               "SteelBlue": ( 70, 130, 180),
                     "Tan": (210, 180, 140),
                 "Thistle": (216, 191, 216),
                  "Tomato": (255,  99,  71),
               "Turquoise": ( 64, 224, 208),
                  "Violet": (238, 130, 238),
               "VioletRed": (208,  32, 144),
                   "Wheat": (245, 222, 179),
                   "White": (255, 255, 255),
              "WhiteSmoke": (245, 245, 245),
                  "Yellow": (255, 255,   0),
             "YellowGreen": (154, 205,  50),
}

# Normalize Colours into 4 floats
def _flexCol( col, alpha=None ):
    sz = 0
    if col==None:
        _col = (1.,0.,0.)
        sz = 3
    else:
        _col = col
        sz   = len( col )
        
    gl_col = [ _col[0], _col[1], _col[2], 1.0 ]
    
    if ( sz==4 ):
        gl_col[3] = col[3]
    if not alpha == None:
            gl_col[3] = alpha
            
    return gl_col

    
def web24f( val, alpha=None ):
    a = alpha if not alpha==None else 1.0
    r, g, b = web23f( val )
    return ( r, g, b, a )
    
    
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
    
    
def int2glf( integers ):
    return map( lambda x: float(x)/255., integers )

    
def hex2rgb8( val, _cache={} ): # The cache is local to this function
    if val in _cache:
        return _cache[val]
    val_sz = len(val)
    v = ""
    if val.startswith( "#" ):
        # Web colour
        if( val_sz==7 ): # '#123456'
            v = val[1:7]
        elif( val_sz==4 ): # '#123' -> '#112233'
            v = val[1] + val[1] + val[2] + val[2] + val[3] + val[3]
    elif val in X11LUT_RGB8:
        ret = X11LUT_RGB8[val] # stash it
        _cache[val] = ret
        return ret
    else:
        v = val[:6] # Try trunkating
        
    r, g, b = 128, 128, 128
    try:
        r = int( v[0:2], 16 )
        g = int( v[2:4], 16 )
        b = int( v[4:6], 16 )
    except e:
        # assume one of the casts failed
        r, g, b = 255, 0, 0 # red is the tradional colour of an error
        
    ret = (r, g, b)
    _cache[val] = ret
    return ret

    
def gl3f2hslf( rgbf ):
    """
    Attempt at https://en.wikipedia.org/wiki/HSL_and_HSV#Hue_and_chroma
    see also: http://www.niwa.nu/2013/05/math-behind-colorspace-conversions-rgb-hsl/
    """
    r, g, b = rgbf
    h, s, l = 0., 0., 0.
    
    M = max( r, g, b )  
    m = min( r, g, b )  
    C = M - m # chroma
    l = (M+m)*0.5 # Lightness
    
    # if no chroma, then a grey shade (r==g==b)
    if C==0.:
        return (0., 0., l)
    
    # piecewise hue computation
    H_ = 0.
    if   (M==r):
        H_ = ((g-b)/C)%6.
    elif (M==g):
        H_ = ((b-r)/C)+2
    elif (M==b):
        H_ = ((r-g)/C)+4
    h = H_ /6. # [0..1]
    
    # saturation
    s = 0. if (l==1.) else (C/(1-abs((2*l)-1)))
    
    return (h, s, l)
    

# Selector shuffle based on interval    
_INTERVALS = ( (1., (1,2,0)),  # (C, X, 0)
               (2., (2,1,0)),  # (X, C, 0)
               (3., (0,1,2)),  # (0, C, X)
               (4., (0,2,1)),  # (0, X, C)
               (5., (2,0,1)),  # (X, 0, C)
               (6., (1,0,2)) ) # (C, 0, X)
def hslf2gl3f( hslf ):
    # https://en.wikipedia.org/wiki/HSL_and_HSV#Converting_to_RGB
    h, s, l = hslf
    
    C  = (1. - abs( (l*2.) - 1. ) ) * s # chroma
    h6 = h*6. # h=[0,1] algo wants h=[0,360] to then divide by 60
    X  = C * (1. - abs( (h6%2) - 1. ) )
    
    # sanity test
    if (h6<0.) or (h6>6.):  # if H is bad
        return (0., 0., 0.)
        
    # Pick correct shuffle of C, X, and 0 piecewise 
    R_, G_, B_ = 0., 0., 0.
    vals = [0., C, X]
    for interval, selector in _INTERVALS:
        if (h6<=interval):
            _1, _2, _3 = selector
            R_, G_, B_ = vals[_1], vals[_2], vals[_3]
            break
            
    # compute
    m = l - (C*0.5)
    return ( (R_+m), (G_+m), (B_+m) )

    
class GLchroma( object ): # Doesn't really need to be an object, but for teaching...
    R, G, B, A = 0, 1, 2, 3
    
    def __init__( self, first=None, second=None, third=None, four=None, mode=""):
        # main colour (for ogl)
        self.col = np.array( [0., 0., 0., 1.], dtype=np.float32 )
        # HSL for shade wheeling
        self.h, self.s, self.l, self.h_deg = 0., 0., 0., 0.
        if first == None:
            # default constructor
            return
            
        # interpret input
        if( type( first )==str ):
            # assume web colours
            self.col[:3] = int2glf( hex2rgb8( first ) )
            # test for alpha
            if second != None:
                if( type( second )==float ):
                    # if a float assume it's alpha for the web colour
                    self.col[A] = np.clip( second, 0., 1. )
                elif( type( second )==int ):
                    # if it's an int assume 0==0, 1==1, 2..255 = 0.05..1.0, 255> = 1.
                    if( second>1 and second<255 ):
                        self.col[A] = float( second / 255. )
                    else:
                        self.col[A] = 1. if second>0 else 0.
                        
        elif( type( first )==int ):
            # assume RGB8 values
            self.col = np.array( [first, second, third, 255], dtype=np.float32 )
            self.col /= 255.
            
            if four != None:
                if( type( four )==int ):
                    self.col[A] = float( four ) / 255.
                elif( type( four )==float ):
                    self.col[A] = np.clip( four, 0., 1. )
                    
        elif( type( first )==float ):
            # assume 3 or 4 floats
            self.col = np.array( [first, second, third, 1.], dtype=np.float32 )
            self.col[A] = four if four!=None else 1.
            self.col = np.clip( self.col, 0., 1. )
            
        # compute hsl
        self._recompHSL()
        
        
    def _recompHSL( self ):
        self.h, self.s, self.l = gl3f2hslf( (self.col[self.R], self.col[self.G], self.col[self.B]) )
        self.h_deg = 360. * self.h
        
        
    def _recompRGB( self ):
        r, g, b = hslf2gl3f( (self.h, self.s, self.l))
        a = self.col[GLchroma.A]
        self.col = np.array( [r, g, b, a] )
        
        
    def fromHSL( self, h, s, l, alpha=None ):
        self.h, self.s, self.l = h, s, l
        self.h_deg = 360. * self.h
        if alpha != None:
            self.col[GLchroma.A] = alpha
        self._recompRGB()
        
        
    def __str__(self):
        return "Chroma: (R:{}, G:{}, B{}, A:{}) (H:{} Deg)".format(
            self.col[self.R], self.col[self.G], self.col[self.B], self.col[self.A],
            self.h_deg )


def steppedTones( steps, start_chroma, end_chroma ):
    # TODO: this is buggy!
    start_angle = start_chroma.h_deg / 360.
    end_angle   = end_chroma.h_deg   / 360.
    # initally seed from start s/l/ab
    saturation, lightness, alpha = start_chroma.s, start_chroma.l, start_chroma.col[3]
    ret = []
    off = (end_angle - start_angle) / steps
    for i in xrange( steps ):
        newCol = GLchroma()
        newCol.fromHSL( start_angle + (off+(i-1)), saturation, lightness, alpha )
        ret.append( newCol )
    return ret
    
if __name__ == "__main__":    
    rgb_ = X11LUT_RGB8["AliceBlue"]
    rgb = int2glf( rgb_ )
    hsl = gl3f2hslf( rgb )
    print rgb_, rgb, hsl
    rgb3 = hslf2gl3f( hsl )
    print rgb3, map(lambda x: int(x*255.), rgb3)

    ab = GLchroma( "AliceBlue" )
    print ab.h_deg
    print ab.col
    print ab

    l = steppedTones(5, ab, GLchroma( "Olive" ) )
    for i in l:
        print i
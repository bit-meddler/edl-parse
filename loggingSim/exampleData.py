''' Logging  Dict, DATA generated wih the Henchman sim. '''
import datetime as DT
import calendar as CR
from copy import deepcopy

import tcLite   as TC

dat = {
    1 : {
     'REGIONS': [[1504457535.072, 1504457537.904], [1504457538.888, 1504457543.504], [1504457544.621, 1504457547.256], [1504457548.806, 1504457568.556], [1504457573.139, 1504457587.355], [1504457593.238, 1504457601.022], [1504457611.954, 1504457620.104]],
     'START': 1504457532.722,
     'END': 1504457623.171,
     'MARKS': [1504457540.671, 1504457541.338, 1504457542.171, 1504457544.989, 1504457545.489, 1504457545.972, 1504457546.456, 1504457556.272, 1504457560.221, 1504457563.339, 1504457567.339, 1504457575.571, 1504457580.339, 1504457586.122]
    },
    2 : {
     'REGIONS': [[1504457636.219, 1504457641.403], [1504457644.185, 1504457655.103], [1504457656.136, 1504457665.535]],
     'START': 1504457634.421,
     'END': 1504457668.069,
     'MARKS': []
    },
    3 : {
    'REGIONS': [[1504729728.944, 1504729739.264], [1504729744.288, 1504729754.12], [1504729758.632, 1504729763.335], [1504729768.128, 1504729778.248]],
    'START': 1504729724.544,
    'END': 1504729778.248,
    'MARKS': []
    }
}

# Turn this lot into timecodes
logging = deepcopy( dat )

code = TC.Timecode( 25, (1./1.000) )

for id, logs in logging.iteritems():
    # get TC epoch 
    start_stamp = logs['START']
    start_time  = DT.datetime.fromtimestamp( start_stamp )
    log_time    = DT.datetime( start_time.year, start_time.month, start_time.day, 0, 0, 0, 0 )
    log_epoch   = CR.timegm( log_time.timetuple() )
    # for every event in the log, subtract the epoch
    code.setSecs( logs['START'] - log_epoch )
    logs['START'] = code.toString()
    code.setSecs( logs['END'] - log_epoch )
    logs['END'] = code.toString()
    for r in logs['REGIONS']: # can manip a reffed object
        code.setSecs( r[0] - log_epoch )
        r[0] = code.toString()
        code.setSecs( r[1] - log_epoch )
        r[1] = code.toString()
    for i, m in enumerate( logs['MARKS'] ): # but not a number
        code.setSecs( m - log_epoch )
        logs['MARKS'][i] = code.toString()
        
print logging
# TODO: Devise logging format


from baseoccquery import BaseOccQuery
from drverrflagbase import DRVErrFlag_Base
from drverrflagbottom import DRVErrFlag_bottom
from drverrflagtop import DRVErrFlag_Top
from drverrflagftside import DRVErrFlag_FTSide
from drverrflagpipeside import DRVErrFlag_PipeSide
from evtratesum import EVTRate_Sum
from maxbuffocc import MaxBuff_OCC
from minbuffocc import MinBuff_OCC
from ts0ok import TS0OKQuery
from ts1ok import TS1OKQuery

query_classes = (DRVErrFlag_bottom, DRVErrFlag_Top, DRVErrFlag_FTSide, 
                 DRVErrFlag_PipeSide, EVTRate_Sum, MaxBuff_OCC, 
                 MinBuff_OCC, TS0OKQuery, TS1OKQuery)


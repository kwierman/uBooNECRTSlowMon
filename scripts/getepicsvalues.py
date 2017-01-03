from epics import PV
import logging
from SCMon import settings

logging.basicConfig(level=logging.DEBUG)
logging.info(settings.BASE_PATH+'/'+settings.DRVErrFlag_FTSide_Path)
logging.info(PV(settings.BASE_PATH+'/'+settings.DRVErrFlag_FTSide_Path).get())
logging.info(settings.BASE_PATH+'/'+settings.DRVErrFlag_bottom_Path)
logging.info(PV(settings.BASE_PATH+'/'+settings.DRVErrFlag_bottom_Path).get())
logging.info(settings.BASE_PATH+'/'+settings.DRVErrFlag_pipeside_Path)
logging.info(PV(settings.BASE_PATH+'/'+settings.DRVErrFlag_pipeside_Path).get())
logging.info(settings.BASE_PATH+'/'+settings.DRVErrFlag_top_Path)
logging.info(PV(settings.BASE_PATH+'/'+settings.DRVErrFlag_top_Path).get())
logging.info(settings.BASE_PATH+'/'+settings.EVTRate_Sum_Path)
logging.info(PV(settings.BASE_PATH+'/'+settings.EVTRate_Sum_Path).get())
logging.info(settings.BASE_PATH+'/'+settings.MaxBuff_OCC_Path)
logging.info(PV(settings.BASE_PATH+'/'+settings.MaxBuff_OCC_Path).get())
logging.info(settings.BASE_PATH+'/'+settings.MinBuff_OCC_Path)
logging.info(PV(settings.BASE_PATH+'/'+settings.MinBuff_OCC_Path).get())
FT_FEBS=[26, 27, 28, 29, 30, 31, 55, 56, 57, 58, 59, 60, 61]
PIPE_FEBS=[32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 15, 
           16, 20, 21, 46, 47, 48, 49, 50, 51, 52, 53, 54]
BOTTOM_FEBS=[11, 12, 14, 17, 18, 19, 22, 23, 24]
TOP_FEBS=[62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 
           78, 79, 80, 81, 82, 83, 84, 85]

time_interval= 'time > now() - 1d'
limit_queries = 1

PYEPICS_LIBCA="/home/kwierman/base-3.15.5/lib/linux-x86_64/libca.so"
EPICS_BASE="/home/kwierman/base-3.15.5"
EPICS_HOST_ARCH="linux-x86_64"

PV_NAMING_SCHEME="{detector}_{subsys}_{rack}_{unit}/{var}"

BASE_PATH="uB_DAQStatus_CRTDAQX_evb"
DRVErrFlag_FTSide_Path = "drverrflag_FTside"
DRVErrFlag_bottom_Path = "drverrflag_bottom"
DRVErrFlag_pipeside_Path = "drverrflag_pipeside"
DRVErrFlag_top_Path = "drverrflag_top"
EVTRate_Sum_Path = "evtrate_sum"
MaxBuff_OCC_Path = "maxbuff_occ"
MinBuff_OCC_Path = "minbuff_occ"
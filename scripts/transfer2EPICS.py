import epics
from SCMon import (MessageQuery,
                   FEBStatsQuery,
                   DRVStatsQuery,
                   EventsQuery)
from . import settings

query_classes = (MessageQuery, FEBStatsQuery, DRVStatsQuery, EventsQuery)

def initialize():
  pass

def main():
  client = MessageQuery.default_client()
  global query_classes

  while( 1 ):
    for query_cls in query_classes:
        query = query_cls(client, columns='*', 
                          constraints=settings.time_interval, 
                          limit=settings.limit_queries)
        dataframe = query.constuct_query()
        for i in dataframe():
            print i

    break

if __name__ == "__main__":
    main()







class IFBDtoEPICS:
    """The main class for reading a set of variables from IFBeamData,
    summarizing them, and writing them out to EPICS"""
    def __init__(self):
        """Constructor takes no arguments.
        Normally one should call load_config() immediately after constructing.
        """
        self.vlist = []
        self.pvdict = {}
        self.lookback_time = 123  # a little over two supercycles
        self.latency = 30         # a little optimistic, but works
        self.cron_time = 100
        self.debug = False
        self.dryrun = False
        #-- delta-t statistic parameters
        # format for pv to receive mindt statistics, %s needed for event pair
        self.mindtpv = None
        # cut in ms for scoring events too close in time
        self.dtcut = 35
        # format for pv to receive percent of events too-close in time
        self.pctdtcutpv = None
        # format for pv to receive percent of beam too-close in time
        self.pctbeamdtcutpv = None
        # pv to receive dtcut value used
        self.dtcutpv = None
        # pv to receive rate calculated from event and timestamp data
        self.ratepv = None
        # pv to receive beam rate (per second/s)
        self.beampv = None

    def load_config(self, config_file):
        """Loads the list of variables to read from the csv-formmated
        config file.  The config_file parameter should be a file-like object.
        Each non-comment row should contain the following comma-separated
        columns:
            ifbdname,event,pvname,ts_pvname
        where
            ifbdname = name of variable in IFBeamData database
            event    = name of event in IFBeamData database
            pvname   = name of epics variable in which to store average
            ts_pvname= name of epics variable in which to store latest time
            condition= condition on which to select samples for averaging

        Example rows:

E:TOR860,"e,1d",uB_BeamData_BEAM_BNB_TOR860/protons,uB_BeamData_BEAM_BNB_TOR860/timestamp
E:TOR875,"e,1d",uB_BeamData_BEAM_BNB_TOR875/protons
E:THCURR,"e,1d",uB_BeamData_BEAM_BNB_THCURR/current,,E:TOR875>0.2

--mindtpv,uB_BeamData_BEAM/mindt_%s
--dtcut,35 uB_BeamData_BEAM/dtcut
--pctdtcutpv,uB_BeamData_BEAM/pct_dtcut_%s
--pctbeamdtcutpv,uB_BeamData_BEAM/pctbeam_dtcut_%s
        """
        rdr = csv.reader(config_file)
        for row in rdr:
            # skip blank and comment lines
            if len(row) < 2 or row[0].startswith('#'):
                continue
            # process optional argument line
            if row[0].startswith("--"):
                if row[0] == "--mindtpv":
                    self.mindtpv = row[1].strip()
                elif row[0] == "--dtcut":
                    self.dtcut = float(row[1])
                elif row[0] == "--dtcutpv":
                    self.dtcutpv = row[1].strip()
                elif row[0] == "--pctdtcutpv":
                    self.pctdtcutpv = row[1].strip()
                elif row[0] == "--pctbeamdtcutpv":
                    self.pctbeamdtcutpv = row[1].strip()
                elif row[0] == "--ratepv":
                    self.ratepv = row[1].strip()
                elif row[0] == "--beampv":
                    self.beampv = row[1].strip()
                continue
            if len(row) < 3:
                continue
            # unpack
            ifbdname, event, pvname = row[:3]
            ts_pvname = len(row)>3 and row[3] or None
            condition = len(row)>4 and row[4] or None
            # add to list
            self.vlist.append( (ifbdname, event, pvname,
                                ts_pvname, condition) )
            # make pv and add to dictionary
            self.pvdict[pvname] = epics.get_pv(
                pvname, connect=False, timeout=0.5, connection_timeout=0.5)
            # add ts, if not already in dictionary
            if ts_pvname and not ts_pvname in self.pvdict:
                self.pvdict[ts_pvname] = epics.get_pv(
                    ts_pvname, connect=False, timeout=0.5,
                    connection_timeout=0.5)

    def go(self):
        """Fetch the IFBeamData and write it to EPICS"""
        #-- sleep a little to try to avoid syncing with other cron jobs
        time.sleep(random.random()*0.1*self.cron_time)
        #-- make sure we don't end up waiting longer for data than we have
        #   time for
        socket.setdefaulttimeout(0.7*self.cron_time /
                                 (len(self.vlist)+1))
        nv = len(self.vlist)
        avg_list = [None]*nv
        time_list = [None]*nv
        data_vals = {}
        data_ts = {}
        ts_event = {}
        for iv in range(nv):
            ifbdname, event, pvname, ts_pvname, condition = self.vlist[iv]
            request = IFBD_FMT % (ifbdname, event,
                                  self.lookback_time+self.latency,
                                  self.latency)
            if self.debug:
                print request
            try:
                time.sleep(0.1*self.cron_time / (len(self.vlist)+1))
                urlf = urllib2.urlopen(request)
                data = list( row for row in csv.reader(urlf) )
            except Exception, e:
                print "Error handling ",request, e
                continue
            if len(data) <= 1:
                continue
            header = data[0]
            if self.debug:
                print header
            try:
                i_value = header.index("Value(s)")
                i_ts = header.index("Clock")
                if header[0] == 'Event' and data[1][0] == 'e':
                    print "Doing ugly hack for missing quotes: %s" % pvname
                    i_value += 1
                    i_ts += 1
                vals = list( float(row[i_value]) for row in data[1:] )
                ts = list( float(row[i_ts]) for row in data[1:] )
                data_vals[ifbdname] = list(vals)
                data_ts[ifbdname] = list(ts)
                if ts_pvname:
                    ts_event.update( (ts[i],(event,vals[i])) for i in range(len(ts)) )
                if self.debug:
                    print "number of data points: ", len(vals)
                if condition:
                    self.apply_condition(condition, ifbdname,
                                         vals, ts, data_vals, data_ts)
                if len(vals) <= 0:
                    continue
                avg_list[iv] = sum(vals)/len(vals)
                time_list[iv] = ts[-1]*0.001
                if not self.dryrun:
                    self.pvdict[pvname].put( avg_list[iv] )
                if self.debug:
                    print pvname, avg_list[iv]
                if ts_pvname:
                    if not self.dryrun:
                        self.pvdict[ts_pvname].put( time_list[iv] )
                    if self.debug:
                        print ts_pvname, time_list[iv]
            except Exception, e:
                try:
                    print "Traceback: ", traceback.print_exc()
                    print "Error in parsing data for ", pvname
                    print "Exception: ", e
                    print "Header: ", header
                    print "Data: ", data
                except:
                    print "Execption in exception handling"
        #
        dt_stats = self.check_times(ts_event, self.dtcut)
        #-- write dt_stats to slowmon variables
        if not self.dryrun:
            for ekey in dt_stats:
                e1e2 = ''.join(ekey).replace('e,', '')
                if self.mindtpv:
                    epics.caput(self.mindtpv%e1e2, dt_stats[ekey][0])
                if self.pctdtcutpv:
                    epics.caput(self.pctdtcutpv%e1e2, dt_stats[ekey][1])
                if self.pctbeamdtcutpv:
                    epics.caput(self.pctbeamdtcutpv%e1e2, dt_stats[ekey][2])
                if self.ratepv:
                    epics.caput(self.ratepv%e1e2, dt_stats[ekey][3])
                if self.beampv:
                    epics.caput(self.beampv%e1e2, dt_stats[ekey][4])
            if self.dtcutpv:
                epics.caput(self.dtcutpv, self.dtcut)
        #-- end of "go"
    

    def apply_condition(self, condition, ifbdname,
                        vals, ts,
                        data_vals, data_ts):
        """Strip out any data from vals that doesn't match the condition.
        If no data is left, that's just how it is.
        """
        isep = condition.find('>')
        if isep < 0:
            print "Error, only > is supported as a condition currently."
            return
        #-- parse condition
        cvar = condition[:isep].strip()
        if not cvar in data_vals:
            print "No data for condition variable %s" % cvar
            del vals[0:]
            del ts[0:]
            return
        cvals = data_vals[cvar]
        cts = data_ts[cvar]
        cut = float(condition[isep+1:])
        #-- now scan through and remove any values not matching condition
        i = 0
        j = 0
        while (i<len(vals) and j<len(cvals)):
            #-- only use data matched in time to control var
            if ts[i] > cts[j]+8:
                j += 1
            elif cts[j] > ts[i]+8:
                vals.pop(i)
                ts.pop(i)
            else:
                if cvals[j] > cut:
                    #-- we have a sample passing the cut
                    i += 1
                    j += 1
                else:
                    vals.pop(i)
                    ts.pop(i)
                    j += 1
        if (i < len(vals)):
            del vals[i:]
            del ts[i:]
        if self.debug:
            print "Number of data points after cut: ", len(vals)
        #-- end of cut condition

    def check_times(self, ts_event, cut, dtres=8):
        """check_times(ts_event) will check a dictionary ts_event
        containing a timestamp-to-(eventtype,value) dict and calculate the
        minimum timestamp difference between each, the percentage of
        time differences less than some cut, unweighted and weighted
        by the variable value, and unweighted and weigted rates.
        Counts events of the same type within dtres of each other as
        being the same event.
        Uses a window between first and last supercycle marker (e,00)
        to avoid aliasing, or entire time range if not enough (e,00) found.
        Returns a dictionary of
        { (event_type_1, event_type_2): stats }
        where stats = [mindt, pctcut, pctbeamcut, eventrate, beamrate]
        """
        #-- get list of all event types
        etypes = list(set( v[0] for v in ts_event.values() ))
        etypes.sort()
        if self.debug:
            print "Event types: ",etypes
        #-- get list of all timestamps
        tslist = ts_event.keys()
        tslist.sort()
        #-- pick first and last event time using supercycle markers if avail
        if 'e,00' in etypes:
            ts00 = list(t[0] for t in ts_event.items() if t[1][0] == 'e,00')
            if self.debug:
                print "e,00 times: ", ts00
            ts_initial = min(ts00)
            ts_final = max(ts00)
        else:
            ts_initial = ts_final = -1
        if ts_initial == ts_final:
            print "Warning, not enough e,00 for full supercycle %d %d" % (ts_initial, ts_final)
            ts_initial = min(tslist)
            ts_final = max(tslist)
        #-- pick window
        #it_initial = bisect.bisect_left( tslist, ts_initial-dtres )
        #it_final = bisect.bisect_left( tslist, ts_final+dtres+1 )
        it_initial = tslist.index(ts_initial)
        it_final = tslist.index(ts_final)
        if self.debug:
            print "it_initial, it_final, window = %d, %d, %g ms" % (
                it_initial, it_final, tslist[it_final]-tslist[it_initial] )
        #-- initialize statistics and last timestamp accumulators
        first_ts = dict( (et,0) for et in etypes )
        last_ts = dict( (et,0) for et in etypes )
        stats = dict(((et1,et2),[ts_final-ts_initial,0.0,0.0,0.0,0.0]) for et1 in etypes for et2 in etypes)
        #-- loop over all timestamps
        for ts in tslist[it_initial:it_final+1]:
            e2,v2 = ts_event[ts]
            if self.debug:
                print "%d %s" % (ts, e2)
            for e1 in etypes:
                if first_ts[e1] == 0:
                    continue
                dt = ts - last_ts[e1]
                if dt < dtres and e1 == e2:
                    if self.debug:
                        print "skipping too-close times for same event type"
                    continue
                stat = stats[(e1,e2)]
                if dt < stat[0]:
                    stat[0] = dt
                    if self.debug:
                        print "new minimum dt %d for %s,%s" % (dt,e1,e2)
                if dt < cut:
                    stat[1] += 1
                    stat[2] += abs(v2)
                stat[3] += 1
                stat[4] += abs(v2)
            if first_ts[e2] == 0:
                first_ts[e2] = ts
            last_ts[e2] = ts
        if self.debug:
            print "Timestamp stats (raw): ", stats
            print "First and last times: ",first_ts, last_ts
        for e1 in etypes:
            for e2 in etypes:
                stat = stats[(e1,e2)]
                #-- percent cut, with and without weighting
                if stat[3] > 0:
                    stat[1] = stat[1]*100.0/stat[3]
                if stat[4] > 0:
                    stat[2] = stat[2]*100.0/stat[4]
                #-- rates
                # note the first event is not counted in stat[3] or stat[4],
                # which means the number of samples summed is consistent with
                # the time interval.
                n = stat[3]  
                t1 = max(first_ts[e1], first_ts[e2])
                t2 = last_ts[e2]
                dt_s = 1e-3*(t2 - t1)
                if dt_s > 0.0:
                    stat[3] = n / dt_s
                    stat[4] = stat[4] / dt_s
        if self.debug:
            print "Timestamp stats (cooked): ", stats
        return stats



def main(argv):
    ifbd = IFBDtoEPICS()
    if "--debug" in argv:
        argv.pop(argv.index("--debug"))
        ifbd.debug = True
    if "--dryrun" in argv:
        argv.pop(argv.index("--dryrun"))
        ifbd.dryrun = True
    ifbd.load_config(file(argv[1]))
    ifbd.go()

if __name__ == "__main__":
    import sys
    main(sys.argv)
"""IFBDtoEPICS.py is a specialized application to read recent data
2	
from the IFBeamData [1] database at Fermilab and write summary values to
3	
EPICS.
4	
   
5	
[1] https://cdcvs.fnal.gov/redmine/projects/ifbeamdata/wiki
6	

7	
:author: Glenn Horton-Smith 2015-10-16
8	
"""
9	
10	
import urllib2
11	
import socket
12	
import epics
13	
import csv
14	
import traceback
15	
import time
16	
import random
17	
import bisect
18	
19	
# IFBeamDB data download format
20	
IFBD_FMT = "http://ifb-data.fnal.gov:8089/ifbeam/data/data?v=%s&e=%s&t0=-%g&t1=-%g&f=csv"
21	
22	
23	
24	
class IFBDtoEPICS:
25	
    """The main class for reading a set of variables from IFBeamData,
26	
    summarizing them, and writing them out to EPICS"""
27	
    def __init__(self):
28	
        """Constructor takes no arguments.
29	
        Normally one should call load_config() immediately after constructing.
30	
        """
31	
        self.vlist = []
32	
        self.pvdict = {}
33	
        self.lookback_time = 123  # a little over two supercycles
34	
        self.latency = 30         # a little optimistic, but works
35	
        self.cron_time = 100
36	
        self.debug = False
37	
        self.dryrun = False
38	
        #-- delta-t statistic parameters
39	
        # format for pv to receive mindt statistics, %s needed for event pair
40	
        self.mindtpv = None
41	
        # cut in ms for scoring events too close in time
42	
        self.dtcut = 35
43	
        # format for pv to receive percent of events too-close in time
44	
        self.pctdtcutpv = None
45	
        # format for pv to receive percent of beam too-close in time
46	
        self.pctbeamdtcutpv = None
47	
        # pv to receive dtcut value used
48	
        self.dtcutpv = None
49	
        # pv to receive rate calculated from event and timestamp data
50	
        self.ratepv = None
51	
        # pv to receive beam rate (per second/s)
52	
        self.beampv = None
53	
54	
    def load_config(self, config_file):
55	
        """Loads the list of variables to read from the csv-formmated
56	
        config file.  The config_file parameter should be a file-like object.
57	
        Each non-comment row should contain the following comma-separated
58	
        columns:
59	
            ifbdname,event,pvname,ts_pvname
60	
        where
61	
            ifbdname = name of variable in IFBeamData database
62	
            event    = name of event in IFBeamData database
63	
            pvname   = name of epics variable in which to store average
64	
            ts_pvname= name of epics variable in which to store latest time
65	
            condition= condition on which to select samples for averaging
66	

67	
        Example rows:
68	

69	
E:TOR860,"e,1d",uB_BeamData_BEAM_BNB_TOR860/protons,uB_BeamData_BEAM_BNB_TOR860/timestamp
70	
E:TOR875,"e,1d",uB_BeamData_BEAM_BNB_TOR875/protons
71	
E:THCURR,"e,1d",uB_BeamData_BEAM_BNB_THCURR/current,,E:TOR875>0.2
72	

73	
--mindtpv,uB_BeamData_BEAM/mindt_%s
74	
--dtcut,35 uB_BeamData_BEAM/dtcut
75	
--pctdtcutpv,uB_BeamData_BEAM/pct_dtcut_%s
76	
--pctbeamdtcutpv,uB_BeamData_BEAM/pctbeam_dtcut_%s
77	
        """
78	
        rdr = csv.reader(config_file)
79	
        for row in rdr:
80	
            # skip blank and comment lines
81	
            if len(row) < 2 or row[0].startswith('#'):
82	
                continue
83	
            # process optional argument line
84	
            if row[0].startswith("--"):
85	
                if row[0] == "--mindtpv":
86	
                    self.mindtpv = row[1].strip()
87	
                elif row[0] == "--dtcut":
88	
                    self.dtcut = float(row[1])
89	
                elif row[0] == "--dtcutpv":
90	
                    self.dtcutpv = row[1].strip()
91	
                elif row[0] == "--pctdtcutpv":
92	
                    self.pctdtcutpv = row[1].strip()
93	
                elif row[0] == "--pctbeamdtcutpv":
94	
                    self.pctbeamdtcutpv = row[1].strip()
95	
                elif row[0] == "--ratepv":
96	
                    self.ratepv = row[1].strip()
97	
                elif row[0] == "--beampv":
98	
                    self.beampv = row[1].strip()
99	
                continue
100	
            if len(row) < 3:
101	
                continue
102	
            # unpack
103	
            ifbdname, event, pvname = row[:3]
104	
            ts_pvname = len(row)>3 and row[3] or None
105	
            condition = len(row)>4 and row[4] or None
106	
            # add to list
107	
            self.vlist.append( (ifbdname, event, pvname,
108	
                                ts_pvname, condition) )
109	
            # make pv and add to dictionary
110	
            self.pvdict[pvname] = epics.get_pv(
111	
                pvname, connect=False, timeout=0.5, connection_timeout=0.5)
112	
            # add ts, if not already in dictionary
113	
            if ts_pvname and not ts_pvname in self.pvdict:
114	
                self.pvdict[ts_pvname] = epics.get_pv(
115	
                    ts_pvname, connect=False, timeout=0.5,
116	
                    connection_timeout=0.5)
117	
118	
    def go(self):
119	
        """Fetch the IFBeamData and write it to EPICS"""
120	
        #-- sleep a little to try to avoid syncing with other cron jobs
121	
        time.sleep(random.random()*0.1*self.cron_time)
122	
        #-- make sure we don't end up waiting longer for data than we have
123	
        #   time for
124	
        socket.setdefaulttimeout(0.7*self.cron_time /
125	
                                 (len(self.vlist)+1))
126	
        nv = len(self.vlist)
127	
        avg_list = [None]*nv
128	
        time_list = [None]*nv
129	
        data_vals = {}
130	
        data_ts = {}
131	
        ts_event = {}
132	
        for iv in range(nv):
133	
            ifbdname, event, pvname, ts_pvname, condition = self.vlist[iv]
134	
            request = IFBD_FMT % (ifbdname, event,
135	
                                  self.lookback_time+self.latency,
136	
                                  self.latency)
137	
            if self.debug:
138	
                print request
139	
            try:
140	
                time.sleep(0.1*self.cron_time / (len(self.vlist)+1))
141	
                urlf = urllib2.urlopen(request)
142	
                data = list( row for row in csv.reader(urlf) )
143	
            except Exception, e:
144	
                print "Error handling ",request, e
145	
                continue
146	
            if len(data) <= 1:
147	
                continue
148	
            header = data[0]
149	
            if self.debug:
150	
                print header
151	
            try:
152	
                i_value = header.index("Value(s)")
153	
                i_ts = header.index("Clock")
154	
                if header[0] == 'Event' and data[1][0] == 'e':
155	
                    print "Doing ugly hack for missing quotes: %s" % pvname
156	
                    i_value += 1
157	
                    i_ts += 1
158	
                vals = list( float(row[i_value]) for row in data[1:] )
159	
                ts = list( float(row[i_ts]) for row in data[1:] )
160	
                data_vals[ifbdname] = list(vals)
161	
                data_ts[ifbdname] = list(ts)
162	
                if ts_pvname:
163	
                    ts_event.update( (ts[i],(event,vals[i])) for i in range(len(ts)) )
164	
                if self.debug:
165	
                    print "number of data points: ", len(vals)
166	
                if condition:
167	
                    self.apply_condition(condition, ifbdname,
168	
                                         vals, ts, data_vals, data_ts)
169	
                if len(vals) <= 0:
170	
                    continue
171	
                avg_list[iv] = sum(vals)/len(vals)
172	
                time_list[iv] = ts[-1]*0.001
173	
                if not self.dryrun:
174	
                    self.pvdict[pvname].put( avg_list[iv] )
175	
                if self.debug:
176	
                    print pvname, avg_list[iv]
177	
                if ts_pvname:
178	
                    if not self.dryrun:
179	
                        self.pvdict[ts_pvname].put( time_list[iv] )
180	
                    if self.debug:
181	
                        print ts_pvname, time_list[iv]
182	
            except Exception, e:
183	
                try:
184	
                    print "Traceback: ", traceback.print_exc()
185	
                    print "Error in parsing data for ", pvname
186	
                    print "Exception: ", e
187	
                    print "Header: ", header
188	
                    print "Data: ", data
189	
                except:
190	
                    print "Execption in exception handling"
191	
        #
192	
        dt_stats = self.check_times(ts_event, self.dtcut)
193	
        #-- write dt_stats to slowmon variables
194	
        if not self.dryrun:
195	
            for ekey in dt_stats:
196	
                e1e2 = ''.join(ekey).replace('e,', '')
197	
                if self.mindtpv:
198	
                    epics.caput(self.mindtpv%e1e2, dt_stats[ekey][0])
199	
                if self.pctdtcutpv:
200	
                    epics.caput(self.pctdtcutpv%e1e2, dt_stats[ekey][1])
201	
                if self.pctbeamdtcutpv:
202	
                    epics.caput(self.pctbeamdtcutpv%e1e2, dt_stats[ekey][2])
203	
                if self.ratepv:
204	
                    epics.caput(self.ratepv%e1e2, dt_stats[ekey][3])
205	
                if self.beampv:
206	
                    epics.caput(self.beampv%e1e2, dt_stats[ekey][4])
207	
            if self.dtcutpv:
208	
                epics.caput(self.dtcutpv, self.dtcut)
209	
        #-- end of "go"
210	
    
211	
212	
    def apply_condition(self, condition, ifbdname,
213	
                        vals, ts,
214	
                        data_vals, data_ts):
215	
        """Strip out any data from vals that doesn't match the condition.
216	
        If no data is left, that's just how it is.
217	
        """
218	
        isep = condition.find('>')
219	
        if isep < 0:
220	
            print "Error, only > is supported as a condition currently."
221	
            return
222	
        #-- parse condition
223	
        cvar = condition[:isep].strip()
224	
        if not cvar in data_vals:
225	
            print "No data for condition variable %s" % cvar
226	
            del vals[0:]
227	
            del ts[0:]
228	
            return
229	
        cvals = data_vals[cvar]
230	
        cts = data_ts[cvar]
231	
        cut = float(condition[isep+1:])
232	
        #-- now scan through and remove any values not matching condition
233	
        i = 0
234	
        j = 0
235	
        while (i<len(vals) and j<len(cvals)):
236	
            #-- only use data matched in time to control var
237	
            if ts[i] > cts[j]+8:
238	
                j += 1
239	
            elif cts[j] > ts[i]+8:
240	
                vals.pop(i)
241	
                ts.pop(i)
242	
            else:
243	
                if cvals[j] > cut:
244	
                    #-- we have a sample passing the cut
245	
                    i += 1
246	
                    j += 1
247	
                else:
248	
                    vals.pop(i)
249	
                    ts.pop(i)
250	
                    j += 1
251	
        if (i < len(vals)):
252	
            del vals[i:]
253	
            del ts[i:]
254	
        if self.debug:
255	
            print "Number of data points after cut: ", len(vals)
256	
        #-- end of cut condition
257	
258	
    def check_times(self, ts_event, cut, dtres=8):
259	
        """check_times(ts_event) will check a dictionary ts_event
260	
        containing a timestamp-to-(eventtype,value) dict and calculate the
261	
        minimum timestamp difference between each, the percentage of
262	
        time differences less than some cut, unweighted and weighted
263	
        by the variable value, and unweighted and weigted rates.
264	
        Counts events of the same type within dtres of each other as
265	
        being the same event.
266	
        Uses a window between first and last supercycle marker (e,00)
267	
        to avoid aliasing, or entire time range if not enough (e,00) found.
268	
        Returns a dictionary of
269	
        { (event_type_1, event_type_2): stats }
270	
        where stats = [mindt, pctcut, pctbeamcut, eventrate, beamrate]
271	
        """
272	
        #-- get list of all event types
273	
        etypes = list(set( v[0] for v in ts_event.values() ))
274	
        etypes.sort()
275	
        if self.debug:
276	
            print "Event types: ",etypes
277	
        #-- get list of all timestamps
278	
        tslist = ts_event.keys()
279	
        tslist.sort()
280	
        #-- pick first and last event time using supercycle markers if avail
281	
        if 'e,00' in etypes:
282	
            ts00 = list(t[0] for t in ts_event.items() if t[1][0] == 'e,00')
283	
            if self.debug:
284	
                print "e,00 times: ", ts00
285	
            ts_initial = min(ts00)
286	
            ts_final = max(ts00)
287	
        else:
288	
            ts_initial = ts_final = -1
289	
        if ts_initial == ts_final:
290	
            print "Warning, not enough e,00 for full supercycle %d %d" % (ts_initial, ts_final)
291	
            ts_initial = min(tslist)
292	
            ts_final = max(tslist)
293	
        #-- pick window
294	
        #it_initial = bisect.bisect_left( tslist, ts_initial-dtres )
295	
        #it_final = bisect.bisect_left( tslist, ts_final+dtres+1 )
296	
        it_initial = tslist.index(ts_initial)
297	
        it_final = tslist.index(ts_final)
298	
        if self.debug:
299	
            print "it_initial, it_final, window = %d, %d, %g ms" % (
300	
                it_initial, it_final, tslist[it_final]-tslist[it_initial] )
301	
        #-- initialize statistics and last timestamp accumulators
302	
        first_ts = dict( (et,0) for et in etypes )
303	
        last_ts = dict( (et,0) for et in etypes )
304	
        stats = dict(((et1,et2),[ts_final-ts_initial,0.0,0.0,0.0,0.0]) for et1 in etypes for et2 in etypes)
305	
        #-- loop over all timestamps
306	
        for ts in tslist[it_initial:it_final+1]:
307	
            e2,v2 = ts_event[ts]
308	
            if self.debug:
309	
                print "%d %s" % (ts, e2)
310	
            for e1 in etypes:
311	
                if first_ts[e1] == 0:
312	
                    continue
313	
                dt = ts - last_ts[e1]
314	
                if dt < dtres and e1 == e2:
315	
                    if self.debug:
316	
                        print "skipping too-close times for same event type"
317	
                    continue
318	
                stat = stats[(e1,e2)]
319	
                if dt < stat[0]:
320	
                    stat[0] = dt
321	
                    if self.debug:
322	
                        print "new minimum dt %d for %s,%s" % (dt,e1,e2)
323	
                if dt < cut:
324	
                    stat[1] += 1
325	
                    stat[2] += abs(v2)
326	
                stat[3] += 1
327	
                stat[4] += abs(v2)
328	
            if first_ts[e2] == 0:
329	
                first_ts[e2] = ts
330	
            last_ts[e2] = ts
331	
        if self.debug:
332	
            print "Timestamp stats (raw): ", stats
333	
            print "First and last times: ",first_ts, last_ts
334	
        for e1 in etypes:
335	
            for e2 in etypes:
336	
                stat = stats[(e1,e2)]
337	
                #-- percent cut, with and without weighting
338	
                if stat[3] > 0:
339	
                    stat[1] = stat[1]*100.0/stat[3]
340	
                if stat[4] > 0:
341	
                    stat[2] = stat[2]*100.0/stat[4]
342	
                #-- rates
343	
                # note the first event is not counted in stat[3] or stat[4],
344	
                # which means the number of samples summed is consistent with
345	
                # the time interval.
346	
                n = stat[3]  
347	
                t1 = max(first_ts[e1], first_ts[e2])
348	
                t2 = last_ts[e2]
349	
                dt_s = 1e-3*(t2 - t1)
350	
                if dt_s > 0.0:
351	
                    stat[3] = n / dt_s
352	
                    stat[4] = stat[4] / dt_s
353	
        if self.debug:
354	
            print "Timestamp stats (cooked): ", stats
355	
        return stats
356	
357	
358	
359	
def main(argv):
360	
    ifbd = IFBDtoEPICS()
361	
    if "--debug" in argv:
362	
        argv.pop(argv.index("--debug"))
363	
        ifbd.debug = True
364	
    if "--dryrun" in argv:
365	
        argv.pop(argv.index("--dryrun"))
366	
        ifbd.dryrun = True
367	
    ifbd.load_config(file(argv[1]))
368	
    ifbd.go()
369	
370	
if __name__ == "__main__":
371	
    import sys
372	
    main(sys.argv)

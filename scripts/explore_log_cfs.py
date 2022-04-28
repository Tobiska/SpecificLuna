#!/usr/bin/env python3

# The program reads the joint log file obtained from lo3 and writes two files:
# *.cfs.done   - list of CFs (and thair correcponding events), which finished their execution on a given node
# *.cfs.undone - list of CFs, which did not finish thair execution
# Multiple events with the same "name" are correctly processed and listed separately.

# The log file for this program may be prepared from multiple log.* files by the command:
#   cat log.* > log

import sys
import re

events = {"Create","Migrate","Receive","Finish","Invoke","Wait","POST","requested","responded"}
events_cf = {"Create","Finish","Invoke","Wait","requested","responded","Migrate","Receive"}
events_df = {"Wait","POST","requested","responded"}

events_cf_start = {"Create","Receive"}
events_cf_finish = {"Migrate","Finish"}

ITIME = 0
IEVENT =  1
IDESCR = 2

ICFNAME = 0
IRANK = 1
IVERSION = 2
IEVENTS = 3

def read_file_lines(filename):
  """Issue text from file line by line with line numbers"""
  with open(filename,"r") as f:
    linenumber = 1
    for line in f:
      yield linenumber,line.strip()
      linenumber = linenumber + 1

def get_rank_time_event_description(s):
  """Extract rank, time and event type from string"""
  m = re.match("\s*(?P<rank>\d*)\s*\|\s*(?P<time>\S*)\s*\|\s*(?P<event>\S*)\s*(?P<description>[^\|]*)",s)
  if m:
    d = m.groupdict()
    return int(d["rank"]),float(d["time"]),d["event"],d["description"].strip()
  else:
    return None,None,None,None

def get_cf_name(s):
  """Exrtact CF name from string"""
  return re.findall("CF (\S*) : (\d*)",s)[0]

def get_df_name(s):
  return re.findall("ID<[^>]*>",s)[0]

def read_cfs(filename):
  """Extract list of events grouped by CFs from file (events in file should be ordered by time within each rank)"""
  cfs = []     # element: [cfname,rank,version, [ event0, event1, ... ] ], eventX: (time,event,description)
  cfsmap = {}  # key: (cfname,rank), value: [ num_in_cfs_with_version_0, num_in_cfs_with_version_1, ... ]
  for i,s in read_file_lines(filename):
    rank,time,event,description = get_rank_time_event_description(s)
    if event == None:
      print((i,s))
    if event in events_cf:
      cfname = get_cf_name(s)[0]
      key = (cfname,rank)
      event_record = (time,event,description)
      map_record = cfsmap.get(key)
      if map_record == None:
        cfs.append([cfname,rank,0,[ event_record ]])
        cfsmap[key] = [ len(cfs)-1 ]
      elif event in events_cf_start:
        cfs.append([cfname,rank,len(map_record),[ event_record ]])
        map_record.append(len(cfs)-1)
      else:
        cfs[map_record[-1]][IEVENTS].append(event_record)
  return cfs,cfsmap

def split_done_undone(cfs):
  cfs_done = []
  cfs_undone = []
  for cf in cfs:
    if cf[IEVENTS][-1][IEVENT] in events_cf_finish:
      cfs_done.append(cf)
    else:
      cfs_undone.append(cf)
  return cfs_done,cfs_undone

def output_cfs(filename,cfs):
  with open(filename,"w") as f:
    f.write("Count: " + str(len(cfs)) + "\n")
    for cf in cfs:
      f.write(str(cf[ICFNAME]) + " " + str(cf[IRANK]) + " " + str(cf[IVERSION]) + "\n")
      for event in cf[IEVENTS]:
        f.write("  " + str(event[ITIME]) + " | " + event[IEVENT] + " | " + event[IDESCR] + "\n")

#------------------------------------------------------------------

if len(sys.argv) == 1:
  print(("Usage:",sys.argv[0],"<filename>"))
  sys.exit()

logfilename = sys.argv[1]

# cfs - list of CFs, each with list of events.
#       Events within each CF are ordered by time.
#       CFs in the list are ordered by creation time (first event time).
# cfsmap - maps the pair (name_of_cf,rank) to the list of indices in cfs list.
#          May be used for fast search of CFs with certain name and rank.

cfs,cfsmap = read_cfs(logfilename)
#output_cfs(logfilename+".cf",cfs)
cfs_done,cfs_undone = split_done_undone(cfs)
output_cfs(logfilename+".cf.done",cfs_done)
output_cfs(logfilename+".cf.undone",cfs_undone)


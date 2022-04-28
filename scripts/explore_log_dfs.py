#!/usr/bin/env python3

# The program reads the joint log file obtained from lo3 and writes two files:
# *.dfs.resp   - list of DFs (and thair correcponding events), which were "responded" on each "requested"
# *.dfs.unresp - list of DFs, which are "requested", but not "responded"

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
IFLAG = 3

IDFNAME = 0
IRANK = 1
IEVENTS = 2
IFLAGS = 3

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
  return re.findall("ID<[^>]*>",s)

def read_dfs(filename):
  """Extract list of events grouped by DFs from file (events in file should be ordered by time within each rank)"""
  dfs = []     # element: [dfname,rank, [ event0, event1, ... ] ], eventX: (time,event,description)
  dfsmap = {}  # key: (dfname,rank), value: num_in_dfs
  for i,s in read_file_lines(filename):
    rank,time,event,description = get_rank_time_event_description(s)
    if event == None:
      print((i,s))
    if event in events_df:
      dfname = get_df_name(s)[0]
      key = (dfname,rank)
      event_record = (time,event,description)
      map_record = dfsmap.get(key)
      if map_record == None:
        dfs.append([dfname,rank,[ event_record ]])
        dfsmap[key] = len(dfs)-1
      else:
        dfs[map_record][IEVENTS].append(event_record)
  return dfs,dfsmap

def split_dfs_resp_unresp(dfs):
  dfs_resp = []
  dfs_unresp = []
  for df in dfs:
    reqs = {}
    n = 0
    for act in df[IEVENTS]:
      if act[IEVENT] == "requested":
        cf,tmp = get_cf_name(act[IDESCR])
        assert(cf not in reqs),"cf not in reqs: "+str(cf)+", df: "+str(df[IDFNAME])+" "+str(df[IRANK])
        reqs[cf] = n
      elif act[IEVENT] == "responded":
        cf,tmp = get_cf_name(act[IDESCR])
        assert(cf in reqs),"cf in reqs: "+str(cf)+", df: "+str(df[IDFNAME])+" "+str(df[IRANK])
        del reqs[cf]
      n = n + 1
    if len(reqs) == 0:
      dfs_resp.append(df)
    else:
      newdf = [ df[IDFNAME], df[IRANK], [], len(reqs) ]
      n = 0
      for event in df[IEVENTS]:
        if n in list(reqs.values()):
          newevent = ( event[0],event[1],event[2],1 )
        else:
          newevent = ( event[0],event[1],event[2],0 )
        n = n + 1
        newdf[IEVENTS].append(newevent)
      dfs_unresp.append(newdf)
  return dfs_resp,dfs_unresp

def output_dfs(filename,dfs):
  with open(filename,"w") as f:
    f.write("Count: " + str(len(dfs)) + "\n")
    for df in dfs:
      f.write(str(df[IDFNAME]) + " " + str(df[IRANK]) + "\n")
      for event in df[IEVENTS]:
        f.write("  " + str(event[ITIME]) + " | " + event[IEVENT] + " | " + event[IDESCR] + "\n")

def output_dfs_unresp(filename,dfs):
  with open(filename,"w") as f:
    f.write("Count: " + str(len(dfs)) + "\n")
    for df in dfs:
      f.write(str(df[IDFNAME]) + " " + str(df[IRANK]) + " " + str(df[IFLAGS]) + "\n")
      for event in df[IEVENTS]:
        if event[IFLAG] == 0:
          f.write("  " + str(event[ITIME]) + " | " + event[IEVENT] + " | " + event[IDESCR] + "\n")
        else:
          f.write("* " + str(event[ITIME]) + " | " + event[IEVENT] + " | " + event[IDESCR] + "\n")

#------------------------------------------------------------------

if len(sys.argv) == 1:
  print(("Usage:",sys.argv[0],"<filename>"))
  sys.exit()

logfilename = sys.argv[1]

# dfs - list of DFs, each with list of events.
#       Events within each DF are ordered by time.
#       DFs in the list are ordered by creation time (first event time).
# dfsmap - maps the pair (name_of_df,rank) to the index in dfs list.
#          May be used for fast search of DFs with certain name and rank.

dfs,dfsmap = read_dfs(logfilename)
#output_dfs(logfilename+".dfs",dfs)
dfs_resp,dfs_unresp = split_dfs_resp_unresp(dfs)
output_dfs(logfilename+".dfs.resp",dfs_resp)
output_dfs_unresp(logfilename+".dfs.unresp",dfs_unresp)

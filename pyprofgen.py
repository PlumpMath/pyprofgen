#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

# $Id$
# pyprofgen: gprof front-end HTML generator
# Copyright (C) 2005  Seong-Kook Shin <cinsky@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

GPROF_PATH = "/usr/bin/gprof"
DOT_PATH = "/usr/bin/dot"

PREFIX = "/usr/local"


EXE_FILE = "demo"
MON_FILE = "gmon.out"

document_dir = "prof"


# DO NOT TOUCH LINES BELOW ---------------------------------------------------

import os;
import re;
import sys;
import time;
import getopt;
import popen2;

HTML_DIR = "%s/html" % document_dir
MISC_DIR = "%s/misc" % document_dir

verbose_mode = 1;
debug_mode = 0;

DOT_NODE_FONT = "Courier-Bold"
DOT_LABEL_FONT = "Courier-Bold"
DOT_EDGE_FONT = "Courier-Bold"

pyprofgen_version = "0.3";


PPG_LIB_DIR = "";
LOGO_FILE = "";
CSS_FILE = "";


def debug(msg):
    global debug_mode;
    if debug_mode:
        sys.stdout.write("debug: %s\n" % msg);
	sys.stdout.flush();

def error(fin, msg):
    sys.stdout.flush();
    sys.stderr.write("error: ");
    sys.stderr.write(msg);
    sys.stderr.write("\n");
    sys.stderr.flush();
    if fin:
	sys.exit(fin);

def msg_out(msg):
    global verbose_mode;
    if verbose_mode:
        sys.stdout.write(msg);
	sys.stdout.flush();


def init():
    global PPG_LIB_DIR, LOGO_FILE, CSS_FILE;

    PPG_LIB_DIR = "%s/share/pyprofgen-%s" % (PREFIX, pyprofgen_version)
    if not os.path.exists(PPG_LIB_DIR):
        debug("sanity check: %s not found" % PPG_LIB_DIR);
        PPG_LIB_DIR = "%s/share/pyprofgen" % PREFIX;
        if not os.path.exists(PPG_LIB_DIR):
            debug("sanity check: %s not found" % PPG_LIB_DIR);
            PPG_LIB_DIR = "./lib";
            if not os.path.exists(PPG_LIB_DIR):
                debug("sanity check: %s not found" % PPG_LIB_DIR);
                error(1, "pyprofgen is not properly installed.");

    debug("sanity check: %s found" % PPG_LIB_DIR);

    LOGO_FILE = "%s/pyprofgen.png" % PPG_LIB_DIR;
    CSS_FILE = "%s/pyprofgen.css" % PPG_LIB_DIR;

    if not os.path.exists(LOGO_FILE):
        error(1, "logo file(%s) not found", LOGO_FILE);
    if not os.path.exists(CSS_FILE):
        error(1, "CSS file(%s) not found", CSS_FILE);

def tmp_name(prefix = "/tmp/pyprofgen-"):
    return "%s%u-%f" % (prefix, os.getpid(), time.time());

def execute(cmdline, error_msg = ""):
    global verbose_mode;
    fin, fout, ferr = os.popen3(cmdline);
    fin.close();
    errmsg = ferr.readline();
    if errmsg:
	if verbose_mode:
	    error(0, errmsg);
	if verbose_mode:
	    error(0, "cannot execute \"%s\"" % cmdline);
	if error_msg:
	    error(1, error_msg);
	else:
	    sys.exit(1);
    ferr.close();
    return fout;


class GrabberException(Exception):
    def __init__(self, value):
	self.value = value;
    def __str__(self):
	return repr(self.value);

class Grabber:
    def __init__(self, cmdline, datafile):
	self.cmdline = "";
	self.retcode = 0;
	self.fname = datafile;
	debug("Grabber: calls popen2.Popen3(%s)" % cmdline);
	self.opener = popen2.Popen3(cmdline);
	self.file = None;

	# while True:		# wait for the child termination.
	#     ret = self.opener.poll();
	#     if ret != -1:
	#	 break;
	self.retcode = self.opener.wait();
	if self.retcode != 0:
	    raise GrabberException(1);
	self.file = open(self.fname, "r"); # may raise IOError or OSError

    def __del__(self):
	try:
	    debug("Grabber: removing %s" % self.fname);
	    os.unlink(self.fname);
	except OSError:		# self.fname is already removed.
	    pass;

	if self.file != None:
	    self.file.close();
	    
    def __repr__(self):
	return "Grabber(\"%s\", \"%s\")" % (self.cmdline, self.fname);
    
	

def pyprofgen_footer(fd):
    datestr = time.ctime(time.time());
    fd.write("<hr size=\"1\">\n");
    fd.write("<address style=\"align: right;\">\n");
    fd.write("<small>Generated on %s for " % datestr);
    fd.write("<strong>%s</strong> by&nbsp;\n" % EXE_FILE);
    fd.write("<a href=\"http://www.cinsk.org/sw/pyprofgen/\"><img\n");
    fd.write("  src=\"pyprofgen.png\" alt=\"pyprofgen\"\n");
    fd.write("  align=\"middle\" border=\"0\"></a> ");
    fd.write("  %s </small></address>\n" % pyprofgen_version);

def pyprofgen_header(fd, title, css):
    fd.write("""\
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE html PUBLIC
  "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml"
      xml:lang="en" lang="en">

<head>
  <meta http-equiv="Content-Type"
        content="text/html; charset=iso-8859-1"/>\n""");

    fd.write(" <link rel=\"stylesheet\" type=\"text/css\" \n");
    fd.write("       href=\"%s\" title=\"default\"></link>\n" % css);
    fd.write(" <title>%s</title>\n" % title);

    fd.write("""
</head>

<body>
  <div class=\"qindex\">
    <a class=\"qindex\" href=\"index.html\">Main</a> |
    <a class=\"qindex\" href=\"prof_flat.html\">Flat Profile</a> |
    <a class=\"qindex\" href=\"prof_cgraph.html\">Call Graph List</a> |
    ...
  </div>\n""");



class image_map:
    map_entries = [];
    def __init__(self, mapfile):
        self.map_entries = [];
        f = open(mapfile, "r");
        f.readline();                   # eat up the first line
        while True:
            line = f.readline();
            if line == "":
                break;
            tokens = line.split();
            self.map_entries.append(tokens);
        f.close();
        
    def write(self, name, fd = sys.stdout):
        fd.write("<map name=\"%s\">\n" % name);
        for entry in self.map_entries:
            fd.write("  <area href=\"%s\" shape=\"%s\" coords=\"%s,%s\"/>\n" % \
                     (entry[1], entry[0], entry[2], entry[3]));
        fd.write("</map>\n");
         
            

class callee_entry:
    "An entry of the call graph, this is the basic unit"
    
    tm_self = 0.0;                      # self
    tm_children = 0.00;                 # children
    
    called = 0;
    called_overall = 0;                 # called/called_overall
    called_recurse = 0;                 # called+called_recurse

    name = "";
    cycle = -1;
    refer = -1;                         # id of the gdict.

    def __init__(self, self_, children, \
		 c, c_overall, c_recurse, name, cycle, refer):
	self.tm_self = self_;
	self.tm_children = children;
	self.called = c;
	self.called_overall = c_overall;
	self.called_recurse = c_recurse;
	self.name = name;
	self.cycle = cycle;
	self.refer = refer;

    def __repr__(self):
	return "callee_entry(%f, %f, %d, %d, %d, \"%s\", %d, %d)" % \
	    (self.tm_self, self.tm_children, \
	     self.called, self.called_overall, self.called_recurse, \
	     self.name, self.cycle, self.refer);



class call_graph:
    "A call graph is a dictionary of callee_entry"
    callee = []			# A list of callees
    gid = 0;                            # index field
    index = 0;
    
    tm_time = 0;
    def __init__(self):
	self.callee = [];
	self.index = 0;
        self.gid = 0;
	self.tm_time = 0;

    def add_callee(self, callee):
	self.callee.append(callee);

    def set_gid(self, gid):
	self.gid = gid;
	return gid;

    def set_index(self, index):
	self.index = index;
	return index;
    
    def set_time(self, time):
	self.tm_time = time;

    def write_html(self, fd):
        fd.write("""
<table>
  <tr>
    <th class=\"fragment\">Index</th>
    <th class=\"fragment\">Time</th>
    <th class=\"fragment\">Self</th>
    <th class=\"fragment\">Children</th>
    <th class=\"fragment\">Called</th>
    <th class=\"fragment\">C. Overall</th>
    <th class=\"fragment\">C. Recurse</th>
    <th class=\"fragment\">Cycle</th>
    <th class=\"fragment\">Name</th>
  </tr>\n""");

        i = 0;
        while i < len(self.callee):
            fd.write("<tr>\n");
            if self.index == i:
                fd.write("<td class=\"center\">[%d]</td>" % self.gid);
                fd.write("<td class=\"right\">%.2f %%</td>" % self.tm_time);
            else:
                fd.write("<td>&nbsp;</td>");
                fd.write("<td>&nbsp;</td>");
            fd.write("<td class=\"right\">%.2f</td>" % self.callee[i].tm_self);
            fd.write("<td class=\"right\">%.2f</td>" % self.callee[i].tm_children);
            fd.write("<td class=\"right\">%d</td>" % self.callee[i].called);
            fd.write("<td class=\"right\">%d</td>" % self.callee[i].called_overall);
            fd.write("<td class=\"right\">%d</td>" % self.callee[i].called_recurse);
            fd.write("<td class=\"right\">%d</td>" % self.callee[i].cycle);
            # fd.write("<td align=\"right\">%d</td>" % self.callee[i].refer);
            if self.callee[i].refer != 0:
                fd.write("<td class=\"left\"><a href=\"./prof_g_%d.html\">%s</a> [%d]</td>\n" % (self.callee[i].refer, self.callee[i].name, self.callee[i].refer));
            else:
                fd.write("<td class=\"left\">%s</td>" % self.callee[i].name);
            fd.write("</tr>\n");
            i = i + 1;
        fd.write("</table>\n");
        
cgraph_dict = dict([])                        # gdict is a dictionary of graph


class flat_entry:
    tm_time = 0;
    tm_csec = 0;
    tm_self = 0;
    calls = 0;
    tm_call_self = 0;
    tm_call = 0;
    name = "";

    def __init__(self, tm_time, tm_csec, tm_self, calls, \
                 tm_call_self, tm_call, name):
        self.tm_time = tm_time;
        self.tm_csec = tm_csec;
        self.tm_self = tm_self;
        self.calls = calls;
        self.tm_call_self = tm_call_self;
        self.tm_call = tm_call;
        self.name = name;

    def __repr__(self):
	return "flat_entry(%f, %f, %f, %d, %f, %f, \"%s\")" % \
	    (self.tm_time, self.tm_csec, self.tm_self, self.calls, \
	     self.tm_call_self, self.tm_call, self.name);
    


class index_builder:
    def __init__(self, exefile, monfile):
	self.gprof_version = "";
	self.mon_version = "";
	self.n_his = 0;
	self.n_cg = 0;
	self.n_bbc = 0;
	self.lineno = 0;
	self.iprof = None;
	self.vprof = None;

	tmpfile = tmp_name();
        shstr = "%s -i %s %s >%s 2>/dev/null" % \
	    ( GPROF_PATH, exefile, monfile, tmpfile);

	self.iprof = Grabber(shstr, tmpfile);
        #self.f_out = execute(shstr, "Perhaps GPROF_PATH is invalid");
        lineno = 0;

	tmpfile = tmp_name();
	shstr = "%s --version >%s 2>/dev/null" % (GPROF_PATH, tmpfile);
	self.vprof = Grabber(shstr, tmpfile);

    def parse_summary(self):
	line = self.iprof.file.readline();
	self.lineno = self.lineno + 1;
	self.mon_version = re.compile(r"[^(]*\((.*)\)").match(line).group(1);

	line = self.iprof.file.readline();
	self.lineno = self.lineno + 1;
	self.n_his = int(re.compile(r"[\t\v ]*([0-9]+)").match(line).group(1));

	line = self.iprof.file.readline();
	self.lineno = self.lineno + 1;
	self.n_cg = int(re.compile(r"[\t\v ]*([0-9]+)").match(line).group(1));

	line = self.iprof.file.readline();
	self.lineno = self.lineno + 1;
	self.n_bbc = int(re.compile(r"[\t\v ]*([0-9]+)").match(line).group(1));

	self.gprof_version = self.vprof.file.readline();

    def build_index_file(self, html_dir):
        if not os.access(html_dir, os.F_OK):
            os.makedirs(html_dir);
	msg_out("Creating index file:\n");
	os.system("/bin/cp %s %s" % (CSS_FILE, html_dir));
	idxfile = "%s/index.html" % html_dir;
	fd = open(idxfile, "w");
	pyprofgen_header(fd, "Profile Data: %s" % EXE_FILE, "pyprofgen.css");
	fd.write("<h1>Profiling Data: %s</h1>\n" % EXE_FILE);
	fd.write("""
<h2>Introduction</h2>
<p>
  Profiling allows you to learn where your program spent its time and
  which functions called which other functions while it was executing.
  This information can show you which pieces of your program are slower
  than you expected, and might be candidates for rewriting to make your
  program execute faster.  It can also tell you which functions are being
  called more or less often than you expected.  This may help you spot bugs
  that had otherwise been unnoticed.
</p>

<p>
  Since the profiler uses information collected during the actual execution
  of your program, it can be used on programs that are too large or too 
  complex to analyze by reading the source.  However, how your program is
  run will affect the information that shows up in the profile data.  If 
  you don't use some feature of your program while it is being profiled, 
  no profile information will be generated for that feature.</p>\n""");

	fd.write("<h2>Summary</h2>\n");
	fd.write("<center>\n");
	fd.write("<table><tr>\n");
	fd.write(" <th>Summary Description</th><th>Value</th></tr>\n");
	fd.write(" <tr><td class=\"left\">Profiler</td>\n");
	fd.write("     <td class=\"left\">%s</td><tr>\n" % \
		 self.gprof_version);

	fd.write(" <tr><td class=\"left\"># of Histogram</td>\n");
	fd.write("     <td class=\"right\">%d</td></tr>\n" % self.n_his);

	fd.write(" <tr><td class=\"left\"># of Call Graphs</td>\n");
	fd.write("     <td class=\"right\">%d</td></tr>\n" % self.n_cg);

	fd.write(" <tr><td class=\"left\"># of Basic-Block Count Records</td>\n");
	fd.write("     <td class=\"right\">%d</td></tr>\n" % self.n_bbc);
	fd.write("</table>\n");
	fd.write("</center>\n");
	pyprofgen_footer(fd);
	msg_out("\n");



class fgraph_builder:
    def __init__(self, exefile, monfile):
	self.entries = [];
        self.lineno = 0;
	tmpfile = tmp_name();
        shstr = "%s -b -p %s %s >%s 2>/dev/null" % \
	    ( GPROF_PATH, exefile, monfile, tmpfile);
	self.flat = Grabber(shstr, tmpfile);
        #self.f_out = execute(shstr, "Perhaps GPROF_PATH is invalid");
        
    def eatup_header(self):
        # Eat the header strings from the output.
        while True:
            line = self.flat.file.readline();
            if re.compile("^[ ]*time[ ]+second").match(line):
                break;

    def parse_fgraph(self):
        self.eatup_header();
        while True:
            line = self.flat.file.readline();
            self.lineno = self.lineno + 1;
            if not line:
                break;
            tokens = line.split();
            self.entries.append(flat_entry(float(tokens[0]), \
                                           float(tokens[1]), \
                                           float(tokens[2]), \
                                           int(tokens[3]), \
                                           float(tokens[4]), \
                                           float(tokens[5]), \
                                           tokens[6]));
        
    def write_html(self, fd):
        fd.write("""
<table>
  <tr>
    <th>Time</th>
    <th>Cumulative Seconds</th>
    <th>Self seconds</th>
    <th>Calls</th>
    <th>Self ms/call</th>
    <th>Total ms/call</th>
    <th>Name</th>
  </tr>\n""");
        for entry in self.entries:
            fd.write("""
  <tr>
    <td class=\"right\">%.2f</td>
    <td class=\"right\">%.2f</td>
    <td class=\"right\">%.2f</td>
    <td class=\"right\">%d</td>
    <td class=\"right\">%.2f</td>
    <td class=\"right\">%.2f</td>
    <td class=\"left\">%s</td>
  </tr>\n""" % (entry.tm_time, entry.tm_csec, entry.tm_self, \
		entry.calls, entry.tm_call_self, entry.tm_call, \
		entry.name));

	fd.write("</table>\n");

    def write_flat_footnote(self, fd):
	fd.write("""
<h2>Glossary</h2>
  <ul>
    <li><strong>Time</strong> -- 
      This is the percentage of the total execution time your program spent
      in this function.  These should all add up to 100%.</li>
    <li><strong>Cumulative Seconds</strong> -- 
      This is the cumulative total number of seconds the computer spent 
      executing this functions, plus the time spent in all the functions
      above this one in this table.</li>
    <li><strong>Self Seconds</strong> -- 
      This is the number of seconds accounted for by this function alone. 
      The flat profile listing is sorted first by this number.</li>
    <li><strong>Calls</strong> -- 
      This is the total number of times the function was called.  If the 
      function was never called, or the number of times it was called cannot
      be determined (probably because the function was not compiled with
      profiling enabled), the \"calls\" field is blank.</li>
    <li><strong>Self ms/call</strong> -- 
      This represents the average number of milliseconds spent in this function
      per call, if this function is profiled.  Otherwise, this field is blank 
      for this function.</li>
    <li><strong>Total ms/call</strong> -- 
      This represents the average number of milliseconds spent in this 
      function and its descendants per call, if this function is profiled.
      Otherwise, this field is blank for this function.  This is the only 
      field in the flat profile that uses call graph analysis.</li>
    <li><strong>Name</strong> -- 
      This is the name of the function. The flat profile is sorted by this
      field alphabetically after the \"self seconds\" and \"calls\" fields
      are sorted.</li>
  </ul>\n""");

    def build_html_file(self, html_dir):
        if not os.access(html_dir, os.F_OK):
            os.makedirs(html_dir);
        htmlfile = "%s/prof_flat.html" % (html_dir);

        fd = open(htmlfile, "w");
	pyprofgen_header(fd, "Pyprof -- Flat Profile", "pyprofgen.css");
        fd.write("""
<h1>Flat Profile</h1>
<p>
  The &quot;flat profile&quot; shows the total amount of time your program
  spent executing each function.  Functions with no apparent time spent in
  them, and no apparent calls to them, are not mentioned.  Note that if a 
  function was not compiled for profiling, and didn't run long enough to
  show up on the program counter histogram, it will be indistinguishable
  from a function that was never called.
</p>
<center>\n""");
        self.write_html(fd);
        fd.write("</center>\n");

	self.write_flat_footnote(fd);
	pyprofgen_footer(fd);
	fd.write("</body></html>\n");
        fd.close();
        


class cgraph_builder:
    def __init__(self, exefile, monfile):
	self.lineno = 0;
	self.gid = 0;
	self.tm_time = 0;
	tmpfile = tmp_name();
        shstr = "%s -b -q %s %s >%s 2>/dev/null" % \
	    (GPROF_PATH, exefile, monfile, tmpfile);
	self.cprof = Grabber(shstr, tmpfile);
        #self.f_out = execute(shstr, "Perhaps GPROF_PATH is invalid");

    def eatup_header(self):
        "Eatup the caller table header from gprof output"
        while True:
            line = self.cprof.file.readline();
            self.lineno = self.lineno + 1;
            if not line:
                break
            if re.compile("^index").match(line):
                break

# index % time    self  children    called     name
#                                                 <spontaneous>
# [1]    100.0    0.00    0.61                 __libc_start_main [1]
#                 0.00    0.61       1/1           main [2]
#                 0.00    0.00       1/1           exit [71]
#                 0.00    0.00       1/1           __guard_setup [742]
# -----------------------------------------------
#                 0.00    0.61       1/1           __libc_start_main [1]
# [2]     99.9    0.00    0.61       1         main [2]
#                 0.00    0.23    4096/4096        putchar [9]

    def build_callee(self, line):
	"build_calleee() will clear self.index to zero"
        pat_float = r" *([0-9]*\.[0-9]*)";
        index = 0;
        tm_time = 0.0;
        tm_self = 0.0;
        tm_child = 0.0;
        called = 0;
        called_overall = 0;
        called_recurse = 0;
        end = 0;
        name = "__NONE__";
        cycle = 0;
        refer = 0;
	self.gid = 0;
        if line[0] != " ":              # we have 'index' field.
            index = int(re.compile(r"^\[([0-9]+)\]").match(line).group(1));
        if line[10] != " ":             # we have 'time' field.
            tm_time = float(re.compile(pat_float).match(line[7:]).group(1));
        if line[17] != " ":             # we have 'self' field
            tm_self = float(re.compile(pat_float).match(line[14:]).group(1));
        if line[25] != " ":             # we have 'children' field
            tm_child = float(re.compile(pat_float).match(line[22:]).group(1));
        if line[35] != " ":             # we have 'called' field
            if line[36] == " ":         # we have 'ddd' form
                start = line.rfind(" ", 0, 35);
                end = line.find(" ", 35);
                called = int(line[start:end]);
            elif line[36] == "/":       # we have 'ddd/ddd' form
                start = line.rfind(" ", 0, 35);
                end = 36;
                called = int(line[start:end]);
                end = line.find(" ", 36);
                called_overall = int(line[37:end]);
            elif line[36] == "+":       # we have 'ddd+ddd' form
                start = line.rfind(" ", 0, 35);
                end = 36;
                called = int(line[start:end]);
                end = line.find(" ", 36);
                called_recurse = int(line[37:end]);
            else:
                print "error";          # error: don't understand.
        if end == 0:
            start = 35;
        else:
            start = end + 1;
        while line[start] == " ":
            start = start + 1;
        end = line.find(" ", start);
        if end < 0:
            name = "__NONE__";
        else:
            if line[start] != "<":      # we do not have any name
                name = line[start:end];
                start = end + 1;
                
            if len(line) > start:   # we do have something after name.
                if line[start] == "<":          # we have '<cycle N>' form
                    start = start + 1;
                    cycle = int(re.compile(r"cycle ([0-9]+)").match(line[start:]).group(1));
                    start = line.find(">", start) + 2;
                if line[start] == "[":      # we have referer.
                    refer = int(re.compile(r"\[([0-9]+)\]").match(line[start:]).group(1))
	self.gid = index;
	self.tm_time = tm_time;
	return callee_entry(tm_self, tm_child, \
			    called, called_overall, called_recurse, \
			    name, cycle, refer);
#        print "index=%d, time=%f, self=%f, children=%f" % \
#              (index, tm_time, tm_self, tm_child);
#        print "called=%d, called_overall=%d, called_recurse=%d" % \
#              (called, called_overall, called_recurse);
#        print "name=%s, cycle=%d, refer=%d" % (name, cycle, refer);
    
    def parse_cgraph(self):
        global cgraph_dict;
	cgraph = call_graph();
        self.eatup_header();
	msg_out("Parse call graph(s):");
        while True:
            line = self.cprof.file.readline();
            self.lineno = self.lineno + 1;
            if not line:
                break;
            # TODO: try to understand the call-graph line here
            if line[0] == "-":          # we found a separator
		cgraph_dict[cgraph.gid] = cgraph;
		# print "\t* graph %d has %d callee(s)" % (cgraph.gid, len(cgraph.callee))
		msg_out(".");
		del cgraph;
		cgraph = call_graph();
                continue;		# TODO: register to the dictionary
            if line[0] == "\f":         # no more call graphs
                break;
            # print "%d: " % self.lineno;
	    self.gid = 0;
            callee = self.build_callee(line);
	    cgraph.add_callee(callee);
	    if self.gid != 0:
                cgraph.set_gid(self.gid);
		cgraph.set_index(len(cgraph.callee) - 1);
		cgraph.set_time(self.tm_time);
	msg_out("\n");
        
    def create_img_file(self, gid, html_dir, misc_dir):
        dotfile = "%s/prof_g_%d.dot" % (misc_dir, gid);
        imgfile = "%s/prof_g_%d.png" % (html_dir, gid);
        #msg_out("Generating img file %s..." % imgfile);
        os.system("%s -Tpng -o %s %s" % (DOT_PATH, imgfile, dotfile));
        #msg_out("done.\n");
	msg_out(".");
        
    def create_misc_files(self, gid, dirname):
        # create .dot and .map files
        dotfile = "%s/prof_g_%d.dot" % (dirname, gid);
        mapfile = "%s/prof_g_%d.map" % (dirname, gid);
        #msg_out("Generating dot file %s..." % dotfile);
        self.gen_dot_src(gid, dotfile);
        #msg_out("done.\nGenerating map file %s..." % mapfile);
        os.system("%s -Timap -o %s %s" % (DOT_PATH, mapfile, dotfile));
        #msg_out("done.\n");
	msg_out(".");

    def write_call_footnote(self, fd):
	fd.write("""
<h2>Glossary</h2>
<ul>
  <li><strong>Index</strong> -- Entries are numbered with consecutive
    integers.  Each function therefore has an index number, which appears
    at the beginning of its primary line.  Each cross-reference to a
    function, as a caller or subroutine of another, gives its index number
    as well as its name.  The index number guides you if you wish to look
    for the entry for that function.</li>
  <li><strong>Time</strong> -- This is the percentage of the total time that
    was spent in this function, including time spent in subroutines called 
    from this function. The time spent in this function is counted again 
    for the callers of this function.  Therefore, adding up these percentages
    is meaningless.</li>
  <li><strong>Self</strong> -- This is the total amount of time spent in
    this function.  This should be identical to the number printed in the
    `seconds' field for this function in the flat profile.</li>
  <li><strong>Children</strong> -- This is the total amount of time spent
    in the subroutine calls made by this function.  This should be equal
    to the sum of all the `self' and `children' entries of the children
    listed directly below this function.</li>
  <li><strong>Called</strong> -- This is the number of times the function
    was called. If the function called itself recursively, there are two
    numbers, separated by a `+'.  The first number counts non-recursive
    calls, and the second counts recursive calls. </li>
  <li><strong>Name</strong> -- This is the name of the current function.
    The index number is repeated after it.</li>
</ul>\n""");

    def create_html_file(self, gid, html_dir, misc_dir):
        #htmlfile, dotfile, mapfile):
        mapfile = "%s/prof_g_%d.map" % (misc_dir, gid);
        imgfile = "prof_g_%d.png" % (gid);
        htmlfile = "%s/prof_g_%d.html" % (html_dir, gid);

        #msg_out("Generating html file %s..." % htmlfile);
        f_html = open(htmlfile, "w");
        imap = image_map(mapfile);
        name = cgraph_dict[gid].callee[cgraph_dict[gid].index].name;
	pyprofgen_header(f_html, "PyProfGen -- %s" % name, "pyprofgen.css");
        f_html.write("<h1>Call graph of &quot;<em>%s</em>&quot;</h1>" % name);
	f_html.write("""
<p>
  The &quot;call graph&quot; shows how much time was spent in each
  function and its children.  From this information, you can find
  functions that, while they themselves may not have used much time,
  called other functions that did use unusual amounts of time.

<h2>Call Graph</h2>""");
        f_html.write("""
<center><img src=\"%s\" border=\"0\"
             usemap=\"#prof_g_%d_map\"></img></center>""" % (imgfile, gid));
        imap.write("prof_g_%d_map" % gid, f_html);
        f_html.write("<hr></hr>\n");
	f_html.write("<center>\n");

        cgraph_dict[gid].write_html(f_html);

	f_html.write("</center>\n");
	f_html.write("<hr></hr>\n");
	self.write_call_footnote(f_html);
	pyprofgen_footer(f_html);
        f_html.write("</body></html>\n");
        f_html.close();
        del imap;
        # msg_out("done.\n");
        msg_out(".");
        
    def build_misc_files(self, misc_dir):
        if not os.access(misc_dir, os.F_OK):
            os.makedirs(misc_dir);
	msg_out("Creating misc. file(s):\n");
	for cg_id, cg in cgraph_dict.iteritems():
            self.create_misc_files(cg_id, misc_dir);
	msg_out("\n");

    def build_img_files(self, html_dir, misc_dir):
        if not os.access(misc_dir, os.F_OK):
            os.makedirs(misc_dir);
        if not os.access(html_dir, os.F_OK):
            os.makedirs(html_dir);
	msg_out("Creating image file(s):\n");
	for cg_id, cg in cgraph_dict.iteritems():
            self.create_img_file(cg_id, html_dir, misc_dir);
	os.system("/bin/cp %s %s" % (LOGO_FILE, html_dir));
	msg_out("\n");

    def build_list_html(self, html_dir):
	listfile = "%s/prof_cgraph.html" % html_dir;
        if not os.access(html_dir, os.F_OK):
            os.makedirs(html_dir);
	fd = open(listfile, "w");
	pyprofgen_header(fd, "PyProfGen -- Call Graph List", "pyprofgen.css");
        fd.write("""
<h1>List of Call Graphs</h1>
<p>
  This is the list of all call graphs that the profiler recognized.
  Simply follow the link in the last field to see each call graph.
</p>
<center>\n");
<table>\n");
  <tr>
    <th>Index</th>
    <th>Time</th>
    <th>Self</th>
    <th>Children</th>
    <th>Called</th>
    <th>C. Overall</th>
    <th>C. Recurse</th>
    <th>Cycle</th>
    <th>Name</th>
  </tr>\n""");

	for cg_id, cg in cgraph_dict.iteritems():
	    callee = cg.callee[cg.index];
            fd.write("<tr>\n");
	    fd.write("<td class=\"center\">[%d]</td>" % cg.gid);
	    fd.write("<td class=\"right\">%.2f %%</td>" % cg.tm_time);
            fd.write("<td class=\"right\">%.2f</td>" % callee.tm_self);
            fd.write("<td class=\"right\">%.2f</td>" % callee.tm_children);
            fd.write("<td class=\"right\">%d</td>" % callee.called);
            fd.write("<td class=\"right\">%d</td>" % callee.called_overall);
            fd.write("<td class=\"right\">%d</td>" % callee.called_recurse);
            fd.write("<td class=\"right\">%d</td>" % callee.cycle);
            if callee.refer != 0:
                fd.write("<td class=\"left\"><a href=\"./prof_g_%d.html\">%s</a> [%d]</td>\n" % (callee.refer, callee.name, callee.refer));
            else:
                fd.write("<td class=\"left\">%s</td>" % callee.name);
            fd.write("</tr>\n");
	fd.write("</table>\n");
        fd.write("</center>\n");
	fd.write("<hr></hr>\n");
	self.write_call_footnote(fd);
	pyprofgen_footer(fd);
	fd.write("</body></html>\n");
	fd.close();

    def build_html_files(self, html_dir, misc_dir):
        if not os.access(misc_dir, os.F_OK):
            os.makedirs(misc_dir);
        if not os.access(html_dir, os.F_OK):
            os.makedirs(html_dir);
	msg_out("Creating html file(s):\n");
	for cg_id, cg in cgraph_dict.iteritems():
            self.create_html_file(cg_id, html_dir, misc_dir);
	self.build_list_html(html_dir);
	os.system("/bin/cp %s %s" % (CSS_FILE, html_dir));
	msg_out("\n");
	

    def gen_dot_src(self, gid, dotfile = ""):
        if dotfile == "":
            outf = sys.stdout;
        else:
            outf = open(dotfile, "w");
	outf.write("digraph prof_g_%d {\n" % cgraph_dict[gid].gid);
        #outf.write("\tsize=\"5,4\"\n");
        outf.write("\tbgcolor=\"transparent\";\n")
        outf.write("\tedge [fontname=\"%s\", fontsize=10, " % DOT_EDGE_FONT);
        outf.write("labelfontname=\"%s\", labelfontsize=10];\n" % DOT_LABEL_FONT);
        outf.write("\tnode [fontname=\"%s\", fontsize=10, shape=box, height=0.2];\n" % DOT_NODE_FONT);
	for c in cgraph_dict[gid].callee:
	    if c.refer == -1:
		continue;
	    outf.write("\t%s [URL=\"./prof_g_%d.html\"];\n" % (c.name, c.refer))
	outf.write("\t%s [color=\"white\" fillcolor=\"purple\" style=\"filled\" fontcolor=\"white\"]\n" % cgraph_dict[gid].callee[cgraph_dict[gid].index].name);
	outf.write("\t");
	outf.write("%s" % cgraph_dict[gid].callee[0].name);
	i = 1;
	while i < len(cgraph_dict[gid].callee):
	    outf.write(" -> ");
	    outf.write("%s" % cgraph_dict[gid].callee[i].name);
	    i = i + 1;
	outf.write(";\n");
	outf.write("}\n");
        if outf != sys.stdout:
            outf.close();
            
    def gen_dot_src_all(self, dotfile = ""):
        if dotfile == "":
            outf = sys.stdout;
        else:
            outf = open(dotfile, "w");
	outf.write("digraph Gall {\n");

	for k, v in cgraph_dict.iteritems():
	    outf.write("\t");
	    outf.write("%s" % v.callee[0].name);
	    i = 1;
	    while i < len(v.callee):
		outf.write(" -> ");
		outf.write("%s" % v.callee[i].name);
		i = i + 1;
	    outf.write(";\n");

	outf.write("}\n");
        if outf != sys.stdout:
            outf.close();



def version():
    print "pyprofgen version %s" % pyprofgen_version;

def usage():
    print """\
USAGE: pyprofgen [OPTION...] executable [gmon.out]
Generate HTML documents from gmon.out

  -d DIR,               Set the output directory to DIR,
      --directory=DIR     (default: doc)
  -q, --quiet           Quite mode, (default: verbose mode)
  -h, --help            Show help message
  -v, --version         Print version information

Report bugs to <cinsky@gmail.com>.

"""


def main():
    global verbose_mode, document_dir;
    global MON_FILE, EXE_FILE;
    global debug_mode, HTML_DIR, MISC_DIR, PPG_LIB_DIR;
    
    try:
	opts, arg = getopt.getopt(sys.argv[1:], "d:qhvD", \
				  ["help", "directory=", "quiet", "version", \
				   "debug"]);
    except getopt.GetoptError:
	usage();
	sys.exit(1);
        
    for o, a in opts:
	if o in ("-v", "--version"):
	    version();
	    sys.exit(0);
	if o in ("-h", "--help"):
	    usage();
	    sys.exit(0);
	if o in ("-q", "--quiet"):
	    verbose_mode = 0;
	if o in ("-d", "--directory"):
	    document_dir = a;
	if o in ("-D", "--debug"):
	    debug_mode = 1;

    msg_out("pyprofgen version %s  \n" % pyprofgen_version);

    debug("Debug mode: %d" % debug_mode);
    init();
    debug("Base Library directory: %s" % PPG_LIB_DIR);
    debug("Output HTML directory: %s" % HTML_DIR);
    debug("Output MISC directory: %s" % MISC_DIR);
    
    if len(arg) != 1 and len(arg) != 2:
	error(0, "wrong number of argument(s).")
	error(1, "use '-h' option for more.")
	
    EXE_FILE = arg[0];
    if len(arg) == 2:
	MON_FILE = arg[1];
    else:
	MON_FILE = "gmon.out"

    if not os.access(EXE_FILE, os.R_OK):
	error(1, "cannot access \"%s\", permission denied." % EXE_FILE);

    if not os.access(MON_FILE, os.R_OK):
	error(1, "cannot access \"%s\", permission denied." % MON_FILE);

    # grabber = Grabber("/bin/ls > tmp.tmp", "tmp.tmp");
    # grabber.grab();

#def dummy():
    # generate

    cbuilder = cgraph_builder(EXE_FILE, MON_FILE);
    cbuilder.parse_cgraph();
    cbuilder.build_misc_files(MISC_DIR);
    cbuilder.build_img_files(HTML_DIR, MISC_DIR);
    cbuilder.build_html_files(HTML_DIR, MISC_DIR)

    fbuilder = fgraph_builder(EXE_FILE, MON_FILE);
    fbuilder.parse_fgraph();
    fbuilder.build_html_file(HTML_DIR);

    ibuilder = index_builder(EXE_FILE, MON_FILE);
    ibuilder.parse_summary();
    ibuilder.build_index_file(HTML_DIR);

if __name__ == "__main__":
    main()


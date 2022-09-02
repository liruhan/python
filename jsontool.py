#! /usr/bin/python

import sys
import re
import json
import os

ACT = {
	"r": ["r"],
	"e!":   ["e!"],
	"quit": ["q", "quit", "exit"],
	"dir":  ["dir"],
	"ls":   ["ls"],
	"edit": ["edit"],
	"cd":   ["cd"],
	"pwd":  ["pwd"],
	"w!":   ["w!"],
}

def abspath (path, name):
	if not name.startswith ("/"): name = ("" if path.endswith ("/") else path) + "/" + name
	path = os.path.abspath (name)
	return path

def testpath (obj, path):
	path = path.split ("/")
	for i in path:
		if len (i) == 0: continue
		if isinstance (obj, dict):
			if not i in obj: return False
			obj = obj[i]
		elif isinstance (obj, list):
			obj = obj[int (i)]
		else: return False
	return True
	
def getvalue (obj, path):
	path = path.split ("/")
	for i in path:
		if len (i) == 0: continue
		if isinstance (obj, dict):
			obj = obj[i]
		elif isinstance (obj, list):
			i = int (i)
			obj = obj[int (i)]
	return obj

def setvalue (obj, path, value):
	basename = os.path.basename (path)
	dirname = os.path.dirname (path)
	obj = getvalue (obj, dirname)
	if isinstance (obj, dict):
		obj[basename] = value
	elif isinstance (obj, list):
		obj[int (basename)] = value

def read (string, count):
	value = re.split ("[    \n]+", re.sub ("^[      \n]+|[\n]+$", "", string), count + 1)
	for i in range (len (value), count): value.append ("")
	return value

reload (sys)
sys.setdefaultencoding ("utf-8")
FILE = ""
OBJ = ""
CWD = "/"
TMPFILE = os.tempnam ()
open (TMPFILE, "w+")
while True:
	try:
		sys.stderr.write (FILE + ") ")
		instr = sys.stdin.readline ()
		if len (instr) == 0: break
		[a, b] = read (instr, 2)
		if a in ACT["r"]:
			OBJ = json.load (open (b, "rb"))
			FILE = b
		elif a in ACT["e!"]:
			OBJ = json.load (open (FILE, "rb"))
		elif a in ACT["dir"]:
			path = abspath (CWD, b)
			if testpath (OBJ, path):
				obj = getvalue (OBJ, path)
				isstr = isinstance (obj, unicode) or isinstance (obj, str)
				if isstr:
					print (obj)
					continue
				json.dump (obj, sys.stdout, ensure_ascii = False, sort_keys = True, indent = 4)
				sys.stdout.write ("\n")
		elif a in ACT["cd"]:
			path = abspath (CWD, b)
			if testpath (OBJ, path): CWD = path
			print (CWD)
		elif a in ACT["ls"]:
			path = abspath (CWD, b)
			if testpath (OBJ, path):
				tmp = getvalue (OBJ, path)
				if isinstance (tmp, dict):
					for i in tmp.keys (): print (i)
				elif isinstance (tmp, list):
					print ("0 ... " + str (len (tmp) - 1))
		elif a in ACT["edit"]:
			path = abspath (CWD, b)
			value = getvalue (OBJ, path)
			isstr = isinstance (value, unicode) or isinstance (value, str)
			valuetype = type (value)
			if not isstr:
				value = (json.dumps (getvalue (OBJ, path), ensure_ascii = False, sort_keys = True, indent = 4))
			open (TMPFILE, "wb").write (value)
			os.system ("view " + TMPFILE)
			value = open (TMPFILE, "rb").read ()
			if value[-1] == "\n": value = value[:-1]
			if not isstr:
				value = json.loads (value)
				if type (value) != valuetype: continue
			if path == "/": OBJ = value
			else: setvalue (OBJ, path, value)
		elif a in ACT["w!"]:
			output = open (FILE, "wb")
			json.dump (OBJ, output, ensure_ascii = False, sort_keys = True, indent = 4)
			output.write ("\n")
			print ("w!" + FILE)
			output.close ()
		elif a in ACT["pwd"]:
			print (CWD)
		elif a in ACT["quit"]:
			break
	except Exception as e: sys.stderr.write (str (e) + "\n")

os.unlink (TMPFILE)

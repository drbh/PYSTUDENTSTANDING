import web

import subprocess

import sys
sys.path.append('PYSTUDENTSTANDING/')

import Student as st
import MatchMachine as mm
import Major as mj
import Optimizer as oz

import json


def do_all(EMPLID,ACAD_PLAN,ENROLL_YEAR):
    matcher = mm.MatchMachine( st.Student(EMPLID), mj.Major(ACAD_PLAN,ENROLL_YEAR) )
    opt = oz.Optimizer(matcher)
    result = opt.out, opt.missed_courses, opt.missed_requirments
    return result



urls = (
    '/(.*)', 'hello'
)
app = web.application(urls, globals())

class hello:
    def GET(self, name):


 	# EM = '1203975040'
 	# AP = 'BAMKTBS'
 	# SY = '2011'

	if name[0:4] == "args":
		arguments = name[5:].split("-")
		EM = arguments[0]
		AP = arguments[1]
		SY = arguments[2]

		print EM,AP,SY
		result = do_all(int(EM),str(AP),int(SY))

		# jsonresults = json.dumps(result) 
		return [ True, result ]

if __name__ == "__main__":
    app.run()
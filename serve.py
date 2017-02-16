import web

import subprocess

import sys
sys.path.append('PYSTUDENTSTANDING/')

import Student as st
import MatchMachine as mm
import Major as mj
import Optimizer as oz

import json
from bson import json_util

import time

def do_all(EMPLID,ACAD_PLAN,ENROLL_YEAR):

    start_time = time.time()
    matcher = mm.MatchMachine(st.Student(EMPLID), mj.Major(ACAD_PLAN, ENROLL_YEAR))
    print("--- %s seconds ---" % (time.time() - start_time))

    start_time = time.time()
    opt = oz.Optimizer(matcher)
    print("--- %s seconds ---" % (time.time() - start_time))

    start_time = time.time()
    result = opt.out, opt.missed_courses, opt.missed_requirments
    print("--- %s seconds ---" % (time.time() - start_time))



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

        mtch = result[0][0].to_dict()
        mssreq = result[2].to_dict()
        missed_classes = result[1].to_dict()

        merged_dict = {key: value for (key, value) in (mtch.items() + mssreq.items())}

        merged_dict =  {key: value for (key, value) in (merged_dict.items() + missed_classes.items())}
        # string dump of the merged dict
        matches = json.dumps(merged_dict)


        # missed_requirements = json.dumps(result[2].to_dict())
        return matches


if __name__ == "__main__":
    app.run()
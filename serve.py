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

        if name[0:4] == "args":
            arguments = name[5:].split("-")
            EM = arguments[0]
            AP = arguments[1]
            SY = arguments[2]

            print EM,AP,SY

            opti_result = do_all(int(EM),str(AP),int(SY))

            print opti_result[0][1]

            match = dict({'Optimized Matches' : opti_result[0][0].to_dict() })
            mssreq = dict({'Missed Requirements':  opti_result[2].to_dict() })
            missed_classes = dict({'Missed Classes': opti_result[1].to_dict() })
            percent = dict({'Percentage Complete' : opti_result[0][1] })

            merged_dict = {key: value for (key, value) in (match.items() + mssreq.items())}
            merged_dict =  {key: value for (key, value) in (merged_dict.items() + missed_classes.items())}
            merged_dict = {key: value for (key, value) in (merged_dict.items() + percent.items())}
            # string dump of the merged dict

            matches = json.dumps(merged_dict, sort_keys=True, indent=4, default=json_util.default) #json.dumps(merged_dict)

            return matches


if __name__ == "__main__":
    app.run()
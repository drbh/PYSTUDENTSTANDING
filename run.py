import sys
sys.path.append('/Users/drbh/Desktop/PYSTUDENTSTANDING/')

import Student as st
import MatchMachine as mm
import Major as mj
import Optimizer as oz


def do_all(EMPLID,ACAD_PLAN,ENROLL_YEAR):
#     EMPLID       = 1203975040
#     ACAD_PLAN    = 'BAMKTBS'
#     ENROLL_YEAR  = 2011

    matcher = mm.MatchMachine( st.Student(EMPLID), mj.Major(ACAD_PLAN,ENROLL_YEAR) )
    opt = oz.Optimizer(matcher)
    result = opt.out
    return result


def main():

	EMPLID, ACAD_PLAN, ENROLL_YEAR = sys.argv[1:]

	EMPLID = int(EMPLID)
	ACAD_PLAN = str(ACAD_PLAN)
	ENROLL_YEAR = int(ENROLL_YEAR)

	print EMPLID, ACAD_PLAN, ENROLL_YEAR
	print

	ot = do_all(EMPLID, ACAD_PLAN, ENROLL_YEAR)
	print ot
	return True

if __name__ == '__main__':
	main()
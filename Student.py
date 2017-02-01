# PYTHON 2.7 
# STUDENT STANDING PROGRAM
# 
# David Holtz
# 2017
# Arizona State University
# 
# All inline comments are above code that is relevant

print "Loading files for STUDENT"

import pandas as pd
all_students_meta = pd.read_csv("~/all_students_meta_asupmtst_pre_process.csv", low_memory=False, index_col = 0 )
student_data_sql = pd.read_csv("~/student_data_sql.csv", low_memory=False)
all_courses = pd.read_csv("~/all_courses_asupmtst_pre_process.csv", index_col = 0 )

class Student(object):
    """
    A Student of ASU with a course history. Students have the following properties:
    
    Attributes:
        emplid: A unique identifier
        major_data: A array of major data
        student_hist: A array of classes taken.
    """
    def __init__(self, emplid):
        """
        Return a Student object whose id is *emplid* gets major data and students history
        """

        self.connected = self.connect_to_datasouce()
        self.emplid = emplid
        self.major_data = all_students_meta[all_students_meta['EMPLID'] == self.emplid]
        self.student_hist = self.students_history()

    def connect_to_datasouce(self):
        return True

    def countCourses(self):
        """
        Return the number of classes
        """
        if 0 > self.student_hist.shape[0]:
            raise RuntimeError('No courses.')
        return self.student_hist.shape
    
    def get_majors(self):
        """
        Return major data

        FIX - should return the students major map year and code  
        """
        return self.major_data
        # return [ (self.major_data['ACAD_PLAN_TYPE'] == 'MAJ') & (self.major_data['ADMIT_TERM'] == max(self.major_data['ADMIT_TERM'])) ]
    
    def students_history(self):
        """
        Return students past history
        """

        # Subset to just EMPLID matches
        student_hist = student_data_sql[student_data_sql['EMPLID'] == self.emplid] 

        # Add two new columns FULL name and if ELECTIVE
        student_hist = student_hist.assign( FULL = (student_hist['SUBJECT'] + ' ' + student_hist['CATALOG_NBR']) )
        student_hist = student_hist.assign( ELEC = True )

        # Merge on the all_coursesn table with general studies matrix
        student_hist = student_hist.merge(all_courses,how='left', left_on='FULL', right_on='full')
        return student_hist
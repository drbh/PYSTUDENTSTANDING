# PYTHON 2.7 
# STUDENT STANDING PROGRAM
# 
# David Holtz
# 2017
# Arizona State University
# 
# All inline comments are above code that is relevant
# 
import numpy as np # for general studies matrix
import pandas as pd # to deal with tables
from itertools import chain # for building graph
import re # for parsing out the requirments text 


major_maps_sql = pd.read_csv("~/major_maps_sql_asupmtst_pre_process.csv", low_memory=False, index_col = 0 )
all_courses = pd.read_csv("~/all_courses_asupmtst_pre_process.csv", index_col = 0 )
student_data_sql = pd.read_csv("~/student_data_sql.csv", low_memory=False)



class Major(object):
    """
    A Major at ASU. Majors have the following properties:

    Attribute:
    """
    def __init__(self, map_code, enroll_year):
        """
        Return a Major object includng 
        """
        self.map_code = map_code
        self.major_data = major_maps_sql[(major_maps_sql['ACAD_PLAN'] == self.map_code) & (major_maps_sql['YEAR'] == enroll_year)]
        self.cleaned_major_data = self.clean_map()
        
    def clean_map(self):
        mapd = self.major_data
        if mapd.shape[0] == 0:
            print "NO MAP DATA AVAILABLE"   
            return None
        FULL = mapd['SUBJECT'] + ' ' + mapd['CATALOG_NBR']
        REQID = mapd[['REQUIREMENT_TERM_ID','REQ_MULTIPLE_TERM_ID']].max(axis=1)
        is_track = mapd.apply(lambda row: len(str(row['TRACK_GROUP'])) > 10, axis=1)
        REQID[is_track] = 0
        mapd = mapd.assign( FULL = FULL )
        mapd = mapd.assign( REQID = REQID )
        mapd = mapd.merge(all_courses,how='left', left_on='FULL', right_on='full')
        return mapd #mapd[['FULL','MULT_OUTPUT_MESSAGE','CATEGORY_DESCR', 'REQID', 'GS', 'GS_TYPE1', 'REQ_LEVEL_ADJ']]
        
    def readable_name(self):
        return self.major_data['ACAD_PLAN_DESCR'][0]



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

   
class MatchMachine(object):
    """ This MatchMachine that takes in a student and a major map
    Attributes:
        
    """
    def __init__(self, student, major_map):
        self.student = student
        self.major_map = major_map
        self.general_studies = self.general_studies_self()
        self.subject = self.subject_self()
        self.exact = self.exact_self()
        self.elective = self.elective_self()
        self.graph = self.build_graph()

        self.classes_from , self.requiments_to  = self.build_opt()
        self.expanded = self.class_combinations()


    def general_studies_self(self):
        """
        Returns the requirements ids that match the general studies
        """
        columns_needed = ['L','MA','CS','HU','SB','SQ','SG','C','G','H','Honor']
        
        # Store matrixes for computation
        student_gs_matrix = self.student.student_hist[columns_needed].fillna(value = 0).as_matrix()
        major_gs_matrix = self.major_map.cleaned_major_data[(columns_needed)].fillna(value = 0).as_matrix()
        
        # Match the matrixes with dot product and then check 
        # dot product is equal to the number of reqs needed
        matches = np.dot(student_gs_matrix, major_gs_matrix.T)

        # Check if the number of matches is equal to the total number of matches
        row_sums = np.array([1/sum(row) for row in major_gs_matrix])
        final_frame = pd.DataFrame(matches).mul(row_sums, axis=1).fillna(value = 0 )

        # Only True if the course general studies match all of the requirments general studies
        final_frame = final_frame == 1
        return self.__get_reqs(final_frame)        


    def subject_self(self):
        major_subject_names = self.major_map.cleaned_major_data['FULL'].str[0:3]
        tester = self.student.student_hist['FULL'].str[0:3].apply(lambda sub: sub == major_subject_names )
        return self.__get_reqs(tester)
    
    def exact_self(self):
        exact = self.student.student_hist['FULL'].apply(lambda cls: cls == self.major_map.cleaned_major_data['FULL'] )
        return self.__get_reqs(exact)
    
    def elective_self(self):
        upper = []
        lower = []
        return False

    def __get_reqs(self, match_matrix):
        reqids = self.major_map.cleaned_major_data['REQID']
        reduced_matches = np.array([reqids[x].dropna().drop_duplicates().astype('str').str.cat(sep=', ') for x in match_matrix.values])
        return pd.DataFrame(reduced_matches, dtype='str', columns=['REQIDS'])

    def build_graph(self):
        # make new matrix of the student classes and their general studies matrix
        all_matches = pd.concat([self.student.student_hist['FULL'].reset_index(drop=True),self.general_studies], axis=1)    #, self.subject, self.exact], axis=1)
        all_matches.columns = [['FULL','ALL']]
        all_matches.columns
        split_reqs = [reqs.split(', ') for reqs in all_matches['ALL'].as_matrix() ]
        rep_values = [line.count(",") + 1 for line in all_matches['ALL']]
        CLS = np.repeat(all_matches['FULL'].as_matrix(), rep_values  )
        REQ = np.array(list(chain.from_iterable(split_reqs)))
        graph = pd.DataFrame([CLS, REQ]).T
        graph.columns = ['CLS','REQ']
        return graph

    def build_opt(self):
        requiments = self.major_map.cleaned_major_data[['REQID','DESCR.y']]
        student_taken = self.student.student_hist[['FULL','DESCR.y']]

        requiments.is_copy = False
        requiments['REQID'] = requiments['REQID'].astype('str')
 
        requiments_to = pd.merge(self.graph, requiments, how='left', left_on='REQ', right_on='REQID')
        classes_from = pd.merge(self.graph, student_taken, how='left', left_on='CLS', right_on='FULL')

        return classes_from, requiments_to

    def class_combinations(self):

        classes_from = self.classes_from

        # Split the AND from the OR text eg. ['(HU or SB) ', 'G']
        gs_split = [ '' if pd.isnull(x) else x.split('& ') for x in classes_from['DESCR.y'].as_matrix() ]

        # lambda map through two levels of list to remove ',' and '(' and ')' from text
        # split all of the values that contain or again for expanding the frame
        regex = re.compile('[,\)\(]')
        or_split = map(lambda x: map(lambda y: regex.sub('', y ) ,x) if len(x) > 0 else x , gs_split)
        or_split = [ g[0].split("or") if len(g) > 0 else ' ' for g in or_split]

        # number of times to repeat based on length of values in list eg. each OR needs a new row
        or_rep = [ len(g) for g in or_split]

        # repeat class names the right amount of times
        classname = np.repeat(classes_from['FULL'].as_matrix(), or_rep )

        # unlist the or split to have the correct values per row
        or_reqs = list(chain.from_iterable(or_split))

        # extract all AND req text
        and_reqs = [ g[1:] if len(g) > 1 else ' ' for g in gs_split]

        # if theres a list we concat them together
        concat_reqs = [ ''.join(map(str, g)) if isinstance(g, list) else '' for g in and_reqs]

        # repeat correct number of AND reqs
        and_reqs = np.repeat(concat_reqs, or_rep)

        # make dataframe, concat columns of interest
        # rename columns 
        # HEAVY ---------
        expanded = pd.DataFrame([classname, or_reqs, and_reqs]).T
        expanded.columns = ['CLS','OR','AND']
        as_strings = expanded['OR'] + expanded['AND'] 
        expanded =  pd.DataFrame([classname, as_strings]).T
        expanded.columns = ['CLS','GS']
        expanded = expanded.drop_duplicates()

        return expanded


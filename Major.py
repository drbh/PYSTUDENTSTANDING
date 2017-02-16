# PYTHON 2.7 
# STUDENT STANDING PROGRAM
# 
# David Holtz
# 2017
# Arizona State University
# 
# All inline comments are above code that is relevant

print "Loading files for MAJOR"

import pandas as pd
import re
import time

major_maps_sql = pd.read_csv("~/major_maps_sql_asupmtst_pre_process.csv", low_memory=False, index_col = 0 )

start_time_3 = time.time()
all_courses = pd.read_pickle('all_courses.pickle')
print "--- ALL COURSES --- %s seconds ---" % (time.time() - start_time_3) 


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
        self.cleaned_major_data = self.__clean_map()
        
    def __clean_map(self):
        mapd = self.major_data
        if mapd.shape[0] == 0:
            print "NO MAP DATA AVAILABLE"   
            return None

        # combind subject and catalog number for full name
        FULL = mapd['SUBJECT'] + ' ' + mapd['CATALOG_NBR']
        # get one value for requirment id
        REQID = mapd[['REQUIREMENT_TERM_ID','REQ_MULTIPLE_TERM_ID']].max(axis=1)
        # check if the row has text in track group
        is_track = mapd.apply(lambda row: len(str(row['TRACK_GROUP'])) > 10, axis=1)
        # id is track make reqid 0
        REQID[is_track] = 0

        # add columns to frame
        mapd = mapd.assign( FULL = FULL )
        mapd = mapd.assign( REQID = REQID )


        # get the pattern for classes
        regex = re.compile('[A-Z]{3} [0-9]{3}')
        # find all of the classes that are course specific but dont have a course
        course_no_explicit = mapd[(mapd['REQUIREMENT_TYPE'] == 'C') & (mapd['FULL'].isnull())]['MULT_OUTPUT_MESSAGE']
        # find all courses in multi output text
        or_courses_extracted = [regex.findall(i) for i in course_no_explicit]
        # hold the index for update
        indexes = course_no_explicit.index.values

        for i in range(0, len(or_courses_extracted)):
            expanded_row = pd.concat([mapd.loc[[indexes[i]]]] * len(or_courses_extracted[i]))
            expanded_row['FULL'] = or_courses_extracted[i]
            mapd = pd.concat([mapd, expanded_row])

        # join classes by full
        mapd = mapd.merge(all_courses,how='left', left_on='FULL', right_on='full')
        # filter frame by requirments that are courses, general studies and electives
        mapd = mapd[ mapd['REQUIREMENT_TYPE'].apply(lambda x: x in ['C','G','E'])]
        # make new frame with choosen columns
        A = mapd[['FULL','MULT_OUTPUT_MESSAGE','REQID','DESCR.y','SINGLE_OUTPUT_MESSAGE','REQUIREMENT_TYPE','full','GS','GS_TYPE1','GS_TYPE2','GS_TYPE3']]
        # make general studies matrix from frame
        general_sudies_matrix = self.__extract_reqs_from_major_map(mapd)
        # concatenate the matrix and smaller frame
        mapd = pd.concat([A, general_sudies_matrix], axis=1)

        return mapd #mapd[['FULL','MULT_OUTPUT_MESSAGE','CATEGORY_DESCR', 'REQID', 'GS', 'GS_TYPE1', 'REQ_LEVEL_ADJ']]
        
    def readable_name(self):
        """
        Returns readable major name
        """
        return self.major_data['ACAD_PLAN_DESCR'][0]

    def __extract_reqs_from_major_map(self, df):
        test = df['GS'] + ' ' + df['GS_TYPE1'] + ' ' + df['GS_TYPE2'] + ' ' + df['GS_TYPE3']
        regex = re.compile('[ \-\)\(]')
        extract_general_reqs = [ regex.sub('', g ).split('&') if isinstance(g, str) else '' for g in test ]

        results = list()
        ASU_REQS = ['L','MA','CS','HU','SB','SQ','SG','C','G','H','Honor']

        # loop thorough each row
        for requirement_gs in extract_general_reqs:
            row_res = dict((el,0) for el in ASU_REQS)
            if len(requirement_gs) > 0:

                # loop through all extracted GS text
                for gs in requirement_gs:

                    # compare to all ASU general studies types
                    for general_study in ASU_REQS:

                        # if match update the dict
                        if gs == general_study:
                            row_res.update({general_study : 1})
            results.append(row_res)

        # list of dicts into a pandas object
        return pd.DataFrame(results)
# PYTHON 2.7 
# STUDENT STANDING PROGRAM
# 
# David Holtz
# 2017
# Arizona State University
# 
# All inline comments are above code that is relevant
import numpy as np # for general studies matrix
import pandas as pd # to deal with tables
from itertools import chain # for building graph
from itertools import combinations # for doing combinatorics data
import re # for parsing out the requirments text 
   
class MatchMachine(object):
    """ This MatchMachine that takes in a student and a major map
    Attributes:
        
    """
    def __init__(self, student, major_map):
        """
        Returns an object of the MatchMachine class.
        """
        self.student            = student
        self.major_map          = major_map

        # matches 
        self.general_studies    = self.__general_studies_self()
        self.subject            = self.__subject_self()
        self.exact              = self.__exact_self()
        self.low_elective       = self.__low_elective_self()
        self.up_elective        = self.__up_elective_self()

        # expanded matches
        self.graph              = self.__build_graph()

        # linear optimization lookup tables
        self.classes_from , self.requirements_to    = self.build_opt()

        # 
        self.expanded           = self.class_combinations()
        self.all_combos         = self.get_all_combinations()

        self.matches = self.___matches()

    def __general_studies_self(self):
        """
        Returns the requirements ids that match the general studies
        """
        columns_needed = ['L','MA','CS','HU','SB','SQ','SG','C','G','H','Honor']
        
        # Store matrixes for computation
        student_gs_matrix = self.student.student_hist[columns_needed].fillna(value = 0).as_matrix()

        df = self.major_map.cleaned_major_data

        major_gs_matrix = df[(columns_needed)].fillna(value = 0).as_matrix()
        
        pop = self.major_map.cleaned_major_data['REQUIREMENT_TYPE'] == 'C'
        new = list()
        for index, item in enumerate(major_gs_matrix):
            if pop[index]:
                new.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            else: 
                new.append(list(item))
        major_gs_matrix = np.array(new)


        # Match the matrixes with dot product and then check 
        # dot product is equal to the number of reqs needed
        matches = np.dot(student_gs_matrix, major_gs_matrix.T)

        # Check if the number of matches is equal to the total number of matches
        row_sums = np.array([1/sum(row) if sum(row) > 0 else 0 for row in major_gs_matrix])
        final_frame = pd.DataFrame(matches).mul(row_sums, axis=1).fillna(value = 0 )

        # Only True if the course general studies match all of the requirments general studies
        final_frame = final_frame == 1
        return self.__get_reqs(final_frame)        


    def __subject_self(self):
        """
        Returns all of the matches were the subject is the same
        """
        # Iterate over each row in the dataframe, check if the requirement type is not C and the name is a string (avoid NAs) and then extract the three letter subject code
        major_subject_names = pd.Series([ row['FULL'][0:3] if row['REQUIREMENT_TYPE'] != 'C' and isinstance(row['FULL'],str) else np.NAN for idx, row in self.major_map.cleaned_major_data.iterrows()])
        # Expand these matches over all of the students classes and all of the requirements
        tester = self.student.student_hist['FULL'].str[0:3].apply(lambda sub: sub == major_subject_names )
        return self.__get_reqs(tester)
    
    def __exact_self(self):
        """
        Returns all of the exact class matches
        """
        exact = self.student.student_hist['FULL'].apply(lambda cls: cls == self.major_map.cleaned_major_data['FULL'] )
        return self.__get_reqs(exact)
    
    def __low_elective_self(self):
        """
        Returns the requirements ids that match the general studies
        """
        lower_div_electives = pd.Series([ True if row['REQUIREMENT_TYPE'] == 'E' and 'Upper' not in row['SINGLE_OUTPUT_MESSAGE'] else False for idx, row in self.major_map.cleaned_major_data.iterrows()])

        result = list()
        for iselective in self.student.student_hist['ELEC']:
            if iselective:
                row = lower_div_electives
            else:
                row = np.repeat(False, len(lower_div_electives) )
            result.append(row)
        lower = pd.DataFrame(result)

        upper = []
        return self.__get_reqs(lower)

    def __up_elective_self(self):
        """
        Returns the requirements ids that match the general studies
        """
        upper_div_electives = pd.Series([ True if row['REQUIREMENT_TYPE'] == 'E' and 'Upper' in row['SINGLE_OUTPUT_MESSAGE'] else False for idx, row in self.major_map.cleaned_major_data.iterrows()])

        result = list()
        for iselective in self.student.student_hist['ELEC']:
            if iselective:
                row = upper_div_electives
            else:
                row = np.repeat(False, len(upper_div_electives) )
            result.append(row)
        upper = pd.DataFrame(result)
        return self.__get_reqs(upper)

    def __get_reqs(self, match_matrix):
        """
        Returns the requirements ids that match the general studies
        """
        reqids = self.major_map.cleaned_major_data['REQID']
        reduced_matches = np.array([reqids[x].dropna().drop_duplicates().astype('str').str.cat(sep=', ') for x in match_matrix.values])
        return pd.DataFrame(reduced_matches, dtype='str', columns=['REQIDS'])

    def get_reqs(self, match_matrix):
        """
        Returns the requirements ids that match the general studies
        """
        reqids = self.major_map.cleaned_major_data['REQID']
        reduced_matches = np.array([reqids[x].dropna().drop_duplicates().astype('str').str.cat(sep=', ') for x in match_matrix.values])
        return pd.DataFrame(reduced_matches, dtype='str', columns=['REQIDS'])


    def ___matches(self):
        all_matches = pd.concat([self.student.student_hist['FULL'].reset_index(drop=True),  self.exact, self.subject, self.general_studies, self.low_elective, self.up_elective], axis=1)
        all_matches.columns = ['FULL','EXACT','SUBJECT','GENERAL','LOWELECT','UPELECT']
        all_matches['ALL'] = all_matches['EXACT'] + ', '+ all_matches['SUBJECT'] + ', ' + all_matches['LOWELECT'] + ', ' + all_matches['UPELECT'] + ', ' + all_matches['GENERAL'] 
        return all_matches

    def __build_graph(self):
        """
        Returns the requirements ids that match the general studies
        """
        all_matches = self.___matches()
        # make new matrix of the student classes and their general studies matrix
        split_reqs = [reqs.split(', ') for reqs in all_matches['ALL'].as_matrix() ]
        rep_values = [line.count(",") + 1 for line in all_matches['ALL']]
        CLS = np.repeat(all_matches['FULL'].as_matrix(), rep_values  )
        REQ = np.array(list(chain.from_iterable(split_reqs)))
        graph = pd.DataFrame([CLS, REQ]).T
        graph.columns = ['CLS','REQ']
        graph = graph.drop_duplicates()
        return graph

    def build_opt(self):
        """
        Returns the requirements ids that match the general studies
        """
        student_taken = self.student.student_hist[['FULL','DESCR.y']]

        requiments = self.major_map.cleaned_major_data[['REQID','L','MA','CS','HU','SB','SQ','SG','C','G','H','Honor']]

        requiments.is_copy = False
        requiments['REQID'] = requiments['REQID'].astype('str')

        requirements_to = pd.merge(self.graph, requiments, how='inner', left_on='REQ', right_on='REQID')
 
        # requirements_to = pd.merge(self.graph, requiments, how='left', left_on='REQ', right_on='REQID')
        classes_from = pd.merge(self.graph, student_taken, how='left', left_on='CLS', right_on='FULL')

        return classes_from, requirements_to

    def class_combinations(self):
        """
        Return the expanded combinations of AND and OR general studies requirements
        """
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


    def all_subsets(self, ss):
        """
        Suporting function for all combinations that follows 
        """
        return chain(*map(lambda x: combinations(ss, x), range(1, len(ss)+1)))



    def all_combinations(self, stuffs):
        combinations = []
        req = []
        for idx, stuff in enumerate(stuffs):
            for subset in self.all_subsets(stuff):
                filtersubset = filter(lambda item: item != '', subset)
                req.append(idx)
                combinations.append(list(filtersubset))
        return req, combinations


    def get_all_combinations(self):
        """
        Returns all fo the combinations of 
        """
        stuffs = map(lambda row: row.split(" "), self.expanded['GS'] )

        combs = self.all_combinations(stuffs)

        cls_repeated = self.expanded['CLS'].reset_index(drop=True)[np.array(combs[0])]

        A = cls_repeated.reset_index(drop=True)
        B = pd.Series(combs[1])

        combo_table = pd.DataFrame([A, B]).T

        combo_table.columns = ['CLS','GSCMB']

        df = combo_table

        df['srt'] = [ ' '.join(map(str, g))  for g in df["GSCMB"] ]
        keep_idx = df[[0,2]].drop_duplicates().index
        gewd = df.iloc[keep_idx,:].reset_index(drop=True)[["CLS","GSCMB"]]

        combo_table = gewd

        combo_dict = combo_table.groupby('CLS')['GSCMB'].apply(lambda x: x.tolist())
        return combo_dict
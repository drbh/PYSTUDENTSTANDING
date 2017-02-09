

# PYTHON 2.7 
# STUDENT STANDING PROGRAM
# 
# David Holtz
# 2017
# Arizona State University
# 
# All inline comments are above code that is relevant

import numpy as np
from scipy.optimize import linprog
import itertools
import pandas as pd


class Optimizer(object):
    """
    A Major at ASU. Majors have the following properties:

    Attribute:
    """

    def __init__(self, matcher):
        """
        Return a Major object includng 
        """
        self.matcher = matcher

        self.dv = list(set(self.make_decision_variables()))

        self.objective = np.array([x.count(", ") + 1 for x in self.dv])
        self.constraintix = self.constraint_matrix()
        self.upper_bound = np.repeat(1, len( self.constraintix ))
        self.match_dict = self.make_match_dict()
        self.out = self.output_graph()
        self.missed_requirments = self.missing_requirments()
        self.missed_courses = self.missing_courses()

    def get_class_use_choices(self, cname):
        results = dict()
        setsub = self.matcher.requirements_to[self.matcher.requirements_to['CLS'] == cname].drop_duplicates()
        for allowed in self.matcher.all_combos[ cname ]:
            if len(allowed) > 0:
                hr = list()
                for single in allowed:
                    res = setsub[single] == 1
                    xyz = setsub[res]['REQID'].values
    #                 if res.shape[0] > 0: 
                    hr.append(xyz)
                combs = list(itertools.product(*hr))
                results[cname + ' ' + ' '.join(map(str, allowed))  ] = combs
            else:
                continue
        return results

    def make_match_dict(self):
        nms = list()
        for classn in self.matcher.student.student_hist['FULL']:
            pp = self.get_class_use_choices(classn)
            nms.append(pp)
        return nms

    def make_decision_variables(self):
        results = list()
        nms = list()
        for classn in self.matcher.student.student_hist['FULL']:


            # GENERAL STUDIES MATCHES
            pp = self.get_class_use_choices(classn)
    #         print classn, len(pp)
            for key, value in pp.iteritems():
                for thing in value:
    #                 print key + ' ' + ', '.join(map(str,list(thing)))
                    nms.append(key)
                    results.append(classn + ' GST ' + ':: ' + key + ':: ' + ', '.join(map(str,list(thing))))

            # EXACT MATCHES
            for classn in self.matcher.student.student_hist['FULL']:
                for i in self.matcher.matches[self.matcher.matches['FULL'] == classn]['EXACT'].values:
                    if len(i) > 0:
                        results.append(classn + ' EXT ' + ':: ' + i)

            # SUBJECT MATCHES 
            for classn in self.matcher.student.student_hist['FULL']:
                for i in self.matcher.matches[self.matcher.matches['FULL'] == classn]['SUBJECT'].values:
                    j = i.split(", ")
            #         print classn, len(j), len(i), i
                    if len(i) and len(j) > 0:
            #             print " GOOD: ", classn, len(j), len(i), i
                        for match in j:
                            results.append(classn + ' SUB ' + ':: ' + match)

            # LOWER DIVISION ELECTIVE MATCHES
            for classn in self.matcher.student.student_hist['FULL']:
                for i in self.matcher.matches[self.matcher.matches['FULL'] == classn]['LOWELECT'].values:
                    j = i.split(", ")
                    if len(i) and len(j) > 0:
                        for match in j:
                            results.append(classn + ' ELL ' + ':: ' + match)

            # UPPER DIVISION ELECTIVE MATCHES
            for classn in self.matcher.student.student_hist['FULL']:
                for i in self.matcher.matches[self.matcher.matches['FULL'] == classn]['UPELECT'].values:
                    j = i.split(", ")
                    if len(i) and len(j) > 0:
                        for match in j:
                            results.append(classn + ' ELU ' + ':: ' + match)

        return results#, nms

    def constraint_matrix(self):

        unique_classes = self.matcher.graph['CLS'].unique()
        unique_reqs = self.matcher.graph['REQ'].unique()
        uni = np.concatenate((unique_classes, unique_reqs), axis=0)

        cv = self.dv
        results = list()
        i = 1
        for desc_row in cv:
            row_res = dict( [default,0] for default in uni)
        #     print i, desc_row
            i = i + 1
            for constraint_variable in uni:
                if constraint_variable in desc_row:
                    row_res.update({ constraint_variable : 1})
            results.append(row_res)
        A = pd.DataFrame(results).T
        A.columns = cv
        return A


    def do_optimize(self,c,A_ub,b_ub):
        maximize = True

        if maximize == True:
            xy = c * -1

        res = linprog(xy, 
                      A_ub, 
                      b_ub,
                      options={"disp": False})

        if maximize == True:
            done = res.fun * -1
            
    #     print 'Obj ', done
    #     print 'Decisions ', res.x
        return res

    def build_result_graph(self):
        console = False
        df = self.constraintix.ix[1:]
        c    = np.array([x.count(', ') + 1 for x in self.dv ])
        A_ub = df #opt.constraintix
        b_ub = np.repeat(1, len( df ))

        if console:
            print 'c', c.shape, "example ", c[1:10]
            print 'A_ub', A_ub.shape, "example "
            print 'b_ub', b_ub.shape, "example "

        res = self.do_optimize(c,A_ub,b_ub)
        decided = pd.DataFrame([ self.dv, list(res.x) ]).T
        decided.columns = ['decision','io']
        result_graph = decided[decided['io'] > 0].reset_index(drop=True)
        return result_graph

    def expand_results(self,result_graph):
        rep_list = list()
        clss_list = list()
        req_list = list()
        for i in result_graph['decision']:
            rw = i.split("::")
            if len(rw) == 3:
                rx = rw[2].split(',')
            if len(rw) == 2:
                rx = rw[1].split(',')
            rep_list.append(len(rx))
            clss_list.append(rw[0])
            for i in rx:
                req_list.append(i)

        A = np.repeat(clss_list,rep_list)
        B = req_list
        C = pd.DataFrame([A,B]).T
        C.columns = ['CLS','REQ']
        C['STRREQ'] = [ int(float(i)) for i in C['REQ'] ]
        tbl = pd.merge(C, self.matcher.major_map.cleaned_major_data , how= 'left', left_on='STRREQ', right_on='REQID' )
        D = C[['CLS','REQ']]
        out = tbl[['REQ','CLS','MULT_OUTPUT_MESSAGE']]
        fin = out.drop_duplicates().reset_index(drop=True)
        return fin

    def output_graph(self):
        result_graph = self.build_result_graph()
        fin = self.expand_results(result_graph)
        percent_complete = (len(fin['REQ'].unique()) + .0) / len(self.matcher.major_map.cleaned_major_data['REQID'].unique())
        # print '\n', percent_complete * 100 , "% complete"
        return fin, percent_complete


    def missing_requirments(self):
        all_choices = self.matcher.major_map.cleaned_major_data['REQID']
        choosen = np.array([float(i) for i in self.out[0]['REQ'].unique()])
        idx = [True if choice not in choosen else False for choice in all_choices]
        abc = self.matcher.major_map.cleaned_major_data[idx][['REQID','MULT_OUTPUT_MESSAGE','REQUIREMENT_TYPE']].drop_duplicates()
        result = abc[ abc['REQUIREMENT_TYPE'].apply(lambda x: x in ['C','G','E'])].dropna()
        return result

    def missing_courses(self):
        chooen_classes = self.out[0]['CLS'].apply(lambda row: row[0:-5]).values
        idx = [classm not in chooen_classes for classm in self.matcher.student.student_hist['FULL'].values]
        results = self.matcher.student.student_hist[idx][['FULL','DESCR.y']]
        results.columns = ['FULL','GS']
        return results

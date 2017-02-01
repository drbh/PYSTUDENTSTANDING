# ANALYTIC DEGREE AUDITING Verison 0.0.1
## G.P.A (GRADUATION PROGRESS ASSESMENT)

## Data dependencies
In order for this program to run one must have static CSV files of past student data. In v0.0.1 we are not connecting to any dyanmic datasouce.

## Python dependencies
 - sys
 - re
 - web
 - subprocess
 - itertools
 - numpy
 - pandas
 - scipy.optimize

## Proof of concept

While this proof of concept is not 100% accurate yet, it provides a fast analytics based platform to build a faster degree auditing system

An innovative University like ASU will benifit greatly from building an analytic insights system for looking into students progress. 

*possible uses*

- API accessible for students to do fast audit
- - possibly serve on MYASU with course schedule
- - can power indicators like a progress bar

- API accessible for Colleges to check many students standing quickly
- - help find students near completion 
- - have near real time (weekly?) update on student progress
- - this pairs well with other indicators for understanding bottlenecks in student progress

This platform is based on optimizing a function that sums up the number of requirements that a student has completed towards their respective degree ~ or another degree (what-if)


## TO DO

### dev-ops

 - EC2 move
 - - make script take sys args
 - - add small GET response script
 - - open ports on AWS
 - - long timeout *loads data each response ~10seconds*

 - S3 data buketing - DEV
 - - boto3 integration for VPN

 - Redshift query
 - - boto3 queries?

 - Move to Lambda
 - - After datasource secured package and move to lambda

### model adjustment

 - Add elective matching decisions
 - - handle upper and lower electives
 
 - New datasoucre for student reqs?
 
 - Check out reqs that need multiple courses

### How it works

The fun part!

Overview of situation 

A student has taken classes
A major has requirments
A student graduates when they complete thier requirments
A students classes fill those requirements in many ways

A class can be a
- exact match ( the course name is explicitly provided )
- subject match ( the subject name is provided )
- general studies match ( a single or choice of general studies is provided )

not supported now:
- term match
- gpa match
- elective match ( a type of elective is provided )

First we extract the student and major map data
We have a `Student` class and a `Major` class. These classes handle subsetting the data from the static files and then cleaning the data so we can use it in the `Matcher` class. Once all of the matches are found and saved, we pass the `Matcher` object to the `Optimizer` class that expands all of the combinations of interest and does some linear optmization to find a set of class uses (applying a class to a requirement) that maximizes the number of requirements filled. So we give the student as much credit for the courses they've taken so far.

Framework considerations
We find all of the places a class can have an impact before we build the combination a class can fill. For instance a class like `TCL 314` can fill (L or SB and C and H) or (HU or SB and C and H) which when expanded has many combinations of what requirements that this class can fill. It can fill an L, C and H or a SB and C and maybe there is no open use for the H. This complexity is handled by expanding the combinations after we find the possibilies and then the optimization function solves to choose the options that best fill the requirements. This is handy because if the optimizer returns a weird solution (on that wouldnt work in reality) all we have to do is find and edit that choice before it is sent to the optimizer.

The optimization function works by expanding the expanded choices of use as stated above, and then building a matrix that has N columns as choices and M rows as a class or requirment. This is a binary matrix where a 1 is in a cell that has both similar text in the row index and the column name. So if its REQ X and this choice effect REQ X there is a 1 if not there is a 0. We then set a constraint on the operator function where each choice <= 1 so basicly it can be choosen or not. 


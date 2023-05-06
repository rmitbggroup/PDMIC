This code is the implemetation of the work "Managing Conflicting Interests of Stakeholders in Influencer Marketing" at SIGMOD 2023. 

library requirement: networkx 1.11

The main entry is in 'MPD.py'. Implementation of binary-choice based methods is in 'Binary.py' and the one of integer-choice and continuous-range based methods is in 'Flexible.py'.
Datasets are stored in the folder 'degree'.

Parameter descrpitions:

Commonly used parameters:

--degree : the path to the input dataset where each line records a number denoting the degree of an user. Default is degree/LastFM
--load : the candidate set size. Default is 90.
--dis : sampling distributions with a specific focus. Choices: Macro, Micro, Nano, Uniform.
--method : BCExact,BCMG,ICExact,CRInf,CRMWS.
--ouput : the output home folder. default is output/  . Note that only the parent holder needs to be specified and the program will automatically create subfolder and the file.


Method specific parameters:

--numPieces: the size of integer price choice set for ICExact. default is 10.
--version : 0 for float version of CRInf and 1 for integer version. default is 0.
--infmax : 0 refers to BCExact with profit minimization, and 1 refers to BCExact with influence maximization. default is 0.


Example:   python MPD.py --degree degree/LastFM --load 90 --method CRMWS --dis Macro


output file format: it consists of five lines. 
1st line: index IDs of influencers.
2nd line: influence of influencers.
3rd line: profit expectation of influences.
4th line: price of influencers.
5th line: the running time.

Different evaluations including evaluating profit divergence can be performed based on the output file.


# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 20:18:48 2021

@author: AlexGolden
"""


import subprocess
from sys import exit
import os
import stat
import numpy as np
import copy

from os.path import isfile, join


data_path='/projectnb/biophys/goldalex/rangeExpansions/roughnessRuns'
path='/projectnb2/biophys/goldalex/twitter/'

## name of code to be submitted and submission script
#file_name="asterGrowthModel.py"
file_name="get_tweets_cluster.py"

output_file="Submission_output.txt"
error_file="Submission_error.txt"

os.chdir( path )

sizes = [1000]

#params = [(0.01,0.1,80.0,10.0),(0.01,0.1,25.0,10.0),(0.01,0.1,5.0,10.0),(0.01,0.1,1.0,10.0)]
params = [(0.01,0.1,1.0,10.0)]
n_s_list=[3]
n_masked_list=[0]
sparsity_list=[0,0.5]
init_lrs = [0.01,0.001]
batch_sizes = [32,128]
depths = [4,8]

############## looping and submitting jobs #########################

st = os.stat(file_name)#### changes the file permissions just in case
os.chmod(file_name, st.st_mode | stat.S_IEXEC) 

jobname = "twitter"

#loop over inputs

subscript_str = f"""#!/bin/bash -l


#$ -t 1

echo This is getting twitter data

module load python3
module load pytorch
#$ -j y
#$ -l h_rt=72:00:00
#$ -P biophys
#$ -N twitter
#$ -o logs
python get_tweets_cluster.py
"""

            
with open('sub.sh', "w") as script:
    print(subscript_str, file = script)
    script.close()

###### FOR qsubbing the job:
qsub_command = "qsub sub.sh"
###### if you want to just run it on the cluster computer not as a submitted job
#    qsub_command = "./" + "sub.sh"
print(qsub_command)
exit_status = subprocess.call(qsub_command, shell=True)
if exit_status is 1:  # Check to make sure the job submitted
    print("\n Job {0} failed to submit".format(qsub_command))
    
#os.chdir( home )
print("Done submitting jobs!")




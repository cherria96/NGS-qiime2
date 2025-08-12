# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 12:44:16 2022

@author: Sujin
"""

import pandas as pd
import os
import numpy as np

#fastq directory
ARC = '../fastq/ARC'
BAC = '../fastq/BAC'

#metadata file creating function (requirement : sampleid, option : e.g. time)

def metadata(domain):
    categories = dict()
    n = 0
    for i in os.listdir(domain):
        if n==0:
            print(i.split('_')[0])
            print("input name of the columns with comma and without space (e.g. sampleid,time,experiment)")
            columns = input("Name of columns: ").split(',')
            n += 1
            assert len(columns) == len(i.split('_')[0].split('-')), "Number of columns must match the number of parts in sample name"        
            columns.insert(0, 'sampleid')
            categories = {col: [] for col in columns}
        if i.split('_')[3] == 'R1':
            name = i.split('_')[0]
            categories['sampleid'].append(name)
            for i,col in enumerate(columns):
                if i == 0:
                    continue
                features = name.split('-')
                categories[col].append(features[i-1])
        else: continue
    metadata = pd.DataFrame(categories)
    return metadata
domain = input("input domain that you want to create metadata for (ARC / BAC):")
if domain == "ARC":
	metadata_arc = metadata(ARC)  
	metadata_arc.to_csv('../fastq/sample-metadata-arc.tsv', sep = '\t', index = False)
elif domain == "BAC":
	metadata_bac = metadata(BAC)
	metadata_bac.to_csv('../fastq/sample-metadata-bac.tsv', sep = '\t', index = False)
else:
	print("wrong domain")

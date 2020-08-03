'''
@author: Reem Alatrash
@version: 1.0
=======================

This script converts the fine-grained POS tagset used in the KiDko corpus (extended version of STTS) to the  universal dependency tagset (UD).
For example, sentence 1 which shows the original POS tags used in KiDKo, is converted to sentence 2 which contaisn the coarse-grained tags:

1. Ich  kann   richtig gut   machen das  (En: I can do that really well)
   PPER VMFIN  ADJD    ADJD  VVINF  PDS

2. Ich  kann   richtig gut   machen das  (En: I can do that really well)
   PRON VERB   ADJ     ADJ   VERB   PRON

Tagsets References:
 - STTS: Schiller et al. (1999), Rehbein and Schalowski (2013)
 - UD: Petrov et al. (2012)

'''

'''
******* ********* *********
*******  imports  *********
******* ********* *********
'''
import csv
import os
import codecs
from docopt import docopt
import pandas as pd
import numpy as np

def main():
   
    data_path = "/mount/studenten/projects/alatrarm/thesis/Corpora/kidko2.0/kidko-augmented.conll"
    map_path = "/mount/studenten/projects/alatrarm/thesis/Corpora/tiger-universal.map"
    out_path = "/mount/studenten/projects/alatrarm/thesis/Corpora/kidko2.0/kidko-augmented-coarse.conll"

    # Get the arguments as global variables
    args = docopt("""
    Usage:
        get_coarse_pos_kidko.py <data_dir> <map_path> <output_dir>

    Arguments:
        <data_dir> = path to directory containing interview files
        <map_path> = path to POS tags mapping file
        <output_dir> = path to output directory 
    """)
    
    data_path = args['<data_dir>']
    map_path = args['<map_path>']
    out_path = args['<output_dir>']
    
    # load tagset mapping file into a dictionary
    mapping = {}
    with codecs.open(map_path, 'r') as map_file:
        for line in map_file:
            (key, val) = line.rstrip().split("\t")
            mapping[str(key)] = str(val)

    #print(mapping)
             
    # read tab-seperated file into pandas dataframe  
    interview_df = pd.read_csv(data_path, sep='\t', encoding='utf-8')
    # remove empty lines which are now NAN
    interview_df.dropna(how="all", inplace=True)    

    # replace all fine-grained POS tags with coarse grained ones and keep the non-standard tags which don't have a mapping to the universal tagset
    # interview_df['pos'].map(mapping).fillna(interview_df['pos']) <-- no inplace parameter
    interview_df['pos'].replace(mapping, inplace=True)

    # split into sentences based on new sentence markers
    sentence_df_list = np.split(interview_df, interview_df[interview_df['token'] == "<SOS>"].index)
    print(len(sentence_df_list)) 
    output_file =  codecs.open(out_path, 'w+', 'utf-8')
    add_header = True
    
    # loop over sentences in file and save them
    for df in sentence_df_list[1:]:
        
        # add header before the first dataframe/sentence
        if add_header:
            df.to_csv(output_file, sep='\t', encoding='utf-8',index=False)
            add_header = False
        else:    
            # write dataframe/sentence to file
            df.to_csv(output_file, sep='\t', encoding='utf-8',index=False, header=None) 
        # add empty line
        output_file.write("\n") 
    output_file.close()       

          
if __name__ == "__main__":
   main()

'''
@author: Reem Alatrash
@version: 1.0
=======================

This script samples n rows from given files using pandas
(simple random sampling without replacement)

'''

'''
******* ********* *********
*******  imports  *********
******* ********* *********
'''
import csv
import os
import codecs
import logging
import time
from docopt import docopt
import pandas as pd
import numpy as np


def human_format(num):
    ''' Represents numbers in human readable format.
        Example: 3000 ---> 3K
    '''
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

def main():
    
    # add some logging information
    logging.basicConfig(filename= "../../Corpora/Exp1/" + 'log_' + 'sample' + '.txt', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    start_time = time.time()
    
    pd.options.mode.chained_assignment = None
    sample_size = 100
    corpus_type = "none"
    
    # Get the arguments
    logging.info("Reading given arguments")
    args = docopt("""
    Usage:
        sample_data.py <data_dir> <ngram_size> <sample_size> <no_of_samples> <output_dir>

    Arguments:
        <data_dir> = path to input file
        <ngram_size> = size of ngram
        <sample_size> = number of rows to extract
        <no_of_samples> =  number of samples to extract
        <output_dir> = path to output directory
    """)
    
    
    data_path = args['<data_dir>']
    n_rows = args['<sample_size>']
    ngram_size = args['<ngram_size>']
    n_samples = args['<no_of_samples>']
    output_path = args['<output_dir>']
    
    # append an / to the end of given paths if it's missing
    data_path = os.path.join(data_path, '')
    output_path = os.path.join(output_path, '')
    
    # convert sample size to integer value
    try:
        sample_size = int(n_rows)
        n_samples = int(n_samples)
    except:
        logging.info("invalid sample size, sampling with size (row-count/2)")
        sample_size = -1
        n_samples = 1
        pass    
    
    # get corpus type
    if "kidko" in data_path.lower():
        corpus_type = "kidko"
    else:
        corpus_type = "grain"
    
    # open input file and load it into memory as a pandas dataframe
    input_df = pd.read_csv(data_path, sep='\t', encoding='utf-8')
    
    # if input sample size is invalid then sample half the number of rows
    row_count = input_df.shape[0]
    if sample_size == -1:
        sample_size = int(row_count/2)
    logging.info("sampling size={}".format(sample_size))
    
    # ignore special POS tag DINGS in unigram models
    df1 = input_df[~input_df['pos_seq'].str.contains('DINGS')]
    df = df1[~df1['pos_seq'].str.contains('X')]
    # ~ print(df.head())
    # draw x samples of size n
    merged = "-merged" if "merge" in data_path else ""
    
    for i in range(n_samples):
        
        # shuffle data
        df = df.sample(frac=1).reset_index(drop=True)
        
        # use random_state to ensure the reproducibility of the extracted samples
        # random_state  = Seed for the random number generator (if int), or numpy RandomState object.
        output_df = df.sample(n=sample_size, random_state=i*2)
        
        # write to file
        output_file = os.path.join(output_path, "sample-{}-{}-{}-{}{}.tsv".format(corpus_type, ngram_size, human_format(sample_size), i+1, merged))
        output_df.to_csv(output_file, sep='\t', encoding='utf-8',index=False)
    
    # done processing, add final details in the log
    logging.info("done")
    logging.info("--- {} seconds ---".format(time.time() - start_time)) 
      
if __name__ == "__main__":
   main()
    

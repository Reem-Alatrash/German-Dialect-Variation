'''
@author: Reem Alatrash
@version: 1.0
=======================

This script computes the following statistics for POS ngrams in the given corpus:
1. Raw frequency (count).
2. Relative frequency.
3. Unique speaker count (no. of speakers who produce this pos ngram)
4. Dissemination per pos ngram which measure how popular/used an ngram is in the corpus.

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
from functools import reduce

def main():
   
    data_path = "/mount/studenten/projects/alatrarm/thesis/Corpora/kidko2.0/"
    out_path = "/mount/studenten/projects/alatrarm/thesis/Corpora/kidko2.0/"

    # Get the arguments as global variables
    args = docopt("""
    Usage:
        get_ngram_stats.py <data_file> <ngram_type> <ngram_size> <output_dir>

    Arguments:
        <data_file> = path to ngram file
        <ngram_type> =  type of ngram | token or pos
        <ngram_size> =  size of ngram | numeric
        <output_dir> = path to output directory 
    """)
    
    data_file = args['<data_file>']
    ngram_type = args['<ngram_type>']
    ngram_size = args['<ngram_size>']
    out_path = args['<output_dir>']
    
    '''
    # STEP 1: read tab-seperated files into pandas dataframe
    '''
    # sentence level data to get the total #speakers in corpus
    df = pd.read_csv(data_file, sep='\t', encoding='utf-8')
 
    '''
    # STEP 2: get counts and compute statistics
    '''
    # normalize token ngrams before counting
    df["norm_ngram"] = df["ngram"].str.lower()
    
    col_name = "norm_ngram" if ngram_type.lower() == "token" else "pos_seq"
    # get raw frequency or count per ngram
    raw_freq_df = df[col_name].value_counts().to_frame().reset_index()
    # get relative frequency (count/no. ngram in corpus)
    rel_freq_df = df[col_name].value_counts(normalize=True).to_frame().reset_index()
        
    # give meaningful column names
    raw_freq_df = raw_freq_df.rename(columns={"index":col_name, col_name:"raw_freq"})
    rel_freq_df = rel_freq_df.rename(columns={"index":col_name, col_name:"rel_freq"})
    
    # get unique speakers per ngram
    speakers_df= df.groupby(col_name).speaker.nunique().to_frame().reset_index()
    
    speakers_df = speakers_df.rename(columns={"speaker":"unique_speakers"})
    # get no. of speakers per corpus
    total_speakers = df.speaker.nunique() 
    
    print(raw_freq_df.head())
    print(rel_freq_df.head())
    print(speakers_df.head())
    
    # merge dfs
    data_frames = [raw_freq_df, rel_freq_df,speakers_df]
    counts_df = reduce(lambda  left,right: pd.merge(left,right,on=col_name,
                                            how='outer'), data_frames)
    
    # Dissemination per ngram
    # uniq-spkrs-per-ngram/corpus-speakers X (1-rel_freq)  [weighting by inverse of rel freq is optional]
    counts_df["dissemination"] = counts_df["unique_speakers"]/total_speakers
    # weighted dissemination
    counts_df["w_dissemination"] = (counts_df["unique_speakers"]/total_speakers) * (1-counts_df["rel_freq"])
    
    print(counts_df.head())
    
    '''
    # STEP 4: save stats to file  
    '''
        
    # save to file
    corpus = "grain" if "grain" in data_file else "kidko"
    is_coarse = "_coarse" if "coarse" in data_file else ""
    output_file = os.path.join(out_path, "{}_{}{}_{}_grams_freqs.tsv".format(corpus,ngram_type,is_coarse,ngram_size))
    counts_df.to_csv(output_file, sep='\t', encoding='utf-8',index=False)
    
    '''
    # STEP 4: add freq stats to each ngram instance and save to file 
    '''
    merged_df = pd.merge(df[['pos_seq','ngram','speaker', 'sentence_length']], counts_df, on="pos_seq")
    
    if corpus == "kidko":
        merged_df["corpus_type"] = 1
    else:
        merged_df["corpus_type"] = 0
    
    # save to file
    output_file = os.path.join(out_path, "{}_{}_grams_{}.tsv".format(corpus, ngram_size,ngram_type))
    merged_df.to_csv(output_file, sep='\t', encoding='utf-8',index=False)
    

if __name__ == "__main__":
   main()

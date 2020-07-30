'''
@author: Reem Alatrash
@version: 1.0
=======================

This script extracts n-grams from given corpus.

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
import general_utility

gender_map = {"f":"-1", "m":"1", "u":"2"}
tags_to_lexicalize = set(["NOUN","VERB","ADV","ADJ"])

def add_to_map(key, val, mapping):
    '''
    adds a key and int value to a dictionary
    '''
    val +=1
    mapping[key] = val
    return val

def main():
    
    # add some logging information
    logging.basicConfig(filename= 'log_get-n-grams.txt', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    start_time = time.time()
    
    data_path = "/mount/studenten/projects/alatrarm/thesis/Corpora/kidko2.0/kidko-augmented.conll"
    map_path = "/mount/studenten/projects/alatrarm/thesis/Corpora/comparison/tiger-universal.map"
    
    # Get the arguments 
    logging.info("Reading given arguments")
    args = docopt("""
    Usage:
        generate_ngrams.py <data_dir> <corpus_name> <ngram_size> <remove_markers> <tag_to_lexicalize> <output_dir>

    Arguments:
        <data_dir> = path to CONLL file
        <corpus_name> =  name of corpus
        <ngram_size> = size of ngram
        <remove_markers>  = remove sentence markers? accepts either T for True or F for False
        <tag_to_lexicalize> = POS tag to be lexicalized
        <output_dir> = path to output directory
    """)
    
    data_path = args['<data_dir>']
    corpus_name = args['<corpus_name>']
    ngram_size = int(args['<ngram_size>'])
    remove_markers = True if args['<remove_markers>'].lower() == 't' else False
    tag2lex = args['<tag_to_lexicalize>']
    out_path = args['<output_dir>']
    # append an / to the end of given paths if it's missing
    if os.path.isdir(data_path):
        data_path = os.path.join(data_path, '')
    if os.path.isdir(out_path):
        out_path = os.path.join(out_path, '')
    
    # check if POS tags of sentence markers are merged with others
    is_merged = True if "merge" in data_path else False

    # ~ # add poistional mapping using a map
    # ~ # load tagset mapping file into a dictionary
    # ~ mapping = {}
    # ~ i = 0
    # ~ with codecs.open(map_path, 'r') as map_file:
        # ~ for line in map_file:
            # ~ coarse_pos = line.rstrip().split("\t")[1]
            # ~ if is_merged:
                # ~ pos_s  = "SOS_{}".format(coarse_pos)
                # ~ if pos_s not in mapping:
                    # ~ pos_m  = "{}_MID".format(coarse_pos)
                    # ~ pos_e  = "{}_EOS".format(coarse_pos)
                    # ~ next_i = i+ 1
                    # ~ next_i = add_to_map(pos_s, next_i, mapping)
                    # ~ next_i = add_to_map(pos_m, next_i, mapping)
                    # ~ i = add_to_map(pos_e, next_i, mapping)
            # ~ else:
                # ~ if coarse_pos not in mapping:
                    # ~ i+= 1
                    # ~ mapping[coarse_pos] = i
    # ~ print(mapping)    
        
    # open CONLL file and generate n-grams then save data in new file 
    input_df = pd.read_csv(data_path, sep='\t', encoding='utf-8')
    # filter for sentences of at least length n (size of ngrams)
    input_df.drop(input_df[input_df['sentence_length'] < ngram_size].index, inplace=True) 
    
    if corpus_name.lower() == "grain":
        input_df["isKD"] = 0
   
    # split into sentences based on new sentence markers
    sentence_df_list = [] 
    if is_merged:
        # drop empty lines which are now filled with NaN
        input_df.dropna(how="all", inplace=True)
        input_df.reset_index(drop=True,inplace=True)
        sentence_df_list = np.split(input_df, input_df[input_df.pos.str.contains("SOS")].index)
    elif corpus_name.lower() == "grain":
        sentence_df_list = np.split(input_df, input_df[input_df['sentIdx'] == 0].index)
    else:
        sentence_df_list = np.split(input_df, input_df[input_df['token'] == "<SOS>"].index) 
    
    row_list = []
   
    # for each sentence get all tagged n-grams
    for df1 in sentence_df_list:
        
        # skip empty dataframes
        if df1.empty:
            continue
            
        # ~ print(df1.head())
        
        # drop empty lines which are now filled with NaN
        df1.dropna(how="all", inplace=True)
        df = df1
       
        # remove sos and eos sentence markers
        if remove_markers:
            tok_markers = ["<SOS>", "<EOS>"]
            df = df1[~df1.token.isin(tok_markers)]
        
        # get lists of lemmas and POS
        lemmas = df.lemma.tolist()
        pos_tags = df.pos.tolist()
        
        # replace pos tags with their corresponding lemma if the tag is to be lexicalized
        for i in range(len(pos_tags)):
            if pos_tags[i].lower() == tag2lex.lower():
                pos_tags[i] = lemmas[i]
                    
        # generate ngrams
        tok_pos_pairs = list(zip(df.token, pos_tags))
        n_grams = general_utility.get_n_grams(tok_pos_pairs, ngram_size)
        for gram in n_grams:
            
            if gram == "ADV X ADV":
                print(df1['full_sentence'].iloc[0])
             
            # create row and add it to list of rows
            toks, pos = zip(*list(gram))
            toks = list(str(x) for x in toks)
            pos = list(str(x) for x in pos)
            row = {"ngram": " ".join(toks).strip(),"pos_seq":" ".join(pos).strip(), "full_sentence": df['full_sentence'].iloc[0], "fileName":df.fileName.iloc[0],
                    "speaker": df.speaker.iloc[0], "sentence_length":df['sentence_length'].iloc[0], "isKD":df.isKD.iloc[0]}
            row_list.append(row)
    
    # create dataframe from the rows
    df=pd.DataFrame(row_list, columns=["ngram","pos_seq","full_sentence","fileName","speaker", "sentence_length", "isKD"])
    
    # split pos sequence into columns of length n (ngram size)
    pos_cols = df['pos_seq'].str.split(' ',expand=True).add_prefix('pos_')
    
    # ~ # code pos tags into numbers
    # ~ pos_cols.replace(mapping, inplace=True)
    # ~ print(pos_cols.head())
 
    df = pd.concat([df,pos_cols],axis=1)
   
    # write to file
    coarse = "_coarse" if "coarse" in data_path else ""
    markers = "_no_markers" if remove_markers else ""
    merged = "_merged" if is_merged else ""
    output_file = os.path.join(out_path, "{}_{}_grams{}{}{}_lexicalized_{}.tsv".format(corpus_name, ngram_size, coarse, markers, merged, tag2lex.lower()))
    df.to_csv(output_file, sep='\t', encoding='utf-8',index=False)
    
    # done processing, add final details in the log
    logging.info("done")
    logging.info("--- {} seconds ---".format(time.time() - start_time))     
        
if __name__ == "__main__":
   main()

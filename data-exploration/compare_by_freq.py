'''
@author: Reem Alatrash
@version: 1.0
=======================

This script plots a frequency comparison between the token/pos Ngrams of the corpora. 
The resulting bar plot can show either raw frequency or relative frequency (scaled by 1 million) depending on the passed arguments.

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
from nltk import ngrams
from collections import Counter, OrderedDict
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

ngram_size_map = {"1":"Unigram","2":"Bigram", "3":"Trigram"}

def plot_col_comparison(ngram_df, out_path, ngram_type, ngram_size,is_coarse, col_name, freq_name):
    '''
    creates a bar plot comparison
    '''
    
    # use the same colors for each corpus regardless of the values 
    # https://stackoverflow.com/questions/46173419/seaborn-change-bar-colour-according-to-hue-name
    my_palette = {"KiDKo":"C0","GRAIN":"C1"}
    
    # reset index to make it a column and force the plot to use the index to order values instead of alphabet
    # draw plot
    my_plot = sns.catplot(y=col_name, x=freq_name, kind="bar", hue="corpus",
    data=ngram_df, palette = my_palette)
      
    # ~ # rotate x-axis labels to make them readable
    # ~ my_plot.set_xticklabels(rotation=90)
    
    # add comma after thousands in y-axis values
    for ax in my_plot.axes[0]:
        ax.xaxis.set_major_formatter(tkr.EngFormatter())
    
    # edit axes names and title
    ylab = "{} {} Type".format(ngram_type,ngram_size_map[ngram_size])
    xlab = "Raw Frequency" if freq_name == "raw_freq" else "Relative Frequency"
    my_plot.set(xlabel=xlab,ylabel=ylab)
    # ~ plt.ylabel("Frequency",weight='bold')
    # ~ plt.xlabel("POS Tag",weight='bold')
    
    # set plot size
    if not is_coarse:
        s = 10
        my_plot.fig.set_size_inches(s,s)
    
    # save plot as pdf
    fname = "{}{}_{}_comparison_plot_{}.pdf".format(ngram_type.lower(),is_coarse,ngram_size.lower(), freq_name)
    fig_path = os.path.join(out_path, fname)
    plt.savefig(fig_path,bbox_inches='tight')

def main():

    # Get the arguments as global variables
    args = docopt("""
    Usage:
        compare_by_freq.py <kd_path> <sg_path> <ngram_type> <ngram_size> <freq_type> <output_dir>
            
    Arguments:
        <kd_path> = path to Kidko file
        <sg_path> =  path to grain file
        <ngram_type> =  type of ngram | token or pos
        <ngram_size> =  size of ngram | numeric
        <freq_type> =  type of frequency | raw or relative
        <output_dir> = path to output directory 
    """)
    
    kd_path = args['<kd_path>']
    sg_path = args['<sg_path>']
    ngram_type = args['<ngram_type>']
    ngram_size = args['<ngram_size>']
    freq_type = args['<freq_type>']
    out_path = args['<output_dir>']
   
    # read tab-seperated file into pandas dataframe
    kd_df = pd.read_csv(kd_path, sep='\t', encoding='utf-8')
    kd_df["corpus"] = "KiDKo"
    sg_df = pd.read_csv(sg_path, sep='\t', encoding='utf-8')
    sg_df["corpus"] = "GRAIN"
    
    
 
    '''
      bar plot comparison
    '''
    
    # set column name to match infile name
    col_name = "norm_ngram" if ngram_type.lower() == "token" else "pos_seq"
    # set freq column name to match infile name
    freq_name = "raw_freq"
    if freq_type.lower() == "relative":
        
        freq_name = "rel_freq"
        
        # scale relative frequency ==> multiply it by 1M
        kd_df["rel_freq"] *= 1000000
        sg_df["rel_freq"] *= 1000000
    
    # if token ngram or pos ngram > 1, get top 10
    n = 10
    top_list = []
    df = pd.concat([kd_df,sg_df], ignore_index=True)
    
    is_coarse = "_coarse" if "coarse" in kd_path else ""
    
    # check if n-gram has too many levels and get top 10
    is_ngram_high = True
    if is_coarse and int(ngram_size) == 1:
        is_ngram_high = False
    
    if ngram_type.lower() == "token" or is_ngram_high:
        # order KiDKo by frequency
        kd_df.sort_values(by=[freq_name], inplace=True, ascending=False)
        # get top n
        top_kd = kd_df.head(n)        
        top_list = top_kd[col_name].tolist()
        # get these top n from grain
        top_grain = sg_df[sg_df[col_name].isin(top_list)]
        df = pd.concat([top_kd,top_grain], ignore_index=True, sort=True)

    # order merged by frequency
    # ~ df.sort_values(by=[freq_name], inplace=True, ascending=False)
    
    # plot them
    plot_col_comparison(df,out_path, ngram_type, ngram_size,is_coarse, col_name, freq_name)    
   
    
if __name__ == "__main__":
   main()

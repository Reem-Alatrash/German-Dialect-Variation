 '''
@author: Reem Alatrash
@version: 1.0
=======================

This script creates a boxplot comparing the sentence length in both corpora specified in the arguments.
It also zooms in on the KiDKo box to improve visual reading of the values.

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

def main():
   
    data_path = "/mount/studenten/projects/alatrarm/thesis/Corpora/kidko2.0/"
    out_path = "/mount/studenten/projects/alatrarm/thesis/Corpora/kidko2.0/"

    # Get the arguments as global variables
    args = docopt("""
    Usage:
        plot_sentence_length.py <kd_file> <sg_file> <output_dir>

    Arguments:
        <kd_file> = path to directory containing KiDKo file
        <sg_file> =  path to directory containing GRAIN file
        <output_dir> = path to output directory 
    """)
    
    kd_file_path = args['<kd_file>']
    sg_file_path = args['<sg_file>']
    out_path = args['<output_dir>']
    
    # read tab-seperated file into pandas dataframe
    kd_df = pd.read_csv(kd_file_path, sep='\t', encoding='utf-8')
    kd_df["corpus"] = "KiDKo"
    sg_df = pd.read_csv(sg_file_path, sep='\t', encoding='utf-8')
    sg_df["corpus"] = "GRAIN"
    all_df = pd.concat([kd_df,sg_df])

    # draw box plot via grouping data by corpus type in order to compare both corpora
    sns.set_style("whitegrid")
    my_plot = sns.boxplot(x="corpus", y="length", data=all_df, showmeans=True, meanline=True, whis="range")
    ptitle ="Sentence Length Comparison"
    my_plot.set(title="",xlabel='Corpus',ylabel='Sentence Length')
    
    # add zoom in subplot in the top right area
    # 222 means 2x2 plot in 2nd position (top righ)
    # https://stackoverflow.com/questions/3584805/in-matplotlib-what-does-the-argument-mean-in-fig-add-subplot111
    ax2 = plt.axes([0.22, 0.5, .2, .25]) # left, bottom, width, height (range 0 to 1)
    z2 = sns.boxplot(x="corpus", y="length", data=kd_df,ax=ax2, showmeans=True, meanline=True, whis="range")
    z2.set_title('zoom')
    z2.set_xticks([])
    z2.set(xlabel=None)
    z2.set(ylabel=None)
    ax2.set_ylim([0,4])
    
    # save plot as pdf
    fig_path = os.path.join(out_path, "boxplot_comaprison_sent_len.pdf")
    plt.savefig(fig_path)
 
if __name__ == "__main__":
   main()

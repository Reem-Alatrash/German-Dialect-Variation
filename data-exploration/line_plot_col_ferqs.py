'''
@author: Reem Alatrash
@version: 1.0
=======================

This script plots the ranked frequencies (raw or relative) of token/pos Ngrams in the corpora. 
The resulting line plot zooms in on the middle are of the zipfian curve to show the real values.


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
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

def main():
    
    # initialize some variables
    kd_data = "/mount/studenten/projects/alatrarm/thesis/Corpora/Exp1/kidko/kidko_pos_trigram_counts_coarse_no_markers_freq_stats.tsv"
    sg_data = "/mount/studenten/projects/alatrarm/thesis/Corpora/Exp1/grain/grain_pos_trigram_counts_coarse_no_markers_freq_stats.tsv"
    out_path = "/mount/studenten/projects/alatrarm/thesis/Corpora/Exp1/"
    
    ngram_size_map = {"1":"Unigram","2":"Bigram", "3":"Trigram"}
    
    '''
    # STEP 1: read given arguments
    '''

    args = docopt("""
    Usage:
        line_plot_col_ferqs.py <kd_data> <sg_data> <col_name> <ngram_size> <freq_type> <output_dir>

    Arguments:
        <kd_data> = path to Kidko ngram file
        <sg_data> =  path to grain ngram file
        <col_name> = name of column to be plotted (token or pos ngram)
        <ngram_size> = size of ngram
        <freq_type> =  type of frequency | raw or relative
        <output_dir> = path to output directory 
    """)
      
    kd_data = args['<kd_data>']
    sg_data = args['<sg_data>']
    col_name = args['<col_name>']
    ngram_size = args['<ngram_size>']
    freq_type = args['<freq_type>']
    out_path = args['<output_dir>']
    
    '''
    # STEP 2: load tab-seperated files into memonry as pandas dataframe
    '''
    
    # read tab-seperated file into pandas dataframe
    kd_df = pd.read_csv(kd_path, sep='\t', encoding='utf-8')
    kd_df["corpus"] = "KiDKo"
    sg_df = pd.read_csv(sg_path, sep='\t', encoding='utf-8')
    sg_df["corpus"] = "GRAIN"
    
    # ~ print(kd_df.head())
    # ~ print(sg_df.head())
    
    # reset index to create rank column
    kd_df.reset_index(inplace=True)
    kd_df = kd_df.rename(columns={"index":"rank"})
    kd_df["rank"] += 1
    
    sg_df.reset_index(inplace=True)
    sg_df = sg_df.rename(columns={"index":"rank"})
    sg_df["rank"] += 1

    '''
    # STEP 3: draw plot
    '''
    
    # ~ sns.set_style("whitegrid")
    fig = plt.figure()
    
    # prepare axes names before plotting
    ngram_type = "Token" if col_name == "token" else "POS"
    freq_name = "raw_freq" if freq_type.lower() == "raw" else "rel_freq"
    y_lab = "{} {} Rank".format(ngram_type, ngram_size_map[ngram_size])
    x_lab = "Raw Frequency" if freq_name == "raw_freq" else "Relative Frequency"
    
    # plot
    ax = sns.lineplot(x="rank", y=freq_name, data=kd_df)
    sns.lineplot(x="rank", y=freq_name, data=sg_df)
    
    # set title
    plt.title('')
    # Set x-axis label
    plt.xlabel(x_lab)
    # Set y-axis label
    plt.ylabel(y_lab)
    fig.legend(labels=['KidKo','GRAIN'])
    
    # format x axis numbers to be human readable e.g. 1k instead of 1000
    ax.xaxis.set_major_formatter(tkr.EngFormatter())
    # format y axis numbers to be human readable e.g. 1k instead of 1000
    ax.yaxis.set_major_formatter(tkr.EngFormatter())
    
    is_coarse = "_coarse" if "coarse" in kd_data else ""
    # check if n-gram has too few levels
    is_ngram_high = True
    if not is_coarse and int(ngram_size) == 1:
        is_ngram_high = False
    
    if col_name == "token" or is_ngram_high:
        # add zoom in subplot in the top right area
        # 222 means 2x2 plot in 2nd position (top righ)
        # https://stackoverflow.com/questions/3584805/in-matplotlib-what-does-the-argument-mean-in-fig-add-subplot111
        ax2 = plt.axes([0.5, 0.5, .3, .3]) # left, bottom, width, height (range 0 to 1)
        z2 = sns.lineplot(x="rank", y=freq_name, data=kd_df[499:9999],ax=ax2)
        sns.lineplot(x="rank", y=freq_name, data=sg_df[499:9999],ax=ax2)
        z2.set_title('zoom')
        z2.set(xlabel=None)
        z2.set(ylabel=None)
        # format x axis numbers to be human readable e.g. 1k instead of 1000
        ax2.xaxis.set_major_formatter(tkr.EngFormatter())

    # save file to disk
    fname = "{}_{}_line_plot_with_zoom_{}.pdf"
    fig_path = os.path.join(out_path, fname.format(col_name, ngram_size, freq_name))
    plt.savefig(fig_path)
    

if __name__ == "__main__":
   main()

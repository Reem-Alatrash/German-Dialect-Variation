########################################################################
##########################   Exp1: GLMMS   #############################
########################################################################

getwd()
# setwd("D:/Uni-Stuttgart/thesis/Corpora/Exp1/samples/")
setwd("/mount/studenten/projects/alatrarm/thesis/Corpora/Exp1/")
getwd()

# load libs
library(lsr)
library(ggplot2)  # load the package

##STEP 0: set gloabal option to ignore scientific notation (numbers with E at the end)
options(scipen = 999)

## STEP 1: Load data frames
library(readr)
sample.grain.100k <- read.delim("samples/sample-grain-trigrams-100K-1.tsv", encoding="UTF8")

sample.kidko.100k <- read.delim("samples/sample-kidko-trigrams-100K-1.tsv", encoding="UTF8")

## STEP 1: Concatenate data frames
# STEP 1.1 use row bind | requires both dataframes to have the same columns
data.200k.sampled.df <- rbind(sample.grain.100k, sample.kidko.100k)

# STEP 1.2 shuffle rows 
# By default sample() randomly reorders the elements passed as the first argument. 
# This means that the default size is the size of the passed array. 
# Passing parameter replace=FALSE (the default) to sample(...) 
# ensures that sampling is done without replacement which accomplishes a row wise shuffle.
data.200k.sampled.df <- data.200k.sampled.df[sample(nrow(data.200k.sampled.df)),]

# STEP 1.3 factor our predictors and outcome
data.200k.sampled.df$pos_seq <- factor(data.200k.sampled.df$pos_seq)


svg(filename = 'output/pos-trigram-rel-freq.svg')
plot(x = data.200k.sampled.df$pos_seq,
     y = data.200k.sampled.df$rel_freq,
     main="", 
     xlab="POS trigram", 
     ylab="Relative Frequency",
     pch =23)
dev.off()

#Create a df for freq and means of norms and clusters
corr_colums <- data.frame(as.numeric(data.200k.sampled.df$pos_seq), data.200k.sampled.df$rel_freq, data.200k.sampled.df$prominence,
                          data.200k.sampled.df$dissemination, data.200k.sampled.df$w_dissemination)
cor(corr_colums, method = "spearman")

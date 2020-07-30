########################################################################
##########################   Exp1: GLMMS   #############################
########################################################################

getwd()
# setwd("D:/Uni-Stuttgart/thesis/Corpora/Exp1/samples/")
setwd("/mount/studenten/projects/alatrarm/thesis/Corpora/Exp1/")
getwd()

# load libs
library(lsr)
library(lme4)
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

# check how many levels/unique values we have for our predictor
length(unique(data.200k.sampled.df[["pos_seq"]]))

# STEP 1.3 factor our predictors and outcome
data.200k.sampled.df$pos_seq <- factor(data.200k.sampled.df$pos_seq)
lvls <- levels(data.200k.sampled.df$pos_seq)
# save factor to label mapping
write.table(lvls, file = "output/trigrams-200k-dummy-ngram-levels.csv", sep = "\t")

# STEP 3 create POSt model and compare to previous model

# use family=binomial to turn our factor columns into numerical values
start_time <- Sys.time()

POSt.glm <- glm(corpus_type ~ pos_seq + rel_freq + prominence + dissemination + w_dissemination, family = "binomial", data = data.200k.sampled.df)

end_time <- Sys.time()
total_time <- end_time - start_time
print(total_time)

# STEP 3.2 analyze model
# STEP 3.2.1 summary of the model
model.summary <- summary(POSt.glm)
model.summary

# STEP 3.2.2 save the coefficients/results of the model
model.summary.coeff <- model.summary$coef
write.table(model.summary.coeff, file = "output/trigrams-200k-dummy-coeff.csv", sep = "\t")

# detect multicollinearity in the regression model
library(car)
mult <- car::vif(POSt.glm)
print(mult)

#Create a df for freq and means of norms and clusters
corr_colums <- data.frame(data.200k.sampled.df$rel_freq, data.200k.sampled.df$prominence,
                          data.200k.sampled.df$dissemination, data.200k.sampled.df$w_dissemination)
cor(corr_colums, method = "spearman")

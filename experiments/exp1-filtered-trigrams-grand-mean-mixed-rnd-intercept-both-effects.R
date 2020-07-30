########################################################################
##########################   Exp1: GLMMS   #############################
########################################################################

getwd()
setwd("D:/Uni-Stuttgart/thesis/Corpora/Exp1")
#setwd("/mount/studenten/projects/alatrarm/thesis/Corpora/Exp1/")
getwd()

# load libs
library(lsr)
library(lme4)
library(ggplot2)  # load the package

##STEP 0: set gloabal option to ignore scientific notation (numbers with E at the end)
options(scipen = 999)

## STEP 1: Load data frames
library(readr)
sample.grain.50k <- read.delim("samples/sample-grain-trigrams-52.9K-1.tsv", encoding="UTF8")

sample.kidko.50k <- read.delim("kidko/kidko_trigram_coarse_no_markers_freq_stats_filtered.tsv", encoding="UTF8")

## STEP 1: Concatenate data frames
# STEP 1.1 use row bind | requires both dataframes to have the same columns
data.100k.sampled.df <- rbind(sample.grain.50k, sample.kidko.50k)

# STEP 1.2 shuffle rows 
# By default sample() randomly reorders the elements passed as the first argument. 
# This means that the default size is the size of the passed array. 
# Passing parameter replace=FALSE (the default) to sample(...) 
# ensures that sampling is done without replacement which accomplishes a row wise shuffle.
data.100k.sampled.df <- data.100k.sampled.df[sample(nrow(data.100k.sampled.df)),]

print(length(unique(data.100k.sampled.df[["pos_seq"]])))

# STEP 1.3 factor our predictors and outcome
data.100k.sampled.df$pos_seq <- factor(data.100k.sampled.df$pos_seq)
lvls <- levels(data.100k.sampled.df$pos_seq)
# save factor to label mapping
write.table(lvls, file = "output/filtered-trigrams-grand-mean-ngram-levels-mixed-rnd-intercept.csv", sep = "\t")

data.100k.sampled.df$speaker <- factor(data.100k.sampled.df$speaker)
spkr_lvls <- levels(data.100k.sampled.df$speaker)
# save factor to label mapping
write.table(spkr_lvls, file = "output/filtered-trigrams-grand-mean-spkr-levels-mixed-rnd-intercept.csv", sep = "\t")
data.100k.sampled.df$ngram <- factor(data.100k.sampled.df$ngram)


# STEP 2 create POSt model and compare to previous model
# set contrast to "contr.sum"
# sum contrasts compare the mean of each group\level to the grand mean/mean of all levels
# https://stats.idre.ucla.edu/r/library/r-library-contrast-coding-systems-for-categorical-variables/#DEVIATION
# see novarro book p.536  
# contrasts(data.100k.sampled.df$pos_seq) <- "contr.sum"
my.contrasts <- list(pos_seq = contr.sum)

# use family=binomial to turn our factor columns into numerical values
# to allow the glmer to converge, set maximal number of iterations using optCtrl
# (BOBYQA optimizer recommends at least 100,000 iterations)
# 100k = 1e5 in scientific notation, don't try more since we don't have more than 100k rows
# nAGQ specifies the type of approximation or smoothing to perform, default is 1 meaning Laplace

start_time <- Sys.time()

# use random intercepts, meaning that the effect of speaker should be the same for each spoken ngram
POSt.glmer <- glmer(corpus_type ~ 1 + pos_seq + (1|speaker)  + (1|ngram), contrasts = my.contrasts,
                  family = "binomial", data = data.100k.sampled.df, nAGQ=0,
                  glmerControl(optimizer="bobyqa", optCtrl = list(maxfun = 1e5)))

end_time <- Sys.time()
total_time <- end_time - start_time
print(total_time)

# STEP 2.2 analyze model
# STEP 2.2.1 summary of the model
model.summary <- summary(POSt.glmer)
print(model.summary)

vcov(model.summary)
options(max.print=100000)
print(model.summary, correlation=TRUE)

#save to rda file
save(POSt.glmer, file = "output/filteredTriGlmer.rda")

# STEP 2.2.2 save the coefficients/results of the model
model.summary.coeff <- model.summary$coef
write.table(model.summary.coeff, file = "output/filtered-trigrams-grand-mean-coeff-mixed-rnd-intercept.csv", sep = "\t")

# STEP 3.3 Perform Optimizer Checks
#library(optimx)
#library(dfoptim)

# get no. of cores 
#library(parallel)
#ncores <- detectCores()

# use method allFit from lme4
# tries to fit the model using various optimizers
#diff_optims <- allFit(POSt.glmer, maxfun = 1e5, parallel = 'multicore', ncpus = ncores)

# print warning messages (if present) for each optimizer
#is.OK <- sapply(diff_optims, is, "merMod")
#diff_optims.OK <- diff_optims[is.OK]
#lapply(diff_optims.OK,function(x) x@optinfo$conv$lme4$messages)

# results from all optmizers
#ss <- summary(diff_optims)
#ss$fixef               ## extract fixed effects
#write.table(ss$fixef, file = "output/filtered-trigrams-grand-mean-fixef-mixed-rnd-intercept.csv", sep = "\t")
#ss$llik                ## log-likelihoods
#write.table(ss$llik, file = "output/filtered-trigrams-grand-mean-llik-mixed-rnd-intercept.csv", sep = "\t")
#ss$sdcor               ## SDs and correlations
#write.table(ss$sdcor, file = "output/filtered-trigrams-grand-mean-sdcor-mixed-rnd-intercept.csv", sep = "\t")
#ss$theta               ## Cholesky factors
#write.table(ss$theta, file = "output/filtered-trigrams-grand-mean-theta-mixed-rnd-intercept.csv", sep = "\t")
#ss$which.OK            ## which fits worked
#write.table(ss$which.OK, file = "output/filtered-trigrams-grand-mean-which.OK-mixed-rnd-intercept.csv", sep = "\t")

########################################################################
##########################   Exp1: GLMMS   #############################
########################################################################

getwd()
# setwd("D:/Uni-Stuttgart/thesis/Corpora/Exp3")
setwd("/mount/projekte50/projekte/semrel/Users/reem/thesis/Corpora/Exp3/")
getwd()

# load libs
library(lsr)
library(lme4)
library(ggplot2)  # load the package

##STEP 0: set gloabal option to ignore scientific notation (numbers with E at the end)
options(scipen = 999)

## STEP 1: Load data frames
library(readr)
sample.grain.10k <- read.delim("samples/sample-grain-unigrams-10K-1.tsv", encoding="UTF8")

sample.kidko.10k <- read.delim("samples/sample-kidko-unigrams-10K-1.tsv", encoding="UTF8")

## STEP 1.1: Concatenate data frames
# use row bind | requires both dataframes to have the same columns
data.20k.sampled.df <- rbind(sample.grain.10k, sample.kidko.10k)

# STEP 1.2 shuffle rows 
# By default sample() randomly reorders the elements passed as the first argument. 
# This means that the default size is the size of the passed array. 
# Passing parameter replace=FALSE (the default) to sample(...) 
# ensures that sampling is done without replacement which accomplishes a row wise shuffle.
data.20k.sampled.df <- data.20k.sampled.df[sample(nrow(data.20k.sampled.df)),]

# Rename column where names is "isKD"
names(data.20k.sampled.df)[names(data.20k.sampled.df) == "isKD"] <- "corpus_type"

#View(data.20k.sampled.df)
# summary(data.20k.sampled.df)

print(length(unique(data.20k.sampled.df[["pos_seq"]])))

# STEP 1.3 factor our predictors and outcome
data.20k.sampled.df$pos_seq <- factor(data.20k.sampled.df$pos_seq)
lvls <- levels(data.20k.sampled.df$pos_seq)
write.table(lvls, file = "output/unigrams-20k-grand-mean-ngram-levels.csv", sep = "\t")

# STEP 2 create null/baseline model
# model only the intercept
null.glm = glm(corpus_type ~ 1, family = "binomial", data = data.20k.sampled.df)
summary(null.glm)

# STEP 3 create POSt model and compare to previous model
# set contrast to "contr.sum"
# sum contrasts compare the mean of each group\level to the grand mean/mean of all levels
# https://stats.idre.ucla.edu/r/library/r-library-contrast-coding-systems-for-categorical-variables/#DEVIATION
# see novarro book p.536  
# contrasts(data.20k.sampled.df$pos_seq) <- "contr.sum"
my.contrasts <- list(pos_seq = contr.sum)

# use family=binomial to turn our factor columns into numerical values
start_time <- Sys.time()

#POSt.glm <- glm(corpus_type ~ 1 + pos_seq, contrasts = my.contrasts,
#                  family = "binomial", data = data.20k.sampled.df)

library(boot)
library(parallel)

# function to return bootstrapped coefficients
myLogitCoef <- function(data, indices, formula, contrs) {
    d <- data[indices,]
    fit <- glm(formula, data=d, family = binomial(link = "logit"))
    return(coef(fit))
}

# set up cluster of 4 CPU cores
cl<-makeCluster(4)
clusterExport(cl, 'myLogitCoef')

# set random seed to ensure reproducibility 
set.seed(333)
# bootstrap data 500 times
coef.boot <- boot(data=data.20k.sampled.df, statistic=myLogitCoef, R=500, 
                  formula= corpus_type ~ 1 + pos_seq,
                  # process in parallel across 4 CPU cores
                  parallel = 'snow', ncpus=4, cl=cl)
stopCluster(cl)

end_time <- Sys.time()
total_time <- end_time - start_time

print(total_time)


# STEP 3.2 analyze model

# STEP 3.2.1 summary of the model
model.summary <- coef.boot$t0
write.table(model.summary, file = "output/unigrams-20k-grand-mean-coeff.csv", sep = "\t")

# STEP 3.2.2 summary of the model
boots.summary <- coef.boot$t
write.table(boots.summary, file = "output/unigrams-20k-grand-mean-coeff-boots.csv", sep = "\t")

# STEP 3.3 confidence intervals
con-int <- boot.ci(myBootstrap, index=1, type='norm')$norm
write.table(con-int, file = "output/unigrams-20k-grand-mean-boots-conf-int.csv", sep = "\t")

# STEP 4 get the estimate for the last level (VERB) using emmeans
# Estimated Marginal Means, aka Least-Squares Means (emmeans)
library(emmeans)
groups <- emmeans(POSt.glm, "pos_seq")

em.df <- summary(groups)

# save emmeans
write.table(em.df, file = "output/unigrams-20k-grand-mean-emmeans.csv", sep = "\t")

# plot distribution of bootstrap realizations
# https://www.datacamp.com/community/tutorials/bootstrap-r
svg(filename = 'output/pos-unigram-grand-mean-boots.svg')
plot(myBootstrap, index=1)
dev.off()

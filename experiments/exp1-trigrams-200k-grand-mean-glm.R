########################################################################
##########################   Exp1: GLMMS   #############################
########################################################################

getwd()
 setwd("D:/Uni-Stuttgart/thesis/Corpora/Exp1")
#setwd("/mount/projekte50/projekte/semrel/Users/reem/thesis/Corpora/Exp1/")
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

## STEP 1.1: Concatenate data frames
# use row bind | requires both dataframes to have the same columns
data.200k.sampled.df <- rbind(sample.grain.100k, sample.kidko.100k)

# STEP 1.2 shuffle rows 
# By default sample() randomly reorders the elements passed as the first argument. 
# This means that the default size is the size of the passed array. 
# Passing parameter replace=FALSE (the default) to sample(...) 
# ensures that sampling is done without replacement which accomplishes a row wise shuffle.
data.200k.sampled.df <- data.200k.sampled.df[sample(nrow(data.200k.sampled.df)),]

#View(data.200k.sampled.df)
# summary(data.200k.sampled.df)

print(length(unique(data.200k.sampled.df[["pos_seq"]])))

# STEP 1.3 factor our predictors and outcome
data.200k.sampled.df$pos_seq <- factor(data.200k.sampled.df$pos_seq)
lvls <- levels(data.200k.sampled.df$pos_seq)
write.table(lvls, file = "output/trigrams-200k-grand-mean-ngram-levels.csv", sep = "\t")

# STEP 2 create null/baseline model
# model only the intercept
null.glm = glm(corpus_type ~ 1, family = "binomial", data = data.200k.sampled.df)
summary(null.glm)

# STEP 3 create POSt model and compare to previous model
# set contrast to "contr.sum"
# sum contrasts compare the mean of each group\level to the grand mean/mean of all levels
# https://stats.idre.ucla.edu/r/library/r-library-contrast-coding-systems-for-categorical-variables/#DEVIATION
# see novarro book p.536  
# contrasts(data.200k.sampled.df$pos_seq) <- "contr.sum"
my.contrasts <- list(pos_seq = contr.sum)

# use family=binomial to turn our factor columns into numerical values
start_time <- Sys.time()

POSt.glm <- glm(corpus_type ~ 1 + pos_seq, contrasts = my.contrasts,
                  family = "binomial", data = data.200k.sampled.df)

end_time <- Sys.time()
total_time <- end_time - start_time

print(total_time)


# STEP 3.1 compare models using anova
anova(null.glm , POSt.glm, test="LRT") 
AIC(null.glm, POSt.glm)

# STEP 3.2 analyze model

# STEP 3.2.1 summary of the model
model.summary <- summary(POSt.glm)
print(model.summary)

# STEP 3.2.2 save the coefficients/results of the model
model.summary.coeff <- model.summary$coef
write.table(model.summary.coeff, file = "output/trigrams-200k-grand-mean-coeff.csv", sep = "\t")

# STEP 3.2.3 print contrasts matrix as a sanity check
print(POSt.glm$contrasts)

# STEP 4 get the estimate for the last level (VERB) using emmeans
# Estimated Marginal Means, aka Least-Squares Means (emmeans)
library(emmeans)
groups <- emmeans(POSt.glm, "pos_seq")

em.df <- summary(groups)

# save emmeans
write.table(em.df, file = "output/trigrams-200k-grand-mean-emmeans.csv", sep = "\t")

# plot emmeans
svg(filename = 'output/trigram-geand-mean-emmeans-probs.svg', width = 8, height = 15)
plot(groups, type = "response", comparisons = TRUE,
     xlab="Probability of Kiezdeutsch", ylab="POS trigram")+
  theme_bw() +
  theme(axis.text.y=element_blank())
dev.off()

# plot emmeans
svg(filename = 'output/trigram-geand-mean-emmeans-logits.svg', width = 8, height = 15)
plot(groups, 
     xlab="Probability of Kiezdeutsch", ylab="POS trigram")+
  theme_bw() +
  theme(axis.text.y=element_blank())
dev.off()

# plot Pairwise P-value 
svg(filename = 'output/pos-trigram-grand-mean-pwpp-7e-4.svg', width = 2065, height = 1200)
pwpp(groups, type = "response", xlab="Adjusted P-Value", ylab="POS trigram")+
  theme_bw() +
  scale_x_continuous(limits = c(0.00007, 0.0001))
dev.off()

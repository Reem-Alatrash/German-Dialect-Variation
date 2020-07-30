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
sample.grain.50k <- read.delim("samples/sample-grain-bigrams-100K-1.tsv", encoding="UTF8")
#View(sample.grain.50k)
#summary(sample.grain.50k)

sample.kidko.50k <- read.delim("samples/sample-kidko-bigrams-100K-1.tsv", encoding="UTF8")
#View(sample.kidko.50k)

## STEP 1: Concatenate data frames
# STEP 1.1 use row bind | requires both dataframes to have the same columns
data.100k.sampled.df <- rbind(sample.grain.50k, sample.kidko.50k)

# STEP 1.2 shuffle rows 
# By default sample() randomly reorders the elements passed as the first argument. 
# This means that the default size is the size of the passed array. 
# Passing parameter replace=FALSE (the default) to sample(...) 
# ensures that sampling is done without replacement which accomplishes a row wise shuffle.
data.100k.sampled.df <- data.100k.sampled.df[sample(nrow(data.100k.sampled.df)),]

View(data.100k.sampled.df)
# summary(data.100k.sampled.df)

# check how many levels/unique values we have for our predictor(s)
length(unique(data.100k.sampled.df[["pos_seq"]]))
length(unique(data.100k.sampled.df[["speaker"]]))

# STEP 1.3 factor our predictors and outcome
data.100k.sampled.df$pos_seq <- factor(data.100k.sampled.df$pos_seq)
lvls <- levels(data.100k.sampled.df$pos_seq)
# save factor to label mapping
write.table(lvls, file = "output/bigrams-200k-dummy-ngram-levels-mixed-rnd-intercept.csv", sep = "\t")

data.100k.sampled.df$speaker <- factor(data.100k.sampled.df$speaker)
speaker_lvls <- levels(data.100k.sampled.df$speaker)
# save factor to label mapping
write.table(speaker_lvls, file = "output/bigrams-200k-dummy-spkr-levels-mixed-rnd-intercept.csv", sep = "\t")

# STEP 2 create null/baseline model
# model only the intercept
null.glm = glm(corpus_type ~ 1, family = "binomial", data = data.100k.sampled.df)
summary(null.glm)

# STEP 3 create POSt model and compare to previous model
# POSt is the word in the middle of our 5-gram (col=pos_3)

# STEP 3.1 create models

# fixed-effects Model
start_time <- Sys.time()

POSt.glm <- glm(corpus_type ~ 1 + pos_seq,
                family = "binomial", data = data.100k.sampled.df)

end_time <- Sys.time()
total_time <- end_time - start_time
print(total_time)

anova(null.glm , POSt.glm, test="LRT")

# summary of the model
model.summ <- summary(POSt.glm)
model.summ

model.summ <- model.summ$coef
write.table(model.summ, file = "output/bigrams-200k-dummy-coeff.csv", sep = "\t")

# use family=binomial to turn our factor columns into numerical values
# to allow the glmer to converge, set maximal number of iterations using optCtrl
# (BOBYQA optimizer recommends at least 100,000 iterations)
# 100k = 1e5 in scientific notation, don't try more since we don't have more than 100k rows
# nAGQ specifies the type of approximation or smoothing to perform, default is 1 meaning Laplace

# mixed-effects Model
start_time <- Sys.time()

POSt.glmer <- glmer(corpus_type ~ 1 + pos_seq + (1|speaker), nAGQ=0,
                  family = "binomial", data = data.100k.sampled.df,
                  glmerControl(optimizer="bobyqa", optCtrl = list(maxfun = 100000)))

end_time <- Sys.time()
total_time <- end_time - start_time
print(total_time)

# STEP 3.2 analyze model

# STEP 3.2.1 summary of the model
model.summary <- summary(POSt.glmer)
model.summary

print(POSt.glmer, correlation=TRUE)

# STEP 3.2.2 save the coefficients/results of the model
model.summary.coeff <- model.summary$coef
write.table(model.summary.coeff, file = "output/bigrams-200k-dummy-coeff-mixed-rnd-intercept.csv", sep = "\t")

# STEP 3.2.3 post hoc analysis
# Estimated Marginal Means, aka Least-Squares Means (emmeans)
# preform pair-wise comparisons between the predictor levels (in our case the POs tags)
library(emmeans)
groups <- emmeans(POSt.glmer, "pos_seq", contr="tukey")

pairs(groups)

write.table(groups$emmeans, file = "output/bigrams-200k-dummy-emmeans-mixed-rnd-intercept.csv", sep = "\t")

sig_lett <- CLD(groups, adjust = "tukey", Letters = letters)
df <- data.frame(sig_lett)

svg(filename = 'output/pos-bigram-cld-emmeans.svg')
ggplot(data = df, aes(x = Variante)) +
  geom_pointrange(aes(y = emmean, ymin = lower.CL, ymax = upper.CL)) +
  geom_text(aes(y = upper.CL, label = trimws(.group)), vjust = -1) 

dev.off()


# STEP 3.3 compare models using anova
anova(POSt.glm , POSt.glmer, test="LRT")

# for multilevel within groups, use mvt instead of tukey
# details here: 
#https://stats.stackexchange.com/questions/387486/problem-with-tuckey-correction-for-planned-contrasts-with-emmeans-and-pairs-in
# summary(pairs(trustee_time_step),
#         by = NULL, adjust = “mvt”)

# STEP 4 Perform Optimizer Checks
library(optimx)
library(dfoptim)
# use method allFit from lme4
all.fits <- allFit(POSt.glm)
# all.fits.logliks <- sort(sapply(all.fits,logLik))
ss <- summary(all.fits)
ss$fixef               ## extract fixed effects
ss$llik                ## log-likelihoods
ss$sdcor               ## SDs and correlations
ss$theta               ## Cholesky factors
ss$which.OK            ## which fits worked

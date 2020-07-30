########################################################################
##########################   Exp1: GLMMS   #############################
########################################################################

getwd()
# setwd("D:/Uni-Stuttgart/thesis/Corpora/Exp1")
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

## STEP 1.1: Concatenate data frames
# use row bind | requires both dataframes to have the same columns
data.200k.sampled.df <- rbind(sample.grain.100k, sample.kidko.100k)

# STEP 1.2 shuffle rows 
# By default sample() randomly reorders the elements passed as the first argument. 
# This means that the default size is the size of the passed array. 
# Passing parameter replace=FALSE (the default) to sample(...) 
# ensures that sampling is done without replacement which accomplishes a row wise shuffle.
data.200k.sampled.df <- data.200k.sampled.df[sample(nrow(data.200k.sampled.df)),]
colnames(data.200k.sampled.df) <- c("ngram", "pos_seq", "full_sentence", "fileName",
                        "speaker","sentence_length","corpus_type","pos_0","pos_1","pos_2")

View(data.200k.sampled.df)
# summary(data.200k.sampled.df)

length(unique(data.200k.sampled.df[["pos_seq"]]))

# STEP 1.3 factor our predictors and outcome
data.200k.sampled.df$pos_seq <- factor(data.200k.sampled.df$pos_seq)
lvls <- levels(data.200k.sampled.df$pos_seq)
write.table(lvls, file = "output/trigrams-200k-dummy-ngram-levels.csv", sep = "\t")

# STEP 2 create null/baseline model
# model only the intercept
null.glm = glm(corpus_type ~ 1, family = "binomial", data = data.200k.sampled.df)
summary(null.glm)


# STEP 3 create POSt model and compare to previous model

start_time <- Sys.time()

# use family=binomial to turn our factor columns into numerical values
POSt.glm <- glm(corpus_type ~ 1 + pos_seq,family = "binomial", data = data.200k.sampled.df)

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

# STEP 3.2.3 post hoc analysis
# preform pair-wise comparisons between the predictor levels (in our case the POs tags)

library(userfriendlyscience)
library(multcompView)

my.cld <- function(post.hoc.results){
  # this fucntion gets the compact letter description of post anaylsis
  ### Extract dataframe with post hoc test results,
  ### and overwrite object 'res'
  res <- post.hoc.results$intermediate$posthoc
  
  ### Extract p-values and comparison 'names'
  pValues <- res$p
  
  dif3 <- NULL
  if (post.hoc.results$input$posthoc == "tukey") {
    ### Assign names (row names of post hoc test dataframe)
    dif3 <- res$pos_seq[,'p adj']
  } else {
    ### Create logical vector, assuming alpha of .05
    letter.alpha <- post.hoc.results$input$posthocLetterAlpha
    dif3 <- pValues < letter.alpha
    
    ### Assign names (row names of post hoc test dataframe)
    names(dif3) <- row.names(res)
  }
  
  ### convert this vector to the letters to compare
  ### the group means (see `?multcompView` for the
  ### references for the algorithm):
  # library(multcompView)
  cld <- multcompLetters(dif3)
  
  return (cld)
}

# Compute post-hoc statistics using the games-howell method

start_time <- Sys.time()

# different implementation of the games-howell method
one.way <- oneway(x=data.200k.sampled.df$pos_seq, y = data.200k.sampled.df$corpus_type,
                  posthoc = 'games-howell', pvalueDigits=6, t=FALSE, conf.level=.95)
one.way

write.table(one.way$intermediate$posthoc, file = "output/trigrams-200k-dummy-post-hoc.csv", sep = "\t")

my.cld(one.way)

end_time <- Sys.time()
total_time <- end_time - start_time
print(total_time)

#### test tukey HSD

start_time <- Sys.time()

# different implementation of the games-howell method
tukey.results <- oneway(x=data.200k.sampled.df$pos_seq, y = data.200k.sampled.df$corpus_type,
                        posthoc = 'tukey', pvalueDigits=6, t=FALSE, conf.level=.95)
tukey.results

my.cld(tukey.results)

end_time <- Sys.time()
total_time <- end_time - start_time
print(total_time)
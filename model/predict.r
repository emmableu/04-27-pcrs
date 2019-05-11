if (!require(plyr)) install.packages("plyr")
library(plyr)
setwd("~/bkt/04-27-pcrs")

runMe <- function() {
  # Get all data
  predict <- read.csv("data/Predict.csv")
  # Build a model using full dataset for training
  model <- buildModel(predict)
  summary(model)
  
  # Crossvalidate the model
  results <- crossValidate()
  evaluateByProblem <- evaluatePredictions(results, c("ProblemID"))
  evaluateOverall <- evaluatePredictions(results, c())
  
  # Write the results
  write.csv(results, "generated-data/cv_predict.csv", row.names = F)
  write.csv(evaluateByProblem, "generated-data/evaluation_by_problem.csv", row.names = F)
  write.csv(evaluateOverall, "generated-data/evaluation_overall.csv", row.names = F)
}


buildModel <- function(training) {

  model <- glm(FirstCorrect ~ pCorrectForProblem + medAttemptsForProblem + 
               priorAttempts + priorPercentCorrect + priorPercentCompleted, 
               data=training, family = "binomial")
  
  return (model)
}


makePredictions <- function(training, test) {
  model <- buildModel(training)
  print(predict(model, test))
  test$prediction <- predict(model, test) > 0.5
  return (test)
}


crossValidate <- function() {
  results <- NULL
  for (fold in 0:9) {
    training <- read.csv(paste0("data/CV/Fold", fold, "/Training_orig.csv"))
    test <- read.csv(paste0("data/CV/Fold", fold, "/Test_orig.csv"))
    test <- makePredictions(training, test)
    test$fold <- fold
    results <- rbind(results, test)
  }
  results
}

# Evaluate a given set of classifier prediction results using a variety of metrics
evaluatePredictions <- function(results, groupingCols) {
  eval <- ddply(results, groupingCols, summarize,
                pCorrect = mean(FirstCorrect),
                pPredicted = mean(prediction),
                tp = mean(FirstCorrect & prediction),
                tn = mean(!FirstCorrect & !prediction),
                fp = mean(!FirstCorrect & prediction),
                fn = mean(FirstCorrect & !prediction),
                accuracy = tp + tn,
                precision = tp / (tp + fp),
                recall = tp / (tp + fn)
  )
  eval$f1 <- 2 * eval$precision * eval$recall / (eval$precision + eval$recall)
  pe <- eval$pCorrect * eval$pPredicted + (1-eval$pCorrect) * (1-eval$pPredicted)
  eval$kappa <- (eval$accuracy - pe) / (1 - pe)
  return (eval)
}


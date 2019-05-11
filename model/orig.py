import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import *


def addTrainAttributes_orig(data):
    # data = predict
    problemStats = data.groupby(['ProblemID']).agg({'FirstCorrect':np.mean, 'Attempts':np.median})
    problemStats = problemStats.rename(columns = {'FirstCorrect':"pCorrectForProblem", 'Attempts':'medAttemptsForProblem'})
    data = pd.merge(data,problemStats,on='ProblemID')
    data = addStudentAttributes_orig(data)
    return data

def addStudentAttributes_orig(data):
    data = data.sort_values(['SubjectID', 'StartOrder'], ascending = [1, 1]).reset_index(drop = True)
    data['priorPercentCorrect'] = 0.5
    data['priorPercentCompleted'] = 0.5
    data['priorAttempts'] = 0

    lastStudent = ""
    # Go through each row in the data...
    for i in range(len(data.index)):
        # If this is a new student, reset our counters
        student = data.ix[i,'SubjectID']
        if (student != lastStudent):
            attempts  =  0
            firstCorrectAttempts =  0
            completedAttempts = 0
        lastStudent = student

        data.ix[i, 'priorAttempts'] = attempts
    # If this isn't their first attempt, calculate their prior percent correct and completed
        if (attempts > 0):
            data.ix[i, 'priorPercentCorrect'] = firstCorrectAttempts / attempts
            data.ix[i, 'priorPercentCompleted'] = completedAttempts / attempts

        attempts = attempts + 1
        if (data.ix[i,"FirstCorrect"]):
            firstCorrectAttempts  = firstCorrectAttempts + 1
        if (data.ix[i, "EverCorrect"]):
            completedAttempts  = completedAttempts + 1
    return data

def addTestAttributes_orig(train, test):
    problemStats = train.groupby(['ProblemID']).agg({'pCorrectForProblem':np.mean, 'medAttemptsForProblem':np.mean})
    test = pd.merge(test,problemStats,on='ProblemID')
    test = addStudentAttributes_orig(test)
    return test



def getTrainTest_orig(fold):
        train = pd.read_csv("data/CV/Fold" + str(fold) + "/Training.csv")
        test = pd.read_csv("data/CV/Fold" + str(fold) + "/Test.csv")

        train = addTrainAttributes_orig(train).fillna(0)

        (train.ix[:, 'FirstCorrect']) = (train.ix[:, 'FirstCorrect']).apply(int)
        test = addTestAttributes_orig(train,test).fillna(0)
        (test.ix[:, 'FirstCorrect']) = (test.ix[:, 'FirstCorrect']).apply(int)

        train.to_csv("data/CV/Fold" + str(fold) + "/Training_orig.csv")
        test.to_csv("data/CV/Fold" + str(fold) + "/Test_orig.csv")

for fold in range(10):
    getTrainTest_orig(fold)
scores = []

def changeto01(value):
    if value <0.5:
        return 0
    else:
        return 1


for fold in range(10):
    # getTrainTest_orig(fold)
    train = pd.read_csv("data/CV/Fold" + str(fold) + "/Training_orig.csv")
    test = pd.read_csv("data/CV/Fold" + str(fold) + "/Test_orig.csv")
    cols = ["pCorrectForProblem", 'medAttemptsForProblem', 'priorPercentCorrect', 'priorPercentCompleted', 'priorAttempts']
    X_train = (train.loc[:, cols]).fillna(0)
    y_train = train.loc[:, 'FirstCorrect']
    X_test = (test.loc[:, cols]).fillna(0)
    y_test = test.loc[:, 'FirstCorrect']
    # clf = DecisionTreeClassifier().fit(X_train.values, y_train.values)
    # no_estimators = 65
    # model = BaggingClassifier(base_estimator=clf, n_estimators=no_estimators, random_state=7)
    # model=model.fit(X_train.values,y_train.values)
    model = LogisticRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    # y_pred = y_pred.apply(changeto01)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cohen_kappa = cohen_kappa_score(y_test, y_pred)
    scores.append({'accuracy': accuracy, 'precision': precision, 'recall': recall, 'f1': f1, 'cohen_kappa': cohen_kappa})
scores = pd.DataFrame(scores)
print(scores)


print(scores.mean())
fold = 0
filename = "data/CV/Fold"+str(fold)
train_data = filename + 'Training_orig.csv'
test_data = filename + 'Test_orig.csv'




data = pd.read_csv("data/Predict.csv",  error_bad_lines=False)
data_group = data

import os
os.mkdir('tempDir')
get_per_problem_patterns(data_group):
    problems = data_group['ProblemID'].unique()
    for problem in problems:
        dirname = "result/featured-patterns/problem" + str(problem)
        os.mkdir(dirname)
        print("Problem:", problem)
        problem_data = data_group[(data_group['ProblemID'] == problem)].sort_values('StartOrder', ascending=1).reset_index(drop=True)
        print(len(problem_data.index))
        cv_fold = 0
        sequence_mining(data_group, problem, cv_fold)
        pattern_success = pd.read_csv(filename+str(cv_fold)+'pattern_success.csv')
        pattern_both_success = pd.read_csv(filename + str(cv_fold) + 'pattern_both_success.csv')
        pattern_failure = pd.read_csv(filename+str(cv_fold)+'pattern_failure.csv')
        pattern_both_failure = pd.read_csv(filename + str(cv_fold) + 'pattern_both_failure.csv')
        pattern = pd.concat(pattern_success, pattern_both_success, pattern_failure, pattern_both_failure)

for i in range(len(train_data.index)):
    student = train_data.ix[i, 'SubjectID']

import numpy as np
import pandas as pd
from scipy import stats

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import *
import re
import time
'''
data_group(from Predict, for a specific problem) has n rows, includes n students,
every student's previous attempts: s
every attempt's has p patterns
'''

pd.options.display.max_columns = 30
data = pd.read_csv("data/Predict.csv",  error_bad_lines=False)
orig_data  = pd.read_csv("original-data/StG108.2017.code_data_reexecuted.csv",  error_bad_lines=False)
data = data.sort_values(['SubjectID', 'ProblemID'], ascending=[1,1]).reset_index(drop=True)
# student = 1
data = pd.read_csv("data/Predict.csv",  error_bad_lines=False)
data_group = data
cur_problem = 4
groupname = 'failure'
cv_fold = 0
def get_student_pattern_per_problem(data_group, cur_problem, groupname):
    # O(nsp), 1 min for 193 students (30655 patterns)
    start = time.time()
    problem_data = data_group[(data_group['ProblemID'] == cur_problem) ].sort_values('StartOrder', ascending=1).reset_index(drop=True)
    problem_data = problem_data[(data_group['FirstCorrect'] == (groupname == 'success'))].reset_index(drop = True)
    student_pattern_per_problem = pd.DataFrame(columns= ['Student'])
    for i in range(len(problem_data.index)):
        student = problem_data.at[i, 'SubjectID']
        labels = get_labels_for_student(student, cur_problem, orig_data)
        labels['Student'] = student
        student_pattern_per_problem = student_pattern_per_problem.append(labels, ignore_index=True)
    student_pattern_per_problem = student_pattern_per_problem.fillna(0)
    student_pattern_per_problem.to_pickle("generated-data/student-pattern-per-problem" + str(cur_problem) + "-" + groupname + ".pkl")
    end = time.time()
    print((end-start)/60)
    return student_pattern_per_problem

def sequence_mining(cur_problem, groupname):
    start = time.time()
    student_pattern_per_problem = pd.read_pickle("generated-data/student-pattern-per-problem" + str(cur_problem) + "-" + groupname + ".pkl")
    colnames = ['Pattern','SSupport', 'ISupport', 'ISupportVariance',  'TotalStudent', 'ISupportVarianceTotal', 'ISupportTotal']
    pattern_statistics = pd.DataFrame(columns= colnames).set_index('Pattern')
    for pattern in student_pattern_per_problem.columns[1:]:
        s_support, i_support, i_support_variance, total_student, i_support_variance_total, i_support_total = 0, 0, 0, 0, 0, 0
        for i in range(len(student_pattern_per_problem.index)):
            # print(i)
            # if (i >= 10): break
            count = student_pattern_per_problem.at[i, pattern]
            s_support += np.sign(count)
            i_support_total += count
            i_support_variance_total += count ** 2
            i_support = i_support_total/len(student_pattern_per_problem.index)
            i_support_variance = i_support_variance_total/len(student_pattern_per_problem.index)
        pattern_row = {'Pattern': pattern, 'SSupport': s_support, 'ISupport': i_support, 'ISupportVariance': i_support_variance,
                       'TotalStudent': len(student_pattern_per_problem.index), 'ISupportVarianceTotal': i_support_variance_total, 'ISupportTotal': i_support_total}
        pattern_statistics.at[pattern] = (pattern_row)
    pattern_statistics.to_pickle("generated-data/pattern_statistics-per-problem" + str(cur_problem) + "-" + groupname +".pkl")
    end = time.time()
    print((end - start) / 60)
    return pattern_statistics


def t_test(x1, x2, s1, s2, n1, n2):
    import math
    sdelta = math.sqrt((s1**2)/n1 + (s2**2)/n2)
    t = (x1-x2)/sdelta
    df_up = ((s1**2)/n1 + (s2**2)/n2)**2
    df_down = ((s1**2)/n1)**2/(n1-1) +  ((s2**2)/n2)**2/(n2-1)
    df = df_up/df_down
    pvalue = 1 - stats.t.cdf(t, df = df)
    return t, df, pvalue

def get_featured_patterns(cur_problem):
    start = time.time()
    success_statistics = pd.read_pickle("generated-data/pattern_statistics-per-problem" + str(cur_problem) + "-" + 'success' +".pkl")
    failure_statistics =  pd.read_pickle("generated-data/pattern_statistics-per-problem" + str(cur_problem) + "-" + 'failure' +".pkl")
    colnames = ['Pattern', 'SuccessSSupport', 'SuccessISupport', 'FailureSSupport', 'FailureISupport']
    pattern_success, pattern_both_success, pattern_failure, pattern_both_failure = pd.DataFrame(columns=colnames), pd.DataFrame(columns=colnames), pd.DataFrame(columns=colnames), pd.DataFrame(columns=colnames)
    for pattern in success_statistics.index:
        if pattern not in failure_statistics.index:
            continue
        success_s_support = success_statistics.at[pattern, 'SSupport']
        success_total_student = success_statistics.at[pattern, 'TotalStudent']

        failure_s_support = failure_statistics.at[pattern, 'SSupport']
        failure_total_student = failure_statistics.at[pattern, 'TotalStudent']
        if success_s_support < 0.4* success_total_student and failure_s_support < 0.4* failure_total_student:
            continue
        success_i_support = success_statistics.at[pattern, 'ISupport']
        success_i_support_variance = success_statistics.at[pattern, 'ISupportVariance']
        failure_i_support = failure_statistics.at[pattern, 'ISupport']
        failure_i_support_variance = failure_statistics.at[pattern, 'ISupportVariance']
        pvalue = t_test(success_i_support, failure_i_support,success_i_support_variance, failure_i_support_variance,
                  success_total_student, failure_total_student)[2]
        if pvalue > 0.05:
            continue


        newrow = {"Pattern": pattern, 'SuccessSSupport': success_s_support,
                  'SuccessISupport': success_i_support,
                  'FailureSSupport': failure_s_support, 'FailureISupport': failure_i_support}
        if success_s_support >=  0.4* success_total_student and failure_s_support >= 0.4* failure_total_student:
            if success_s_support > failure_s_support:
                pattern_both_success = pattern_both_success.append(newrow, ignore_index=True)
            else:
                pattern_both_failure = pattern_both_failure.append(newrow, ignore_index=True)
        elif success_s_support >= 0.4* success_total_student:
            pattern_success = pattern_success.append(newrow, ignore_index=True)
        else:
            pattern_failure = pattern_failure.append(newrow, ignore_index=True)
    pattern_success.to_csv("result/featured-patterns/problem" + str(cur_problem)+ "/pattern-success.csv")
    pattern_both_success.to_csv("result/featured-patterns/problem" + str(cur_problem)+"/pattern-both-success.csv")
    pattern_failure.to_csv("result/featured-patterns/problem" + str(cur_problem)+"/pattern-failure.csv")
    pattern_both_failure.to_csv("result/featured-patterns/problem" + str(cur_problem)+"/pattern-both-failure.csv")

    # i = i + 1
    end = time.time()
    print((end-start)/60)
    return pattern_success, pattern_both_success, pattern_failure, pattern_both_failure










# cv_fold = 0
# def sequence_mining(data_group, cur_problem, cv_fold):
#     start = time.time()
#     problem_data = data_group[(data_group['ProblemID'] == cur_problem)].sort_values('StartOrder', ascending=1).reset_index(drop=True)
#     success_group = problem_data[(problem_data['FirstCorrect'] == True)].sort_values('StartOrder', ascending=1).reset_index(drop=True)
#     len_success = len(success_group.index)
#     failure_group = problem_data[(problem_data['FirstCorrect'] == False)].sort_values('StartOrder', ascending=1).reset_index(drop=True)
#     len_failure = len(failure_group.index)
#     colnames = ['Pattern', 'SuccessSSupport', 'SuccessISupport', 'FailureSSupport', 'FailureISupport']
#     patterns = get_patterns(data_group, cur_problem)
#     # 30s, O(
#     pattern_success, pattern_both_success, pattern_failure, pattern_both_failure = pd.DataFrame(columns=colnames), pd.DataFrame(columns=['Pattern']), pd.DataFrame(columns=['Pattern']),pd.DataFrame(columns=['Pattern'])
#     i = 0
#     for pattern in patterns['Pattern']:
#         success_s_support = get_s_support(success_group, cur_problem, pattern)
#         success_i_support = get_i_support(success_group, cur_problem, pattern)
#         failure_s_support = get_s_support(failure_group, cur_problem, pattern)
#         failure_i_support = get_i_support(failure_group, cur_problem, pattern)
#         i = i + 1
#         # if(i >= 500):
#         #     break
#         if success_s_support >= 0.4*len_success or failure_s_support >= 0.4*len_failure:
#             if abs(success_i_support - failure_i_support) >=0.3:
#                 # change to t test
#                 # print(pattern)
#                 newrow = {"Pattern": pattern, 'SuccessSSupport': success_s_support,
#                           'SuccessISupport': success_i_support,
#                           'FailureSSupport': failure_s_support, 'FailureISupport': failure_i_support}
#                 if success_s_support >= 2 and failure_s_support >= 2:
#                     if success_s_support > failure_s_support:
#                         pattern_both_success = pattern_both_success.append(newrow, ignore_index=True)
#                     else:
#                         pattern_both_failure = pattern_both_failure.append(newrow, ignore_index=True)
#                 elif success_s_support >= 2:
#                     pattern_success = pattern_success.append(newrow, ignore_index=True)
#                 else:
#                     pattern_failure = pattern_failure.append(newrow, ignore_index=True)
#     pattern_success.to_csv("data/CV/Fold" + str(cv_fold)+ "/pattern-success.csv")
#     pattern_both_success.to_csv("data/CV/Fold" + str(cv_fold)+ "/pattern-both-success.csv")
#     pattern_failure.to_csv("data/CV/Fold" + str(cv_fold)+ "/pattern-failure.csv")
#     pattern_both_failure.to_csv("data/CV/Fold" + str(cv_fold)+ "/pattern-both-failure.csv")
#
#     # i = i + 1
#     end = time.time()
#     print((end-start)/60)
#     return pattern_success, pattern_both_success, pattern_failure, pattern_both_failure
# # data_group = data.loc[0:1000,]
#
# cur_problem = 4



# def get_patterns(data_group, cur_problem):
#     problem_data = data_group[(data_group['ProblemID'] == cur_problem)].sort_values('StartOrder', ascending=1).reset_index(drop=True)
#     patterns = pd.DataFrame(columns = ['Pattern'])
#     for i in range(len(problem_data.index)):
#         student = problem_data.ix[i, 'SubjectID']
#         labels = get_labels_for_student(student, cur_problem, orig_data)
#         for pattern in labels.keys():
#             if patterns.empty or (patterns.Pattern == pattern).any() == False:
#                 patterns = patterns.append({'Pattern': pattern}, ignore_index=True)
#             else:
#                 pass
#     return patterns

# def get_s_support(data_group, cur_problem, pattern):
#     problem_data = data_group[(data_group['ProblemID'] == cur_problem)].sort_values('StartOrder', ascending=1).reset_index(drop=True)
#     s_support = 0
#     for i in range(len(problem_data.index)):
#         # print(i)
#         # data_group = data.loc[0:10,]
#         student = problem_data.ix[i, 'SubjectID']
#         labels = get_labels_for_student(student, cur_problem, orig_data)
#         try:
#             s_support = s_support + np.sign(labels[pattern])
#         except:
#             continue
#     return s_support



#
# student = data.ix[0, 'SubjectID']
# cur_problem = data.ix[0, 'ProblemID']
# pattern = '116 midterm1 midterm2'
# s_support = get_s_support(data.loc[0:1000,], cur_problem, pattern)
# #
#
# def get_i_support(data_group, cur_problem, pattern):
#     # data_group = success_group
#     # pattern = '116 midterm1 midterm2'
#     problem_data = data_group[(data_group['ProblemID'] == cur_problem)].sort_values('StartOrder', ascending=1).reset_index(drop=True)
#
#     i_support_total = 0
#     for i in range(len(problem_data.index)):
#         # print('isupport:', i)
#         # data_group = data.loc[0:10,]
#         student = problem_data.ix[i, 'SubjectID']
#         # print(student)
#         labels = get_labels_for_student(student, cur_problem, orig_data)
#         # print(labels)
#         try:
#             i_support_total = i_support_total + (labels[pattern])
#         except:
#             continue
#         # print(i_support_total)
#         # print('i_support_total: ', i_support_total)
#     return i_support_total/len(problem_data.index)
# i_support = get_i_support(data.loc[0:1000,], cur_problem, '116 midterm1 midterm2')


# patterns = get_patterns(data.loc[0:1000,], cur_problem)
#

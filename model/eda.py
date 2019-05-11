import pandas as pd

pd.options.display.max_columns = 30

col_names  = ['SubjectID','ProblemID', 'StartOrder', 'FirstCorrect', 'EverCorrect', 'Attempts']


data = pd.read_csv("original-data/StG108.2017.code_data_reexecuted.csv",  error_bad_lines=False)
data = data.sort_values(['user_id', 'problem_id'], ascending=[1,1]).reset_index(drop=True)
Predict = pd.DataFrame(columns = col_names)
for i in range(0, len(data.index)):
    if i == 0:
        subject_id = data.ix[0, 'user_id']
        problem_id = data.ix[0, 'problem_id']
        start_order = data.ix[0, 'submission_id']
        first_correct = True
        ever_correct = True
        attempts = 1
        Predict.loc[len(Predict)] = new_record

    else:
        if data.ix[i, 'user_id'] != subject_id or data.ix[i, 'problem_id'] != problem_id:
            new_record = ({'SubjectID': subject_id,
                           'ProblemID': problem_id,
                           'StartOrder': start_order,
                           'FirstCorrect': first_correct,
                           'EverCorrect': ever_correct,
                           'Attempts': attempts})
            Predict.loc[len(Predict)] = new_record
            subject_id = data.ix[i, 'user_id']
            problem_id = data.ix[i, 'problem_id']
            start_order = data.ix[i, 'submission_id']
            first_correct = (data.ix[i, 'status'] == 'Pass')
            ever_correct = (data.ix[i, 'status'] == 'Pass')
            attempts = 1
        else:
            ever_correct = (ever_correct or (data.ix[i, 'status'] == 'Pass'))
            attempts = attempts + 1


data.head()
print(Predict.head())
Predict.to_csv('data/Predict.csv')
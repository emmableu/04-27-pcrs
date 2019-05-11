import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import *
pd.options.display.max_columns = 30

import re
orig_data = pd.read_csv("original-data/StG108.2017.code_data_reexecuted.csv",  error_bad_lines=False)
orig_data = orig_data.sort_values(['user_id', 'problem_id'], ascending=[1,1]).reset_index(drop=True)

def generate_ngrams(s, n):
    # s = orig_data.ix[0, 'code']
    s = re.sub("[\\s|\\n|\\r]+", " ", s)
    tokens = []
    delimiters = [" ", "(", ")", "+", "-", ",", ":", "\\", "/", "*", "//", "/", "[", "]", "{", "}",
                  "==", "=", ">", "<", "'", "\"", ".", "?", "!", "%", "^", "*"]
    token = ""
    for i in range(len(s)):
        d = False
        for delim in delimiters:
            if (len(delim) + i >= len(s)):
                continue
            #  到达末尾了，所以不用做了
            if str.startswith(s[i:], (delim)):
                tokens.append(token)
                if (delim != (" ")):
                    tokens.append(delim)
                token = ""
                i += len(delim) - 1
                d = True
                break
        if not d:
            token += s[i]
    if token != "":
        tokens.append(token)
    return_tokens = []
    for token in tokens:
        if token == "":
            continue
        else:
            return_tokens.append(token)
    ngrams = zip(*[return_tokens[i:] for i in range(n)])
    return [" ".join(ngram) for ngram in ngrams]
#
s = orig_data.ix[0, 'code']
ngrams = generate_ngrams(s, 2)

class CodeShape:
    def __init__(self, ngram, problem):
        self.ngrams = ngram
        self.problem = problem
        self.shape = str(problem) + " " + ngram

def get_code_shapes_from_code(problem, code):
    # code = orig_data.ix[0, 'code']
    ngrams = generate_ngrams(code, 2)[1:-1]
    # problem = str(orig_data.ix[0, 'problem_id'])
    codeshape_count_map = {}
    i = 0
    for ngram in ngrams:
        # ngram = ngrams[2]
        # print(i)
        i = i + 1
        codeshape = CodeShape(ngram, problem).shape
        if codeshape not in codeshape_count_map.keys():
            codeshape_count_map[codeshape] = 1
        else:
            codeshape_count_map[codeshape] += 1
    return codeshape_count_map


class ProblemCodeMap:
    def __init__(self, problem, code):
        self.problem = problem
        self.code = code
        self.map = {problem: code}

def get_attempts_before_problem(student, cur_problem):
    'O(s)'
    # student = orig_data.ix[0, 'user_id']
    # cur_problem = orig_data.ix[0, 'problem_id']
    student_orig_data = orig_data[(orig_data['user_id'] == student)].sort_values('submission_id', ascending=1).reset_index(drop=True)
    last_problem = ''
    problem_code_maps = {}
    map = {}
    for i in range(len(student_orig_data.index)):
        problem = student_orig_data.at[i, 'problem_id']
        if problem == cur_problem:
            continue
        else:
            if problem != last_problem:
                problem_code_maps.update(map)
            last_problem = problem
            code = student_orig_data.at[i, 'code']
            map = ProblemCodeMap(problem, code).map
    return problem_code_maps


def get_code_shapes_before_problem(problem_code_maps):
    # 'O(sp)'
    codeshape_count_maps = {}
    for problem, code in problem_code_maps.items():
        codeshape_count_map = get_code_shapes_from_code(problem, code)
        # O(p)
        codeshape_count_maps.update(codeshape_count_map)
    return codeshape_count_maps

def get_labels_for_student(student, cur_problem, orig_data):
    # "O(sp)"
    problem_code_maps = get_attempts_before_problem(student, cur_problem)
    codeshape_count_maps = get_code_shapes_before_problem(problem_code_maps)
    return codeshape_count_maps

# get_labels_for_student(2, 3, orig_data) == get_labels_for_student(1, 3, orig_data)
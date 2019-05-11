Predict = pd.read_csv('data/Predict.csv')

for i in range(10):

    test_start = i*7024
    test_end = test_start + 7024
    print(test_end)
    test = Predict[test_start:test_end]
    train = pd.concat([Predict[:test_start] , Predict[(test_end):]])

    test.to_csv('data/CV/Fold'+ str(i) + '/Test.csv')
    train.to_csv('data/CV/Fold'+ str(i)+ '/Training.csv')


for i in range(10):
    test = pd.read_csv('data/CV/Fold'+ str(i) + '/Test.csv')
    train= pd.read_csv('data/CV/Fold'+ str(i)+ '/Training.csv')
    print(len(test.index))
    print(len(train.index))


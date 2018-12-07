from __future__ import division
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd
import csv
import pickle

numberOfTree = 250
numberOfSubject = 9
numberOfYear = 3
markData = []
markDataNature = []
markDataSocial = []

# Covert .xlsx to .csv
pd.read_excel('markData.xlsx', 'Sheet1', index_col=None).to_csv('markData.csv', encoding='utf-8')

with open('markData.csv', 'rt') as csvfile:
    csvObj = csv.reader(csvfile, delimiter=',')
    for row in csvObj:
        markData.append(row)

markData = np.array(markData)
for line in markData[2:, 2:]:
    if (line[-1] != '0'):
        markDataSocial.append(line)
    else:
        markDataNature.append(line)

markDataNature = np.array(markDataNature)
markDataSocial = np.array(markDataSocial)

# Train markDataNature Model
# train, test= train_test_split(markDataNature, test_size=0.1)
# trainData = train[:,:numberOfSubject*numberOfYear]
# trainLabel = train[:,numberOfSubject*numberOfYear:]
# testData = test[:,:numberOfSubject*numberOfYear]
# testLabel = test[:,numberOfSubject*numberOfYear:]
trainData = markDataNature[:,:numberOfSubject*numberOfYear]
trainLabel = markDataNature[:,numberOfSubject*numberOfYear:]
clf = RandomForestRegressor(n_estimators  = numberOfTree)
clf.fit(trainData, trainLabel)
# Save Model
pickle.dump(clf, open('markDataNature.sav', 'wb'))
print('Nature Trained!')
# print('Predict: ')
# for i in range(len(testData)):
#     print(clf.predict(testData[i].reshape(1,-1)))
# print('Real Value: ')
# print(testLabel)

# Train markDataSocial Model
# train, test= train_test_split(markDataSocial, test_size=0.1)
# trainData = train[:,:numberOfSubject*numberOfYear]
# trainLabel = train[:,numberOfSubject*numberOfYear:]
# testData = test[:,:numberOfSubject*numberOfYear]
# testLabel = test[:,numberOfSubject*numberOfYear:]
trainData = markDataSocial[:,:numberOfSubject*numberOfYear]
trainLabel = markDataSocial[:,numberOfSubject*numberOfYear:]
clf = RandomForestRegressor(n_estimators  = numberOfTree)
clf.fit(trainData, trainLabel)
# Save Model
pickle.dump(clf, open('markDataSocial.sav', 'wb'))
print('Social Trained!')
# print('Predict: ')
# for i in range(len(testData)):
#     print(clf.predict(testData[i].reshape(1,-1)))
# print('Real Value: ')
# print(testLabel)

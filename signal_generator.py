'''
Created on Feb 3, 2023

@author: ANIK
'''

import random


def getTankData(sigID):

    file = open("data_fp/sig_{}.txt".format(sigID))
    line = file.readline()
    data = []

    while line:

        param = line.split('\t')
        values = []

        for i in range(2):

            values.append(int(param[i].strip()))

        data.append(values)
        line = file.readline()

    return data


def genData(oldData, sigID):
    
    newData = []
    
    for i in range(len(oldData)):
        
        if oldData[i][1] == 0:
            
            if sigID == 0:

                # newData.append([oldData[i][0], 1 + random.random()])  # 0
                newData.append([oldData[i][0], 0.5 + random.random(), 0.75 + random.random(), 1 + random.random()])  # 0 UAV

            else:

                newData.append([oldData[i][0], 3.1 - random.random(), 3.26 - random.random(), 3.51 - random.random()])  # 1
            
        else:
            
            if sigID == 0:

                newData.append([oldData[i][0], 2.0012427683572508, 2.0008747649449031, 2.0037546304797856])  # 0

            else:

                newData.append([oldData[i][0], 2.0012427683572508, 2.0008747649449031, 2.0037546304797856])  # 1
            
    return newData


def setData(newData, sigID):
    
    file = open("data_fp/fp_{}.txt".format(sigID), "w")
    
    for i in range(len(newData)):

        # file.write("{}\t{}\n".format(newData[i][0], newData[i][1]))
        file.write("{}\t{}\t{}\t{}\n".format(newData[i][0], newData[i][1], newData[i][2], newData[i][3]))


def main():

    oldData = getTankData(0)
    newData = genData(oldData, 0)
    setData(newData, 0)

    oldData = getTankData(1)
    newData = genData(oldData, 1)
    setData(newData, 1)


if __name__ == '__main__':

    main()
    pass

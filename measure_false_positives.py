'''
Created on Jan 29, 2023

@author: ANIK
'''


def getTankData(id):

    file = open("data/wt/s36000_tank_{}".format(id))
    line = file.readline()
    data = []

    while line:

        param = line.split('\t')
        values = []

        for i in range(2):

            values.append(float(param[i].strip()))

        data.append(values)
        line = file.readline()

    return data


def getDroneData(id):

    file = open("data/uav/s36000_uav_{}".format(id))
    line = file.readline()
    data = []

    while line:

        param = line.split('\t')
        values = []

        for i in range(4):

            values.append(float(param[i].strip()))

        data.append(values)
        line = file.readline()

    return data


def lineIntersection(line1, line2):

    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):

        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)

    if xdiff[0] * ydiff[1] - xdiff[1] * ydiff[0] == 0:

        return 'lines do not intersect'

    else:

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div

    return x, y


def hasViolation(line1, line2):

    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):

        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)

    if xdiff[0] * ydiff[1] - xdiff[1] * ydiff[0] == 0:

        return False

    else:

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        # y = det(d, ydiff) / div

        if line1[0][0] <= x and x < line2[1][0]:

            return True

        else:

            return False


def getTankStats(data0, data1, eps):
    
    dur = len(data0)
    # hit0 = 0
    # hit1 = 0
    hitMatch = 0
    trueMatch = 0

    for i in range(dur - 1):

        for j in range(max(i - eps, 0), min(i + eps + 1, dur - 1)):

            if hasViolation([[i, data0[i][1]], [i + 1, data0[i + 1][1]]], [[i, data1[j][1]], [i + 1, data1[j + 1][1]]]):
                
                hitMatch += 1 
                
                if i + eps == j:
                    
                    trueMatch += 1

                    # print(((i, data0[i][1]), (i + 1, data0[i + 1][1])), ((j, data1[j][1]), (j + 1, data1[j + 1][1])))

        # print(" ")

    #print("Total Events\t:\t{}".format(dur))
    # print("Total Hits (0)\t:\t{} ({}%)".format(hit0, round((hit0 / dur) * 100, 2)))
    # print("Total Hits (1)\t:\t{} ({}%)".format(hit1, round((hit1 / dur) * 100, 2)))
    #print("Total Matches\t:\t{} ({}%)".format(hitMatch, round((hitMatch / dur) * 100, 2)))
    #print("True Matches\t:\t{} ({}%)".format(trueMatch, round((trueMatch / dur) * 100, 2)))
    
    print("{}\t{}\t\t{}\t\t{}\t\t{}%%\n".format(eps / 20, trueMatch, hitMatch, hitMatch - trueMatch, round(((hitMatch - trueMatch) / hitMatch) * 100, 2)))


def getDroneStats(data0, data1, eps):

    dur = len(data0)
    # hit0 = 0
    # hit1 = 0
    hitMatch = 0
    trueMatch = 0

    for i in range(dur - 1):

        for j in range(max(i - eps, 0), min(i + eps + 1, dur - 1)):

            if hasViolation([[i, data0[i][1]], [i + 1, data0[i + 1][1]]], [[i, data1[j][1]], [i + 1, data1[j + 1][1]]]) and hasViolation([[i, data0[i][2]], [i + 1, data0[i + 1][2]]], [[i, data1[j][2]], [i + 1, data1[j + 1][2]]]) and hasViolation([[i, data0[i][3]], [i + 1, data0[i + 1][3]]], [[i, data1[j][3]], [i + 1, data1[j + 1][3]]]):

                hitMatch += 1

                if i + eps == j:

                    trueMatch += 1

                    # print(((i, data0[i][1]), (i + 1, data0[i + 1][1])), ((j, data1[j][1]), (j + 1, data1[j + 1][1])))

        # print(" ")

    # print("Total Events\t:\t{}".format(dur))
    # print("Total Hits (0)\t:\t{} ({}%)".format(hit0, round((hit0 / dur) * 100, 2)))
    # print("Total Hits (1)\t:\t{} ({}%)".format(hit1, round((hit1 / dur) * 100, 2)))
    # print("Total Matches\t:\t{} ({}%)".format(hitMatch, round((hitMatch / dur) * 100, 2)))
    # print("True Matches\t:\t{} ({}%)".format(trueMatch, round((trueMatch / dur) * 100, 2)))

    print("{}\t{}\t\t{}\t\t{}\t\t{}%%\n".format(eps / 20, trueMatch, hitMatch, hitMatch - trueMatch, round(((hitMatch - trueMatch) / hitMatch) * 100, 2)))


def main():

    data0 = getTankData(0)
    data1 = getTankData(1)
    
    print("Water tank false positives:\n")
    print("Clock\tTrue\t\tDetected\tFalse\t\tFalse +ve")
    print("Skew\tViolations\tViolations\tPositives\tPercentage\n")
    
    for i in range(10):

        getTankStats(data0, data1, i + 1)

    data0 = getDroneData(0)
    data1 = getDroneData(1)

    print("UAV false positives:\n")
    print("Clock\tTrue\t\tDetected\tFalse\t\tFalse +ve")
    print("Skew\tViolations\tViolations\tPositives\tPercentage\n")
    
    for i in range(10):

        getTankStats(data0, data1, i + 1)


if __name__ == '__main__':

    main()
    pass

'''
@author: ANIK
'''

import time

from z3 import *
from z3.z3 import ForAll

# set_param('parallel.enable', True)
set_option(rational_to_decimal = True)


def prog_tanks_pressure(eps, sigDur, segCount):

    # initialize z3 solver
    s = Solver()

    # ===== VAR INIT START ===== #

    t0 = 0.00  # First time-stamp on agent that is to be re-timed
    t1 = 0.05  # Second time-stamp on agent that is to be re-timed

    if sigDur / segCount < t1:

        segCount = sigDur / t1

    if t0 != 0:

        return

    segmentDuration = sigDur / segCount
    delta = 0
    nSAT = 1  # Number of SAT assignments the solver will display per segment; set to -1 for allSAT

    # multiplier adjustments
    multiplier = 1 / t1
    eps *= multiplier
    segmentDuration *= multiplier
    sigDur *= multiplier

    # ===== VAR INIT END ===== #

    # ===== READ DATA START ===== #

    data_0 = getDataTank(0)
    data_1 = getDataTank(1)

    i = 0
    solvers = []
    entryFound = True

    while(entryFound):

        # Flag to be set True if at least one entry is found in the current iteration
        entryFound = False

        # Initialize solver
        s = Solver()

        # Calculate upper and lower time bound for current segment
        segmentLowerBound = int((i * segmentDuration) - eps)
        segmentUpperBound = int((i + 1) * segmentDuration)

        timestamps0 = []

        tank0 = Function('tank0', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_0)):

                timestamps0.append(int(data_0[j][0] * multiplier))

                s.add(tank0(int(data_0[j][0] * multiplier)) == data_0[j][1])

                if(int(data_0[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_0[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps1 = []

        tank1 = Function('tank1', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_1)):

                timestamps1.append(int(data_1[j][0] * multiplier))

                s.add(tank1(int(data_1[j][0] * multiplier)) == data_1[j][1])

                if(int(data_1[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_1[j][0] * multiplier == sigDur:

                    entryFound = False

        i += 1

        # force terminate after one loop
        entryFound = False

        # ===== READ DATA END ===== #

        # ===== CONCUT FLOW START ===== #

        # global clock to local clock mappings
        c0 = Function('c0', IntSort(), IntSort())
        s.add(And([Or([c0(i) == ((i - eps) + j) for j in range(2 * int(eps) + 1)]) for i in range(timestamps0[0], timestamps0[-1] + 1)]))
        s.add(Not(Or(c0(timestamps0[0]) == timestamps0[0] - 1, c0(timestamps0[-1]) == timestamps0[-1] + 1)))

        c1 = Function('c1', IntSort(), IntSort())
        s.add(And([Or([c1(i) == ((i - eps) + j) for j in range(2 * int(eps) + 1)]) for i in range(timestamps1[0], timestamps1[-1] + 1)]))
        s.add(Not(Or(c1(timestamps1[0]) == timestamps1[0] - 1, c1(timestamps1[-1]) == timestamps1[-1] + 1)))

        # local clocks are bound by epsilon
        s.add(And([And(c0(i) - c1(i) <= eps, c0(i) - c1(i) >= -eps) for i in range(timestamps0[0], timestamps0[-1] + 1)]))

        # global clock to local clock mappings are ordered
        s.add(And([And([Implies(i <= j, And(c0(i) <= c0(j), c1(i) <= c1(j))) for j in range(timestamps0[0], timestamps0[-1] + 1)]) for i in range(timestamps0[0], timestamps0[-1] + 1)]))

        # consistent cut flow
        c_flow = Function('c_flow', IntSort(), RealSort())
        # c_flow = Function('c_flow', IntSort(), IntSort())

        # addition
        s.add(And([c_flow(i) == (tank0(c0(i)) + tank1(c1(i))) for i in range(timestamps0[0], timestamps0[-1] + 1)]))

        # violation check
        v = Real('v')
        s.add(And(v >= timestamps0[0], v <= timestamps0[-1]))

        s.add(ForAll(v, Implies(And(v >= timestamps0[0], v <= timestamps0[-1]), z3Interpolate(c_flow, v) >= 10)))
        # s.add(z3Interpolate(c_flow, v) == 15)
        # s.add(v == 10)

        if s.check() == sat:

            m = s.model()
            # out = "%s %s" % (m[test], m[test2])
            # print(m)

        s.reset()


def prog_tanks_pressure_3(eps, sigDur, segCount):

    # initialize z3 solver
    s = Solver()

    # ===== VAR INIT START ===== #

    t0 = 0.00  # First time-stamp on agent that is to be re-timed
    t1 = 0.05  # Second time-stamp on agent that is to be re-timed

    if sigDur / segCount < t1:

        segCount = sigDur / t1

    if t0 != 0:

        return

    segmentDuration = sigDur / segCount
    delta = 0
    nSAT = 1  # Number of SAT assignments the solver will display per segment; set to -1 for allSAT

    # multiplier adjustments
    multiplier = 1 / t1
    eps *= multiplier
    segmentDuration *= multiplier
    sigDur *= multiplier

    # ===== VAR INIT END ===== #

    # ===== READ DATA START ===== #

    data_0 = getDataTank(0)
    data_1 = getDataTank(1)
    data_2 = getDataTank(2)

    i = 0
    solvers = []
    entryFound = True

    while(entryFound):

        # Flag to be set True if at least one entry is found in the current iteration
        entryFound = False

        # Initialize solver
        s = Solver()

        # Calculate upper and lower time bound for current segment
        segmentLowerBound = int((i * segmentDuration) - eps)
        segmentUpperBound = int((i + 1) * segmentDuration)

        timestamps0 = []

        tank0 = Function('tank0', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_0)):

                timestamps0.append(int(data_0[j][0] * multiplier))

                s.add(tank0(int(data_0[j][0] * multiplier)) == data_0[j][1])

                if(int(data_0[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_0[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps1 = []

        tank1 = Function('tank1', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_1)):

                timestamps1.append(int(data_1[j][0] * multiplier))

                s.add(tank1(int(data_1[j][0] * multiplier)) == data_1[j][1])

                if(int(data_1[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_1[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps2 = []

        tank2 = Function('tank2', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_2)):

                timestamps2.append(int(data_2[j][0] * multiplier))

                s.add(tank2(int(data_2[j][0] * multiplier)) == data_2[j][1])

                if(int(data_2[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_2[j][0] * multiplier == sigDur:

                    entryFound = False

        i += 1

        # force terminate after one loop
        entryFound = False

        # ===== READ DATA END ===== #

        # ===== CONCUT FLOW START ===== #

        # global clock to local clock mappings
        c0 = Function('c0', IntSort(), IntSort())
        s.add(And([Or([c0(i) == ((i - eps) + j) for j in range(2 * int(eps) + 1)]) for i in range(timestamps0[0], timestamps0[-1] + 1)]))
        s.add(Not(Or(c0(timestamps0[0]) == timestamps0[0] - 1, c0(timestamps0[-1]) == timestamps0[-1] + 1)))

        c1 = Function('c1', IntSort(), IntSort())
        s.add(And([Or([c1(i) == ((i - eps) + j) for j in range(2 * int(eps) + 1)]) for i in range(timestamps1[0], timestamps1[-1] + 1)]))
        s.add(Not(Or(c1(timestamps1[0]) == timestamps1[0] - 1, c1(timestamps1[-1]) == timestamps1[-1] + 1)))

        c2 = Function('c2', IntSort(), IntSort())
        s.add(And([Or([c2(i) == ((i - eps) + j) for j in range(2 * int(eps) + 1)]) for i in range(timestamps2[0], timestamps2[-1] + 1)]))
        s.add(Not(Or(c2(timestamps2[0]) == timestamps2[0] - 1, c2(timestamps2[-1]) == timestamps2[-1] + 1)))

        # local clocks are bound by epsilon
        s.add(And([And(c0(i) - c1(i) <= eps, c0(i) - c1(i) >= -eps) for i in range(timestamps0[0], timestamps0[-1] + 1)]))
        s.add(And([And(c1(i) - c2(i) <= eps, c1(i) - c2(i) >= -eps) for i in range(timestamps1[0], timestamps1[-1] + 1)]))
        s.add(And([And(c2(i) - c0(i) <= eps, c2(i) - c0(i) >= -eps) for i in range(timestamps2[0], timestamps2[-1] + 1)]))

        # global clock to local clock mappings are ordered
        s.add(And([And([Implies(i <= j, And(c0(i) <= c0(j), c1(i) <= c1(j), c2(i) <= c2(j))) for j in range(timestamps0[0], timestamps0[-1] + 1)]) for i in range(timestamps0[0], timestamps0[-1] + 1)]))

        # consistent cut flow
        c_flow = Function('c_flow', IntSort(), RealSort())
        # c_flow = Function('c_flow', IntSort(), IntSort())

        # addition
        s.add(And([c_flow(i) == (tank0(c0(i)) + tank1(c1(i)) + tank2(c2(i))) for i in range(timestamps0[0], timestamps0[-1] + 1)]))

        # violation check
        v = Real('v')
        s.add(And(v >= timestamps0[0], v <= timestamps0[-1]))

        s.add(ForAll(v, Implies(And(v >= timestamps0[0], v <= timestamps0[-1]), z3Interpolate(c_flow, v) >= 15)))
        # s.add(z3Interpolate(c_flow, v) == 15)
        # s.add(v == 10)

        if s.check() == sat:

            m = s.model()
            # out = "%s %s" % (m[test], m[test2])
            # print(m)

        s.reset()


def prog_tanks_pressure_4(eps, sigDur, segCount):

    # initialize z3 solver
    s = Solver()

    # ===== VAR INIT START ===== #

    t0 = 0.00  # First time-stamp on agent that is to be re-timed
    t1 = 0.05  # Second time-stamp on agent that is to be re-timed

    if sigDur / segCount < t1:

        segCount = sigDur / t1

    if t0 != 0:

        return

    segmentDuration = sigDur / segCount
    delta = 0
    nSAT = 1  # Number of SAT assignments the solver will display per segment; set to -1 for allSAT

    # multiplier adjustments
    multiplier = 1 / t1
    eps *= multiplier
    segmentDuration *= multiplier
    sigDur *= multiplier

    # ===== VAR INIT END ===== #

    # ===== READ DATA START ===== #

    data_0 = getDataTank(0)
    data_1 = getDataTank(1)
    data_2 = getDataTank(2)
    data_3 = getDataTank(3)

    i = 0
    solvers = []
    entryFound = True

    while(entryFound):

        # Flag to be set True if at least one entry is found in the current iteration
        entryFound = False

        # Initialize solver
        s = Solver()

        # Calculate upper and lower time bound for current segment
        segmentLowerBound = int((i * segmentDuration) - eps)
        segmentUpperBound = int((i + 1) * segmentDuration)

        timestamps0 = []

        tank0 = Function('tank0', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_0)):

                timestamps0.append(int(data_0[j][0] * multiplier))

                s.add(tank0(int(data_0[j][0] * multiplier)) == data_0[j][1])

                if(int(data_0[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_0[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps1 = []

        tank1 = Function('tank1', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_1)):

                timestamps1.append(int(data_1[j][0] * multiplier))

                s.add(tank1(int(data_1[j][0] * multiplier)) == data_1[j][1])

                if(int(data_1[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_1[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps2 = []

        tank2 = Function('tank2', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_2)):

                timestamps2.append(int(data_2[j][0] * multiplier))

                s.add(tank2(int(data_2[j][0] * multiplier)) == data_2[j][1])

                if(int(data_2[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_2[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps3 = []

        tank3 = Function('tank3', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_3)):

                timestamps3.append(int(data_3[j][0] * multiplier))

                s.add(tank3(int(data_3[j][0] * multiplier)) == data_3[j][1])

                if(int(data_3[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_3[j][0] * multiplier == sigDur:

                    entryFound = False

        i += 1

        # force terminate after one loop
        entryFound = False

        # ===== READ DATA END ===== #

        # ===== CONCUT FLOW START ===== #

        # global clock to local clock mappings
        c0 = Function('c0', IntSort(), IntSort())
        s.add(And([Or([c0(i) == ((i - eps) + j) for j in range(2 * int(eps) + 1)]) for i in range(timestamps0[0], timestamps0[-1] + 1)]))
        s.add(Not(Or(c0(timestamps0[0]) == timestamps0[0] - 1, c0(timestamps0[-1]) == timestamps0[-1] + 1)))

        c1 = Function('c1', IntSort(), IntSort())
        s.add(And([Or([c1(i) == ((i - eps) + j) for j in range(2 * int(eps) + 1)]) for i in range(timestamps1[0], timestamps1[-1] + 1)]))
        s.add(Not(Or(c1(timestamps1[0]) == timestamps1[0] - 1, c1(timestamps1[-1]) == timestamps1[-1] + 1)))

        c2 = Function('c2', IntSort(), IntSort())
        s.add(And([Or([c2(i) == ((i - eps) + j) for j in range(2 * int(eps) + 1)]) for i in range(timestamps2[0], timestamps2[-1] + 1)]))
        s.add(Not(Or(c2(timestamps2[0]) == timestamps2[0] - 1, c2(timestamps2[-1]) == timestamps2[-1] + 1)))

        c3 = Function('c3', IntSort(), IntSort())
        s.add(And([Or([c3(i) == ((i - eps) + j) for j in range(2 * int(eps) + 1)]) for i in range(timestamps3[0], timestamps3[-1] + 1)]))
        s.add(Not(Or(c3(timestamps3[0]) == timestamps3[0] - 1, c3(timestamps3[-1]) == timestamps3[-1] + 1)))

        # local clocks are bound by epsilon
        s.add(And([And(c0(i) - c1(i) <= eps, c0(i) - c1(i) >= -eps) for i in range(timestamps0[0], timestamps0[-1] + 1)]))
        s.add(And([And(c1(i) - c2(i) <= eps, c1(i) - c2(i) >= -eps) for i in range(timestamps1[0], timestamps1[-1] + 1)]))
        s.add(And([And(c2(i) - c0(i) <= eps, c2(i) - c0(i) >= -eps) for i in range(timestamps2[0], timestamps2[-1] + 1)]))

        s.add(And([And(c0(i) - c3(i) <= eps, c0(i) - c3(i) >= -eps) for i in range(timestamps3[0], timestamps3[-1] + 1)]))
        s.add(And([And(c1(i) - c3(i) <= eps, c1(i) - c3(i) >= -eps) for i in range(timestamps3[0], timestamps3[-1] + 1)]))
        s.add(And([And(c2(i) - c3(i) <= eps, c2(i) - c3(i) >= -eps) for i in range(timestamps3[0], timestamps3[-1] + 1)]))

        # global clock to local clock mappings are ordered
        s.add(And([And([Implies(i <= j, And(c0(i) <= c0(j), c1(i) <= c1(j), c2(i) <= c2(j), c3(i) <= c3(j))) for j in range(timestamps0[0], timestamps0[-1] + 1)]) for i in range(timestamps0[0], timestamps0[-1] + 1)]))

        # consistent cut flow
        c_flow = Function('c_flow', IntSort(), RealSort())
        # c_flow = Function('c_flow', IntSort(), IntSort())

        # addition
        s.add(And([c_flow(i) == (tank0(c0(i)) + tank1(c1(i)) + tank2(c2(i)) + tank3(c3(i))) for i in range(timestamps0[0], timestamps0[-1] + 1)]))

        # violation check
        v = Real('v')
        s.add(And(v >= timestamps0[0], v <= timestamps0[-1]))

        s.add(ForAll(v, Implies(And(v >= timestamps0[0], v <= timestamps0[-1]), z3Interpolate(c_flow, v) >= 20)))
        # s.add(z3Interpolate(c_flow, v) == 15)
        # s.add(v == 10)

        if s.check() == sat:

            m = s.model()
            # out = "%s %s" % (m[test], m[test2])
            # print(m)

        s.reset()


def z3Interpolate(f, p):

    return (f(ToInt(p)) + ((f(ToInt(p) + 1) - f(ToInt(p))) * (p - ToInt(p))))


def z3Abs(x):

    return If(x >= 0, x, -x)


def z3SqDist3d(x1, x2, y1, y2, z1, z2):

    return (((x2 - x1) * (x2 - x1)) + ((y2 - y1) * (y2 - y1)) + ((z2 - z1) * (z2 - z1)))


def z3SqDist2d(x1, x2, y1, y2):

    return (((x2 - x1) * (x2 - x1)) + ((y2 - y1) * (y2 - y1)))


def z3SqDist1d(x1, x2):

    return z3Abs(x2 - x1)


def getDataTank(agent_ID):

    file = open('data/wt/s5_tank_{}'.format(agent_ID))
    line = file.readline()

    data = []

    while line:

        param = line.split('\t')

        values = []

        for i in range(2):

            values.append(float(param[i].strip()))

        data.append(values)

        line = file.readline()

    file.close()

    # print(data)

    return data


def main():

    repeat = 10
    eps = 0.05

    agents2 = True
    agents3 = True
    agents4 = True

    if len(sys.argv) == 3:

        epsTemp = max(float(sys.argv[1]), 0.01)
        eps = min(epsTemp, 0.05)
        agentsTemp = max(int(sys.argv[2]), 2)
        agents = min(agentsTemp, 4)

        if agents == 2:

            agents3 = False
            agents4 = False

        if agents == 3:

            agents2 = False
            agents4 = False

        if agents == 4:

            agents2 = False
            agents3 = False

    print("Reproducing experiments...\n")

    print("Pressure level safety property:\n")

    print("\t Duration 1s\t\t Duration 2s\t\t Duration 3s\t\t Duration 4s\t\t Duration 5s", end = " ")

    if agents2:

        print("\n\n2 Tanks\t", end = " ")

        for i in range(5):

            total_time = 0

            for j in range(repeat):

                start = time.time()
                prog_tanks_pressure(eps, i + 1, 1)
                end = time.time()
                dur = end - start
                total_time += dur

            print("{}\t".format(total_time / repeat), end = " ")

    if agents3:

        print("\n\n3 Tanks\t", end = " ")

        for i in range(5):

            total_time = 0

            for j in range(repeat):

                start = time.time()
                prog_tanks_pressure_3(eps, i + 1, 1)
                end = time.time()
                dur = end - start
                total_time += dur

            print("{}\t".format(total_time / repeat), end = " ")

    if agents4:

        print("\n\n4 Tanks\t", end = " ")

        for i in range(5):

            total_time = 0

            for j in range(repeat):

                start = time.time()
                prog_tanks_pressure_4(eps, i + 1, 1)
                end = time.time()
                dur = end - start
                total_time += dur

            print("{}\t".format(total_time / repeat), end = " ")


if __name__ == '__main__':

    main()
    pass

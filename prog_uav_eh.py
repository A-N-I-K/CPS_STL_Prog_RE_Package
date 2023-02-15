'''
@author: ANIK
'''

from multiprocessing import freeze_support
import multiprocessing
import time

from z3 import *
from z3.z3 import ForAll

# set_param('parallel.enable', True)
set_option(rational_to_decimal = True)


def prog_uav_hover(eps, sigDur, segCount, segID):

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

    data_0 = getTankData("s{}_uav_0".format(segID))
    data_1 = getTankData("s{}_uav_1".format(segID))

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

        drone0_z = Function('drone0_z', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_0)):

                timestamps0.append(int(data_0[j][0] * multiplier))

                s.add(drone0_z(int(data_0[j][0] * multiplier)) == data_0[j][3])

                if(int(data_0[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_0[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps1 = []

        drone1_z = Function('drone1_z', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_1)):

                timestamps1.append(int(data_1[j][0] * multiplier))

                s.add(drone1_z(int(data_1[j][0] * multiplier)) == data_1[j][3])

                if(int(data_1[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_1[j][0] * multiplier == sigDur:

                    entryFound = False

        # if segmentUpperBound ==

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

        # ===== HOVER START ===== #

        # hover
        s.add(And([Or(c_flow(i) == (drone0_z(c0(i)) + drone1_z(c1(i))), c_flow(i) == z3Abs(drone0_z(c0(i)) - drone1_z(c1(i)))) for i in range(timestamps0[0], timestamps0[-1] + 1)]))
        # s.add(And([(c_flow(i) == (drone0_z(c0(i)) + drone1_z(c1(i)))) for i in range(timestamps0[0], timestamps0[-1] + 1)]))

        # violation check (1s, 2s)
        if segID == 1 or segID == 2:

            v = Real('v')
            s.add(And(v >= timestamps0[0], v <= timestamps0[-1]))

            s.add(z3Interpolate(c_flow, v) > 0)

        # violation check (2s)
        if segID == 2:

            w = Real('w')
            s.add(And(w > v, w <= timestamps0[-1]))

            s.add(ForAll(w, Implies(And(w >= v, w <= timestamps0[-1]), z3Interpolate(c_flow, w) <= 10)))

        # violation check (3s, 4s, 5s)
        if segID == 3 or segID == 4 or segID == 5:

            u = Real('u')
            s.add(And(u >= timestamps0[0], u <= timestamps0[-1]))

            s.add(ForAll(u, Implies(And(u >= timestamps0[0], u <= timestamps0[-1]), z3Interpolate(c_flow, u) <= 10)))

        # s.add(z3Interpolate(c_flow, v) == 15)
        # s.add(v == 10)

        # ===== HOVER END ===== #

        # ===== TEST SMT END ===== #

        start = time.time()

        if s.check() == sat:

            m = s.model()
            # out = "%s %s" % (m[test], m[test2])
            # print(m)

        end = time.time()

        # else:
        #
        #     print("unsat")

        s.reset()

        dur = end - start
        return dur


def prog_uav_hover_3(eps, sigDur, segCount, segID):

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

    data_0 = getTankData("s{}_uav_0".format(segID))
    data_1 = getTankData("s{}_uav_1".format(segID))
    data_2 = getTankData("s{}_uav_2".format(segID))

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

        drone0_z = Function('drone0_z', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_0)):

                timestamps0.append(int(data_0[j][0] * multiplier))

                s.add(drone0_z(int(data_0[j][0] * multiplier)) == data_0[j][3])

                if(int(data_0[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_0[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps1 = []

        drone1_z = Function('drone1_z', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_1)):

                timestamps1.append(int(data_1[j][0] * multiplier))

                s.add(drone1_z(int(data_1[j][0] * multiplier)) == data_1[j][3])

                if(int(data_1[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_1[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps2 = []

        drone2_z = Function('drone2_z', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_2)):

                timestamps2.append(int(data_2[j][0] * multiplier))

                s.add(drone2_z(int(data_2[j][0] * multiplier)) == data_2[j][3])

                if(int(data_2[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_2[j][0] * multiplier == sigDur:

                    entryFound = False

        # if segmentUpperBound ==

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

        # ===== HOVER START ===== #

        # hover
        s.add(And([Or(c_flow(i) == (drone0_z(c0(i)) + drone1_z(c1(i)) + drone2_z(c2(i))),
                      c_flow(i) == z3Abs(drone0_z(c0(i)) - drone1_z(c1(i))),
                      c_flow(i) == z3Abs(drone1_z(c1(i)) - drone2_z(c2(i))),
                      c_flow(i) == z3Abs(drone2_z(c2(i)) - drone0_z(c0(i)))) for i in range(timestamps0[0], timestamps0[-1] + 1)]))

        # violation check (1s, 2s)

        v = Real('v')
        s.add(And(v >= timestamps0[0], v <= timestamps0[-1]))

        s.add(z3Interpolate(c_flow, v) > 0)

        # violation check (1s, 2s)
        if segID == 1 or segID == 2:

            v = Real('v')
            s.add(And(v >= timestamps0[0], v <= timestamps0[-1]))

            s.add(z3Interpolate(c_flow, v) > 0)

        # violation check (2s)
        if segID == 2:

            w = Real('w')
            s.add(And(w > v, w <= timestamps0[-1]))

            s.add(ForAll(w, Implies(And(w >= v, w <= timestamps0[-1]), z3Interpolate(c_flow, w) <= 10)))

        # violation check (3s, 4s, 5s)
        if segID == 3 or segID == 4 or segID == 5:

            u = Real('u')
            s.add(And(u >= timestamps0[0], u <= timestamps0[-1]))

            s.add(ForAll(u, Implies(And(u >= timestamps0[0], u <= timestamps0[-1]), z3Interpolate(c_flow, u) <= 10)))

        # s.add(z3Interpolate(c_flow, v) == 15)
        # s.add(v == 10)

        # ===== HOVER END ===== #

        # ===== TEST SMT END ===== #

        start = time.time()

        if s.check() == sat:

            m = s.model()
            # out = "%s %s" % (m[test], m[test2])
            # print(m)

        end = time.time()

        # else:
        #
        #     print("unsat")

        s.reset()

        dur = end - start
        return dur


def prog_uav_hover_4_old(eps, sigDur, segCount, segID):

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

    data_0 = getTankData("s{}_uav_0".format(segID))
    data_1 = getTankData("s{}_uav_1".format(segID))
    data_2 = getTankData("s{}_uav_2".format(segID))
    data_3 = getTankData("s{}_uav_3".format(segID))

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

        drone0_z = Function('drone0_z', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_0)):

                timestamps0.append(int(data_0[j][0] * multiplier))

                s.add(drone0_z(int(data_0[j][0] * multiplier)) == data_0[j][3])

                if(int(data_0[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_0[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps1 = []

        drone1_z = Function('drone1_z', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_1)):

                timestamps1.append(int(data_1[j][0] * multiplier))

                s.add(drone1_z(int(data_1[j][0] * multiplier)) == data_1[j][3])

                if(int(data_1[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_1[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps2 = []

        drone2_z = Function('drone2_z', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_2)):

                timestamps2.append(int(data_2[j][0] * multiplier))

                s.add(drone2_z(int(data_2[j][0] * multiplier)) == data_2[j][3])

                if(int(data_2[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_2[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps3 = []

        drone3_z = Function('drone3_z', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_3)):

                timestamps3.append(int(data_3[j][0] * multiplier))

                s.add(drone3_z(int(data_3[j][0] * multiplier)) == data_3[j][3])

                if(int(data_3[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_3[j][0] * multiplier == sigDur:

                    entryFound = False

        # if segmentUpperBound ==

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
        s.add(And([And(c0(i) - c2(i) <= eps, c0(i) - c2(i) >= -eps) for i in range(timestamps0[0], timestamps0[-1] + 1)]))
        s.add(And([And(c0(i) - c3(i) <= eps, c0(i) - c3(i) >= -eps) for i in range(timestamps0[0], timestamps0[-1] + 1)]))
        s.add(And([And(c1(i) - c2(i) <= eps, c1(i) - c2(i) >= -eps) for i in range(timestamps1[0], timestamps1[-1] + 1)]))
        s.add(And([And(c1(i) - c3(i) <= eps, c1(i) - c3(i) >= -eps) for i in range(timestamps1[0], timestamps1[-1] + 1)]))
        s.add(And([And(c2(i) - c3(i) <= eps, c2(i) - c3(i) >= -eps) for i in range(timestamps2[0], timestamps2[-1] + 1)]))

        # global clock to local clock mappings are ordered
        s.add(And([And([Implies(i <= j, And(c0(i) <= c0(j), c1(i) <= c1(j), c2(i) <= c2(j), c3(i) <= c3(j))) for j in range(timestamps0[0], timestamps0[-1] + 1)]) for i in range(timestamps0[0], timestamps0[-1] + 1)]))

        # consistent cut flow
        c_flow = Function('c_flow', IntSort(), RealSort())
        # c_flow = Function('c_flow', IntSort(), IntSort())

        # ===== HOVER START ===== #

        # hover
        s.add(And([Or(c_flow(i) == (drone0_z(c0(i)) + drone1_z(c1(i)) + drone2_z(c2(i)) + drone3_z(c3(i))),
                      c_flow(i) == z3Abs(drone0_z(c0(i)) - drone1_z(c1(i))),
                      c_flow(i) == z3Abs(drone0_z(c0(i)) - drone2_z(c2(i))),
                      c_flow(i) == z3Abs(drone0_z(c0(i)) - drone3_z(c3(i))),
                      c_flow(i) == z3Abs(drone1_z(c1(i)) - drone2_z(c2(i))),
                      c_flow(i) == z3Abs(drone1_z(c1(i)) - drone3_z(c3(i))),
                      c_flow(i) == z3Abs(drone2_z(c2(i)) - drone3_z(c3(i)))) for i in range(timestamps0[0], timestamps0[-1] + 1)]))

        # violation check (1s, 2s)

        v = Real('v')
        s.add(And(v >= timestamps0[0], v <= timestamps0[-1]))

        s.add(z3Interpolate(c_flow, v) > 0)

        # violation check (1s, 2s)
        if segID == 1 or segID == 2:

            v = Real('v')
            s.add(And(v >= timestamps0[0], v <= timestamps0[-1]))

            s.add(z3Interpolate(c_flow, v) > 0)

        # violation check (2s)
        if segID == 2:

            w = Real('w')
            s.add(And(w > v, w <= timestamps0[-1]))

            s.add(ForAll(w, Implies(And(w >= v, w <= timestamps0[-1]), z3Interpolate(c_flow, w) <= 10)))

        # violation check (3s, 4s, 5s)
        if segID == 3 or segID == 4 or segID == 5:

            u = Real('u')
            s.add(And(u >= timestamps0[0], u <= timestamps0[-1]))

            s.add(ForAll(u, Implies(And(u >= timestamps0[0], u <= timestamps0[-1]), z3Interpolate(c_flow, u) <= 10)))

        # s.add(z3Interpolate(c_flow, v) == 15)
        # s.add(v == 10)

        # ===== HOVER END ===== #

        # ===== TEST SMT END ===== #

        start = time.time()

        if s.check() == sat:

            m = s.model()
            # out = "%s %s" % (m[test], m[test2])
            # print(m)

        end = time.time()

        # else:
        #
        #     print("unsat")

        s.reset()

        dur = end - start
        return dur


def prog_uav_hover_4(eps, sigDur, segCount, segID):

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

    data_0 = getTankData("s{}_uav_0".format(segID))
    data_1 = getTankData("s{}_uav_1".format(segID))
    data_2 = getTankData("s{}_uav_2".format(segID))
    data_3 = getTankData("s{}_uav_3".format(segID))

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

        drone0_z = Function('drone0_z', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_0)):

                timestamps0.append(int(data_0[j][0] * multiplier))

                s.add(drone0_z(int(data_0[j][0] * multiplier)) == data_0[j][3])

                if(int(data_0[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_0[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps1 = []

        drone1_z = Function('drone1_z', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_1)):

                timestamps1.append(int(data_1[j][0] * multiplier))

                s.add(drone1_z(int(data_1[j][0] * multiplier)) == data_1[j][3])

                if(int(data_1[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_1[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps2 = []

        drone2_z = Function('drone2_z', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_2)):

                timestamps2.append(int(data_2[j][0] * multiplier))

                s.add(drone2_z(int(data_2[j][0] * multiplier)) == data_2[j][3])

                if(int(data_2[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_2[j][0] * multiplier == sigDur:

                    entryFound = False

        timestamps3 = []

        drone3_z = Function('drone3_z', IntSort(), RealSort())

        for j in range ((segmentLowerBound + 0), (segmentUpperBound + 1)):

            if(j >= 0 and j < len(data_3)):

                timestamps3.append(int(data_3[j][0] * multiplier))

                s.add(drone3_z(int(data_3[j][0] * multiplier)) == data_3[j][3])

                if(int(data_3[j][0] * multiplier) > (i * segmentDuration)):

                    entryFound = True

                if data_3[j][0] * multiplier == sigDur:

                    entryFound = False

        # if segmentUpperBound ==

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
        s.add(And([And(c0(i) - c2(i) <= eps, c0(i) - c2(i) >= -eps) for i in range(timestamps0[0], timestamps0[-1] + 1)]))
        s.add(And([And(c0(i) - c3(i) <= eps, c0(i) - c3(i) >= -eps) for i in range(timestamps0[0], timestamps0[-1] + 1)]))
        s.add(And([And(c1(i) - c2(i) <= eps, c1(i) - c2(i) >= -eps) for i in range(timestamps1[0], timestamps1[-1] + 1)]))
        s.add(And([And(c1(i) - c3(i) <= eps, c1(i) - c3(i) >= -eps) for i in range(timestamps1[0], timestamps1[-1] + 1)]))
        s.add(And([And(c2(i) - c3(i) <= eps, c2(i) - c3(i) >= -eps) for i in range(timestamps2[0], timestamps2[-1] + 1)]))

        # global clock to local clock mappings are ordered
        s.add(And([And([Implies(i <= j, And(c0(i) <= c0(j), c1(i) <= c1(j), c2(i) <= c2(j), c3(i) <= c3(j))) for j in range(timestamps0[0], timestamps0[-1] + 1)]) for i in range(timestamps0[0], timestamps0[-1] + 1)]))

        # consistent cut flow
        c_flow = Function('c_flow', IntSort(), RealSort())
        # c_flow = Function('c_flow', IntSort(), IntSort())

        # ===== HOVER START ===== #

        # hover
        s.add(And([Or(c_flow(i) == (drone0_z(c0(i)) + drone1_z(c1(i)) + drone2_z(c2(i)) + drone3_z(c3(i))),
                      c_flow(i) == z3Abs(drone0_z(c0(i)) - drone1_z(c1(i))),
                      c_flow(i) == z3Abs(drone1_z(c1(i)) - drone2_z(c2(i))),
                      c_flow(i) == z3Abs(drone2_z(c2(i)) - drone3_z(c3(i))),
                      c_flow(i) == z3Abs(drone3_z(c3(i)) - drone0_z(c0(i)))) for i in range(timestamps0[0], timestamps0[-1] + 1)]))

        # violation check (1s, 2s)

        v = Real('v')
        s.add(And(v >= timestamps0[0], v <= timestamps0[-1]))

        s.add(z3Interpolate(c_flow, v) > 0)

        # violation check (1s, 2s)
        if segID == 1 or segID == 2:

            v = Real('v')
            s.add(And(v >= timestamps0[0], v <= timestamps0[-1]))

            s.add(z3Interpolate(c_flow, v) > 0)

        # violation check (2s)
        if segID == 2:

            w = Real('w')
            s.add(And(w > v, w <= timestamps0[-1]))

            s.add(ForAll(w, Implies(And(w >= v, w <= timestamps0[-1]), z3Interpolate(c_flow, w) <= 10)))

        # violation check (3s, 4s, 5s)
        if segID == 3 or segID == 4 or segID == 5:

            u = Real('u')
            s.add(And(u >= timestamps0[0], u <= timestamps0[-1]))

            s.add(ForAll(u, Implies(And(u >= timestamps0[0], u <= timestamps0[-1]), z3Interpolate(c_flow, u) <= 10)))

        # s.add(z3Interpolate(c_flow, v) == 15)
        # s.add(v == 10)

        # ===== HOVER END ===== #

        # ===== TEST SMT END ===== #

        start = time.time()

        if s.check() == sat:

            m = s.model()
            # out = "%s %s" % (m[test], m[test2])
            # print(m)

        end = time.time()

        # else:
        #
        #     print("unsat")

        s.reset()

        dur = end - start
        return dur


def getTankData(agent_ID):

    file = open('data/uav/{}'.format(agent_ID))
    line = file.readline()

    data = []

    while line:

        param = line.split('\t')

        values = []

        for i in range(4):

            values.append(float(param[i].strip()))

        data.append(values)

        line = file.readline()

    file.close()

    # print(data)

    return data


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


def main():

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

    print("Eventually hover:\n")

    repeat = 4
    multiproc = False;

    print("\t\tSegment 1\t\tSegment 2\t\tSegment 3\t\tSegment 4\t\tSegment 5", end = "")

    if agents2:

        print("\n\n2 Agents\t", end = "")

        for i in range(5):

            total_time = 0

            if multiproc:

                pool = multiprocessing.Pool()

                inputs = [(eps, 1, 1, i + 1) for j in range(repeat)]
                outputs = pool.starmap(prog_uav_hover, inputs)

                total_time = sum(outputs)

            else:

                for j in range(repeat):

                    start = time.time()
                    # prog_uav_hover(eps, 1, 1, i + 1)
                    end = time.time()
                    dur = end - start
                    total_time += prog_uav_hover(eps, 1, 1, i + 1)

            print("{}\t".format(total_time / repeat), end = "")

    if agents3:

        print("\n\n3 Agents\t", end = "")

        for i in range(5):

            total_time = 0

            if multiproc:

                pool = multiprocessing.Pool()

                inputs = [(eps, 1, 1, i + 1) for j in range(repeat)]
                outputs = pool.starmap(prog_uav_hover_3, inputs)

                total_time = sum(outputs)

            else:

                for j in range(repeat):

                    start = time.time()
                    # prog_uav_hover_3(eps, 1, 1, i + 1)
                    end = time.time()
                    dur = end - start
                    total_time += prog_uav_hover_3(eps, 1, 1, i + 1)

            print("{}\t".format(total_time / repeat), end = "")

    if agents4:

        print("\n\n4 Agents\t", end = "")

        for i in range(5):

            total_time = 0

            if multiproc:

                pool = multiprocessing.Pool()

                inputs = [(eps, 1, 1, i + 1) for j in range(repeat)]
                outputs = pool.starmap(prog_uav_hover_4, inputs)

                total_time = sum(outputs)

            else:

                for j in range(repeat):

                    start = time.time()
                    # prog_uav_hover_4(eps, 1, 1, i + 1)
                    end = time.time()
                    dur = end - start
                    total_time += prog_uav_hover_4(eps, 1, 1, i + 1)

            print("{}\t".format(total_time / repeat), end = "")

    print()


if __name__ == '__main__':

    # freeze_support()
    main()
    pass

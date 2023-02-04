
# Repeatability Evaluation Package for Monitoring Signal Temporal Logic in Distributed Cyber-physical Systems

This is a Repeatability Evaluation Package for the ICCPS 2023 paper Monitoring Signal Temporal Logic in Distributed Cyber-physical Systems.

## Installation Instructions

- Clone this repository on an Ubuntu (22.04) desktop or server machine with Python 3.1+ installed.
- Install the following dependancy packages:
     - [Z3 Theorem Prover](https://github.com/Z3Prover/z3)
     - [TreeLib Tool](https://github.com/caesar0301/treelib)
     - [Algebraic Expression Parser](https://github.com/mohamedsalahh/Algebraic-Expression-Parser)
- Execute the Python scripts from within the CPS_STL_Prog_RE_Package directory to generate results reported in the paper Monitoring Signal Temporal Logic in Distributed Cyber-physical Systems.
- Alternatively an Open Virtual Appliance file with all the prerequisites installed can be obtained from [here](https://drive.google.com/drive/u/1/folders/1IcoNuNLWhI4AHDvDWieHcKazeUa9qhJA).

## Repeatability Evaluation Package Elements

**STL formula to SMT syntax tree conversion and SMT syntax tree partitioning tool.**

Usage:

```
python3 tp_tool.py <STL formula> <time>
```

Where the required arguments are an STL formula (string) and a partition time (float) respectively.

Examples:

```
python3 tp_tool.py "F[0, 10]p" 5
python3 tp_tool.py "F[0, 10](p AND G[0, 5] ~q)" 5
```

**Script for monitoring different flight properties.**

Usage:

```
python3 prog_uav.py <eps> <agents>
```

Where the required arguments are 𝜀 and number of agents respectively.

Examples:

```
python3 prog_uav.py 0.05 3
python3 prog_uav.py
```

**Script for measuring the false positive verdicts.**

Usage:

```
python3 measure_false_positives.py <eps>
```

Where the required argument is 𝜀.

Examples:

```
python3 measure_false_positives.py 0.45
python3 measure_false_positives.py
```

**Script for monitoring impact of segment duration and number of water tanks on runtime.**

Usage:

```
python3 prog_tank.py <eps> <tanks>
```

Where the required arguments are 𝜀 and number of water tanks respectively.

Examples:

```
python3 prog_tank.py 0.05 3
python3 prog_tank.py
```
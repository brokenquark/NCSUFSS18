import csv, re, Utils, math, sys, Node, timeit, os, psutil, numpy as np

dts = 'lb'
sz = 25

def readRowsLineByLine(csvFile, classIndex, split, root, d, n, t, s):

    if dts == 'ab': ln = 71443
    if dts == 'lb': ln = 19724
    if dts == 'lm': ln = 5693
    if dts == 'md': ln = 1172

    list = []
    numeric = []
    categorical = []
    chunks = []
    streamIndex = 0
    loc = 0
    for row in Utils.csvRowsGenerator(csvFile):
        attributeIndex = 0
        dictionary = {}
        for item in row:
            isNumeric = None
            if Utils.getType(item.strip()) is "num":
                item = float(item.strip())
                isNumeric = True
            elif Utils.getType(item.strip()) is "str":
                item = str(item.strip())
                isNumeric = False
            else:
                return
            if attributeIndex == classIndex:
                dictionary['class'] = item
            else:
                key = 'a' + str(attributeIndex)
                dictionary[key] = item
                if streamIndex is 0:
                    if isNumeric:
                        numeric.append(key)
                    else:
                      categorical.append(key)

            attributeIndex = attributeIndex + 1
        list.append(dictionary)

        root.numeric = numeric
        root.categorical = categorical

        if root.deadEnd == False:
            Node.visitTree(root, dictionary, minDepth=d, pushExamplesToLeaf=False, isAdaptive=False, nmin=n, tie=t, split=s)

        else:
            # print(f'finished building the tree with {streamIndex} examples')
            break

        streamIndex = streamIndex + 1




        if streamIndex%100 is 0:
            pass
            # print(f'{streamIndex} examples processed so far...')
            # process = psutil.Process(os.getpid())
            # memory = process.memory_info()[0] / float(2 ** 20)
            # print(memory)

        if streamIndex >= (ln*split)/100 :
            # print(f'loc read: {loc}')
            break

    return list, chunks, root, loc

def readRowsForTest(csvFile, classIndex, split, root):
    list = []
    numeric = []
    categorical = []
    chunks = []
    streamIndex = 0
    hits = []
    miss = []
    predictionMatrix = []
    for row in Utils.csvRowsGenerator(csvFile):
        # if streamIndex > split:
        if True:
            attributeIndex = 0
            dictionary = {}
            for item in row:
                isNumeric = None
                if Utils.getType(item.strip()) is "num":
                    item = float(item.strip())
                    isNumeric = True
                elif Utils.getType(item.strip()) is "str":
                    item = str(item.strip())
                    isNumeric = False
                else:
                    return
                if attributeIndex == classIndex:
                    dictionary['class'] = item
                else:
                    key = 'a' + str(attributeIndex)
                    dictionary[key] = item
                    if streamIndex is 0:
                        if isNumeric:
                            numeric.append(key)
                        else:
                          categorical.append(key)

                attributeIndex = attributeIndex + 1
            list.append(dictionary)

            root.numeric = numeric
            root.categorical = categorical

            Node.visiTreeForTest(root, dictionary, hits, miss, predictionMatrix)

        streamIndex = streamIndex + 1

        if streamIndex%100000 is 0:
            pass
            # print(f'{streamIndex} examples processed so far...')

    # print(f'finished building the tree with {len(hits)+len(miss)} examples')
    # print(f'{len(hits)} # {len(miss)}')

    return Utils.calCulateFMeasure(predictionMatrix)

def de(fobj, bounds, mut=0.8, crossp=0.7, popsize=20, its=1000):
    dimensions = len(bounds)
    pop = np.random.rand(popsize, dimensions)
    min_b, max_b = np.asarray(bounds).T
    diff = np.fabs(min_b - max_b)
    pop_denorm = min_b + pop * diff
    fitness = np.asarray([fobj(ind) for ind in pop_denorm])
    best_idx = np.argmin(fitness)
    best = pop_denorm[best_idx]
    for i in range(its):
        print(i)
        for j in range(popsize):
            idxs = [idx for idx in range(popsize) if idx != j]
            a, b, c = pop[np.random.choice(idxs, 3, replace = False)]
            mutant = np.clip(a + mut * (b - c), 0, 1)
            cross_points = np.random.rand(dimensions) < crossp
            if not np.any(cross_points):
                cross_points[np.random.randint(0, dimensions)] = True
            trial = np.where(cross_points, mutant, pop[j])
            trial_denorm = min_b + trial * diff
            f = fobj(trial_denorm)
            if f < fitness[j]:
                fitness[j] = f
                pop[j] = trial
                if f < fitness[best_idx]:
                    best_idx = j
                    best = trial_denorm
        yield best, fitness[best_idx]

def obj(args):
    root = Node.Node('root')
    result = readRowsLineByLine(f'{dts}-train.csv', 0, sz, root, math.floor(args[0]), math.floor(args[1]), args[2], math.floor(args[3])  )
    root.deadEnd = False
    try:
        result = readRowsForTest(f'{dts}-test.csv', 0, 0, root)
    except:
        result = [0,0,0]
    root = None
    r = result[2] * 100
    return 100 - r

print(f'{dts} vfdt {sz}')
it = list(de(obj, bounds=[ (2,20), (5,500), (.001, .99), (5,500)  ], its=10))

print(100 - it[-1][1])

for index in range(-1, -2, -1):
    depth = math.floor(it[index][0][0])
    nmin = math.floor(it[index][0][1])
    tau = it[index][0][2]
    split = math.floor(it[index][0][3])
    root = Node.Node('root')
    result = readRowsLineByLine(f'{dts}-train.csv', 0, 25, root, math.floor(depth), math.floor(nmin), tau, math.floor(split))
    root.deadEnd = False
    result = readRowsForTest(f'{dts}-test.csv', 0, 0, root)
    root = None
    print(f'{result[2]}')
    root = Node.Node('root')
    result = readRowsLineByLine(f'{dts}-train.csv', 0, 50, root, math.floor(depth), math.floor(nmin), tau,
                                math.floor(split))
    root.deadEnd = False
    result = readRowsForTest(f'{dts}-test.csv', 0, 0, root)
    root = None
    print(f'{result[2]}')
    root = Node.Node('root')
    result = readRowsLineByLine(f'{dts}-train.csv', 0, 75, root, math.floor(depth), math.floor(nmin), tau,
                                math.floor(split))
    root.deadEnd = False
    result = readRowsForTest(f'{dts}-test.csv', 0, 0, root)
    root = None
    print(f'{result[2]}')
    root = Node.Node('root')
    result = readRowsLineByLine(f'{dts}-train.csv', 0, 100, root, math.floor(depth), math.floor(nmin), tau, math.floor(split))
    root.deadEnd = False
    result = readRowsForTest(f'{dts}-test.csv', 0, 0, root)
    root = None
    print(f'{result[2]}')

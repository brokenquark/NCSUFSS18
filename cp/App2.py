import csv, re, Utils, math, sys

def readRowsLineByLine(csvFile, classIndex):
    list = []
    numeric = []
    categorical = []
    chunks = []
    streamIndex = 0
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
        streamIndex = streamIndex + 1

        if streamIndex%120 is 0:
            pass

            splits = []
            chunks = []


            for item in numeric:
                out = Utils.getBestSplitNumeric(list, item)
                splits.append(out[0])
                for item in out[1]:
                    chunks.append(item)


            for item in categorical:
                out = Utils.getBestSplitCategorical(list, item)
                splits.append(out[0])
                for item in out[1]:
                    chunks.append(item)

            numOfAttributes = len(row) - 1
            splits.sort(key=lambda k: k['averageEntropy'])
            min = splits[0]['averageEntropy']
            # max = splits[-1]['averageEntropy']
            max = splits[ math.floor( math.sqrt(numOfAttributes) ) ]['averageEntropy']
            criticalPoint = (max - min) / math.sqrt(numOfAttributes)
            # criticalPoint = (max - min) / numOfAttributes

            delta = .05
            unique = Utils.retrieveSet(list, 'class')
            epsilon = math.log(len(unique), math.e) * math.sqrt(( math.log(1/delta, math.e) ) / streamIndex)
            print(f'distance: {epsilon - criticalPoint}, total inputs: {streamIndex}')

            if epsilon - criticalPoint < 0:
                print("success")
                return list, chunks

    return list, chunks





# result = readRowsLineByLine("/media/rr/8E30E13030E12047/bigdata/higgs.csv", classIndex=0)
result = readRowsLineByLine("iris.csv", classIndex=4)
# result = readRowsLineByLine("weatherLong.csv", classIndex=4)
# result = readRowsLineByLine("d.csv", classIndex=0)
# result = readRowsLineByLine("data.csv", classIndex=0)

list = result[0]
chunks = result[1]
tree = []

while True:
    out = Utils.FFT(list, chunks)
    if len(chunks) == 0 or len(out[0]) == len(list):
        unique = Utils.retrieveSet(list, 'class')
        totalMatrix = [0] * len(unique)
        classMatrix = [''] * len(unique)

        classMatrixIndex = 0
        for item in unique:
            classMatrix[classMatrixIndex] = item
            classMatrixIndex = classMatrixIndex + 1

        for item in list:
            for index in range(0, len(unique)):
                if item['class'] == Utils.getFromSetByIndex(unique, index):
                    totalMatrix[index] = totalMatrix[index] + 1

        total = sum(totalMatrix)
        probabilityIndex = [0] * len(unique)
        for index in range(0, len(probabilityIndex)):
            probabilityIndex[index] = (totalMatrix[index] + .001) / (total + .001)

        tree.append({
            'type': 'leaf',
            'class': classMatrix,
            'probability': probabilityIndex
        })
        break
    list = out[0]
    chunks = out[1]
    tree.append(out[2])


def readTestData(csvFile, classIndex):
    list = []
    numeric = []
    categorical = []
    chunks = []
    streamIndex = 0
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
        streamIndex = streamIndex + 1
    return list


# testList = readTestData('test.csv', 0)
# testList = readTestData('test2.csv', 0)
testList = readTestData('test3.csv', 4)


testData = testList


hits = 0
miss = 0
unpredicted = 0
total = 0
for element in testData:
    predictedClass = None
    for item in tree:
        if item['type'] == 'numeric':
            x = element[item['attribute']]
            if item['min'] <= element[item['attribute']] <= item['max']:
                maxProbability = -1
                maxProbabilityIndex = 0
                for p in item['probability']:
                    if p > maxProbability:
                        maxProbability = p
                        predictedClass = item['class'][maxProbabilityIndex]
                    maxProbabilityIndex = maxProbabilityIndex + 1

        if item['type'] == 'categorical':
            x = element[item['attribute']]
            if item['value'] == element[item['attribute']]:
                maxProbability = -1
                maxProbabilityIndex = 0
                for p in item['probability']:
                    if p > maxProbability:
                        maxProbability = p
                        predictedClass = item['class'][maxProbabilityIndex]
                    maxProbabilityIndex = maxProbabilityIndex + 1

        if predictedClass != None and predictedClass == element['class']:
            # print(f'{predictedClass} {element["class"]} hit')
            hits = hits + 1
            break

        if predictedClass != None and predictedClass != element['class']:
            # print(f'{predictedClass} {element["class"]} miss')
            miss = miss + 1
            break

    if predictedClass == None:
        unpredicted = unpredicted + 1
        maxProbability = -1
        maxProbabilityIndex = 0
        for p in tree[-1]['probability']:
            if p > maxProbability:
                maxProbability = p
                predictedClass = tree[-1]['class'][maxProbabilityIndex]
            maxProbabilityIndex = maxProbabilityIndex + 1


        if predictedClass != None and predictedClass == element['class']:
            # print(f'{predictedClass} {element["class"]} hit')
            hits = hits + 1
            break

        if predictedClass != None and predictedClass != element['class']:
            # print(f'{predictedClass} {element["class"]} miss')
            miss = miss + 1
            break
        # pass


    total = total + 1


print(f'{100*(hits/total)}')
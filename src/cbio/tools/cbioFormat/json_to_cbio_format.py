import json, os, shutil, argparse

wordsToChangeDict = {"BEGINNING_DATE_OF_TREATMENT": "START_DATE", "END_DATE_OF_TREATMENT": "STOP_DATE",
                     "DATE": "DATE_OF_BIRTH", "PARTICIPANTID": "PATIENT_ID"}


def getCommandLineArguments():
    parser = argparse.ArgumentParser(
        description="Process the commandline arguments to cbioportal import format")
    parser.add_argument("-i", "--input", type=str, required=True, help="Input json file from Labkey.")
    parser.add_argument("-f", "--formatFile", type=str, required=True, help="Input json file from Labkey.")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output a directory to save new files.")

    return parser.parse_args()


def readFileToDictionary(fileName):
    with open(fileName) as inputFile:
        dictionary = json.loads(inputFile.read())

    return dictionary


def convertUnicodeToASCII(input):
    if isinstance(input, dict):
        return {convertUnicodeToASCII(key): convertUnicodeToASCII(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convertUnicodeToASCII(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def readDataToFormatSheets(dataFileName):
    inputDataWithUnicode = readFileToDictionary(dataFileName)
    inputData = convertUnicodeToASCII(inputDataWithUnicode)

    return inputData


def createDirectory(dirName):
    if (os.path.isdir(dirName)):
        shutil.rmtree(dirName)

    os.mkdir(dirName)


def getOutputDirectory():
    currectDirectoryPath = os.path.dirname(os.path.realpath(__file__))
    outputDirectory = os.path.join(currectDirectoryPath, outputDir)

    return outputDirectory


def renameColumnNames(inputList):
    outputList = []

    for val in inputList:
        val = val.upper()

        if val in wordsToChangeDict.keys():
            val = wordsToChangeDict.get(val)
        outputList.append(val)

    return outputList


def writeValuesToFile(datasetName, datasetRows):
    fileName = getOutputDirectory() + "/" + datasetName + ".txt"

    if os.path.isfile(fileName):
        open(fileName, 'w').close()  # Erase file content.

    with open(fileName, "w") as outputFile:
        isRowHeader = True

        for row in datasetRows:
            if (isRowHeader):
                header = orderedFormatForCbioDictionary[datasetName]
                renamedHeader = renameColumnNames(header)
                outputFile.write("\t".join(renamedHeader) + "\n")
                isRowHeader = False

            rowList = cBioFormat(datasetName, row)
            rowList = [str(i) for i in rowList]

            outputFile.write("\t".join(rowList) + "\n")

        print("From the dataset " + datasetName + ", the number of rows returned: " + str(len(datasetRows)))


def cBioFormat(datasetName, row):
    if datasetName in orderedFormatForCbioDictionary:

        orderedListOfColumns = orderedFormatForCbioDictionary[datasetName]
        outputLine = []

        for item in orderedListOfColumns:
            itemValue = row[item]
            if (type(itemValue) == str):
                itemValue = itemValue.strip()
                if (itemValue == "NA"):
                    itemValue = ""
            outputLine.append(itemValue)

        return outputLine
    return


def main():
    global outputDir
    global orderedFormatForCbioDictionary

    args = getCommandLineArguments()
    inputfile = args.input.lower()
    cBioFormatFile = args.formatFile
    outputDir = args.output.lower()
    createDirectory(outputDir)

    orderedFormatForCbioDictionary = readDataToFormatSheets(cBioFormatFile)

    unicodeDictionary = readFileToDictionary(inputfile)
    dictionary = convertUnicodeToASCII(unicodeDictionary)

    for key in dictionary.keys():
        writeValuesToFile(key, dictionary[key])


if __name__ == "__main__":
    main()

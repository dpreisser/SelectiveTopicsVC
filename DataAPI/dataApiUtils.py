
from dataApiReport import getDataTypeIdc


DEBUG = False


def trace( str1, str2, newLine=False ):

    global DEBUG

    if not DEBUG:
        return

    if newLine:
        print( str1 )
        print( str2 )
    else:
        print( str1 + " " + str2 )


def getIndentAsString( indentUnit, numIndentUnits ):
    return indentUnit * numIndentUnits


def formatMultiLine( multiLineStr, currentIndent ):

    formattedStr = ""

    currentIndentAsStr = getIndentAsString( "  ", currentIndent )

    lines = multiLineStr.split( "\n" )

    for line in lines:
        formattedStr += currentIndentAsStr + line + "\n"

    return formattedStr


def maxSize( multiLineStr ):

    lines = multiLineStr.split( "\n" )

    maxSize = -1

    for line in lines:
        size = len( line )
        if size > maxSize:
            maxSize = size

    return maxSize


def getDataAsString( tree ):

    dataAsString = ""

    currentIndent = int( tree["indent"] )
    currentIndentAsStr = getIndentAsString( "  ", currentIndent ) 

    label = tree["label"]
    value = tree["value"]

    if None != label:

        if None != value:
            newStr = label + ":"  + value + "\n"
        else:
            newStr = label + "\n"

        dataAsString += currentIndentAsStr + newStr

    children = tree["children"]
        
    for child in children:
        dataAsString += getDataAsString( child, "" )

    return dataAsString


def getDataAsString_2( tree, dataTypeControl, level=0 ):

    dataTypeIdc = getDataTypeIdc( dataTypeControl )

    dataAsString = ""

    currentIndent = int( tree["indent"] )
    currentIndentAsStr = getIndentAsString( "  ", currentIndent )

    addNewLineBefore = [ "Environment", "TestCaseData", "TestCase" ]
    addNewLineAfter = [ "Environment", "TestCase" ]

    omit = [ "Header", "dtIdx"]

    label = tree["label"]
    value = tree["value"]

    if None != label:

        if None != value:
            newStr = label + ": "  + str(value) + "\n"
        else:
            newStr = label + "\n"

        if not label in omit:

            if label in addNewLineBefore:
                dataAsString += "\n"

            dataAsString += currentIndentAsStr + newStr

            if label in addNewLineAfter:
                dataAsString += "\n"

        else:

            if "dtIdx" == label:
                if value != dataTypeIdc[0]:
                    return dataAsString

    elif None != value:
        newStr = str(value) + "\n"
        dataAsString += currentIndentAsStr + newStr

    children = tree["children"]

    for child in children:
        dataAsString += getDataAsString_2( child, dataTypeControl, level=level+1 )

    return dataAsString

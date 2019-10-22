
import pprint


def getDataTypeIdc( dataTypeControl ):

    if 1 == dataTypeControl:
        dataTypeIdc = [ 0 ]
    elif 2 == dataTypeControl:
        dataTypeIdc = [ 1 ]
    elif 3 == dataTypeControl:
        dataTypeIdc = [ 0, 1 ]

    return dataTypeIdc


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


def compare( dataObjectCoords1, dataObjectCoords2 ):

    numDataObjectCoords1 = len( dataObjectCoords1 )
    numDataObjectCoords2 = len( dataObjectCoords2 )

    numDataObjectCoords = min( numDataObjectCoords1, numDataObjectCoords2 )

    for idx in range( numDataObjectCoords ):
        if dataObjectCoords1[idx] < dataObjectCoords2[idx]:
            return -1
        elif dataObjectCoords1[idx] > dataObjectCoords2[idx]:
            return 1

    if numDataObjectCoords1 < numDataObjectCoords2:
        return -1
    elif numDataObjectCoords1 > numDataObjectCoords2:
        return 1

    return 0


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


class FormatString( object ):

    def __init__( self, indentUnit ):

        self.indentUnit = indentUnit

        self.addNewLineBefore = [ "Environment", "TestCaseData", "TestCase" ]
        self.addNewLineAfter = [ "Environment", "TestCase" ]
        
        self.omit = [ "Header", "dtIdx"]

        self.categories = [ "<<GLOBALS>>", "<<UUT>>", "<<SBF>>", "<<STUB>>", "<<TestCase User Code>>" ]


    def getIndentAsString( self, numIndentUnits ):
        return self.indentUnit * numIndentUnits


    def getBeforeSameAfter( category, dataObjectCoords ):

        docTmp = [ None, None, None ]
        beforeSameAfter = [ None, None, None ]

        for data_object_id in self.doidToTree[category].keys():

            currrentObjectCoords = self.doidToTree[category][data_object_id]["doc"]

            cmp = compare( currentObjectCoords, dataObjectCoords ) 

            if -1 == cmp:

                if None != docTmp[0]:
                    cmpTmp = compare( currentObjectCoords, docTmp[0] )
                    if -1 == cmpTmp:
                       docTmp[0] = currentObjectCoords
                else:
                    docTmp[0] = currentObjectCoords

            elif 1 == cmp:

                if None != docTmp[2]:
                    cmpTmp = compare( currentObjectCoords, docTmp[2] )
                    if 1 == cmpTmp:
                        docTmp[2] = currentObjectCoords
                else:
                    docTmp[2] = currentObjectCoords

            else:

                docTmp[1] = currentObjectCoords

        for idx in range( 3 ):
            if None != docTmp[idx]:
                data_object_id = ".".join( [str(item) for item in tmpDoc[idx]] )
                beforeSameAfter[idx] = data_object_id

        return beforeSameAfter


    def getDataAsString( self, tree, dataTypeControl ):

        self.dataTypeIdc = getDataTypeIdc( dataTypeControl )

        dataAsString = self.formatString( tree, 0, prepare=True )
        self.maxSize = maxSize( dataAsString )
        dataAsString = self.formatString( tree, 0, prepare=False )

        pprint.pprint( self.doidToTree )

        return dataAsString


    def formatString( self, tree, dtIdx, prepare=False, category=None, level=0 ):

        dataAsString = ""

        currentIndent = int( tree["indent"] )
        currentIndentAsStr = self.getIndentAsString( currentIndent )

        label = tree["label"]
        value = tree["value"]

        if 0 == level and prepare:

            self.doidToTree = {}

            for category in self.categories:
                self.doidToTree[category] = {}

        if None != label:

            if prepare and 1 == dtIdx:

                if label in self.categories:
                    category = label

                data_object_id = ".".join( [str(item) for item in tree["doc"]] )

                if None != category and "" != data_object_id:
                    self.doidToTree[category][data_object_id] = tree

            if not label in self.omit:

                if None != value:
                    newStr = label + ": " + str(value) + "\n"
                else:
                    newStr = label + "\n"

                if label in self.addNewLineBefore:
                    dataAsString += "\n"

                dataAsString += currentIndentAsStr + newStr

                if label in self.addNewLineAfter:
                    dataAsString += "\n"

            else:

                if "dtIdx" == label:
                    
                    if prepare:

                        dtIdx = value

                    else:

                        if value != self.dataTypeIdc[0]:
                            return dataAsString

        else:

            if None != value:
                formattedStr = formatMultiLine( value, currentIndent )
                dataAsString += formattedStr

        children = tree["children"]

        if 0 == dtIdx:
            for child in children:
                dataAsString += self.formatString( child, dtIdx, prepare=prepare, category=category, level=level+1 )
        else:
            dataAsString_2 = ""
            for child in children:
                dataAsString_2 += self.formatString( child, dtIdx, prepare=prepare, category=category, level=level+1 )

        return dataAsString

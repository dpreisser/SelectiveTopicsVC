
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


def sort( list ):

    numElements = len( list )

    for idx1 in range( numElements, 1, -1 ):

        for idx2 in range( idx1-1 ):

            cmp = compare( list[idx2][0], list[idx2+1][0] )

            if 1 == cmp:
                tmp = list[idx2+1]
                list[idx2+1] = list[idx2]
                list[idx2] = tmp

    return list


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


def equivalence( dataObjectCoords1, dataObjectCoords2, numIdc ):

    for idx in range( numIdc ):

        if dataObjectCoords1[idx] < dataObjectCoords2[idx]:
            return -1
        elif dataObjectCoords1[idx] > dataObjectCoords2[idx]:
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


    def getBeforeSameAfter( self, category, dataObjectCoords, numIdc ):

        beforeSameAfter = [ [], [], [] ]

        for tuple in self.docList:

            currentObjectCoords = tuple[0]

            eqv = equivalence( currentObjectCoords, dataObjectCoords, numIdc )

            beforeSameAfter[eqv+1].append( tuple )

        return beforeSameAfter


    def getDataAsString( self, tree, dataTypeControl ):

        self.dataTypeControl =  dataTypeControl
        self.dataTypeIdc = getDataTypeIdc( dataTypeControl )

        if 3 == dataTypeControl:
            
            dataAsString = self.formatString( tree, 0, prepare=True )

            self.maxSize = maxSize( dataAsString )
            
            for category in self.docList.keys():
                self.docList[category] = sort( self.docList[category] )

            print( self.maxSize )
            pprint.pprint( self.docList )
        
        # dataAsString = self.formatString( tree, 0, prepare=False )

        return dataAsString


    def formatString( self, tree, dtIdx, prepare=False, category=None, level=0 ):

        dataAsString = ""

        currentIndent = int( tree["indent"] )
        currentIndentAsStr = self.getIndentAsString( currentIndent )

        label = tree["label"]
        value = tree["value"]

        if 0 == level:

            if prepare:

                self.doidToTree = {}
                self.docList = {}

                for category in self.categories:
                    self.doidToTree[category] = {}
                    self.docList[category] = []

        if None != label:

            if 1 == dtIdx:

                if prepare:
                    
                    if label in self.categories:
                        category = label

                    if None != category:

                        dataObjectCoords = tree["doc"]

                        if None != dataObjectCoords:

                            data_object_id = ".".join( [str(item) for item in dataObjectCoords] )
                        
                            self.doidToTree[category][data_object_id] = tree
                            self.docList[category].append( (dataObjectCoords,data_object_id) )

                else:

                    if not label in self.omit:

                        if None != value:
                            newStr = label + ": " + str(value) + "\n"
                        else:
                            newStr = label + "\n"

                        if label in self.addNewLineBefore:
                            dataAsString += "\n"

                        dataAsString += self.maxSize + currentIndentAsStr + newStr

                        if label in self.addNewLineAfter:
                            dataAsString += "\n"

            elif 0 == dtIdx:

                beforeSameAfter = None

                if not prepare and 3 == self.dataTypeControl:
                                    
                    if label in self.categories:
                        category = label

                    self.categoryLevel = level

                    if None != category:

                        dataObjectCoords = tree["doc"]

                        if None != dataObjectCoords:

                            numIdc = level - self.categoryLevel + 1
                            beforeSameAfter = self.getBeforeSameAfter( category, dataObjectCoords, numIdc )

                            for tuple in beforeSameAfter[0]:
                                targetTree = self.doidToTree[category][tuple[1]]
                                dataAsString += self.formatString( targetTree, 1, prepare=prepare, category=category, level=level+1 )

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

        elif 1 == dtIdx:

            dataAsString_2 = ""

            for child in children:
                dataAsString_2 += self.formatString( child, dtIdx, prepare=prepare, category=category, level=level+1 )
            
            if not prepare:
                dataAsString += dataAsString_2

        return dataAsString

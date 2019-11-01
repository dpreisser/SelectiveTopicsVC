
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

        print( "category:", category )
        print( self.docList[category] )

        for tuple in self.docList[category]:

            currentObjectCoords = tuple[0]

            # eqv = equivalence( currentObjectCoords, dataObjectCoords, numIdc )
            cmp = compare( currentObjectCoords, dataObjectCoords, numIdc )

            print( currentObjectCoords )
            print( dataObjectCoords )
            print( "cmp:", cmp )

            beforeSameAfter[cmp+1].append( tuple )

        return beforeSameAfter


    def getCurrentString( self, tree, dtIdx, beforeSameAfter=None ):

        if 0 == dtIdx:
            currentIndent = tree["indent"]
        else:
            currentIndent = self.maxSize + tree["indent"]

        currentIndentAsStr = self.getIndentAsString( currentIndent )

        label = tree["label"]
        value = tree["value"]

        currentString = ""
        currentSize = currentIndent
        newLineBefore = ""
        newLineAfter = ""

        if None != label:

            if not label in self.omit:

                if None != value:
                    newStr = label + ": " + str(value)
                else:
                    newStr = label

                currentSize += len( newStr )

                if label in self.addNewLineBefore:
                    newLineBefore = "\n"

                if label in self.addNewLineAfter:
                    newLineAfter = "\n"

        elif None != value:
            
            formattedStr = formatMultiLine( value, currentIndent )
            currentString += formattedStr

        if 1 == dtIdx:

            if currentSize > currentIndent:
                currentString += currentIndentAsStr + newStr + "\n"

        elif 0 == dtIdx:

            extraData = False

            if None != beforeSameAfter:
                if 1 == len( beforeSameAfter[1] ):
                    extraData = True

            if extraData:

                tuple = beforeSameAfter[1][0]
                targetTree = self.doidToTree[category][tuple[1]]

                currentIndent_2 = targetTree["indent"]
                deltaIndent = self.maxSize + currentIndent_2 - currentSize

                label_2 = targetTree["label"]
                value_2 = targetTree["value"]

                if None != label_2:

                    if not label_2 in self.omit:

                        if None != value_2:
                            newStr_2 = label_2 + ": " + str(value_2)
                        else:
                            newStr_2 = label_2

                        deltaIndentAsStr = self.getIndentAsString( deltaIndent )
                        currentString += currentIndentAsStr + newStr + deltaIndentAsStr + newStr_2 + "\n"

                elif None != value_2:
            
                    formattedStr = formatMultiLine( value_2, deltaIndent )
                    currentString += formattedStr

            else:

                if currentSize > currentIndent:
                    currentString += currentIndentAsStr + newStr + "\n"

        finalString = newLineBefore + currentString + newLineAfter

        return finalString


    def getDataAsString( self, tree, dataTypeControl ):

        self.dataTypeControl =  dataTypeControl
        self.dataTypeIdc = getDataTypeIdc( dataTypeControl )

        if 3 == dataTypeControl:

            pprint.pprint( tree )
            
            dataAsString = self.formatString( tree, 0, prepare=True )

            self.maxSize = maxSize( dataAsString )

            for category in self.docList.keys():
                self.docList[category] = sort( self.docList[category] )

            print( self.maxSize )
            pprint.pprint( self.doidToTree )
            pprint.pprint( self.docList )
        
            dataAsString = self.formatString( tree, 0, prepare=False )

        return dataAsString


    def formatString( self, tree, dtIdx, prepare=False, category=None, level=0 ):

        dataAsString = ""

        currentIndent = int( tree["indent"] )
        currentIndentAsStr = self.getIndentAsString( currentIndent )

        label = tree["label"]
        value = tree["value"]

        children = tree["children"]

        if 0 == level:

            if prepare:

                self.doidToTree = {}
                self.docList = {}

                for category in self.categories:
                    self.doidToTree[category] = {}
                    self.docList[category] = []

            else:

                self.categoryLevel = None

        if 1 == dtIdx:

            if prepare:
                    
                if label in self.categories:
                    category = label

                if None != category:

                    dataObjectCoords = tree["doc"]

                    if None != dataObjectCoords:

                        data_object_id = ".".join( [str(item) for item in dataObjectCoords] )
                        
                        if not data_object_id in self.doidToTree[category].keys():
                            self.doidToTree[category][data_object_id] = tree
                            self.docList[category].append( (dataObjectCoords,data_object_id) )

            else:

                dataAsString += self.getCurrentString( tree, dtIdx )

        elif 0 == dtIdx:

            beforeSameAfter = None

            if not prepare and 3 == self.dataTypeControl:
                                    
                if label in self.categories:

                    category = label
                    self.categoryLevel = level

                    if 0 == len( children ):

                        if category in self.docList.keys():
                            print( "category:", category )
                            if len( self.docList[category] ) > 0:
                                beforeSameAfter = [ [], [], [] ]
                                tuple = self.docList[category][0]
                                beforeSameAfter[0].append( tuple )

                if None != category:

                    dataObjectCoords = tree["doc"]

                    if None != dataObjectCoords:

                        numIdc = level - self.categoryLevel
                        beforeSameAfter = self.getBeforeSameAfter( category, dataObjectCoords, numIdc )

                        print( "category:", category )
                        print( "dataObjectCoords:", dataObjectCoords )
                        print( "numIdc:", numIdc )
                        pprint.pprint( beforeSameAfter )

            currentString = self.getCurrentString( tree, dtIdx, beforeSameAfter )

            if not prepare and 3 == self.dataTypeControl:

                if None != beforeSameAfter:

                    if self.categoryLevel == level:
                        dataAsString += currentString

                    for tuple in beforeSameAfter[0]:
                        targetTree = self.doidToTree[category][tuple[1]]
                        dataAsString += self.formatString( targetTree, 1, prepare=prepare, category=category, level=level+1 )

                    if self.categoryLevel != level:
                        dataAsString += currentString

            if "dtIdx" == label:
                    
                if prepare:

                    dtIdx = value

                else:

                    if value != self.dataTypeIdc[0]:
                        return dataAsString

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

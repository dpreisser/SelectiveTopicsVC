
import pprint


def getDataTypeIdc( dataTypeControl ):

    if 1 == dataTypeControl:
        dataTypeIdc = [ 0 ]
    elif 2 == dataTypeControl:
        dataTypeIdc = [ 1 ]
    elif 3 == dataTypeControl:
        dataTypeIdc = [ 0, 1 ]

    return dataTypeIdc


def getIndentAsString( numIndentUnits, indentUnit=" " ):
    return numIndentUnits * indentUnit 


def formatMultiLine( multiLineStr, currentIndent ):

    formattedStr = ""

    currentIndentAsStr = getIndentAsString( currentIndent )

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
    currentIndentAsStr = getIndentAsString( currentIndent, "  " ) 

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


class FormatHandler( object ):

    def __init__( self, traceHandler, \
                  indentUnit=2, \
                  widthLine=72, \
                  widthGrp1=32, widthGrp2=32, \
                  adjustWidthGrp1=False ):

        self.traceHandler = traceHandler

        self.indentUnit = indentUnit
        self.widthLine = widthLine
        self.widthGrp1 = widthGrp1
        self.widthGrp2 = widthGrp2

        self.adjustWidthGrp1 = adjustWidthGrp1

        self.addNewLineBefore = [ "Environment", "TestCase", "Slots", "Test Case Data", "Notes", "Execution Results", "Slot", "Events" ]
        self.addNewLineAfter = [ "Events" ]
 
        self.omit = [ "Header", "dtIdx"]

        self.categories = [ "<<GLOBAL DATA>>", "<<UUT>>", "<<SBF>>", "<<STUB>>", "<<TestCase User Code>>" ]


    def getIndentAsString( self, numIndentUnits ):
        return numIndentUnits * self.indentUnit


    def getBeforeSameAfter( self, testcaseID, category, dataObjectCoords ):

        beforeSameAfter = [ [], [], [] ]

        count_b = 0
        count_a = 0

        for tuple in self.docList[testcaseID][category]:

            currentObjectCoords = tuple[0]
            currentNumDigits = len( currentObjectCoords )

            cmp = compare( currentObjectCoords, dataObjectCoords )

            if cmp < 0:

                count_b += 1

                if 1 == count_b:

                    leadingObjectCoords_b = currentObjectCoords
                    leadingNumDigits_b = currentNumDigits
                    beforeSameAfter[cmp+1].append( tuple )

                else:

                    numDigits = min( currentNumDigits, leadingNumDigits_b )
                    eqv = equivalence( currentObjectCoords, leadingObjectCoords_b, numDigits )
                
                    if eqv > 0:
                        leadingObjectCoords_b = currentObjectCoords
                        leadingNumDigits_b = currentNumDigits
                        beforeSameAfter[cmp+1].append( tuple )
                    elif eqv < 0:
                        msg = "getBeforeSameAfter:\n"
                        msg += "Catastrophic internal logical error!!!"
                        self.traceHandler.addErrMessage( msg )
                        return [ [], [], [] ]

            elif cmp > 0:

                count_a += 1

                if 1 == count_a:

                    leadingObjectCoords_a = currentObjectCoords
                    leadingNumDigits_a = currentNumDigits
                    beforeSameAfter[cmp+1].append( tuple )

                else:

                    numDigits = min( currentNumDigits, leadingNumDigits_a )
                    eqv = equivalence( currentObjectCoords, leadingObjectCoords_a, numDigits )
                
                    if eqv > 0:
                        leadingObjectCoords_a = currentObjectCoords
                        leadingNumDigits_a = currentNumDigits
                        beforeSameAfter[cmp+1].append( tuple )
                    elif eqv < 0:
                        msg = "getBeforeSameAfter:\n"
                        msg += "Catastrophic internal logical error!!!"
                        self.traceHandler.addErrMessage( msg )
                        return [ [], [], [] ]

            else:

                beforeSameAfter[cmp+1].append( tuple )

        return beforeSameAfter


    def addGroupValues( self, dtIdx, currentString, currentWidth, currentIndent, valuesGrp1, valuesGrp2 ):

        newStringList = []
        newStr = ""

        currentIndentWidth1 = currentIndent * len( self.indentUnit )
        currentIndentAsStr1 = getIndentAsString( currentIndentWidth1  )

        if 0 == dtIdx:
            widthGrp1 = self.widthGrp1
            widthGrp2 = self.widthGrp2
        elif 1 == dtIdx:
            widthGrp1 = self.widthGrp2
            widthGrp2 = widthGrp1

        numValuesGrp1 = 0
        newStr1 = ""
        widthNewStr1 = 0

        if None != valuesGrp1:
            numValuesGrp1 = len( valuesGrp1 )
            newStr1 = ",".join( valuesGrp1 )
            widthNewStr1 = len( newStr1 )

        numValuesGrp2 = 0
        newStr2 = ""
        widthNewStr2 = 0

        if 0 == dtIdx:

            if None != valuesGrp2:
                numValuesGrp2 = len( valuesGrp2 )
                newStr2 = ",".join( valuesGrp2 )
                widthNewStr2 = len( newStr2 )

        if 0 == numValuesGrp1 and 0 == numValuesGrp2:
            newStringList.append( currentString )  
            return newStringList

        if ( currentWidth + widthNewStr1 <= widthGrp1 ) and \
           ( widthNewStr2 <= widthGrp2 ):

            newStr = currentString

            if widthNewStr1 > 0:
                newStr += newStr1

            if widthNewStr2 > 0:

                deltaWidth = self.widthLine - currentWidth - widthNewStr1 - widthNewStr2
                deltaWidthAsStr = getIndentAsString( deltaWidth )

                newStr += deltaWidthAsStr + newStr2

            newStringList.append( newStr ) 

        else:

            newStringList.append( currentString )

            numValues = max( numValuesGrp1, numValuesGrp2 )

            newStrList1 = []
            newStrList2 = []

            idx = 0

            newStr1 = ""
            widthNewStr1 = 0

            newStr2 = ""
            widthNewStr2 = 0

            if numValuesGrp1 > 0:
                value1 = valuesGrp1[idx]
                width1 = len( value1 ) + 1
            else:
                width1 = 0

            if numValuesGrp2 > 0:
                value2 = valuesGrp2[idx]
                width2 = len( value2 ) + 1
            else:
                width2 = 0

            if width1 > 0:
                newStr1 += value1 + ","
                widthNewStr1 += width1

            if width2 > 0:
                newStr2 += value2 + ","
                widthNewStr2 += width2

            newStrList1.append( newStr1 )
            newStrList2.append( newStr2 )

            while idx < numValues - 1:

                idx += 1

                if numValuesGrp1 > 0:
                    value1 = valuesGrp1[idx]
                    width1 = len( value1 ) + 1
                else:
                    width1 = 0

                if numValuesGrp2 > 0:
                    value2 = valuesGrp2[idx]
                    width2 = len( value2 ) + 1
                else:
                    width2 = 0

                if ( currentIndentWidth1 + widthNewStr1 + width1 <= widthGrp1 ) and \
                   ( widthNewStr2 + width2 <= widthGrp2 ):

                    if width1 > 0:
                        newStr1 += value1 + ","
                        widthNewStr1 += width1

                    if width2 > 0:
                        newStr2 += value2 + ","
                        widthNewStr2 += width2
                        
                    newStrList1[-1] = newStr1
                    newStrList2[-1] = newStr2

                else:

                    newStr1 = ""
                    widthNewStr1 = 0

                    newStr2 = ""
                    widthNewStr2 = 0

                    if width1 > 0:
                        newStr1 += value1 + ","
                        widthNewStr1 += width1

                    if width2 > 0:
                        newStr2 += value2 + ","
                        widthNewStr2 += width2

                    newStrList1.append( newStr1 )
                    newStrList2.append( newStr2 )

            lastStr1 = newStrList1[-1]
            lastStr2 = newStrList2[-1]

            newStrList1[-1] = lastStr1.strip( "," )
            newStrList2[-1] = lastStr2.strip( "," )

            numNewStr = len( newStrList1 )
            for idx in range( numNewStr ):

                newStr = ""

                newStr1 = newStrList1[idx]
                widthNewStr1 = len( newStr1 )

                newStr2 = newStrList2[idx]
                widthNewStr2 = len( newStr2 )

                if widthNewStr1 > 0:
                    newStr += currentIndentAsStr1 + newStr1

                if widthNewStr2 > 0:

                    if currentIndentWidth1 + widthNewStr1 > self.widthGrp1 or \
                       widthNewStr2 > self.widthGrp2:

                        if widthNewStr1 > 0:
                            newStringList.append( newStr )
                            newStr = ""

                        if widthNewStr2 <= self.widthLine:
                            deltaWidth = self.widthLine - widthNewStr2
                        else:
                            deltaWidth = 0

                    else:
                    
                        deltaWidth = self.widthLine - currentIndentWidth1 - widthNewStr1 - widthNewStr2

                    deltaWidthAsStr = getIndentAsString( deltaWidth )
                    newStr += deltaWidthAsStr + newStr2

                newStringList.append( newStr )

        return newStringList


    def getCurrentString( self, tree, dtIdx, testcaseID, category, beforeSameAfter=None ):

        stringList = []
        stringList1 = []
        stringList2 = []
        newString = ""

        currentIndent = tree["indent"]
        currentIndentAsStr = self.getIndentAsString( currentIndent )

        currentIndentWidth = currentIndent * len( self.indentUnit )

        label = tree["label"]
        value = tree["value"]

        valuesGrp1 = tree["valuesGrp1"]
        valuesGrp2 = tree["valuesGrp2"]

        newLineBefore = ""
        newLineAfter = ""

        currentString = ""
        currentWidth = 0

        if None != label:

            if not label in self.omit:

                if None != value:
                    newStr = label.strip() + ": " + str(value)
                elif None != valuesGrp1 or None != valuesGrp2:
                    newStr = label.strip() + ": "
                else:
                    newStr = label.strip()

                widthNewStr = len( newStr )

                if widthNewStr > 0:
                    currentString += currentIndentAsStr + newStr
                    currentWidth += currentIndentWidth + widthNewStr

                stringList = self.addGroupValues( dtIdx, currentString, currentWidth, currentIndent, valuesGrp1, valuesGrp2 )

                if label in self.addNewLineBefore:
                    newLineBefore = "\n"

                if label in self.addNewLineAfter:
                    newLineAfter = "\n"

        elif None != value:

            if 1 == dtIdx:
                offsetWidth = self.widthLine - self.widthGrp2
            else:
                offsetWidth = 0

            if self.isInpExpData:
                formattedStr = formatMultiLine( value, offsetWidth + currentIndentWidth )
                currentString += formattedStr
            else:
                formattedPartList = []
                for part in value:
                    formattedPart = formatMultiLine( part, offsetWidth + currentIndentWidth )
                    print( formattedPart )
                    formattedPartList.append( formattedPart )
                formattedStr = ",\n".join( [ formattedPart.rstrip() for formattedPart in formattedPartList ] )
                currentString += formattedStr + "\n"

            newString += currentString

        if 1 == dtIdx:

            stringList2 = stringList

            dataObjectCoords = tree["doc"]
            
            if None != dataObjectCoords:

                data_object_id = ".".join( [str(item) for item in dataObjectCoords] )

                theTuple = ( dataObjectCoords, data_object_id )
                self.docList[testcaseID][category].remove( theTuple )

        elif 0 == dtIdx:

            stringList1 = stringList

            extraData = False

            if None != beforeSameAfter:
                if 1 == len( beforeSameAfter[1] ):
                    extraData = True

            if extraData:

                theTuple = beforeSameAfter[1][0]
                targetTree = self.doidToTree[testcaseID][category][theTuple[1]]

                currentIndent2 = targetTree["indent"]
                currentIndentAsStr2 = self.getIndentAsString( currentIndent2 )

                currentIndentWidth2 = currentIndent2 * len( self.indentUnit )

                label2 = targetTree["label"]
                value2 = targetTree["value"]

                valuesGrp1 = targetTree["valuesGrp1"]
                valuesGrp2 = targetTree["valuesGrp2"]

                currentString2 = ""
                currentWidth2 = 0

                if None != label2:

                    if not label2 in self.omit:

                        if None != value2:
                            newStr2 = label2.strip() + ": " + str(value2)
                        elif None != valuesGrp1:
                            newStr2 = label2.strip() + ": "
                        else:
                            newStr2 = label2.strip()

                        widthNewStr2 = len( newStr2 )

                        if widthNewStr2 > 0:
                            currentString2 += currentIndentAsStr2 + newStr2
                            currentWidth2 += currentIndentWidth2 + widthNewStr2

                        stringList2 = self.addGroupValues( 1, currentString2, currentWidth2, currentIndent2, valuesGrp1, valuesGrp2 )

                elif None != value2:

                    offsetWidth = self.widthLine - self.widthGrp2

                    if self.isInpExpData:
                        formattedStr = formatMultiLine( value2, offsetWidth + currentIndentWidth2 )
                        currentString2 += formattedStr
                    else:
                        formattedPartList = []
                        for part in value2:
                            formattedPart = formatMultiLine( part, offsetWidth + currentIndentWidth2 )
                            formattedPartList.append( formattedPart )
                        formattedStr = ",\n".join( [ formattedPart.rstrip() for formattedPart in formattedPartList ] )
                        currentString2 += formattedStr + "\n"

                    newString += currentString2

                self.docList[testcaseID][category].remove( theTuple )

        numNewStr1 = len( stringList1 )
        numNewStr2 = len( stringList2 )
        numNewStr = max( numNewStr1, numNewStr2 )

        for idx in range( numNewStr ):

            newStr = ""

            if idx < numNewStr1:
                newStr1 = stringList1[idx]
            else:
                newStr1 = ""

            if idx < numNewStr2:
                newStr2 = stringList2[idx]
            else:
                newStr2 = ""

            widthNewStr1 = len( newStr1 )
            widthNewStr2 = len( newStr2 )

            if widthNewStr1 > 0:
                newStr += newStr1

            if widthNewStr2 > 0:

                if widthNewStr1 > self.widthGrp1 or \
                   widthNewStr2 > self.widthGrp2:

                    if widthNewStr1 > 0:
                        newStr += "\n"

                    if widthNewStr2 <= self.widthGrp2:
                        deltaWidth = self.widthLine - self.widthGrp2
                    elif widthNewStr2 <= self.widthLine:
                        deltaWidth = self.widthLine - widthNewStr2
                    else:
                        deltaWidth = 0

                else:
                    
                    deltaWidth = self.widthLine - self.widthGrp2 - widthNewStr1
                    
                deltaWidthAsStr = getIndentAsString( deltaWidth )
                newStr += deltaWidthAsStr + newStr2

            newString += newStr + "\n"

        finalString = newLineBefore + newString + newLineAfter

        return finalString


    def getDataAsString( self, tree, dataTypeControl, isInpExpData ):

        self.dataTypeControl = dataTypeControl
        self.dataTypeIdc = getDataTypeIdc( dataTypeControl )

        self.isInpExpData = isInpExpData 

        if isInpExpData and 3 == dataTypeControl:

            dataAsString = self.formatString( tree, 0, prepare=True )

            if not self.traceHandler.getStatus():
                return dataAsString

            for testcaseID in self.docList.keys():
                for category in self.docList[testcaseID].keys():
                    self.docList[testcaseID][category] = sort( self.docList[testcaseID][category] )

            maxWidthGrp1 = maxSize( dataAsString )

            if self.adjustWidthGrp1:

                deltaWidth = maxWidthGrp1 - self.widthGrp1

                if deltaWidth > 0:
                    self.widthGrp1 += deltaWidth
                    self.widthLine += deltaWidth

            # pprint.pprint( tree )
            # pprint.pprint( self.docList )
            # print( maxWidthGrp1 )
        
        dataAsString = self.formatString( tree, 0, prepare=False )

        return dataAsString


    def formatString( self, tree, dtIdx, prepare=False, testcaseID=None, category=None, level=0 ):

        dataAsString = ""

        currentIndent = int( tree["indent"] )
        currentIndentAsStr = self.getIndentAsString( currentIndent )

        label = tree["label"]

        children = tree["children"]

        if 0 == level:

            if prepare and 3 == self.dataTypeControl:

                self.doidToTree = {}
                self.docList = {}

            else:

                self.categoryLevel = None
                self.beforeSameAfter = None
                self.previousCategory = None

        if 1 == dtIdx:

            if prepare and None != testcaseID:
                    
                if label in self.categories:
                    category = label

                if None != category:

                    dataObjectCoords = tree["doc"]

                    if None != dataObjectCoords:

                        data_object_id = ".".join( [str(item) for item in dataObjectCoords] )
                        
                        if not data_object_id in self.doidToTree[testcaseID][category].keys():
                            self.doidToTree[testcaseID][category][data_object_id] = tree
                            self.docList[testcaseID][category].append( (dataObjectCoords,data_object_id) )

            else:

                dataAsString += self.getCurrentString( tree, dtIdx, testcaseID, category )

        elif 0 == dtIdx:

            beforeSameAfter = None

            if 3 == self.dataTypeControl:

                if "TestCase" == label:

                    if "ID" in tree.keys():

                        testcaseID = tree["ID"]

                        if prepare:

                            self.doidToTree[testcaseID] = {}
                            self.docList[testcaseID] = {}

                            for category in self.categories:
                                self.doidToTree[testcaseID][category] = {}
                                self.docList[testcaseID][category] = []

            if not prepare and None != testcaseID:
                                    
                if label in self.categories:

                    category = label
                    self.categoryLevel = level

                    # Add the remaining items of the previous category.
                    if None != self.beforeSameAfter:
                        
                        for tuple in self.beforeSameAfter[2]:

                            targetTree = self.doidToTree[testcaseID][self.previousCategory][tuple[1]]

                            appendString = self.formatString( targetTree, 1, prepare=prepare, \
                                                              testcaseID=testcaseID, category=self.previousCategory,
                                                              level=level+1 )

                            if not self.traceHandler.getStatus():
                                return dataAsString
                                
                            dataAsString += appendString

                        self.beforeSameAfter = None

                    # Add the leading items of this category.
                    if 0 == len( children ):

                        beforeSameAfter = [ [], [], [] ]
                        beforeSameAfter[0] = self.docList[testcaseID][category]

                # Add the leading items of this category.
                if None != category:

                    dataObjectCoords = tree["doc"]

                    if None != dataObjectCoords:

                        beforeSameAfter = self.getBeforeSameAfter( testcaseID, category, dataObjectCoords )

                        if not self.traceHandler.getStatus():
                            return dataAsString
                        
                        self.beforeSameAfter = beforeSameAfter
                        self.previousCategory = category

            currentString = self.getCurrentString( tree, dtIdx, testcaseID, category, beforeSameAfter )

            if not prepare and None != testcaseID:

                if None != beforeSameAfter:

                    if self.categoryLevel == level:
                        dataAsString += currentString

                    for tuple in beforeSameAfter[0]:

                        targetTree = self.doidToTree[testcaseID][category][tuple[1]]

                        prependString = self.formatString( targetTree, 1, prepare=prepare, \
                                                           testcaseID=testcaseID, category=category, \
                                                           level=level+1 )

                        if not self.traceHandler.getStatus():
                            return dataAsString
                        
                        dataAsString += prependString

                    if self.categoryLevel != level:
                        dataAsString += currentString

                else:

                    dataAsString += currentString

            else:

                dataAsString += currentString

            if "dtIdx" == label:

                value = tree["value"]
                    
                if prepare:

                    dtIdx = value

                else:

                    if value != self.dataTypeIdc[0]:
                        return dataAsString

        if 0 == dtIdx:

            for child in children:

                dataAsString += self.formatString( child, dtIdx, prepare=prepare, \
                                                   testcaseID=testcaseID, category=category, \
                                                   level=level+1 )

                if not self.traceHandler.getStatus():
                    return dataAsString

        elif 1 == dtIdx:

            dataAsString_2 = ""

            for child in children:

                dataAsString_2 += self.formatString( child, dtIdx, prepare=prepare, \
                                                     testcaseID=testcaseID, category=category, \
                                                     level=level+1 )

                if not self.traceHandler.getStatus():
                    return dataAsString
            
            if not prepare:
                dataAsString += dataAsString_2

        return dataAsString

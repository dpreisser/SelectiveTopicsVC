
import os
import sys

import pprint

from copy import deepcopy

from vector.apps.DataAPI.api import Api

from dataApiReportUtils import getDataTypeIdc, getDataAsString


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


def getDefaultTree():

    defaultTree = { "children" : [], \
                    "doc" : None, \
                    "indent" : None, \
                    "label" : None, \
                    "value" : None, \
                    "valuesGrp1" : None, \
                    "valuesGrp2" : None }

    return defaultTree


class DataAPI_Report( object ):

    def __init__( self, workingDirVC, formatHandler, traceHandler ):

        self.workingDirVC = workingDirVC
        self.formatHandler = formatHandler
        self.traceHandler = traceHandler

        self.envApi = {}
        self.inputData = {}
        self.expectedData = {}


    def loadApi( self, envName ):

        if not envName in self.envApi.keys():
            full_env_dir = os.path.join( self.workingDirVC, envName )
            self.envApi[envName] = Api( full_env_dir )

        
    def getApi( self, envName ):

        self.loadApi( envName )
        return self.envApi[envName]


    def getTestcase( self, envName, unitName, functionName, tcName ):

        api = self.getApi( envName )
        testcase = api.TestCase.get( tcName )

        if None == testcase:
            return testcase

        if testcase.unit_display_name == unitName:
            if testcase.function_display_name == functionName:
                return testcase

        testcases = api.TestCase.all()

        for testcase in testcases:
            if testcase.unit_display_name == unitName:
                if testcase.function_display_name == functionName:
                    if testcase.name == tcName:
                        return testcase

        return None


    def getDataAsString_explicit( self, testcase, dataTypeControl, isInpExpData, currentIndent ):

        if isInpExpData:

            if 1 == dataTypeControl:
                dataTypeAsStr = "Input data"
            elif 2 == dataTypeControl:
                dataTypeAsStr = "Expected data"
            elif 3 == dataTypeControl:
                dataTypeAsStr = "Input & Expected data"

        else:

            dataTypeAsStr = "Result data"

        tree = getDefaultTree()
        tree["indent"] = currentIndent

        currentChild = getDefaultTree()
        currentChild["indent"] = currentIndent
        currentChild["label"] = "Header"

        grandChild = getDefaultTree()
        grandChild["indent"] = currentIndent
        grandChild["label"] = "%s for:" % dataTypeAsStr

        if not self.traceHandler.getStatus:
            return ""

        grandChild["children"] = self.getDataAsTree_slots( testcase, dataTypeControl, isInpExpData, currentIndent+1, level=0 )

        currentChild["children"].append( grandChild )
        tree["children"].append( currentChild )

        currentChild = getDefaultTree()
        currentChild["indent"] = currentIndent
        if isInpExpData:
            currentChild["label"] = "TestCaseData"
        else:
            currentChild["label"] = "Results"

        currentChild["children"] = self.getDataAsTree_all( testcase, dataTypeControl, isInpExpData, currentIndent+1 )
        tree["children"].append( currentChild )

        # pprint.pprint( tree )

        if not self.traceHandler.getStatus():
            return ""
        
        dataAsString = self.formatHandler.getDataAsString( tree, dataTypeControl, isInpExpData )

        return dataAsString


    def getDataAsTree_slots( self, testcase, dataTypeControl, isInpExpData, currentIndent, level=0 ):

        children = []

        envName = testcase.get_environment().name
        unitName = testcase.unit_display_name
        functionName = testcase.function_display_name

        if 0 == level:

            envIndent = currentIndent
            unitIndent = currentIndent
            functionIndent = currentIndent
            tcIndent = currentIndent 

            parameterIndent = currentIndent + 1
            slotIndent = currentIndent + 1

            if testcase.is_compound_test:

                tcNameAsStr = "%s (Compound)" % testcase.name

            elif testcase.is_unit_test:

                tcNameAsStr = "%s (Unit)" % testcase.name

            currentChild = getDefaultTree()
            currentChild["indent"] = envIndent
            currentChild["label"] = "Environment"
            currentChild["value"] = envName
            children.append( currentChild )

            currentChild = getDefaultTree()
            currentChild["indent"] = unitIndent
            currentChild["label"] = "Unit"
            currentChild["value"] = unitName
            children.append( currentChild )

            currentChild = getDefaultTree()
            currentChild["indent"] = functionIndent
            currentChild["label"] = "Function"
            currentChild["value"] = functionName
            children.append( currentChild )

            currentChild = getDefaultTree()
            currentChild["indent"] = tcIndent
            currentChild["label"] = "TestCase"
            currentChild["value"] = tcNameAsStr
            children.append( currentChild )

            self.prepareData( testcase, dataTypeControl, isInpExpData )

            if not self.traceHandler.getStatus:
                return children

        else:

            parameterIndent = currentIndent
            slotIndent = currentIndent

        if testcase.is_compound_test:

            if 0 == level:
                currentChild = getDefaultTree()
                currentChild["indent"] = tcIndent
                currentChild["label"] = "Slots"
                children.append( currentChild )

            slots = testcase.slots
            numSlots = len( slots )

            for idx in range( numSlots ):

                tc = slots[idx].testcase

                slotName = ".".join( [tc.unit_display_name, tc.function_display_name, tc.name] )
                slotAsStr = "Slot %s: %s (%s)" % ( str(slots[idx].index), slotName, slots[idx].iteration_count )

                slotTree = getDefaultTree()

                slotTree["indent"] = slotIndent
                slotTree["label"] = slotAsStr

                if tc.is_compound_test:
                    slotTree["children"] = self.getDataAsTree_slots( tc, dataTypeControl, isInpExpData, \
                                                                     slotIndent+1, \
                                                                     level=level+1 )

                if level > 0:
                    children.append( slotTree )
                else:
                    currentChild["children"].append( slotTree )

        return children


    def getDataAsTree_all( self, testcase_p, dataTypeControl, isInpExpData, currentIndent ):

        children = []

        envName = testcase_p.get_environment().name
        api = self.envApi[envName]

        dataTypeIdc = getDataTypeIdc( dataTypeControl )

        arrayChildren = [ [], [], [] ]

        if isInpExpData:

            tmpStore = {}

            for dtIdx in dataTypeIdc:

                for testcaseId in self.tcIdSequence:

                    testcase = api.TestCase.get( testcaseId )

                    grandChild = getDefaultTree()
                    grandChild["indent"] = currentIndent
                    grandChild["label"] = "dtIdx"
                    grandChild["value"] = dtIdx

                    if not testcaseId in tmpStore.keys():

                        currentChild = getDefaultTree()
                        currentChild["indent"] = currentIndent
                        currentChild["ID"] = testcaseId
                        currentChild["label"] = "TestCase"
                        currentChild["value"] = testcase.name

                        tmpStore[testcaseId] = currentChild

                    else:

                        currentChild = tmpStore[testcaseId]

                    trace( "dtIdx:", dtIdx, newLine=True )
                    trace( "testcaseId:", testcaseId, newLine=True )
                    trace( "Input & Expected Data:", self.inpExpData[dtIdx][testcaseId], newLine=True )

                    arrayChildren[0] = self.getDataAsTree_globals( envName,
                                                                   dtIdx, testcaseId, None, None, None, isInpExpData, \
                                                                   currentIndent+1 )

                    arrayChildren[1] = self.getDataAsTree_functions( envName, testcase, \
                                                                     dtIdx, testcaseId, None, None, None, isInpExpData, \
                                                                     currentIndent+1 )

                    arrayChildren[2] = self.getTestcaseUserCode( envName, testcase, \
                                                                 dtIdx, testcaseId, None, None, None, isInpExpData, \
                                                                 currentIndent+1 )

                    for idx in range( len(arrayChildren) ):
                        for child in arrayChildren[idx]:
                           grandChild["children"].append( child )

                    currentChild["children"].append( grandChild )

            for testcaseId in self.tcIdSequence:
                currentChild = tmpStore[testcaseId]
                children.append( currentChild )

        else:

            for slotHistId in self.slotHistIdSequence:

                slotHist = self.envApi[envName].SlotHistory.get( slotHistId )
                tc = slotHist.testcase

                numItr = len( self.actualData[slotHistId] )

                for itrIdx in range( numItr ):

                    ancestryList = self.ancestryInfo[slotHistId][itrIdx]

                    ancestryStrList = []

                    for ancestor in ancestryList:

                        ancestorAsStr = "%s Slot %s (%s) Iteration %s" % \
                                        ( ancestor[0], str(ancestor[1]), \
                                          ancestor[2], str(ancestor[3]) )

                        ancestryStrList.append( ancestorAsStr )

                    currentChild = getDefaultTree()
                    currentChild["indent"] = currentIndent
                    currentChild["label"] = "Slot"
                    currentChild["valuesGrp1"] = ancestryStrList
                    children.append( currentChild )

                    trace( "Actual Input & Result Data:", self.actualData[slotHistId][itrIdx], newLine=True )

                    numEvents = len( self.actualData[slotHistId][itrIdx] )

                    for eventIdx in range( numEvents ):

                        container = self.actualInfo[slotHistId][itrIdx][eventIdx]

                        functionName = self.actualInfo[slotHistId][itrIdx][eventIdx]["functionName"]

                        if 0 == eventIdx:
                            value = "Calling %s: " % functionName
                        elif numEvents - 1 == eventIdx:
                            value = "Returned from %s: " % functionName
                        else:
                            value = "Stubbed %s: " % functionName
                            
                        eventList = [ str(idx) for idx in container["eventIdc"] ]

                        grandChild = getDefaultTree()
                        grandChild["indent"] = currentIndent
                        grandChild["label"] = "Events"
                        grandChild["value"] = value
                        grandChild["valuesGrp1"] = eventList

                        arrayChildren[0] = self.getDataAsTree_globals( envName,
                                                                       None, None, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                                                       currentIndent+1 )

                        arrayChildren[1] = self.getDataAsTree_functions( envName, tc, \
                                                                         None, None, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                                                         currentIndent+1 )

                        arrayChildren[2] = self.getTestcaseUserCode( envName, tc, \
                                                                     None, None, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                                                     currentIndent+1 )

                        for idx in range( len(arrayChildren) ):
                            for child in arrayChildren[idx]:
                                grandChild["children"].append( child )

                        currentChild["children"].append( grandChild )

        return children


    def getDataAsTree_functions( self, envName, testcase, \
                                 dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                 currentIndent ):

        children = []

        if isInpExpData:
            container = self.inpExpData[dtIdx][testcaseId]
        else:
            container = self.actualData[slotHistId][itrIdx][eventIdx]

        api = self.envApi[envName]

        # UUT

        currentChild = getDefaultTree()
        currentChild["indent"] = currentIndent
        currentChild["label"] = "<<UUT>>"

        unitName = testcase.unit_display_name
        unit = api.Unit.get( unitName )

        function = testcase.function

        currentChild["children"] = self.getDataAsTree_parameters( unit, function, \
                                                                  dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                                                  currentIndent )

        children.append( currentChild )

        # SBF

        currentChild = getDefaultTree()
        currentChild["indent"] = currentIndent
        currentChild["label"] = "<<SBF>>"

        tc_unitId = unit.id
        tc_functionIndex = function.index

        for unitId in container.keys():

            unit = api.Unit.get( unitId )

            # Skip the unit if not enabled for SBF
            if not unit.stub_by_function:
                continue

            for functionIndex in container[tc_unitId].keys():

                # Skip globals
                if functionIndex == 0:
                    continue

                # Skip the function associated with the testcase.
                if unitId == tc_unitId:
                    if functionIndex == tc_functionIndex:
                        continue

                # function = self.getFunctionByIndex( unit, functionIndex )
                function = unit.get_function( functionIndex )

                grandChildren = self.getDataAsTree_parameters( unit, function, \
                                                               dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                                               currentIndent )

                for grandChild in grandChildren:
                    currentChild["children"].append( grandChild )

        children.append( currentChild )

        # All other stubs (different units)

        currentChild = getDefaultTree()
        currentChild["indent"] = currentIndent
        currentChild["label"] = "<<STUB>>"

        for unitId in container.keys():

            unit = api.Unit.get( unitId )

            # Skip the unit if not stubbed.
            if not unit.is_stubbed:
                continue

            for functionIndex in container[unitId].keys():

                # Skip globals
                if functionIndex == 0:
                    continue

                # function = self.getFunctionByIndex( unit, functionIndex )
                function = unit.get_function( functionIndex )

                grandChildren = self.getDataAsTree_parameters( unit, function, \
                                                               dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                                               currentIndent )

                for grandChild in grandChildren:
                    currentChild["children"].append( grandChild )

        children.append( currentChild )

        return children


    def getDataAsTree_parameters( self, unit, function, \
                                  dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                  currentIndent ):

        children = []

        unitIndent = currentIndent
        functionIndent = currentIndent + 1
        parameterIndent = currentIndent + 2

        unitChild = getDefaultTree()
        unitChild["doc"] = [ unit.id ]
        unitChild["indent"] = unitIndent
        unitChild["label"] = "Unit"
        unitChild["value"] = unit.name

        functionChild = getDefaultTree()
        functionChild["doc"] = [ unit.id, function.index ]
        functionChild["indent"] = functionIndent
        functionChild["label"] = "Subprogram"

        functionNameAsStr = "%s" % function.name
        functionDataAsStr = None

        if isInpExpData:
        
            if unit.stub_by_function:
                dataObjectCoords = [ unit.id, function.index, function.sbf_index ]
                functionDataAsStr = self.getInpExpData( dtIdx, testcaseId, dataObjectCoords, "data" )

            if None != functionDataAsStr:
                functionNameAsStr = "%s: %s" % ( function.name, functionDataAsStr )

        functionChild["value"] = functionNameAsStr

        parameterIndex = 1
        parameter = function.get_param_by_index( parameterIndex )

        while None != parameter:

            dataObjectCoords = [ unit.id, function.index, parameterIndex ]

            partChildren = self.walkType_Wrapper( parameter, dataObjectCoords, \
                                                  dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                                  parameterIndent )

            for child in partChildren:
                functionChild["children"].append( child )

            parameterIndex += 1
            parameter = function.get_param_by_index( parameterIndex )

        if len( functionChild["children"] ) > 0:
            unitChild["children"].append( functionChild )
            children.append( unitChild )

        return children


    def getDataAsTree_globals( self, envName, \
                               dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                               currentIndent ):

        children = []

        currentChild = getDefaultTree()
        currentChild["indent"] = currentIndent
        currentChild["label"] = "<<GLOBAL DATA>>"

        if isInpExpData:
            container = self.inpExpData[dtIdx][testcaseId]
        else:
            container = self.actualData[slotHistId][itrIdx][eventIdx]

        api = self.envApi[envName]

        functionIndex = 0

        for unitId in container.keys():

            if not functionIndex in container[unitId].keys():
                continue

            unit = api.Unit.get( unitId )

            grandChildren = self.getDataAsTree_globalsInUnit( envName, unit, \
                                                              dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                                              currentIndent )

            for grandChild in grandChildren:
                currentChild["children"].append( grandChild )

        children.append( currentChild )

        return children

    
    def getDataAsTree_globalsInUnit( self, envName, unit, \
                                     dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                     currentIndent ):

        children = []

        unitIndent = currentIndent            
        functionIndent = currentIndent + 1
        parameterIndent = currentIndent + 2

        unitId = unit.id
        functionIndex = 0

        functionNameAsStr = "<<GLOBAL>>"

        if isInpExpData:
            container = self.inpExpData[dtIdx][testcaseId]
        else:
            container = self.actualData[slotHistId][itrIdx][eventIdx]

        unitChild = getDefaultTree()
        unitChild["doc"] = [ unit.id ]
        unitChild["indent"] = unitIndent
        unitChild["label"] = "Unit"
        unitChild["value"] = unit.name

        functionChild = getDefaultTree()
        functionChild["doc"] = [ unit.id, functionIndex ]
        functionChild["indent"] = functionIndent
        functionChild["label"] = functionNameAsStr

        currentData = container[unitId][functionIndex]
        
        for globalVarIndex in currentData.keys():

            dataObjectCoords = [ unitId, functionIndex, globalVarIndex ]

            # globalVar = self.getGlobalVarByIndex( envName, unitId, globalVarIndex )
            globalVar = unit.get_global_by_index( globalVarIndex )

            partChildren = self.walkType_Wrapper( globalVar, dataObjectCoords, \
                                                  dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                                  parameterIndent )

            for child in partChildren:
                functionChild["children"].append( child )

        if len( functionChild["children"] ) > 0:
            unitChild["children"].append( functionChild )
            children.append( unitChild )

        return children


    def getTestcaseUserCode( self, envName, testcase, \
                             dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData,
                             currentIndent ):

        children = []

        unitIndent = currentIndent
        functionIndent = currentIndent + 1
        tcIndent = currentIndent + 2

        api = self.envApi[envName]

        unitName = testcase.unit_display_name
        unit = api.Unit.get( unitName )

        function = testcase.function
        
        tcNameAsStr = "%s: %s" % ( testcase.name, "<<User Code>>" )

        currentChild = getDefaultTree()
        currentChild["indent"] = currentIndent
        currentChild["label"] = "<<TestCase User Code>>"
        children.append( currentChild )

        unitChild = getDefaultTree()
        unitChild["doc"] = [ unit.id ]
        unitChild["indent"] = unitIndent
        unitChild["label"] = "Unit"
        unitChild["value"] = unit.name

        functionChild = getDefaultTree()
        functionChild["indent"] = functionIndent
        functionChild["doc"] = [ unit.id, function.index ]
        functionChild["label"] = "Subprogram"
        functionChild["value"] = function.name

        tcChild = getDefaultTree()
        tcChild["indent"] = tcIndent
        tcChild["doc"] = [ unit.id, function.index, testcase.index ]
        tcChild["label"] = "TestCase "
        tcChild["value"] = tcNameAsStr

        codeChild = None

        if isInpExpData:

            if 1 == dtIdx:
                source = testcase.expected_user_code
            else:
                source = testcase.input_user_code

            for sourceData in source:

                if sourceData.is_testcase_user_code:
                
                    codeChild = getDefaultTree()
                    codeChild["indent"] = tcIndent+1
                    codeChild["doc"] = [ unit.id, function.index, testcase.index, -1 ]
                    codeChild["value"] = sourceData.value
                    tcChild["children"].append( codeChild )

        else:

            container = self.actualInfo[slotHistId][itrIdx][eventIdx]

            if "actuals" in container.keys():

                codeChild = getDefaultTree()
                codeChild["indent"] = tcIndent+1
                codeChild["doc"] = [ unit.id, function.index, testcase.index, -1 ]
                codeChild["valuesGrp1"] = container["actuals"]
                codeChild["valuesGrp2"] = container["match"]
                tcChild["children"].append( codeChild )

        if None != codeChild:
            functionChild["children"].append( tcChild )
            unitChild["children"].append( functionChild )
            currentChild["children"].append( unitChild )

        return children


    def walkType_Wrapper( self, parameter, dataObjectCoords, \
                          dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                          currentIndent ):

        children = self.walkType( parameter.name, parameter.type, dataObjectCoords, \
                                  dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                  currentIndent )

        return children


    def walkType( self, parameterName, parameterType, dataObjectCoords, \
                  dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                  currentIndent ):

        children = []

        indexIndent = currentIndent + 1

        data_object_id = ".".join( [str(item) for item in dataObjectCoords] )

        if isInpExpData:
            values = self.getInpExpData( dtIdx, testcaseId, dataObjectCoords, "data" )
        else:
            values = self.getActualData( slotHistId, itrIdx, eventIdx, dataObjectCoords, "actuals" )

        kind = parameterType.kind
        element = parameterType.element

        trace( "Parameter/Field name:", parameterName )
        trace( "Type kind:", kind )
        trace( "data_object_id:", data_object_id )

        currentChild = getDefaultTree()
        currentChild["doc"] = dataObjectCoords
        currentChild["indent"] = currentIndent
        currentChild["label"] = parameterName

        if isInpExpData:

            if None == values:

                values = self.getInpExpData( dtIdx, testcaseId, dataObjectCoords, "parameter_user_code" )

                if None != values:
                
                    currentChild["value"] = "<<User Code>>"
                    children.append( currentChild )

                    doc = deepcopy( dataObjectCoords )
                    doc.append( -1 )

                    codeChild = getDefaultTree()
                    codeChild["indent"] = currentIndent+1
                    codeChild["doc"] = doc
                    codeChild["value"] = values
                    currentChild["children"].append( codeChild )

                    return children

        isArray = False
        isBasicType = True

        if "ACCE_SS" == kind:

            isArray = True

            if isInpExpData:

                if 1 == dtIdx:
                
                    currentChild["value"] = "<<ACCESS>>"

                else:

                    allocateAsStr = self.getInpExpData( dtIdx, testcaseId, dataObjectCoords, "allocate" )

                    if None == allocateAsStr:
                        # Unfortunately not possible because there is no allocate within stubs.
                        # return children
                        currentChild["value"] = "<<ALLOCATE>>"
                    else:
                        currentChild["value"] = "<<ALLOCATE %s>>" % allocateAsStr

            else:

                currentChild["value"] = "<<ACCESS>>"

        elif "STR_ING" == kind:

            isArray = True

            if "CHAR_ACTER" == element.kind:
                if None != values:
                    isArray = False

            if isInpExpData:

                if 1 == dtIdx:

                    currentChild["value"] = "<<ACCESS>>"

                else:

                    allocateAsStr = self.getInpExpData( dtIdx, testcaseId, dataObjectCoords, "allocate" )
                    if None == allocateAsStr:
                        return children

                    currentChild["value"] = "<<ALLOCATE %s>>" % allocateAsStr

            else:

                currentChild["value"] = "<<ACCESS>>"

        elif "AR_RAY" == kind:

            isArray = True

            size = parameterType.range.size # Still something like "4%%"
            size = size.split( "%" )[0]

            currentChild["value"] = "<<Size %s>>" % size

        elif "REC_ORD" == kind:

            isBasicType = False

            child_fields = parameterType.child_fields

        if isArray:

            arrayIndices = self.getDataObjectCoords_arrayIndices( dataObjectCoords, \
                                                                  dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData )

            trace( "Array: arrayIndices:", str(arrayIndices) )

            for arrayIndex in arrayIndices:

                index_dataObjectCoords = deepcopy( dataObjectCoords )
                index_dataObjectCoords.append( arrayIndex )

                trace( "Array: Basic Type: index_dataObjectCoords:", str(index_dataObjectCoords) )
                trace( "Array: Basic Type: values:", str(values) )

                indexName = "%s[%s]" % ( parameterName, str(arrayIndex) )

                grandChildren = self.walkType( indexName, element, index_dataObjectCoords, \
                                               dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                               indexIndent )

                for grandChild in grandChildren:
                    currentChild["children"].append( grandChild )

            # Check that there is really data otherwise
            # do not include the currentChild to children.
            if len( currentChild["children"] ) > 0: 
                children.append( currentChild )

        else:

            if isBasicType:

                trace( "Basic Type: dataObjectCoords:", str(dataObjectCoords) )
                trace( "Basic Type: values:", str(values) )

                if None != values:

                    if isInpExpData:

                        associatedValues = self.getAssociatedValues( parameterType, valuesAsStr=values )
                        currentChild["valuesGrp1"] = associatedValues

                    else:

                        associatedValues = self.getAssociatedValues( parameterType, valuesAsList=values )
                        currentChild["valuesGrp1"] = associatedValues

                        values = self.getActualData( slotHistId, itrIdx, eventIdx, dataObjectCoords, "match" )
                        if None != values:
                            associatedValues = self.getAssociatedValues( parameterType, valuesAsList=values )
                            currentChild["valuesGrp2"] = associatedValues
                    
                    children.append( currentChild )

            else:

                for child in child_fields:

                    child_dataObjectCoords = deepcopy( dataObjectCoords )
                    child_dataObjectCoords.append( child.index )

                    trace( "None Basic Type: child_dataObjectCoords:", str(child_dataObjectCoords) )

                    grandChildren = self.walkType_Wrapper( child, child_dataObjectCoords,\
                                                           dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData, \
                                                           currentIndent+1 )

                    for grandChild in grandChildren:
                        currentChild["children"].append( grandChild )

                # Check that there is really data otherwise
                # do not include the currentChild to children.
                if len( currentChild["children"] ) > 0: 
                    children.append( currentChild )

        return children


    def prepareData( self, testcase, dataTypeControl, isInpExpData, level=0 ):

        if 0 == level:

            if isInpExpData:

                self.tcIdSequence = []
                self.inpExpData = [ {}, {} ]

            else:

                self.slotHistIdSequence = []
                self.ancestryInfo = {}
                self.actualInfo = {}
                self.actualData = {}

                self.historyId = testcase.history_id
                slot_histories = testcase.history.slot_histories

                self.prepareActualData( slot_histories )

                return

            if not testcase.is_compound_test:

                self.tcIdSequence.append( testcase.id )
                self.prepareInpExpData_Wrapper( testcase, dataTypeControl )

                return

        for slot in testcase.slots:

            tc = slot.testcase

            if tc.is_compound_test:

                self.prepareData( tc, dataTypeControl, isInpExpData, level=level+1 )

            else:

                if not tc.id in self.tcIdSequence:
                    self.tcIdSequence.append( tc.id )
                    self.prepareInpExpData_Wrapper( tc, dataTypeControl )


    def prepareInpExpData_Wrapper( self, testcase, dataTypeControl ):

        dataTypeIdc = getDataTypeIdc( dataTypeControl )

        for dtIdx in dataTypeIdc:
            self.prepareInpExpData( dtIdx, testcase )


    def prepareInpExpData( self, dtIdx, testcase ):

        if testcase.is_compound_test:
            return

        if not testcase.id in self.inpExpData[dtIdx].keys():
            self.inpExpData[dtIdx][testcase.id] = {}
            
        container = self.inpExpData[dtIdx][testcase.id]

        if 1 == dtIdx:
            source1 = testcase.expected
            source2 = testcase.expected_user_code            
        else:
            source1 = testcase.input
            source2 = testcase.input_user_code

        for sourceData in source1:

            typeKey = "data"

            if sourceData.is_allocate:
                typeKey = "allocate"
            elif sourceData.is_control_flow:
                typeKey = "control_flow"
            elif sourceData.is_csv_data:
                typeKey = "csv_data"
            elif sourceData.is_exception:
                typeKey = "exception"

            data_object_id = sourceData.data_object_id
            valuesAsStr = sourceData.value

            comp = data_object_id.split( "." )

            unitId = int( comp[0] )
            functionIndex = int( comp[1] )
            parameterIndex = int( comp[2] )

            if not unitId in container.keys():
                container[unitId] = {}

            if not functionIndex in container[unitId].keys():
                container[unitId][functionIndex] = {}

            if not parameterIndex in container[unitId][functionIndex].keys():
                container[unitId][functionIndex][parameterIndex] = {}

            currentData = container[unitId][functionIndex][parameterIndex]

            if not data_object_id in currentData.keys():
                currentData[data_object_id] = {}

            if typeKey not in currentData[data_object_id].keys():

                currentData[data_object_id][typeKey] = valuesAsStr

            else:

                msg = "Duplicated entry - catastrophic logic error.\n"
                msg += "dtIdx: %s, testcase: %s\n" % ( str(dtIdx), testcase.__str__() )
                msg += "data_object_id: %s, typeKey: %s\n" % ( data_object_id, typeKey )
                msg += "Old value(s): %s\n" % currentData[data_object_id][typeKey]
                msg += "New value(s): %s" % valuesAsStr
                self.traceHandler.addErrMessage( msg )
                return

        for sourceData in source2:

            if not sourceData.is_testcase_user_code:
                typeKey = "parameter_user_code"
            else:
                continue

            data_object_id = sourceData.data_object_id
            valuesAsStr = sourceData.value

            comp = data_object_id.split( "." )

            unitId = int( comp[0] )
            functionIndex = int( comp[1] )
            parameterIndex = int( comp[2] )

            if not unitId in container.keys():
                container[unitId] = {}

            if not functionIndex in container[unitId].keys():
                container[unitId][functionIndex] = {}

            if not parameterIndex in container[unitId][functionIndex].keys():
                container[unitId][functionIndex][parameterIndex] = {}

            currentData = container[unitId][functionIndex][parameterIndex]

            if not data_object_id in currentData.keys():
                currentData[data_object_id] = {}

            if typeKey not in currentData[data_object_id].keys():

                currentData[data_object_id][typeKey] = valuesAsStr

            else:

                msg = "Duplicated entry - catastrophic logic error.\n"
                msg += "dtIdx: %s, testcase: %s\n" % ( str(dtIdx), testcase.__str__() )
                msg += "data_object_id: %s, typeKey: %s\n" % ( data_object_id, typeKey )
                msg += "Old value(s): %s\n" % currentData[data_object_id][typeKey]
                msg += "New value(s): %s" % valuesAsStr
                self.traceHandler.addErrMessage( msg )
                return


    def prepareActualData( self, slot_histories ):

        for slot_history in slot_histories:

            if slot_history.testhistory_id != self.historyId:
                continue

            slotHistId = slot_history.id

            if not slotHistId in self.slotHistIdSequence:
                self.slotHistIdSequence.append( slotHistId )
                self.ancestryInfo[slotHistId] = []
                self.actualInfo[slotHistId] = []
                self.actualData[slotHistId] = []

            ancestry = slot_history.get_slot_ancestry()

            ancestryList = []

            if len( ancestry ) > 0:

                for ancestor in ancestry:

                    ancestryList.append( [ ancestor.testcase.name, ancestor.slot.index, \
                                           ancestor.slot.testcase.name, ancestor.iteration ] )

            else:

                ancestryList.append( [ slot_history.testcase.name, 1, \
                                       slot_history.testcase.name, -1 ] )

            numItr = slot_history.num_iterations

            self.ancestryInfo[slotHistId] = [[]]*numItr
            self.actualInfo[slotHistId] = [[]]*numItr
            self.actualData[slotHistId] = [[]]*numItr

            for iteration in slot_history.iterations:

                itrIdx = iteration.index - 1

                numRangeItr = len( iteration.range_iterations )
                defaultList = ["<<null>>"]*numRangeItr

                numEvents = None

                for range_iteration in iteration.range_iterations:

                    rangeItrIdx = range_iteration.index - 1

                    if None == numEvents:

                        numEvents = len( range_iteration.events )

                        self.actualInfo[slotHistId][itrIdx] = [[]]*numEvents
                        self.actualData[slotHistId][itrIdx] = [[]]*numEvents

                        for eventIdx in range( numEvents ):        
                            self.actualInfo[slotHistId][itrIdx][eventIdx] = deepcopy( { "eventIdc" : [], \
                                                                                        "functionName" : "<<null>>" } )
                            self.actualData[slotHistId][itrIdx][eventIdx] = deepcopy( {} )

                    for event in range_iteration.events:

                        eventIdx = ( event.index - 1 ) % numEvents

                        self.ancestryInfo[slotHistId][itrIdx]
                        if 0 == len( self.ancestryInfo[slotHistId][itrIdx] ):
                            ancestryList[-1][-1] = iteration.index
                            self.ancestryInfo[slotHistId][itrIdx] = deepcopy( ancestryList )

                        self.actualInfo[slotHistId][itrIdx][eventIdx]["eventIdc"].append( event.index )
                        self.actualInfo[slotHistId][itrIdx][eventIdx]["functionName"] = event.function_display_name

                        container = self.actualData[slotHistId][itrIdx][eventIdx]

                        for actual in event.actuals:

                            data_object_id = actual.data_object_id
                            comp = data_object_id.split( "." )

                            if 1 == len( comp ):

                                 currentData = self.actualInfo[slotHistId][itrIdx][eventIdx]
                                 if not "actuals" in currentData.keys():
                                     currentData["actuals"] = deepcopy( defaultList )

                            else:

                                unitId = int( comp[0] )
                                functionIndex = int( comp[1] )
                                parameterIndex = int( comp[2] )

                                if not unitId in container.keys():
                                    container[unitId] = {}

                                if not functionIndex in container[unitId].keys():
                                    container[unitId][functionIndex] = {}

                                if not parameterIndex in container[unitId][functionIndex].keys():
                                    container[unitId][functionIndex][parameterIndex] = {}

                                currentData = container[unitId][functionIndex][parameterIndex]

                                if not data_object_id in currentData.keys():
                                    currentData[data_object_id] = {}
                                    currentData[data_object_id]["actuals"] = deepcopy( defaultList )
                                
                                currentData = currentData[data_object_id]
                                        
                            if None != actual.value:
                                currentData["actuals"][rangeItrIdx] = actual.value
                            else:
                                currentData["actuals"][rangeItrIdx] = actual.usercode_name                                        

                            if actual.is_result:

                                if not "results" in currentData.keys():
                                    currentData["results"] = deepcopy( defaultList )
                                    currentData["match"] = deepcopy( defaultList )
                                
                                if 1 == actual.match:
                                    currentData["results"][rangeItrIdx] = "pass"
                                else:
                                    currentData["results"][rangeItrIdx] = "fail"

                                currentData["match"][rangeItrIdx] = actual.match_string


    def getAncestryList( self, slot_histories ):

        ancestryList = []

        numSlotHistories = len( slot_histories )
        slotHistory = None
        
        for idx in range( numSlotHostories ):

            slotHistory = slot_histories[idx]

            if slot_history.testhistory_id == self.historyId:
                break

        if None == slotHistory:
            return ancestryList

        ancestry = slot_history.get_slot_ancestry()

        for ancestor in ancestry:

            ancestryList.append( [ ancestor.testcase.name, ancestor.slot.index, \
                                   ancestor.slot.testcase.name ] )

        return ancestryList


    def getDataObjectCoords_arrayIndices( self, dataObjectCoords, \
                                          dtIdx, testcaseId, slotHistId, itrIdx, eventIdx, isInpExpData ):

        arrayIndices = []

        if isInpExpData:
            container = self.inpExpData[dtIdx][testcaseId]
        else:
            container = self.actualData[slotHistId][itrIdx][eventIdx]

        if not dataObjectCoords[0] in container.keys():
            return arrayIndices

        if not dataObjectCoords[1] in container[dataObjectCoords[0]].keys():
            return arrayIndices

        if not dataObjectCoords[2] in container[dataObjectCoords[0]][dataObjectCoords[1]].keys():
            return arrayIndices

        currentData = container[dataObjectCoords[0]][dataObjectCoords[1]][dataObjectCoords[2]]

        numDataObjectCoords = len( dataObjectCoords )

        for data_object_id in currentData.keys():

            currrentObjectCoords = data_object_id.split( "." )
            numCurrentObjectCoords = len( currrentObjectCoords )

            if numCurrentObjectCoords > numDataObjectCoords:

                arrayIndex = int( currrentObjectCoords[numDataObjectCoords] )

                if not arrayIndex in arrayIndices:
                    arrayIndices.append( arrayIndex )

        arrayIndices = sorted( arrayIndices )

        return arrayIndices

            
    def getInpExpData( self, dtIdx, testcaseId, dataObjectCoords, typeKey ):

        data = None

        container = self.inpExpData[dtIdx][testcaseId]

        try:

            currentDataSet = container[dataObjectCoords[0]][dataObjectCoords[1]][dataObjectCoords[2]]

            data_object_id = ".".join( [str(item) for item in dataObjectCoords] )

            data = currentDataSet[data_object_id][typeKey]
            
        except KeyError:

            return data

        return data


    def getActualData( self, slotHistId, itrIdx, eventIdx, dataObjectCoords, typeKey ):

        data = None

        container = self.actualData[slotHistId][itrIdx][eventIdx]

        try:

            currentDataSet = container[dataObjectCoords[0]][dataObjectCoords[1]][dataObjectCoords[2]]

            data_object_id = ".".join( [str(item) for item in dataObjectCoords] )
            
            data = currentDataSet[data_object_id][typeKey]
            
        except KeyError:

            return data

        return data


    def getGlobalVarByIndex( self, envName, unitId, globalVarIndex ):

        api = self.envApi[envName]

        globalVarId = 1
        globalVar = api.Global.get( globalVarId )

        while( None != globalVar ):

            if globalVar.unit_id == unitId:
                if globalVar.index == globalVarIndex:
                    return globalVar

            globalVarId += 1
            globalVar = api.Global.get( globalVarId )

        return None


    def getFunctionByIndex( self, unit, functionIndex ):

        functions = unit.functions

        for function in functions:
            if function.index == functionIndex:
                return function

        return None


    def getAssociatedValues( self, parameterType, valuesAsStr=None, valuesAsList=None ):

        associatedValues = []

        if None != valuesAsStr:
            values = valuesAsStr.split( "%" )
        else:
            values = valuesAsList

        if "ENUMERATION" == parameterType.kind:

            for value in values:
                if "<<null>>" != value:
                    status, assocValue = self.getAssocRangeValue( parameterType, value )
                    if not status:
                        try:
                            int_value = int( float(value) )
                            assocValue = self.getEnumNameByValue( parameterType, int_value )
                        except ValueError:
                            assocValue = value
                else:
                    assocValue = value
                associatedValues.append( assocValue )

        elif "CHAR_ACTER" == parameterType.kind:

            for value in values:
                if "<<null>>" != value:
                    status, assocValue = self.getAssocRangeValue( parameterType, value )
                    if not status:
                        try:
                            int_value = int( float(value) )
                            assocValue = unichr( int_value )
                        except ValueError:
                            assocValue = value
                else:
                    assocValue = value
                associatedValues.append( assocValue )

        else:

            for value in values:
                if "<<null>>" != value:
                    status, assocValue = self.getAssocRangeValue( parameterType, value )
                    if not status:
                        assocValue = value
                else:
                    assocValue = value
                associatedValues.append( assocValue )

        return associatedValues


    def getAssocRangeValue( self, parameterType, value ):

        status = False
        assocValue = None

        numChar = len( value )
        isInputCandidate = False

        if numChar > 7:

            if "#RANGE#" == value[:7]:

                isInputCandidate = True

                infoStr = value[7:]
                compList = infoStr.split( "/" )
                numComp = len( compList )

                if 3 == numComp:
                    status = True
                    isInput = True

        if not isInputCandidate:

            compList = value.split( ".." )
            numComp = len( compList )

            if 2 == numComp:
                status = True
                isInput = False

        if not status:
            return status, assocValue

        assocRangeValues = []

        if "ENUMERATION" == parameterType.kind:

            for idx in range( numComp ):

                comp = compList[idx]
                    
                try:
                    int_comp = int( float(comp) )
                    if idx < 2:
                        assocComp = self.getEnumNameByValue( parameterType, int_comp )
                        assocRangeValues.append( assocComp )
                    else:
                        assocRangeValues.append( int_comp )
                        
                except ValueError:
                    assocRangeValues.append( comp )

        elif "CHAR_ACTER" == parameterType.kind:

            for idx in range( numComp ):

                comp = compList[idx]
                    
                try:
                    int_comp = int( float(comp) )
                    if idx < 2:
                        assocComp = unichr( int_comp )
                        assocRangeValues.append( assocComp )
                    else:
                        assocRangeValues.append( int_comp )
                        
                except ValueError:
                    assocRangeValues.append( comp )

        else:

            assocRangeValues = compList

        if isInput:
            assocValue = "VARY FROM: %s TO: %s BY: %s" % \
                         ( assocRangeValues[0], assocRangeValues[1], assocRangeValues[2] )
        else:
            assocValue = "BETWEEN: %s AND: %s" % \
                         ( assocRangeValues[0], assocRangeValues[1] )

        return status, assocValue


    def getEnumNameByValue( self, parameterType, value ):

        # for enum in parameterType.enums:
        #     if enum.value == value:
        #         return enum.name

        enum = parameterType.get_enum_by_value( value )
        if None != enum:
            return enum.name

        return str(value)

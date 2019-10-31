
import os
import sys

import pprint

from copy import deepcopy

from vector.apps.DataAPI.api import Api

from dataApiReportUtils import getDataTypeIdc, \
    getDataAsString, FormatString


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
                    "value" : None }

    return defaultTree


class DataAPI_Report( object ):

    def __init__( self, workingDirVC ):

        self.workingDirVC = workingDirVC

        self.envApi = {}
        self.inputData = {}
        self.expectedData = {}

        self.indentUnit = "  "


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

            if 1 == dataTypeControl:
                dataTypeAsStr = "Actual Input data"
            elif 2 == dataTypeControl:
                dataTypeAsStr = "Actual Result data"
            elif 3 == dataTypeControl:
                dataTypeAsStr = "Actual Input & Result data"

        tree = getDefaultTree()
        tree["indent"] = currentIndent

        currentChild = getDefaultTree()
        currentChild["indent"] = currentIndent
        currentChild["label"] = "Header"

        grandChild = getDefaultTree()
        grandChild["indent"] = currentIndent
        grandChild["label"] = "%s for:" % dataTypeAsStr
        grandChild["children"] = self.getDataAsTree_slots( testcase, dataTypeControl, isInpExpData, currentIndent+1, level=0 )

        currentChild["children"].append( grandChild )
        tree["children"].append( currentChild )

        currentChild = getDefaultTree()
        currentChild["indent"] = currentIndent
        currentChild["label"] = "TestCaseData"

        currentChild["children"] = self.getDataAsTree_all( testcase, dataTypeControl, isInpExpData, currentIndent+1 )
        tree["children"].append( currentChild )

        # pprint.pprint( tree )

        formatString = FormatString( "  " )
        dataAsString = formatString.getDataAsString( tree, dataTypeControl )

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
                        currentChild["label"] = "TestCase"
                        currentChild["value"] = testcase.name

                        tmpStore[testcaseId] = currentChild

                    else:

                        currentChild = tmpStore[testcaseId]

                    trace( "dtIdx:", dtIdx, newLine=True )
                    trace( "testcaseId:", testcaseId, newLine=True )
                    trace( "Input & Expected Data:", self.inpExpData[dtIdx][testcaseId], newLine=True )

                    arrayChildren[0] = self.getDataAsTree_globals( envName,
                                                                   testcaseId, 0, 0, dtIdx, isInpExpData, \
                                                                   currentIndent+1 )

                    arrayChildren[1] = self.getDataAsTree_functions( envName, testcase, \
                                                                     testcaseId, 0, 0, dtIdx, isInpExpData, \
                                                                     currentIndent+1 )

                    arrayChildren[2] = self.getTestcaseUserCode( envName, testcase, \
                                                                 testcaseId, 0, 0, dtIdx, isInpExpData, \
                                                                 currentIndent+1 )

                    for idx in range( len(arrayChildren) ):
                        for child in arrayChildren[idx]:
                           grandChild["children"].append( child )

                    currentChild["children"].append( grandChild )

            for testcaseId in self.tcIdSequence:
                currentChild = tmpStore[testcaseId]
                children.append( currentChild )

        else:

            for slotId in self.slotIdSequence:

                slot = self.envApi[envName].Slot.get( slotId )
                tc = slot.testcase

                numRangeIterations = len( self.slotData[slotId] )
                for itrIdx in range( numRangeIterations ):

                    ancestryList = self.actualData[slotId][itrIdx]["ancestryList"]

                    ancestryAsStr = ""

                    for ancestor in ancestryList:

                        ancestorAsStr = "%s Slot %s (%s) Iteration %s\n" % \
                                        ( ancestor[0], str(ancestor[1]), \
                                          ancestor[2], str(ancestor[3]) )

                        ancestryAsStr += ancestorAsStr

                    currentChild = getDefaultTree()
                    currentChild["indent"] = tcIndent
                    currentChild["label"] = "Slot"
                    currentChild["value"] = ancestryAsStr

                    trace( "Actual Input & Result Data:", self.slotData[slotId][itrIdx], newLine=True )

                    for dtIdx in dataTypeIdc:

                        grandChild = getDefaultTree()
                        grandChild["indent"] = currentIndent
                        grandChild["label"] = "dtIdx"
                        grandChild["value"] = dtIdx

                        arrayChildren[0] = self.getDataAsTree_globals( envName,
                                                                       tc.id, slotId, dtIdx, dataTypeControl, isInpExpData, \
                                                                       currentIndent+1 )

                        arrayChildren[1] = self.getDataAsTree_functions( envName, tc, \
                                                                         tc.id, slotId, dtIdx, dataTypeControl, isInpExpData, \
                                                                         currentIndent+1 )

                        arrayChildren[2] = self.getTestcaseUserCode( envName, tc, \
                                                                     testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                                                                     currentIndent+1 )

                        for idx in range( len(arrayChildren) ):
                            for child in arrayChildren[idx]:
                                grandChild["children"].append( child )

                        currentChild["children"].append( grandChild )
                        
                    children.append( currentChild )

        return children


    def getDataAsTree_functions( self, envName, testcase, \
                                 testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                                 currentIndent ):

        children = []

        if isInpExpData:
            container = self.inpExpData[dtIdx][testcaseId]
        else:
            container = self.actualData[slotId][itrIdx]

        api = self.envApi[envName]

        # UUT

        currentChild = getDefaultTree()
        currentChild["indent"] = currentIndent
        currentChild["label"] = "<<UUT>>"

        unitName = testcase.unit_display_name
        unit = api.Unit.get( unitName )

        function = testcase.function

        currentChild["children"] = self.getDataAsTree_parameters( unit, function, \
                                                                  testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
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
                                                               testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
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
                                                               testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                                                               currentIndent )

                for grandChild in grandChildren:
                    currentChild["children"].append( grandChild )

        children.append( currentChild )

        return children


    def getDataAsTree_parameters( self, unit, function, \
                                  testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
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
                                                  testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
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
                               testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                               currentIndent ):

        children = []

        currentChild = getDefaultTree()
        currentChild["indent"] = currentIndent
        currentChild["label"] = "<<GLOBALS>>"

        if isInpExpData:
            container = self.inpExpData[dtIdx][testcaseId]
        else:
            container = self.actualData[dtIdx][slotId][itrIdx]

        api = self.envApi[envName]

        functionIndex = 0

        for unitId in container.keys():

            if not functionIndex in container[unitId].keys():
                continue

            unit = api.Unit.get( unitId )

            grandChildren = self.getDataAsTree_globalsInUnit( envName, unit, \
                                                              testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                                                              currentIndent )

            for grandChild in grandChildren:
                currentChild["children"].append( grandChild )

        children.append( currentChild )

        return children

    
    def getDataAsTree_globalsInUnit( self, envName, unit, \
                                     testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
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
            container = self.actualData[dtIdx][slotId][itrIdx]

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
                                                  testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                                                  parameterIndent )

            for child in partChildren:
                functionChild["children"].append( child )

        if len( functionChild["children"] ) > 0:
            unitChild["children"].append( functionChild )
            children.append( unitChild )

        return children


    def getTestcaseUserCode( self, envName, testcase, \
                             testcaseId, slotId, itrIdx, dtIdx, isInpExpData,
                             currentIndent ):

        children = []

        unitIndent = currentIndent
        functionIndent = currentIndent + 1
        tcIndent = currentIndent + 2

        if isInpExpData:

            if 1 == dtIdx:
                source = testcase.expected_user_code
            else:
                source = testcase.input_user_code

        api = self.envApi[envName]

        unitName = testcase.unit_display_name
        unit = api.Unit.get( unitName )

        function = testcase.function
        functionNameAsStr = "%s: %s" % ( function.name, "<<User Code>>" )

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
        tcChild["label"] = "TestCase "
        tcChild["value"] = functionNameAsStr

        codeChild = None

        for sourceData in source:

            if sourceData.is_testcase_user_code:
                
                codeChild = getDefaultTree()
                codeChild["indent"] = tcIndent+1
                codeChild["value"] = sourceData.value
                tcChild["children"].append( codeChild )

        if None != codeChild:
            currentChild["children"].append( unitChild )
            currentChild["children"].append( functionChild )
            currentChild["children"].append( tcChild )

        return children


    def walkType_Wrapper( self, parameter, dataObjectCoords, \
                          testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                          currentIndent ):

        children = self.walkType( parameter.name, parameter.type, dataObjectCoords, \
                                  testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                                  currentIndent )

        return children


    def walkType( self, parameterName, parameterType, dataObjectCoords, \
                  testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                  currentIndent ):

        children = []

        indexIndent = currentIndent + 1

        data_object_id = ".".join( [str(item) for item in dataObjectCoords] )

        if isInpExpData:
            valuesAsStr = self.getInpExpData( dtIdx, testcaseId, dataObjectCoords, "data" )
        else:
            valuesAsStr = self.getSlotData( slotId, itrIdx, dtIdx, dataObjectCoords, "data" )

        kind = parameterType.kind
        element = parameterType.element

        trace( "Parameter/Field name:", parameterName )
        trace( "Type kind:", kind )
        trace( "data_object_id:", data_object_id )

        currentChild = getDefaultTree()
        currentChild["doc"] = dataObjectCoords
        currentChild["indent"] = currentIndent
        currentChild["label"] = parameterName

        if None == valuesAsStr:

            valuesAsStr = self.getInpExpData( dtIdx, testcaseId, dataObjectCoords, "parameter_user_code" )

            if None != valuesAsStr:
                
                currentChild["value"] = "<<User Code>>"
                children.append( currentChild )

                currentChild = getDefaultTree()
                currentChild["indent"] = currentIndent+1
                currentChild["value"] = valuesAsStr
                children.append( currentChild )

                return children

        isArray = False
        isBasicType = True

        if "ACCE_SS" == kind:

            isArray = True

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

        elif "STR_ING" == kind:

            isArray = True

            if "CHAR_ACTER" == element.kind:
                if None != valuesAsStr:
                    isArray = False

            if 1 == dtIdx:

                currentChild["value"] = "<<ACCESS>>"

            else:

                allocateAsStr = self.getInpExpData( dtIdx, testcaseId, dataObjectCoords, "allocate" )
                if None == allocateAsStr:
                    return children

                currentChild["value"] = "<<ALLOCATE %s>>" % allocateAsStr

        elif "AR_RAY" == kind:

            isArray = True

            size = parameterType.range.size # Still something like "4%%"
            size = size.split( "%" )[0]

            currentChild["value"] = "<<Size %s>>" % size

        elif "REC_ORD" == kind:

            isBasicType = False

            child_fields = parameterType.child_fields

        if isArray:

            arrayIndices = self.getDataObjectCoords_arrayIndices( dtIdx, testcaseId, dataObjectCoords )
            trace( "Array: arrayIndices:", str(arrayIndices) )

            for arrayIndex in arrayIndices:

                index_dataObjectCoords = deepcopy( dataObjectCoords )
                index_dataObjectCoords.append( arrayIndex )

                trace( "Array: Basic Type: index_dataObjectCoords:", str(index_dataObjectCoords) )
                trace( "Array: Basic Type: valuesAsStr:", str(valuesAsStr) )

                indexName = "%s[%s]" % ( parameterName, str(arrayIndex) )

                grandChildren = self.walkType( indexName, element, index_dataObjectCoords, \
                                               testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
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
                trace( "Basic Type: valuesAsStr:", str(valuesAsStr) )

                if None != valuesAsStr:

                    associatedValues = self.getAssociatedValues( parameterType, valuesAsStr )

                    currentChild["value"] = ",".join( associatedValues )
                    children.append( currentChild )

            else:

                for child in child_fields:

                    child_dataObjectCoords = deepcopy( dataObjectCoords )
                    child_dataObjectCoords.append( child.index )

                    trace( "None Basic Type: child_dataObjectCoords:", str(child_dataObjectCoords) )

                    grandChildren = self.walkType_Wrapper( child, child_dataObjectCoords,\
                                                           testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
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
                self.slotIdSequence = []
                self.actualIData

            self.historyId = testcase.history_id

            if not testcase.is_compound_test:

                if isInpExpData:
                    self.tcIdSequence.append( testcase.id )
                    self.prepareInpExpData_Wrapper( testcase, dataTypeControl )
                else:
                    self.slotIdSequence.append( testcase.id )
                    self.prepareActualData( 0, testcase.history.slot_histories )

                return

        for slot in testcase.slots:

            tc = slot.testcase

            if tc.is_compound_test:

                self.prepareData( tc, dataTypeControl, isInpExpData, level=level+1 )

            else:

                if isInpExpData:
                    if not tc.id in self.tcIdSequence:
                        self.tcIdSequence.append( tc.id )
                        self.prepareInpExpData_Wrapper( tc, dataTypeControl )
                else:
                    self.slotIdSequence.append( slot.id )
                    self.prepareActualData( slot.id, slot.slot_histories )


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

                print( "Duplicated entry - catastrophic logic error.\n" )
                print( dtIdx, testcase )
                print( data_object_id, typeKey )
                print( "Old value(s): %s" % currentData[data_object_id][typeKey] )
                print( "New value(s): %s" % valuesAsStr )
                sys.exit()

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

                print( "Duplicated entry - catastrophic logic error.\n" )
                print( data_oject_id, typeKey )
                print( "Old value(s): %s" % currentData[data_object_id][typeKey] )
                print( "New value(s): %s" % valuesAsStr )
                sys.exit()


    def prepareActualData( self, slotId, slot_histories ):

        if not slotId in self.actualData.keys():
            self.actualData[slotId] = []

        cotainer = self.actualData[slotId]

        for slot_history in slot_histories:

            if slot_history.testhistory_id != self.historyId:
                continue

            ancestry = slot_history.get_slot_ancestry()

            ancestryList = []

            for ancestor in ancestry:

                ancestryList.append( [ ancestor.testcase.name, ancestor.slot.index, \
                                       ancestor.slot.testcase.name, ancestor.iteration ] )

            for iteration in slot_history.iterations:

                numRangeItr = len( iteration.range_iterations )

                container = [{}]*numRangeItr
                defaultList = ["None"]*numRangeItr

                for range_iteration in iteration.range_iterations:

                    numEvents = len( range_iteration.events )

                    for event in range_iteration.events:

                        itrIdx = event.iteration_index - 1
                        rangeItrIdx = event.range_iteration_index - 1

                        ancestryList[-1][-1] = event.iteration_index

                        container[itrIdx]["ancestryList"] = ancestryList

                        for actual in event.actuals:

                            if event.index == numEvents:
                                
                                if actual.is_result:
                                    dataTypeIndex = 1
                                else:
                                    continue

                            else:

                                if actual.is_result:
                                    dataTypeIndex = 1
                                else:
                                    dataTypeIndex = 0

                            data_object_id = actual.data_object_id

                            comp = data_object_id.split( "." )

                            if not data_object_id in container[itrIdx].keys():
                                container[itrIdx][data_object_id] = [ {}, {} ]
                                container[itrIdx][data_object_id][dataTypeIndex]["actuals"] = deepcopy( defaultList )
                                if actual.is_result:
                                    container[itrIdx][data_object_id][dataTypeIndex]["results"] = deepcopy( defaultList )

                            theContainer = container[itrIdx][data_object_id][dataTypeIndex]
                                        
                            if None != actual.value:
                                theContainer["actuals"][rangeItrIdx] = actual.value
                            else:
                                theContainer["actuals"][rangeItrIdx] = actual.usercode_name                                        

                            if actual.is_result:
                                if 1 == actual.match:
                                    theContainer["results"][rangeItrIdx] = "PASS"
                                else:
                                    theContainer["results"][rangeItrIdx] = "FAIL"


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


    def getDataObjectCoords_arrayIndices( self, dtIdx, testcaseId, dataObjectCoords ):

        arrayIndices = []

        container = self.inpExpData[dtIdx][testcaseId]

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


    def getSlotData( self, slotId, itrIdx, dataObjectCoords, dataTypeIdc, typeKey ):

        data = [None]*2

        container = self.slotData[slotId][itrIdx]

        data_object_id = ".".join( [str(item) for item in dataObjectCoords] )

        try:
            currentDataSet = container[data_object_id]
            
        except KeyError:

            return data

        for dtIdx in dataTypeIdc:

            if typeKey in currentDataSet[dtIdx].keys():
                data[dtIdx] = currentDataSet[dtIdx][typeKey]

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


    def getAssociatedValues( self, parameterType, valuesAsStr ):

        associatedValues = []

        values = valuesAsStr.split( "%" )

        isConvertible = True

        try:
            float_value = float( values[0] )
        except ValueError:
            isConvertible = False

        if not isConvertible:
            associatedValues = values
            return associatedValues

        if "ENUMERATION" == parameterType.kind:
            for value in values:
                assocValue = self.getEnumNameByValue( parameterType, int(value) )
                associatedValues.append( assocValue )
        elif "CHAR_ACTER" == parameterType.kind:
            for value in values:
                assocValue = unichr( int(float(value)) )
                associatedValues.append( assocValue )
        else:
            associatedValues = values

        return associatedValues


    def getEnumNameByValue( self, parameterType, value ):

        # for enum in parameterType.enums:
        #     if enum.value == value:
        #         return enum.name

        enum = parameterType.get_enum_by_value( value )
        if None != enum:
            return enum.name

        return str(value)

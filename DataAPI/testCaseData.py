
import os
import sys

import pprint

from copy import deepcopy

from vector.apps.DataAPI.api import Api


DEBUG = True


def trace( str1, str2, newLine=False):

    global DEBUG

    if not DEBUG:
        return

    if newLine:
        print( str1 )
        print( str2 )
    else:
        print( str1 + " " + str2 )


class TestCaseData( object ):

    def __init__( self, envName, unitName, functionName, tcName, dataApi ):

        self.envName = envName
        self.unitName = unitName
        self.functionName = functionName
        self.tcName = tcName

        self.dataApi = dataApi

        self.inputDataAsString = None
        self.expectedDataAsString = None
        self.inpExpDataAsString = None

        self.actualInputDataAsString = None
        self.actualExpectedDataAsString = None
        self.actualInpExpDataAsString = None

        self.initialize()


    def initialize( self ):

        self.dataApi.loadApi( self.envName )

        self.testcase = self.dataApi.getTestcase( self.envName, self.unitName, \
                                                  self.functionName, self.tcName )

        if None == self.testcase:
            print( "No testcase found for following input:" )
            print( self )
            sys.exit()

    def __str__( self ):

        msg = "TestCaseData:\n"
        msg += "Environment: %s\n" % self.envName
        msg += "Unit: %s\n" % self.unitName
        msg += "Function: %s\n" % self.functionName
        msg += "TestCase: %s\n" % self.tcName

        return msg


    def buildInpExpDataAsString( self, dataTypeControl ):

        if 1 == dataTypeControl:
            self.inputDataAsString = self.dataApi.getDataAsString( self.testcase.input_tree )
        elif 2 == dataTypeControl:
            self.expectedDataAsString = self.dataApi.getDataAsString( self.testcase.expected_tree )
        elif 3 == dataTypeControl:
            self.inpExpDataAsString = self.dataApi.getDataAsString( self.testcase.input_tree )
            self.inpExpDataAsString += self.dataApi.getDataAsString( self.testcase.expected_tree )


    def buildInpExpDataAsString_explicit( self, dataTypeControl ):

        if 1 == dataTypeControl:
            self.inputDataAsString = self.dataApi.getDataAsString_explicit( self.testcase, dataTypeControl, True, 0 )
        elif 2 == dataTypeControl:
            self.expectedDataAsString = self.dataApi.getDataAsString_explicit( self.testcase, dataTypeControl, True, 0 )
        elif 3 == dataTypeControl:
            self.inpExpDataAsString = self.dataApi.getDataAsString_explicit( self.testcase, dataTypeControl, True, 0 )


    def getInpExpDataAsString( self, dataTypeControl ):

        buildNeeded = False

        if 1 == dataTypeControl:
            if None == self.inputDataAsString:
                buildNeeded = True
        elif 2 == dataTypeControl:
            if None == self.expectedDataAsString:
                buildNeeded = True
        elif 3 == dataTypeControl:
            if None == self.inpExpDataAsString:
                buildNeeded = True

        if buildNeeded:
            # self.buildInpExpDataAsString( dataTypeControl )
            self.buildInpExpDataAsString_explicit( dataTypeControl )

        if 1 == dataTypeControl:
            return self.inputDataAsString
        elif 2 == dataTypeControl:
            return self.expectedDataAsString
        elif 3 == dataTypeControl:
            return self.inpExpDataAsString


class DataAPI_Wrapper( object ):

    def __init__( self, workingDirVC ):

        self.workingDirVC = workingDirVC

        self.envApi = {}
        self.inputData = {}
        self.expectedData = {}

        self.indentUnit = "  "


    def getDefaultTree( self ):

        defaultTree = { "children" : [], \
                        "indent" : 0, \
                        "label" : None, \
                        "value" : None }

        return defaultTree


    def getDataTypeIdc( self, dataTypeControl ):

        if 1 == dataTypeControl:
            dataTypeIdc = [ 0 ]
        elif 2 == dataTypeControl:
            dataTypeIdc = [ 1 ]
        elif 3 == dataTypeControl:
            dataTypeIdc = [ 0, 1 ]

        return dataTypeIdc


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


    def getIndentAsString( self, numIndentUnits ):
        return self.indentUnit * numIndentUnits

        
    def getDataAsString( self, tree ):

        dataAsString = ""

        currentIndent = int( tree["indent"] )
        currentIndentAsStr = self.getIndentAsString( currentIndent ) 

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
            dataAsString += self.getDataAsString( child, "" )

        return dataAsString


    def getDataAsString_2( self, tree ):

        dataAsString = ""

        currentIndent = int( tree["indent"] )
        currentIndentAsStr = self.getIndentAsString( currentIndent ) 

        label = tree["label"]
        value = tree["value"]

        if None != label:

            if None != value:
                newStr = label + ": "  + str(value) + "\n"
            else:
                newStr = label + "\n"

            dataAsString += currentIndentAsStr + newStr

        children = tree["children"]

        for child in children:
            dataAsString += self.getDataAsString_2( child )

        return dataAsString


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

        tree = self.getDefaultTree()
        tree["indent"] = currentIndent
        tree["label"] = "%s for:\n" % dataTypeAsStr

        tree["children"] = self.getDataAsTree_explicit( testcase, dataTypeControl, isInpExpData, currentIndent+1, level=0 )

        pprint.pprint( tree )

        dataAsString = self.getDataAsString_2( tree )

        return dataAsString


    def getDataAsTree_explicit( self, testcase, dataTypeControl, isInpExpData, currentIndent, level=0 ):

        envName = testcase.get_environment().name
        unitName = testcase.unit_display_name
        functionName = testcase.function_display_name

        children = []

        if 0 == level:

            envIndent = currentIndent
            unitIndent = currentIndent
            functionIndent = currentIndent
            tcIndent = currentIndent 

            parameterIndent = currentIndent + 1
            slotIndent = currentIndent + 1

            if testcase.is_compound_test:

                tcNameAsStr = "%s (Compound)\n" % testcase.name

            elif testcase.is_unit_test:

                tcNameAsStr = "%s (Unit)\n" % testcase.name

            currentChild = self.getDefaultTree()
            currentChild["indent"] = envIndent
            currentChild["label"] = "Environment"
            currentChild["value"] = envName
            children.append( currentChild )

            currentChild = self.getDefaultTree()
            currentChild["indent"] = unitIndent
            currentChild["label"] = "Unit"
            currentChild["value"] = unitName
            children.append( currentChild )

            currentChild = self.getDefaultTree()
            currentChild["indent"] = functionIndent
            currentChild["label"] = "Function"
            currentChild["value"] = functionName
            children.append( currentChild )

            currentChild = self.getDefaultTree()
            currentChild["indent"] = tcIndent
            currentChild["label"] = "Testcase"
            currentChild["value"] = tcNameAsStr
            children.append( currentChild )

            self.prepareData( testcase, dataTypeControl, isInpExpData )

        else:

            parameterIndent = currentIndent
            slotIndent = currentIndent

        if testcase.is_compound_test:

            slots = testcase.slots
            numSlots = len( slots )

            for idx in range( numSlots ):

                tc = slots[idx].testcase

                slotName = ".".join( [tc.unit_display_name, tc.function_display_name, tc.name] )
                slotAsStr = "Slot %s: %s (%s)" % ( str(slots[idx].index), slotName, slots[idx].iteration_count )

                slotTree = self.getDefaultTree()

                slotTree["indent"] = slotIndent
                slotTree["label"] = slotAsStr

                if tc.is_compound_test:
                    slotTree["children"] = self.getDataAsTree_explicit( tc, dataTypeControl, isInpExpData, \
                                                                        slotIndent+1, \
                                                                        level=level+1 )

                if level > 0:
                    children.append( slotTree )
                else:
                    currentChild["children"].append( slotTree )

            if level > 0:
                return children
            else:
                currentChild["children"] = self.getDataAsTree_all( testcase, dataTypeControl, isInpExpData, uniIndent )
                return children


        elif testcase.is_unit_test:

            currentChild["children"] = self.getDataAsTree_all( testcase, dataTypeControl, isInpExpData, unitIndent )

            return children


    def getDataAsTree_all( self, testcase, dataTypeControl, isInpExpData, currentIndent ):

        children = []

        envName = testcase.get_environment().name

        dataTypeIdc = self.getDataTypeIdc( dataTypeControl )

        arrayChildren = [ [], [], [] ]

        if isInpExpData:

            tmpStore = {}

            for dtIdx in dataTypeIdc:

                for testcaseId in self.inpExpData[dtIdx].keys():

                    grandChild = self.getDefaultTree()
                    grandChild["indent"] = currentIndent
                    grandChild["label"] = "branch"
                    grandChild["value"] = dtIdx

                    if not testcaseId in tmpStore.keys():

                        currentChild = self.getDefaultTree()
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

                    # arrayChildren[2] = self.getTestcaseUserCode( testcase, dataTypeControl, unitIndent )

                    for idx in range( len(arrayChildren) ):
                        for child in arrayChildren[idx]:
                           grandChild["children"].append( child )

                    currentChild["children"].append( grandChild )

            for testcaseId, currentChild in tmpStore.items():
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

                    currentChild = self.getDefaultTree()
                    currentChild["indent"] = tcIndent
                    currentChild["label"] = "Slot"
                    currentChild["value"] = ancestryAsStr

                    trace( "Actual Input & Result Data:", self.slotData[slotId][itrIdx], newLine=True )

                    for dtIdx in dataTypeIdc:

                        grandChild = self.getDefaultTree()
                        grandChild["indent"] = currentIndent
                        grandChild["label"] = "branch"
                        grandChild["value"] = dtIdx

                        arrayChildren[0] = self.getDataAsTree_globals( envName,
                                                                       tc.id, slotId, dtIdx, dataTypeControl, isInpExpData, \
                                                                       currentIndent+1 )

                        arrayChildren[1] = self.getDataAsTree_functions( envName, tc, \
                                                                         tc.id, slotId, dtIdx, dataTypeControl, isInpExpData, \
                                                                         currentIndent+1 )

                        # arrayChildren[2] = self.getTestcaseUserCode( tc, isExpectedData, unitIndent )

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

        arrayChildren = [ [], [], [] ]

        if isInpExpData:
            container = self.inpExpData[dtIdx][testcaseId]
        else:
            container = self.actualData[slotId][itrIdx]

        api = self.envApi[envName]

        # UUT

        unitName = testcase.unit_display_name
        unit = self.envApi[envName].Unit.get( unitName )

        function = testcase.function

        arrayChildren[0] = self.getDataAsTree_parameters( unit, function, \
                                                          testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                                                          currentIndent )

        # SBF

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

                partChildren = self.getDataAsTree_parameters( unit, function, \
                                                              testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                                                              currentIndent )

                for child in partChildren:
                    arrayChildren[1].append( child )

        # All other stubs (different units)

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

                partChildren = self.getDataAsTree_parameters( unit, function, \
                                                              testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                                                              currentIndent )

                for child in partChildren:
                    arrayChildren[2].append( child )

        for idx in range( len(arrayChildren) ):
            for child in arrayChildren[idx]:
                children.append( child )

        return children


    def getDataAsTree_parameters( self, unit, function, \
                                  testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                                  currentIndent ):

        children = []

        unitIndent = currentIndent
        functionIndent = currentIndent + 1
        parameterIndent = currentIndent + 2

        currentChild = self.getDefaultTree()
        currentChild["indent"] = unitIndent
        currentChild["label"] = "Unit"
        currentChild["value"] = unit.name

        grandChild = self.getDefaultTree()
        grandChild["indent"] = functionIndent
        grandChild["label"] = "Subprogram"

        functionNameAsStr = "%s" % function.name
        functionDataAsStr = None

        if isInpExpData:
        
            if unit.stub_by_function:
                dataObjectCoords = [ unit.id, function.index, function.sbf_index ]
                functionDataAsStr = self.getInpExpData( dtIdx, testcaseId, dataObjectCoords, "data" )

            if None != functionDataAsStr:
                functionNameAsStr = "%s: %s" % ( function.name, functionDataAsStr )

        grandChild["value"] = functionNameAsStr

        parameterIndex = 1
        parameter = function.get_param_by_index( parameterIndex )

        while None != parameter:

            dataObjectCoords = [ unit.id, function.index, parameterIndex ]

            partChildren = self.walkType_Wrapper( parameter, dataObjectCoords, \
                                                  testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                                                  parameterIndent )

            for child in partChildren:
                grandChild["children"].append( child )

            parameterIndex += 1
            parameter = function.get_param_by_index( parameterIndex )

        currentChild["children"].append( grandChild )
        children.append( currentChild )

        return children


    def getDataAsTree_globals( self, envName, \
                               testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                               currentIndent ):

        children = []

        if isInpExpData:
            container = self.inpExpData[dtIdx][testcaseId]
        else:
            container = self.actualData[dtIdx][slotId][itrIdx]

        api = self.envApi[envName]

        for unitId in container.keys():

            unit = api.Unit.get( unitId )

            partChildren = self.getDataAsTree_globalsInUnit( envName, unit, \
                                                             testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                                                             currentIndent )

            for child in partChildren:
                children.append( child )

        return children

    
    def getDataAsTree_globalsInUnit( self, envName, unit, \
                                     testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                                     currentIndent ):

        children = []

        if "uut_prototype_stubs" == unit.name:
            return children

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

        if not unitId in container.keys():
            return children

        if not functionIndex in container[unitId].keys():
            return children

        children.append( self.getDefaultTree() )
        currentTree = children[-1]
        currentTree["indent"] = unitIndent
        currentTree["label"] = "Unit"
        currentTree["value"] = unit.name

        currentTree["children"].append( self.getDefaultTree() )
        currentTree = currentTree["children"][-1]
        currentTree["indent"] = functionIndent
        currentTree["label"] = functionNameAsStr

        currentData = container[unitId][functionIndex]
        
        for globalVarIndex in currentData.keys():

            dataObjectCoords = [ unitId, functionIndex, globalVarIndex ]

            # globalVar = self.getGlobalVarByIndex( envName, unitId, globalVarIndex )
            globalVar = unit.get_global_by_index( globalVarIndex )

            partChildren = self.walkType_Wrapper( globalVar, dataObjectCoords, \
                                                  testcaseId, slotId, itrIdx, dtIdx, isInpExpData, \
                                                  parameterIndent )

            for child in partChildren:
                currentTree["children"].append( child ) 

        return children


    def getTestcaseUserCode( self, testcase, isExpectedData, currentIndent ):

        currentIndentAsStr = self.getIndentAsString( currentIndent )

        unitIndent = currentIndent
        unitIndentAsStr = self.getIndentAsString( unitIndent )
            
        functionIndent = currentIndent + 1
        functionIndentAsStr = self.getIndentAsString( functionIndent )

        tcIndent = currentIndent + 2
        tcIndentAsStr = self.getIndentAsString( tcIndent )

        dataAsString = ""

        if isExpectedData:
            container = self.expectedData
            source = testcase.expected_user_code
        else:
            container = self.inputData
            source = testcase.input_user_code

        envName = testcase.get_environment().name

        unitNameAsStr = "UUT: %s\n" % testcase.unit_display_name 
        dataAsString += unitIndentAsStr + unitNameAsStr

        functionNameAsStr = "Subprogram: %s\n" % testcase.function_display_name
        dataAsString += functionIndentAsStr + functionNameAsStr

        tcNameAsStr = "Testcase: %s: %s\n" % ( testcase.name, "<<Testcase User Code>>" )
        dataAsString += tcIndentAsStr + tcNameAsStr

        for sourceData in source:

            if sourceData.is_testcase_user_code:
                formattedUserCode= self.formatMultiLine( sourceData.value, tcIndent+1 )
                dataAsString += formattedUserCode

        return dataAsString


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

        currentChild = self.getDefaultTree()
        currentChild["indent"] = currentIndent
        currentChild["label"] = parameterName

        if None == valuesAsStr:

            valuesAsStr = self.getInpExpData( dtIdx, testcaseId, dataObjectCoords, "parameter_user_code" )

            if None != valuesAsStr:
                
                currentChild["value"] = "<<User Code>>"
                children.append( currentChild )

                currentChild = self.getDefaultTree()
                currentChild["indent"] = currentIndent
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
                self.inpExpData = [ {}, {} ]
            else:
                self.slotIdSequence = []
                self.actualIData

            self.historyId = testcase.history_id

            if not testcase.is_compound_test:

                if isInpExpData:
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
                    self.prepareInpExpData_Wrapper( testcase, dataTypeControl )
                else:
                    self.slotIdSequence.append( slot.id )
                    self.prepareActualData( slot.id, slot.slot_histories )


    def prepareInpExpData_Wrapper( self, testcase, dataTypeControl ):

        dataTypeIdc = self.getDataTypeIdc( dataTypeControl )

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
                print( data_oject_id, typeKey )
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


    def formatMultiLine( self, multiLineStr, currentIndent ):

        formattedStr = ""

        currentIndentAsStr = self.getIndentAsString( currentIndent )

        lines = multiLineStr.split( "\n" )

        for line in lines:
            formattedStr += currentIndentAsStr + line + "\n"

        return formattedStr


if "__main__" == __name__:

    numParameters = len( sys.argv ) - 1

    if 0 == numParameters:

        dataApi = DataAPI_Wrapper( "C:\Work\Training\V6.4\MinGW_WorkDir" )
        tcData = TestCaseData( "EXAMPLE", "example", "append", "append.001", dataApi )
        # tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "manager", "Add_Party_To_Waiting_List", "UserCode", dataApi )
        # tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "manager", "Place_Order", "FoolTheBill", dataApi )
        # tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "<<COMPOUND>>", "<<COMPOUND>>", "Asterix&Obelix", dataApi )
        # tcData = TestCaseData( "IO_WRAPPER_BUBEN", "<<COMPOUND>>", "<<COMPOUND>>", "Write&Read", dataApi )
        # tcData = TestCaseData( "ADVANCED", "advanced_stubbing", "temp_monitor", "Celsius_Stub", dataApi )

        print( tcData )

        print( tcData.getInpExpDataAsString( 1 ) )
        # print( tcData.getInpExpDataAsString( 2 ) )

    elif 2 == numParameters:

        dataApi = DataAPI_Wrapper( sys.argv[1] )
        api = dataApi.getApi( sys.argv[2] )

        testcases = api.TestCase.all()

        for testcase in testcases:

            inputDataAsString = dataApi.getDataAsString_explicit( testcase, 1, 0 )
            expectedDataAsString = dataApi.getDataAsString_explicit( testcase, 2, 0 )

            print( inputDataAsString )
            print( expectedDataAsString )

    elif 5 == numParameters:

        dataApi = DataAPI_Wrapper( sys.argv[1] )
        tcData = TestCaseData( sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], dataApi )
        
        print( tcData )

        print( tcData.getInpExpDataAsString( 1 ) )
        print( tcData.getInpExpDataAsString( 2 ) )

    else:

        print( "Inappropriate number of parameters." )

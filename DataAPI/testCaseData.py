
import os
import sys

import pprint

from copy import deepcopy

from vector.apps.DataAPI.api import Api


DEBUG = False


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
                        "values" : [ None, None ] }

        return defaultTree


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

        testcases = api.TestCase.get( tcName )

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
        values = tree["values"]

        if None != label:

            if None != values[0]:
                newStr = label + ":"  + value + "\n"
            else:
                newStr = label + "\n"

            dataAsString += currentIndentAsStr + newStr

        children = tree["children"]

        for child in children:
            dataAsString += self.getDataAsString_2( child )

        return dataAsString


    def getDataAsString_explicit( self, testcase, dataTypeControl, isInpExpData, currentIndent ):

        tree = self.getDefaultTree()
        tree["indent"] = currentIndent
        tree["children"] = self.getDataAsTree_explicit( testcase, dataTypeControl, isInpExpData, currentIndent, level=0 )

        dataAsString = self.getDataAsString_2( tree )

        return dataAsString


    def getDataAsTree_explicit( self, testcase, dataTypeControl, isInpExpData, currentIndent, level=0 ):

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

        envName = testcase.get_environment().name
        unitName = testcase.unit_display_name
        functionName = testcase.function_display_name

        children = []

        if 0 == level:

            envIndent = currentIndent + 1
            unitIndent = currentIndent + 1
            functionIndent = currentIndent + 1
            tcIndent = currentIndent + 1

            parameterIndent = currentIndent + 4
            slotIndent = currentIndent + 4

            if testcase.is_compound_test:

                tcNameAsStr = "TestCase: %s (Compound)" % testcase.name

            elif testcase.is_unit_test:

                tcNameAsStr = "TestCase: %s (Unit)" % testcase.name

            children.append( self.getDefaultTree() )
            currentTree = children[-1]
            currentTree["indent"] = currentIndent
            currentTree["label"] = "%s for:\n" % dataTypeAsStr

            children.append( self.getDefaultTree() )
            currentTree = children[-1]
            currentTree["indent"] = envIndent
            currentTree["label"] = "Environment: %s" % envName

            children.append( self.getDefaultTree() )
            currentTree = children[-1]
            currentTree["indent"] = unitIndent
            currentTree["label"] = "Unit: %s" % unitName

            children.append( self.getDefaultTree() )
            currentTree = children[-1]
            currentTree["indent"] = functionIndent
            currentTree["label"] = "Function: %s" % functionName

            children.append( self.getDefaultTree() )
            currentTree = children[-1]
            currentTree["indent"] = tcIndent
            currentTree["label"] = tcNameAsStr

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
                slotAsStr = "Slot %s: %s (%s)" % ( str(slots[idx].idx), slotName, slots[idx].iteration_count )

                if level > 0:
                    children.append( self.getDefaultTree() )
                    slotTree = children[-1]
                else:
                    currentTree["children"].append( self.getDefaultTree() )
                    slotTree = currentTree["children"][-1]

                slotTree["indent"] = slotIndent
                slotTree["label"] = slotAsStr

                if tc.is_compound_test:
                    slotTree["children"] = self.getDataAsString_explicit( tc, dataTypeControl, isInpExpData, \
                                                                          slotIndent+1, \
                                                                          level=level+1 )

            if level > 0:
                return children

            for slotId in self.slotIdSequence:

                slot = self.envApi[envName].Slot.get( slotId )
                tc = slot.testcase

                ancestryList = self.getAncestryList( slot.slot_histories )

                ancestorAsStr = ""

                for ancestor in ancestryList:

                    ancestorAsStr = "%s Slot %s (%s)\n" % \
                                    ( ancestor[0], str(ancestor[1]), ancestor[2] )

                    ancestryAsStr += ancestorAsStr

                slotNameAsStr = "%s: %s:" %( ancestryAsStr, dataTypeAsStr )

                children.append( self.getDefaultTree() )
                slotTree = children[-1]
                slotTree["indent"] = tcIndent
                slotTree["label"] = slotNameAsStr

                trace( "Input & Expected Data:", self.inpExpData[tc.id], newLine=True )

                # slotTree["children"] = self.getDataAsString_globals( envName,
                #                                                      tc.id, slotId, dataTypeControl, isInpExpData, \
                #                                                      unitIndent )

                # dataAsString += self.getDataAsString_functions( tc, isExpectedData, unitIndent )
                # dataAsString += self.getTestcaseUserCode( tc, isExpectedData, unitIndent )

            return children

        elif testcase.is_unit_test:

            trace( "Input & Expected Data:", self.inpExpData[testcase.id], newLine=True )

            # currentTree["children"] = self.getDataAsString_globals( envName,
            #                                                         testcase.id, 0, 0, dataTypeControl, isInpExpData, \
            #                                                         unitIndent )

            # dataAsString += self.getDataAsString_functions( testcase, dataTypeControl, unitIndent )
            # dataAsString += self.getTestcaseUserCode( testcase, dataTypeControl, unitIndent )

            return children


    def getDataAsString_functions( self, testcase, isExpectedData, currentIndent ):

        dataAsString = ""

        if isExpectedData:
            container = self.expectedData
        else:
            container = self.inputData

        # UUT

        envName = testcase.get_environment().name

        unitName = testcase.unit_display_name
        unit = self.envApi[envName].Unit.get( unitName )

        function = testcase.function

        dataAsString_UUT = self.getDataAsString_parameters( unit, function, isExpectedData, currentIndent )

        # SBF

        dataAsString_SBF = ""

        tc_unitId = unit.id
        tc_functionIndex = function.index

        for functionIndex in container[tc_unitId].keys():

            # Skip globals
            if functionIndex == 0:
                continue

            # Skip the function associated with the testcase.
            if functionIndex == tc_functionIndex:
                continue            

            # function = self.getFunctionByIndex( unit, functionIndex )
            function = unit.get_function( functionIndex )

            dataAsString_SBF += self.getDataAsString_parameters( unit, function, isExpectedData, currentIndent )

        # All other stubs (different units)

        dataAsString_Stub = ""

        for unitId in container.keys():

            # Skip the unit associated with the testcase.
            if unitId == tc_unitId:
                continue

            unit = self.envApi[envName].Unit.get( unitId )

            for functionIndex in container[unitId].keys():

                # Skip globals
                if functionIndex == 0:
                    continue

                # function = self.getFunctionByIndex( unit, functionIndex )
                function = unit.get_function( functionIndex )

                dataAsString_Stub += self.getDataAsString_parameters( unit, function, isExpectedData, currentIndent )

        dataAsString += dataAsString_SBF
        dataAsString += dataAsString_UUT
        dataAsString += dataAsString_Stub

        return dataAsString


    def getDataAsString_parameters( self, unit, function, isExpectedData, currentIndent ):

        dataAsString = ""

        unitIndent = currentIndent
        unitIndentAsStr = self.getIndentAsString( unitIndent )
            
        functionIndent = currentIndent + 1
        functionIndentAsStr = self.getIndentAsString( functionIndent )

        parameterIndent = currentIndent + 2
        parameterIndentAsStr = self.getIndentAsString( parameterIndent )

        unitNameAsStr = "UUT: %s\n" % unit.name
        dataAsString += unitIndentAsStr + unitNameAsStr

        functionDataAsStr = None
        
        if unit.stub_by_function:
            dataObjectCoords = [ unit.id, function.index, function.sbf_index ]
            functionDataAsStr = self.getData( isExpectedData, dataObjectCoords, "data" )

        if None == functionDataAsStr:
            functionNameAsStr = "Subprogram: %s\n" % function.name
            dataAsString += functionIndentAsStr + functionNameAsStr
        else:
            functionNameAsStr = "Subprogram: %s: %s\n" % ( function.name, functionDataAsStr )
            dataAsString += functionIndentAsStr + functionNameAsStr

        parameterIndex = 1
        parameter = function.get_param_by_index( parameterIndex )

        while None != parameter:

            dataObjectCoords = [ unit.id, function.index, parameterIndex ]

            dataAsString += self.walkType_Wrapper( parameter, isExpectedData, \
                                                   dataObjectCoords, parameterIndent )

            parameterIndex += 1
            parameter = function.get_param_by_index( parameterIndex )

        return dataAsString


    def getDataAsString_globals( self, envName, \
                                 testcaseId, slotId, itrIdx, dataTypeControl, isInpExpData, \
                                 currentIndent ):

        dataAsString = ""

        units = self.envApi[envName].Unit.all( )

        for unit in units:
            dataAsString += self.getDataAsString_globalsInUnit( envName, unit, \
                                                                testcaseId, slotId, itrIdx, dataTypeControl, isInpExpData, \
                                                                currentIndent )

        return dataAsString

    
    def getDataAsString_globalsInUnit( self, envName, unit, \
                                       testcaseId, slotId, itrIdx, dataTypeControl, isInpExpData, \
                                       currentIndent ):

        dataAsString = ""

        if "uut_prototype_stubs" == unit.name:
            return dataAsString

        currentIndentAsStr = self.getIndentAsString( currentIndent )

        unitIndent = currentIndent
        unitIndentAsStr = self.getIndentAsString( unitIndent )
            
        functionIndent = currentIndent + 1
        functionIndentAsStr = self.getIndentAsString( functionIndent )

        parameterIndent = currentIndent + 2
        parameterIndentAsStr = self.getIndentAsString( parameterIndent )

        if dataTypeControl > 0:
            container = self.inpExpData[testcaseId]
        elif actualInpExpControl > 0:
            container = self.actualInpResData[slotId]

        unitId = unit.id
        functionIndex = 0

        if "USER_GLOBALS_VCAST" == unit.name:
            unitNameAsStr = "%s\n" % unit.name
        else:
            unitNameAsStr = "UUT: %s\n" % unit.name

        dataAsString += unitIndentAsStr + unitNameAsStr

        functionNameAsStr = "<<GLOBAL>>\n"
        dataAsString += functionIndentAsStr + functionNameAsStr

        if not unitId in container.keys():
            return dataAsString

        if not functionIndex in container[unitId].keys():
            return dataAsString

        currentData = container[unitId][functionIndex]
        
        for globalVarIndex in currentData.keys():

            dataObjectCoords = [ unitId, functionIndex, globalVarIndex ]

            # globalVar = self.getGlobalVarByIndex( envName, unitId, globalVarIndex )
            globalVar = unit.get_global_by_index( globalVarIndex )

            dataAsString += self.walkType_Wrapper( globalVar, dataObjectCoords, \
                                                   testcaseId, slotId, itrIdx, dataTypeControl, isInpExpData, \
                                                   parameterIndent )

        return dataAsString


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
                formattedUserCode= self.formatUserCode( sourceData.value, tcIndent+1 )
                dataAsString += formattedUserCode

        return dataAsString


    def walkType_Wrapper( self, parameter, dataObjectCoords, \
                          testcaseId, slotId, itrIdx, dataTypeControl, isInpExpData, \
                          currentIndent ):

        dataAsString = self.walkType( parameter.name, parameter.type, dataObjectCoords, \
                                      testcaseId, slotId, itrIdx, dataTypeControl, isInpExpData, \
                                      currentIndent )

        return dataAsString


    def walkType( self, parameterName, parameterType, dataObjectCoords, \
                  testcaseId, slotId, itrIdx, dataTypeControl, isInpExpData, \
                  currentIndent ):

        dataStringList = []

        if 1 == dataTypeControl:
            dataTypeIdc = [0]
        elif 2 == dataTypeControl:
            dataTypeIdc = [1]
        elif 3 == dataTypeControl:
            dataTypeIdc = [0,1]

        currentIndentAsStr = self.getIndentAsString( currentIndent )

        indexIndent = currentIndent + 1
        indexIndentAsStr = self.getIndentAsString( indexIndent )

        data_object_id = ".".join( [str(item) for item in dataObjectCoords] )

        if isInpExpData:
            valuesAsStr = self.getInpExpData( testcaseId, dataObjectCoords, dataTypeIdc, "data" )
        else:
            valuesAsStr = self.getSlotData( slotId, itrIdx, dataObjectCoords, dataTypeIdc, "data" )

        kind = parameterType.kind
        element = parameterType.element

        trace( "Parameter/Field name:", parameterName )
        trace( "Type kind:", kind )
        trace( "data_object_id:", data_object_id )

        is_parameter_user_code = [ False, False ]

        for dtIdx in dataTypeIdc:
            
            if None == valuesAsStr[dtIdx]:
                valuesAsStr[dtIdx] = self.getInpExpData( testcaseId, dataObjectCoords, [dtIdx], "parameter_user_code" )
                if None != valuesAsStr[dtIdx]:
                    is_parameter_user_code[dtIdx] = True             

            if is_parameter_user_code[dtIdx]:
                parameterNameAsStr = "%s: <<User Code>>\n" % parameterName
                formattedUserCode = self.formatUserCode( valuesAsStr, currentIndent+1 )
                dataAsString += currentIndentAsStr + parameterNameAsStr
                dataAsString += formattedUserCode

        isArray = False
        isBasicType = True

        parameterNameAdded = False

        if "ACCE_SS" == kind:

            isArray = True

            if isExpectedData:

                parameterNameAsStr = "%s: <<ACCESS>>\n" % parameterName

            else:

                allocateAsStr = self.getData( isExpectedData, dataObjectCoords, "allocate" )
                
                if None == allocateAsStr:
                    # Unfortunately not possible because there is no allocate within stubs.
                    # return dataAsString
                    parameterNameAsStr = "%s: <<ALLOCATE>>\n" % parameterName
                else:
                    parameterNameAsStr = "%s: <<ALLOCATE %s>>\n" % ( parameterName, allocateAsStr )

                dataAsString += currentIndentAsStr + parameterNameAsStr
                parameterNameAdded = True

        elif "STR_ING" == kind:

            isArray = True

            if "CHAR_ACTER" == element.kind:
                if None != valuesAsStr:
                    isArray = False

            if isExpectedData:

                parameterNameAsStr = "%s: <<ACCESS>>\n" % parameterName

            else:

                allocateAsStr = self.getData( isExpectedData, dataObjectCoords, "allocate" )
                if None == allocateAsStr:
                    return dataAsString

                parameterNameAsStr = "%s: <<ALLOCATE %s>>\n" % ( parameterName, allocateAsStr )
                if isArray:
                    dataAsString += currentIndentAsStr + parameterNameAsStr
                    parameterNameAdded = True

        elif "AR_RAY" == kind:

            isArray = True

            size = parameterType.range.size # Still something like "4%%"
            size = size.split( "%" )[0]

            parameterNameAsStr = "%s: <<Size %s>>\n" % ( parameterName, size )

        elif "REC_ORD" == kind:

            isBasicType = False

            parameterNameAsStr = "%s\n" % parameterName

            child_fields = parameterType.child_fields

        if isArray:

            arrayIndices = self.getDataObjectCoords_arrayIndices( isExpectedData, dataObjectCoords )
            trace( "Array: arrayIndices:", str(arrayIndices) )

            arrayDataAsStr = ""

            for arrayIndex in arrayIndices:

                index_dataObjectCoords = deepcopy( dataObjectCoords )
                index_dataObjectCoords.append( arrayIndex )

                trace( "Array: Basic Type: index_dataObjectCoords:", str(index_dataObjectCoords) )
                trace( "Array: Basic Type: valuesAsStr:", str(valuesAsStr) )

                indexName = "%s[%s]" % ( parameterName, str(arrayIndex) )

                arrayDataAsStr += self.walkType( indexName, element, isExpectedData, \
                                                 index_dataObjectCoords, indexIndent )

            if "" != arrayDataAsStr:
                if not parameterNameAdded:
                    dataAsString += currentIndentAsStr + parameterNameAsStr
                dataAsString += arrayDataAsStr

        else:

            if isBasicType:

                trace( "Basic Type: dataObjectCoords:", str(dataObjectCoords) )
                trace( "Basic Type: valuesAsStr:", str(valuesAsStr) )

                if None != valuesAsStr:

                    parameterDataAsStr = ""
                    dataIndentAsStr = currentIndentAsStr

                    associatedValues = self.getAssociatedValues( parameterType, valuesAsStr )

                    if isExpectedData:

                        actuals = self.getData( isExpectedData, dataObjectCoords, "actuals" )
                        results = self.getData( isExpectedData, dataObjectCoords, "results" )

                        if is_parameter_user_code:

                            dataIndentAsStr = ""

                            for idx in range( len(actuals) ):
                                parameterDataAsStr += indexIndentAsStr + \
                                                      "--> %s (%s)\n" % ( actuals[idx], results[idx] )

                        else:

                            parameterDataAsStr = "%s: %s --> %s (%s)\n" % ( parameterName, \
                                                                            ",".join( associatedValues ), \
                                                                            ",".join( actuals ), \
                                                                            ",".join( results ) )

                    else:

                        parameterDataAsStr = "%s: %s\n" % ( parameterName, \
                                                            ",".join( associatedValues ) )

                    dataAsString += dataIndentAsStr + parameterDataAsStr

            else:

                childDataAsStr = ""

                for child in child_fields:

                    child_dataObjectCoords = deepcopy( dataObjectCoords )
                    child_dataObjectCoords.append( child.index )

                    trace( "None Basic Type: child_dataObjectCoords:", str(child_dataObjectCoords) )

                    childDataAsStr += self.walkType_Wrapper( child, isExpectedData, \
                                                             child_dataObjectCoords, currentIndent+1 )

                if "" != childDataAsStr:
                    if not parameterNameAdded:
                        dataAsString += currentIndentAsStr + parameterNameAsStr
                    dataAsString += childDataAsStr

        return dataAsString


    def prepareData( self, testcase, dataTypeControl, isInpExpData, level=0 ):

        if 0 == level:

            if isInpExpData:
                self.inpExpData = {}
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

        if 1 == dataTypeControl:
            self.prepareInpExpData( testcase, False )
        elif 2 == dataTypeControl:
            self.prepareInpExpData( testcase, True )
        elif 3 == dataTypeControl:
            self.prepareInpExpData( testcase, False )
            self.prepareInpExpData( testcase, True )


    def prepareInpExpData( self, testcase, isExpectedData  ):

        if testcase.is_compound_test:
            return

        if not testcase.id in self.inpExpData.keys():
            self.inpExpData[testcase.id] = {}
            
        container = self.inpExpData[testcase.id]

        if isExpectedData:
            dataTypeIndex = 1
            source1 = testcase.expected
            source2 = testcase.expected_user_code            
        else:
            dataTypeIndex = 0
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
                currentData[data_object_id] = [ {}, {} ]

            if typeKey not in currentData[data_object_id][dataTypeIndex].keys():

                currentData[data_object_id][dataTypeIndex][typeKey] = valuesAsStr

            else:

                print( "Duplicated entry - catastrophic logic error.\n" )
                print( data_oject_id, typeKey )
                print( "Old value(s): %s" % currentData[data_object_id][dataTypeIndex][typeKey] )
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
                currentData[data_object_id] = [ {}, {} ]

            if typeKey not in currentData[data_object_id][dataTypeIndex].keys():

                currentData[data_object_id][dataTypeIndex][typeKey] = valuesAsStr

            else:

                print( "Duplicated entry - catastrophic logic error.\n" )
                print( data_oject_id, typeKey )
                print( "Old value(s): %s" % currentData[data_object_id][dataTypeIndex][typeKey] )
                print( "New value(s): %s" % valuesAsStr )
                sys.exit()


    def prepareActualData( self, slotId, slot_histories ):

        if not slotId in self.actualData.keys():
            self.actualData[slotId] = {}

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

                defaultList = ["None"]*numRangeItr

                for range_iteration in iteration.range_iterations:

                    numEvents = len( range_iteration.events )

                    for event in range_iteration.events:

                        itrIdx = event.iteration_index - 1
                        rangeItrIdx = event.range_iteration_index - 1

                        if not itrIdx in container.keys():
                            container[itrIdx] = {}

                        ancestryList[-1][-1] = event.iteration_index

                        ancestryAsStr = ""
                                
                        for ancestor in ancestryList:

                            ancestorAsStr = "%s Slot %s (%s) Iteration %s\n" % \
                                            ( ancestor[0], str(ancestor[1]), \
                                              ancestor[2], str(ancestor[3]) )

                            ancestryAsStr += ancestorAsStr

                        container[itrIdx]["ancestry"] = ancestryAsStr

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


    def getDataObjectCoords_arrayIndices( self, isExpectedData, dataObjectCoords ):

        arrayIndices = []

        if isExpectedData:
            container = self.expectedData
        else:
            container = self.inputData

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

            
    def getInpExpData( self, testcaseId, dataObjectCoords, dataTypeIdc, typeKey ):

        data = [None]*2

        container = self.inpExpData[testcaseId]

        try:

            currentDataSet = container[dataObjectCoords[0]][dataObjectCoords[1]][dataObjectCoords[2]]

            data_object_id = ".".join( [str(item) for item in dataObjectCoords] )
            currentDataSet = currentDataSet[data_object_id]
            
        except KeyError:

            return data

        for dtIdx in dataTypeIdc:

            if typeKey in currentDataSet[dtIdx].keys():
                data[dtIdx] = currentDataSet[dtIdx][typeKey]

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


    def formatUserCode( self, userCode, currentIndent ):

        formattedUserCode = ""

        currentIndentAsStr = self.getIndentAsString( currentIndent )

        lines = userCode.split( "\n" )

        for line in lines:
            formattedUserCode += currentIndentAsStr + line + "\n"

        return formattedUserCode


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
        print( tcData.getInpExpDataAsString( 2 ) )

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


import os
import sys

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


    def buildInputDataAsString( self ):

        self.inputDataAsString = self.dataApi.getDataAsString( self.testcase.input_tree )


    def buildInputDataAsString_explicit( self ):

        self.inputDataAsString = self.dataApi.getDataAsString_explicit( self.testcase, False, 0 )


    def getInputDataAsString( self ):

        if None == self.inputDataAsString:
            # self.buildInputDataAsString()
            self.buildInputDataAsString_explicit()

        return self.inputDataAsString


    def buildExpectedDataAsString( self ):

        self.expectedDataAsString = self.dataApi.getDataAsString( self.testcase.expected_tree )


    def buildExpectedDataAsString_explicit( self ):

        self.expectedDataAsString = self.dataApi.getDataAsString_explicit( self.testcase, True, 0 )


    def getExpectedDataAsString( self ):

        if None == self.expectedDataAsString:
            # self.buildExpectedDataAsString()
            self.buildExpectedDataAsString_explicit()

        return self.expectedDataAsString



class DataAPI_Wrapper( object ):

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


    def getDataAsString_explicit( self, testcase, isExpectedData, currentIndent, level=0, unit_tc_info=[] ):

        dataAsString = ""

        if isExpectedData:
            dataTypeAsStr = "Expected data"
        else:
            dataTypeAsStr = "Input data"

        envName = testcase.get_environment().name
        unitName = testcase.unit_display_name

        if 0 == level:

            tcIndent = currentIndent
            tcIndentAsStr = self.getIndentAsString( tcIndent )

            envIndent = currentIndent + 1
            envIndentAsStr = self.getIndentAsString( envIndent )

            unitIndent = currentIndent + 2
            unitIndentAsStr = self.getIndentAsString( unitIndent )
            
            functionIndent = currentIndent + 3
            functionIndentAsStr = self.getIndentAsString( functionIndent )

            parameterIndent = currentIndent + 4
            parameterIndentAsStr = self.getIndentAsString( parameterIndent )

            slotIndent = currentIndent + 4
            slotIndentAsStr = self.getIndentAsString( slotIndent )

            if testcase.is_compound_test:

                tcNameAsStr = "%s (Compound): %s:\n" %( testcase.name, dataTypeAsStr )
                dataAsString += tcIndentAsStr + tcNameAsStr

            elif testcase.is_unit_test:

                tcNameAsStr = "%s (Unit): %s:\n" %( testcase.name, dataTypeAsStr )
                dataAsString += tcIndentAsStr + tcNameAsStr

            envNameAsStr = "Environment: %s\n" % envName
            dataAsString += envIndentAsStr + envNameAsStr

            unitNameAsStr = "UUT: %s\n" % unitName

            unit_tc_info = []

        else:

            parameterIndent = currentIndent
            parameterIndentAsStr = self.getIndentAsString( parameterIndent )

            slotIndent = currentIndent
            slotIndentAsStr = self.getIndentAsString( slotIndent )

        if testcase.is_compound_test:

            dataAsString += unitIndentAsStr + unitNameAsStr

            functionNameAsStr = "Subprogram: %s\n" % testcase.function_display_name
            dataAsString += functionIndentAsStr + functionNameAsStr

            slots = testcase.slots
            numSlots = len( slots )

            for idx in range( numSlots ):

                tc = slots[idx].testcase

                slotName = ".".join( [tc.unit_display_name, tc.function_display_name, tc.name] )
                slotAsStr = "Slot %s: %s (%s)\n" % ( str(idx), slotName, slots[idx].iteration_count )
                dataAsString += slotIndentAsStr + slotAsStr

                if tc.is_compound_test:
                    slotDataAsString, unit_tc_info = \
                        self.getDataAsString_explicit( tc, isExpectedData, slotIndent+1, \
                                                       level=level+1, unit_tc_info=unit_tc_info )
                    dataAsString += slotDataAsString
                else:
                    unit_tc_info.append( ( slotName, tc.id ) )

            if level > 0:
                return dataAsString, unit_tc_info

            for info in unit_tc_info:

                slotName = info[0]
                tc_id = info[1]

                slotNameAsStr = "%s (Slot): %s:\n" %( slotName, dataTypeAsStr )
                dataAsString += tcIndentAsStr + slotNameAsStr

                tc = self.envApi[envName].TestCase.get( tc_id )

                self.prepareData( tc, isExpectedData )

                trace( "Input Data:", self.inputData, newLine=True )
                trace( "Expected Data:", self.expectedData, newLine=True )

                if isExpectedData:
                    dataAsString += self.getDataAsString_globals( envName, isExpectedData, unitIndent )
                    dataAsString += self.getDataAsString_functions( tc, isExpectedData, unitIndent )
                    dataAsString += self.getTestcaseUserCode( tc, isExpectedData, unitIndent )
                else:
                    dataAsString += self.getTestcaseUserCode( tc, isExpectedData, unitIndent )
                    dataAsString += self.getDataAsString_globals( envName, isExpectedData, unitIndent )
                    dataAsString += self.getDataAsString_functions( tc, isExpectedData, unitIndent )

            return dataAsString

        elif testcase.is_unit_test:

            self.prepareData( testcase, isExpectedData )

            trace( "Input Data:", self.inputData, newLine=True )
            trace( "Expected Data:", self.expectedData, newLine=True )

            if isExpectedData:
                dataAsString += self.getDataAsString_globals( envName, isExpectedData, unitIndent )
                dataAsString += self.getDataAsString_functions( testcase, isExpectedData, unitIndent )
                dataAsString += self.getTestcaseUserCode( testcase, isExpectedData, unitIndent )
            else:
                dataAsString += self.getTestcaseUserCode( testcase, isExpectedData, unitIndent )
                dataAsString += self.getDataAsString_globals( envName, isExpectedData, unitIndent )
                dataAsString += self.getDataAsString_functions( testcase, isExpectedData, unitIndent )

            return dataAsString


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


    def getDataAsString_globals( self, envName, isExpectedData, currentIndent ):

        dataAsString = ""

        units = self.envApi[envName].Unit.all( )

        for unit in units:
            dataAsString += self.getDataAsString_globalsInUnit( envName, unit, isExpectedData, currentIndent )

        return dataAsString

    
    def getDataAsString_globalsInUnit( self, envName, unit, isExpectedData, currentIndent ):

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

        if isExpectedData:
            container = self.expectedData
        else:
            container = self.inputData

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

            dataAsString += self.walkType_Wrapper( globalVar, isExpectedData, \
                                                   dataObjectCoords, parameterIndent )

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


    def walkType_Wrapper( self, parameter, isExpectedData, \
                          dataObjectCoords, currentIndent ):

        dataAsString = self.walkType( parameter.name,  parameter.type, isExpectedData, \
                                      dataObjectCoords, currentIndent )

        return dataAsString


    def walkType( self, parameterName, parameterType, isExpectedData, \
                  dataObjectCoords, currentIndent ):

        dataAsString = ""

        currentIndentAsStr = self.getIndentAsString( currentIndent )

        indexIndent = currentIndent + 1
        indexIndentAsStr = self.getIndentAsString( indexIndent )

        data_object_id = ".".join( [str(item) for item in dataObjectCoords] )
        valuesAsStr = self.getData( isExpectedData, dataObjectCoords, "data" )

        kind = parameterType.kind
        element = parameterType.element

        trace( "Parameter/Field name:", parameterName )
        trace( "Type kind:", kind )
        trace( "data_object_id:", data_object_id )

        is_parameter_user_code = False

        if None == valuesAsStr:
            valuesAsStr = self.getData( isExpectedData, dataObjectCoords, "parameter_user_code" )
            if None != valuesAsStr:
                is_parameter_user_code = True

        if is_parameter_user_code:
            parameterNameAsStr = "%s: <<User Code>>\n" % parameterName
            formattedUserCode = self.formatUserCode( valuesAsStr, currentIndent+1 )
            dataAsString += currentIndentAsStr + parameterNameAsStr
            dataAsString += formattedUserCode
            return dataAsString

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

                    associatedValues = self.getAssociatedValues( parameterType, valuesAsStr )

                    if isExpectedData:

                        actuals = self.getData( isExpectedData, dataObjectCoords, "actuals" )
                        results = self.getData( isExpectedData, dataObjectCoords, "results" )

                        parameterDataAsStr = "%s: %s --> %s (%s)\n" % ( parameterName, \
                                                                        ",".join( associatedValues ), \
                                                                        ",".join( actuals ), \
                                                                        ",".join( results ) )

                    else:

                        parameterDataAsStr = "%s: %s\n" % ( parameterName, \
                                                            ",".join( associatedValues ) )

                    dataAsString += currentIndentAsStr + parameterDataAsStr

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


    def prepareData( self, testcase, isExpectedData ):

        if isExpectedData:
            self.expectedData = {}
            container =  self.expectedData = {}
            source1 = testcase.expected
            source2 = testcase.expected_user_code
        else:
            self.inputData = {}
            container =  self.inputData = {}
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

            if isExpectedData:
                actuals = []
                results = []
                for result in sourceData.results:
                    actuals.append( result.value )
                    if 1 == result.match:
                        results.append( "PASS" )
                    else:
                        results.append( "FAIL" )

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

                if isExpectedData:
                    currentData[data_object_id]["actuals"] = actuals
                    currentData[data_object_id]["results"] = results
                    
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

            
    def getData( self, isExpectedData, dataObjectCoords, typeKey ):

        if isExpectedData:
            container = self.expectedData
        else:
            container = self.inputData

        try:

            currentDataSet = container[dataObjectCoords[0]][dataObjectCoords[1]][dataObjectCoords[2]]

            data_object_id = ".".join( [str(item) for item in dataObjectCoords] )

            data = currentDataSet[data_object_id][typeKey]

        except KeyError:

            data = None

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

        print( tcData.getInputDataAsString() )
        print( tcData.getExpectedDataAsString() )

    elif 2 == numParameters:

        dataApi = DataAPI_Wrapper( sys.argv[1] )
        api = dataApi.getApi( sys.argv[2] )

        testcases = api.TestCase.all()

        for testcase in testcases:

            inputDataAsString = dataApi.getDataAsString_explicit( testcase, False, 0 )
            expectedDataAsString = dataApi.getDataAsString_explicit( testcase, True, 0 )

            print( inputDataAsString )
            print( expectedDataAsString )

    elif 5 == numParameters:

        dataApi = DataAPI_Wrapper( sys.argv[1] )
        tcData = TestCaseData( sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], dataApi )
        
        print( tcData )

        print( tcData.getInputDataAsString() )
        print( tcData.getExpectedDataAsString() )

    else:

        print( "Inappropriate number of parameters." )

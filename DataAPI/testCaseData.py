
import os
import sys

from copy import deepcopy

from vector.apps.DataAPI.api import Api

class TestCaseData( object ):

    def __init__( self, envName, unitName, functionName, tcName, dataApi ):

        self.envName = envName
        self.unitName = unitName
        self.functionName = functionName
        self.tcName = tcName

        self.dataApi = dataApi
        self.dataApi.loadApi( envName )

        self.inputDataAsString = None
        self.expectedDataAsString = None


    def __str__( self ):

        msg = "TestCase:\n"
        msg += "Environment: %s\n" % self.envName
        msg += "Unit: %s\n" % self.unitName
        msg += "Function: %s\n" % self.functionName
        msg += "TestCase: %s\n" % self.tcName

        return msg


    def buildInputDataAsString( self ):

        testcase = self.dataApi.getTestcase( self.envName, self.unitName, \
                                             self.functionName, self.tcName )

        self.inputDataAsString = ""

        self.inputDataAsString = self.dataApi.getDataAsString( testcase.input_tree )

    def buildInputDataAsString_explicit( self ):

        testcase = self.dataApi.getTestcase( self.envName, self.unitName, \
                                             self.functionName, self.tcName )

        self.inputDataAsString = ""

        self.inputDataAsString = self.dataApi.getDataAsString_explicit( testcase, "input", 0 )

    def getInputDataAsString( self ):

        if None == self.inputDataAsString:
            # self.buildInputDataAsString()
            self.buildInputDataAsString_explicit()

        return self.inputDataAsString


    def buildExpectedDataAsString( self ):

        testcase = self.dataApi.getTestcase( self.envName, self.unitName, \
                                             self.functionName, self.tcName )

        self.expectedDataAsString = ""

        self.expectedDataAsString = self.dataApi.getDataAsString( testcase.expected_tree )


    def buildExpectedDataAsString_explicit( self ):

        testcase = self.dataApi.getTestcase( self.envName, self.unitName, \
                                             self.functionName, self.tcName )

        self.expectedDataAsString = ""

        self.expectedDataAsString = self.dataApi.getDataAsString_explicit( testcase, "expected", 0 )

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


    def getDataAsString_explicit( self, testcase, dataType, currentIndent ):

        dataAsString = ""

        if "input" == dataType:
            dataTypeAsStr = "Input data"
        elif "expected" == dataType:
            dataTypeAsStr = "Expected data"

        envName = testcase.get_environment().name

        unitName = testcase.unit_display_name
        unit = self.envApi[envName].Unit.get( unitName )

        if 0 == currentIndent:

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

            if None != unit:
                unitNameAsStr = "UUT: %s\n" % unit.display_name
            else:
                unitNameAsStr = "UUT: %s\n" % unitName

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
                    dataAsString += self.getDataAsString_explicit( tc, slotIndent+1, "" )

        elif testcase.is_unit_test:

            self.prepareData( testcase, dataType )

            print( self.inputData )
            print( self.expectedData )

            dataAsString += self.getDataAsString_globals( testcase, dataType, unitIndent )
            dataAsString += self.getTestcaseUserCode( testcase, dataType, unitIndent )
            dataAsString += self.getDataAsString_parameters( testcase, dataType, unitIndent )

        return dataAsString


    def getDataAsString_parameters( self, testcase, dataType, currentIndent ):

        dataAsString = ""

        unitIndent = currentIndent
        unitIndentAsStr = self.getIndentAsString( unitIndent )
            
        functionIndent = currentIndent + 1
        functionIndentAsStr = self.getIndentAsString( functionIndent )

        parameterIndent = currentIndent + 2
        parameterIndentAsStr = self.getIndentAsString( parameterIndent )

        envName = testcase.get_environment().name

        unitName = testcase.unit_display_name
        unit = self.envApi[envName].Unit.get( unitName )

        function = testcase.function

        unitNameAsStr = "UUT: %s\n" % unit.display_name 
        dataAsString += unitIndentAsStr + unitNameAsStr

        functionNameAsStr = "Subprogram: %s\n" % testcase.function_display_name
        dataAsString += functionIndentAsStr + functionNameAsStr

        parameterIndex = 1
        parameter = function.get_param_by_index( parameterIndex )

        while None != parameter:

            dataObjectCoords = [ unit.id, function.index, parameterIndex ]

            dataAsString += self.walkParameter( parameter, testcase, dataType, \
                                                dataObjectCoords, parameterIndent )

            parameterIndex += 1
            parameter = function.get_param_by_index( parameterIndex )

        return dataAsString


    def getDataAsString_globals( self, testcase, dataType, currentIndent ):

        dataAsString = ""

        envName = testcase.get_environment().name
        units = self.envApi[envName].Unit.all( )

        for unit in units:
            dataAsString += self.getDataAsString_globalsInUnit( unit, testcase, dataType, currentIndent )

        return dataAsString

    
    def getDataAsString_globalsInUnit( self, unit, testcase, dataType, currentIndent ):

        dataAsString = ""

        currentIndentAsStr = self.getIndentAsString( currentIndent )

        unitIndent = currentIndent
        unitIndentAsStr = self.getIndentAsString( unitIndent )
            
        functionIndent = currentIndent + 1
        functionIndentAsStr = self.getIndentAsString( functionIndent )

        parameterIndent = currentIndent + 2
        parameterIndentAsStr = self.getIndentAsString( parameterIndent )

        if "input" == dataType:
            container = self.inputData
            source = testcase.input_user_code
        elif "expected" == dataType:
            container = self.expectedData
            source = testcase.expected_user_code

        unitId = unit.id
        functionIndex = 0

        unitNameAsStr = "%s\n" % unit.display_name 
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

            globalVar = self.getGlobalVarByIndex( testcase, unitId, globalVarIndex )

            dataAsString += self.walkParameter( globalVar, testcase, dataType, \
                                                dataObjectCoords, parameterIndent )

        return dataAsString


    def getTestcaseUserCode( self, testcase, dataType, currentIndent ):

        currentIndentAsStr = self.getIndentAsString( currentIndent )

        unitIndent = currentIndent
        unitIndentAsStr = self.getIndentAsString( unitIndent )
            
        functionIndent = currentIndent + 1
        functionIndentAsStr = self.getIndentAsString( functionIndent )

        tcIndent = currentIndent + 2
        tcIndentAsStr = self.getIndentAsString( tcIndent )

        dataAsString = ""

        if "input" == dataType:
            container = self.inputData
            source = testcase.input_user_code
        elif "expected" == dataType:
            container = self.expectedData
            source = testcase.expected_user_code

        envName = testcase.get_environment().name

        unitName = testcase.unit_display_name
        unit = self.envApi[envName].Unit.get( unitName )

        unitNameAsStr = "UUT: %s\n" % unit.display_name 
        dataAsString += unitIndentAsStr + unitNameAsStr

        functionNameAsStr = "Subprogram: %s\n" % testcase.function_display_name
        dataAsString += functionIndentAsStr + functionNameAsStr

        tcNameAsStr = "Testcase: %s: %s\n" % ( testcase.name, "<<Testcase User Code>>" )
        dataAsString += tcIndentAsStr + tcNameAsStr

        for sourceData in source:

            if sourceData.is_testcase_user_code:
                dataAsString += sourceData.value + "\n"

        return dataAsString


    def walkParameter( self, parameter, testcase, dataType, \
                       dataObjectCoords, currentIndent ):

        dataAsString = ""

        currentIndentAsStr = self.getIndentAsString( currentIndent )

        indexIndent = currentIndent + 1
        indexIndentAsStr = self.getIndentAsString( indexIndent )

        data_object_id = ".".join( [str(item) for item in dataObjectCoords] )
        valuesAsStr = self.getData( dataType, dataObjectCoords, "data" )

        kind = parameter.type.kind
        element = parameter.type.element

        print( parameter.name )
        print( kind )
        print( data_object_id )

        is_parameter_user_code = False

        if None == valuesAsStr:
            valuesAsStr = self.getData( dataType, dataObjectCoords, "parameter_user_code" )
            if None != valuesAsStr:
                is_parameter_user_code = True

        if is_parameter_user_code:
            parameterNameAsStr = "%s: <<User Code>>\n" % parameter.name
            dataAsString += currentIndentAsStr + parameterNameAsStr
            dataAsString += valuesAsStr
            return dataAsString

        child_fields = []

        if None != element:
            if hasattr( element, "child_fields" ):
                child_fields = element.child_fields
        else:
            if hasattr( parameter.type, "child_fields" ):
                child_fields = parameter.type.child_fields

        isArray = False
        isBasicType = True

        if "ACCE_SS" == kind:

            isArray = True

            if "input" == dataType:
                
                allocateAsStr = self.getData( dataType, dataObjectCoords, "allocate" )
                if None == allocateAsStr:
                    return dataAsString

                parameterNameAsStr = "%s: <<ALLOCATE %s>>\n" % ( parameter.name, allocateAsStr )

            else:

                parameterNameAsStr = "%s: <<ACCESS>>\n" % parameter.name

        elif "STR_ING" == kind:

            isArray = True

            if "input" == dataType:

                allocateAsStr = self.getData( dataType, dataObjectCoords, "allocate" )
                if None == allocateAsStr:
                    return dataAsString

                parameterNameAsStr = "%s: <<ALLOCATE %s>>\n" % ( parameter.name, allocateAsStr )

            else:

                parameterNameAsStr = "%s: <<ACCESS>>\n" % parameter.name

            if "CHAR_ACTER" == element.kind:
                if None != valuesAsStr:
                    isArray = False

        elif "AR_RAY" == kind:

            isArray = True

            size = parameter.type.range.size # Still something like "4%%"
            size = size.split( "%" )[0]

            parameterNameAsStr = "%s: <<Size %s>>\n" % ( parameter.name, size )

        elif "REC_ORD" == kind:

            isBasicType = False

            parameterNameAsStr = "%s\n" % parameter.name

        if isArray:

            print( "A.0", element.kind )

            if "ACCE_SS" == element.kind or "STR_ING" == element.kind or "AR_RAY" == element.kind or "REC_ORD" == element.kind:
                isBasicType = False
            else:
                isBasicType = True

            arrayIndices = self.getDataObjectCoords_arrayIndices( dataType, dataObjectCoords )
            print( arrayIndices )

            arrayDataAsStr = ""

            for arrayIndex in arrayIndices:

                index_dataObjectCoords = deepcopy( dataObjectCoords )
                index_dataObjectCoords.append( arrayIndex )

                if isBasicType:

                    valuesAsStr = self.getData( dataType, index_dataObjectCoords, "data" )

                    print( "A.1", isArray, isBasicType )
                    print( "A.1", index_dataObjectCoords )
                    print( "A.1", valuesAsStr )

                    if None != valuesAsStr:

                        associatedNames = self.getAssociatedNames( parameter, valuesAsStr, stringRepresent=False )
                        
                        indexDataAsStr = "%s[%s]: %s\n" % ( parameter.name, str(arrayIndex), ",".join( associatedNames ) )
                        arrayDataAsStr += indexIndentAsStr + indexDataAsStr

                else:

                    indexDataAsStr = "%s[%s]\n" % ( parameter.name, str(arrayIndex) )
                    childDataAsStr = ""

                    for child in child_fields:

                        child_dataObjectCoords = deepcopy( index_dataObjectCoords )
                        
                        if "REC_ORD" == element.kind:
                            child_dataObjectCoords.append( child.index )

                        print( "A.2", isArray, isBasicType )
                        print( "A.2", child_dataObjectCoords )

                        childDataAsStr += self.walkParameter( child, testcase, dataType, \
                                                              child_dataObjectCoords, currentIndent+2 )

                    if "" != childDataAsStr:
                        arrayDataAsStr += indexIndentAsStr + indexDataAsStr
                        arrayDataAsStr += childDataAsStr

            if "" != arrayDataAsStr:
                dataAsString += currentIndentAsStr + parameterNameAsStr
                dataAsString += arrayDataAsStr

        else:

            if isBasicType:

                print( "B.1", isArray, isBasicType )
                print( "B.1", dataObjectCoords )
                print( "B.1", valuesAsStr )

                if None != valuesAsStr:

                    associatedNames = self.getAssociatedNames( parameter, valuesAsStr, stringRepresent=True )

                    parameterDataAsStr = "%s: %s\n" % ( parameter.name, ",".join( associatedNames ) )
                    dataAsString += currentIndentAsStr + parameterDataAsStr

            else:

                childDataAsStr = ""

                for child in child_fields:

                    child_dataObjectCoords = deepcopy( dataObjectCoords )
                    child_dataObjectCoords.append( child.index )

                    print( "B.2", isArray, isBasicType )
                    print( "B.2", child_dataObjectCoords )

                    childDataAsStr += self.walkParameter( child, testcase, dataType, \
                                                          child_dataObjectCoords, currentIndent+1 )

                if "" != childDataAsStr:
                    dataAsString += currentIndentAsStr + parameterNameAsStr
                    dataAsString += childDataAsStr

        return dataAsString


    def prepareData( self, testcase, dataType ):

        if "input" == dataType:
            self.inputData = {}
            container =  self.inputData = {}
            source1 = testcase.input
            source2 = testcase.input_user_code
        elif "expected" == dataType:
            self.expectedData = {}
            container =  self.expectedData = {}
            source1 = testcase.expected
            source2 = testcase.expected_user_code
        else:
            return

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


    def getDataObjectCoords_arrayIndices( self, dataType, dataObjectCoords ):

        arrayIndices = []

        if "input" == dataType:
            container = self.inputData
        elif "expected" == dataType:
            container = self.expectedData
        else:
            return arrayIndices

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

        return arrayIndices

            
    def getData( self, dataType, dataObjectCoords, typeKey ):

        if "input" == dataType:
            container = self.inputData
        elif "expected" == dataType:
            container = self.expectedData
        else:
            return None

        try:

            currentData = container[dataObjectCoords[0]][dataObjectCoords[1]][dataObjectCoords[2]]

            data_object_id = ".".join( [str(item) for item in dataObjectCoords] )

            valuesAsStr = currentData[data_object_id][typeKey]

        except KeyError:

            valuesAsStr = None

        return valuesAsStr


    def getGlobalVarByIndex( self, testcase, unitId, globalVarIndex ):

        envName = testcase.get_environment().name
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


    def getAssociatedNames( self, parameter, valuesAsStr, stringRepresent=True ):

        print( parameter.type.kind )

        associatedNames = []

        values = valuesAsStr.split( "%" )

        isConvertible = True

        try:
            int_value = int(values[0])
        except ValueError:
            isConvertible = False

        if not isConvertible:
            associatedNames = values
            return associatedNames

        if "ENUMERATION" == parameter.type.kind:
            for value in values:
                name = self.getNameFromValue( parameter.type.enums, int(value) )
                associatedNames.append( name )
        elif ( "STR_ING" == parameter.type.kind ) and ( not stringRepresent ):
            for value in values:
                name = unichr( int(value) )
                associatedNames.append( name )
        else:
            associatedNames = values

        return associatedNames


    def getNameFromValue( self, enums, value ):

        for enumItem in enums:
            if enumItem.value == value:
                return enumItem.name

        return str(value)



if "__main__" == __name__:

    dataApi = DataAPI_Wrapper( "C:\Work\Training\V6.4\MinGW_WorkDir" )
    tcData = TestCaseData( "EXAMPLE", "example", "append", "append.001", dataApi )
    # tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "manager", "Add_Party_To_Waiting_List", "UserCode", dataApi )
    # tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "manager", "Place_Order", "FoolTheBill", dataApi )
    # tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "<<COMPOUND>>", "<<COMPOUND>>", "Asterix&Obelix", dataApi )
    # tcData = TestCaseData( "IO_WRAPPER_BUBEN", "<<COMPOUND>>", "<<COMPOUND>>", "Write&Read", dataApi )
    # tcData = TestCaseData( "ADVANCED", "advanced_stubbing", "temp_monitor", "Celsius_Stub", dataApi )
    print( tcData )

    print( tcData.getInputDataAsString() )
    # print( tcData.getExpectedDataAsString() )

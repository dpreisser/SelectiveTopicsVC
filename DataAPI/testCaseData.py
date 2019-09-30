
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

        self.inputDataAsString = self.dataApi.getDataAsString( testcase.input_tree, \
                                                               self.inputDataAsString )

    def buildInputDataAsString_explicit( self ):

        testcase = self.dataApi.getTestcase( self.envName, self.unitName, \
                                             self.functionName, self.tcName )

        self.inputDataAsString = ""

        self.inputDataAsString = self.dataApi.getDataAsString_explicit( testcase, 0, \
                                                                        self.inputDataAsString )

    def getInputDataAsString( self ):

        if None == self.inputDataAsString:
            # self.buildInputDataAsString()
            self.buildInputDataAsString_explicit()

        return self.inputDataAsString


    def buildExpectedDataAsString( self ):

        testcase = self.dataApi.getTestcase( self.envName, self.unitName, \
                                             self.functionName, self.tcName )

        self.expectedDataAsString = ""

        self.expectedDataAsString = self.dataApi.getDataAsString( testcase.expected_tree, \
                                                                  self.expectedDataAsString )

    def getExpectedDataAsString( self ):

        if None == self.expectedDataAsString:
            self.buildExpectedDataAsString()

        return self.expectedDataAsString



class DataAPI_Wrapper( object ):

    def __init__( self, workingDirVC ):

        self.workingDirVC = workingDirVC

        self.envApi = {}
        self.inputData = {}

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

        
    def getDataAsString( self, tree, dataAsString ):

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


    def getDataAsString_explicit( self, testcase, currentIndent, dataAsString ):

        envName = testcase.get_environment().name

        unitName = testcase.unit_display_name
        unit = self.envApi[envName].Unit.get( unitName )

        if 0 == currentIndent:

            tcIndent = currentIndent
            tcIndentAsStr = self.getIndentAsString( tcIndent )

            envIndent = currentIndent
            envIndentAsStr = self.getIndentAsString( envIndent )

            unitIndent = currentIndent + 1
            unitIndentAsStr = self.getIndentAsString( unitIndent )
            
            functionIndent = currentIndent + 2
            functionIndentAsStr = self.getIndentAsString( functionIndent )

            parameterIndent = currentIndent + 3
            parameterIndentAsStr = self.getIndentAsString( parameterIndent )

            slotIndent = currentIndent + 3
            slotIndentAsStr = self.getIndentAsString( slotIndent )

            if testcase.is_compound_test:

                tcNameAsStr = testcase.name + " " + "(Compound)" + ":\n"
                dataAsString += tcIndentAsStr + tcNameAsStr

            elif testcase.is_unit_test:

                tcNameAsStr = testcase.name + " " + "(Unit)" + ":\n"
                dataAsString += tcIndentAsStr + tcNameAsStr

            envNameAsStr = "Environment: %s\n" % envName
            dataAsString += envIndentAsStr + envNameAsStr

            if None != unit:
                unitNameAsStr = "UUT: %s\n" % unit.display_name
            else:
                unitNameAsStr = "UUT: %s\n" % unitName

            dataAsString += unitIndentAsStr + unitNameAsStr

            functionNameAsStr = "Subprogram: %s\n" % testcase.function_display_name
            dataAsString += functionIndentAsStr + functionNameAsStr

        else:

            parameterIndent = currentIndent
            parameterIndentAsStr = self.getIndentAsString( parameterIndent )

            slotIndent = currentIndent
            slotIndentAsStr = self.getIndentAsString( slotIndent )

        if testcase.is_compound_test:

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

            self.prepareInputData( testcase )

            function = testcase.function

            parameterIndex = 1
            parameter = function.get_param_by_index( parameterIndex )

            while None != parameter:

                dataObjectCoords = [ unit.id, function.index, parameterIndex ]

                dataAsString += self.walkParameter( unit, function, parameter, testcase, \
                                                    dataObjectCoords, parameterIndent, "" )

                parameterIndex += 1
                parameter = function.get_param_by_index( parameterIndex )

        return dataAsString


    def walkParameter( self, unit, function, parameter, testcase, \
                       dataObjectCoords, currentIndent, dataAsString ):

        currentIndentAsStr = self.getIndentAsString( currentIndent )

        childIndent = currentIndent + 1
        childIndentAsStr = self.getIndentAsString( childIndent )

        data_object_id = ".".join( [str(item) for item in dataObjectCoords] )
        valuesAsStr = self.getData( dataObjectCoords, "data" )

        kind = parameter.type.kind
        element = parameter.type.element

        print( data_object_id )
        print( kind )

        child_fields = []

        if None != element:
            if hasattr( element, "child_fields" ):
                child_fields = element.child_fields

        isBasicType = True
        isArray = False

        if "ACCE_SS" == kind:

            allocateAsStr = self.getData( dataObjectCoords, "allocate" )
            if None == allocateAsStr:
                return dataAsString

            isArray = True

            parameterNameAsStr = "%s: <<ACCESS %s>>\n" % ( parameter.name, allocateAsStr )
            dataAsString += currentIndentAsStr + parameterNameAsStr
            numArrayElements = int(allocateAsStr)

        elif "STR_ING" == kind:

            allocateAsStr = self.getData( dataObjectCoords, "allocate" )
            if None == allocateAsStr:
                return dataAsString

            isArray = True

            parameterNameAsStr = "%s: <<ACCESS %s>>\n" % ( parameter.name, allocateAsStr )
            dataAsString += currentIndentAsStr + parameterNameAsStr
            numArrayElements = int(allocateAsStr)

            if "CHAR_ACTER" == element.kind:
                if None != valuesAsStr:
                    isArray = False

        elif "AR_RAY" == kind:

            isArray = True

            size = parameter.type.range.size # Still something like "4%%"
            size = size.split( "%" )[0]

            parameterNameAsStr = "%s: <<Size %s>>\n" % ( parameter.name, size )
            dataAsString += currentIndentAsStr + parameterNameAsStr
            numArrayElements = int(size)

        elif "REC_ORD" == kind:

            isBasicType = False

        if isArray:

            print( element.kind )

            if "ACCE_SS" == element.kind or "STR_ING" == element.kind or "AR_RAY" == element.kind or "REC_ORD" == element.kind:
                isBasicType = False
            else:
                isBasicType = True

            for arrayIdx in range( numArrayElements ):

                index_dataObjectCoords = deepcopy( dataObjectCoords )
                index_dataObjectCoords.append( arrayIdx )

                if isBasicType:

                    valuesAsStr = self.getData( index_dataObjectCoords, "data" )

                    print( isArray, isBasicType )
                    print( index_dataObjectCoords )
                    print( valuesAsStr )

                    if None != valuesAsStr:

                        associatedNames = self.getAssociatedNames( parameter, valuesAsStr, stringRepresent=False )
                        
                        elementAsStr = "[%s]: %s\n" % ( str(arrayIdx), ",".join( associatedNames ) )
                        dataAsString += childIndentAsStr + elementAsStr
                    
                else:

                    elementAsStr = "[%s]\n" % str(arrayIdx)
                    dataAsString += childIndentAsStr + elementAsStr

                    for child in child_fields:

                        child_dataObjectCoords = deepcopy( index_dataObjectCoords )
                        
                        if "REC_ORD" == element.kind:
                            child_dataObjectCoords.append( child.index )

                        print( isArray, isBasicType )
                        print( child_dataObjectCoords )

                        dataAsString += self.walkParameter( unit, function, child, testcase, \
                                                            child_dataObjectCoords, currentIndent+2, "" )

        else:

            if isBasicType:

                print( isArray, isBasicType )
                print( dataObjectCoords )
                print( valuesAsStr )

                if None != valuesAsStr:

                    associatedNames = self.getAssociatedNames( parameter, valuesAsStr, stringRepresent=True )

                    componentAsStr = "%s: %s\n" % ( parameter.name, ",".join( associatedNames ) )
                    dataAsString += currentIndentAsStr + componentAsStr

            else:

                for child in child_fields:

                    child_dataObjectCoords = deepcopy( dataObjectCoords )
                    child_dataObjectCoords.append( child.index )

                    print( isArray, isBasicType )
                    print( child_dataObjectCoords )

                    dataAsString += self.walkParameter( unit, function, child, testcase, \
                                                        child_dataObjectCoords, currentIndent+1, "" )

        return dataAsString

    
    def prepareInputData( self, testcase ):

        self.inputData = {}

        input = testcase.input

        for currentInput in input:

            data_object_id = currentInput.data_object_id
            valuesAsStr = currentInput.value

            typeKey = "data"

            if currentInput.is_allocate:
                typeKey = "allocate"
            elif currentInput.is_control_flow:
                typeKey = "control_flow"
            elif currentInput.is_csv_data:
                typeKey = "csv_data"
            elif currentInput.is_exception:
                typeKey = "exception"

            comp = data_object_id.split( "." )

            unitId = int( comp[0] )
            functionIndex = int( comp[1] )
            parameterIndex = int( comp[2] )

            if not unitId in self.inputData.keys():
                self.inputData[unitId] = {}

            if not functionIndex in self.inputData[unitId].keys():
                self.inputData[unitId][functionIndex] = {}

            if not parameterIndex in self.inputData[unitId][functionIndex].keys():
                self.inputData[unitId][functionIndex][parameterIndex] = {}

            inputData = self.inputData[unitId][functionIndex][parameterIndex]

            if not data_object_id in inputData.keys():
                inputData[data_object_id] = {}

            if typeKey not in inputData[data_object_id].keys():
                inputData[data_object_id][typeKey] = valuesAsStr
            else:
                print( "Duplicated entry - catastrophic logic error.\n" )
                print( data_oject_id, typeKey )
                print( "Old value(s): %s" % inputData[data_object_id][typeKey] )
                print( "New value(s): %s" % valuesAsStr )
                sys.exit()

            
    def getData( self, dataObjectCoords, typeKey ):

        try:

            inputData = self.inputData[dataObjectCoords[0]][dataObjectCoords[1]][dataObjectCoords[2]]

            data_object_id = ".".join( [str(item) for item in dataObjectCoords] )

            valuesAsStr = inputData[data_object_id][typeKey]

        except KeyError:

            valuesAsStr = None

        return valuesAsStr


    def getAssociatedNames( self, parameter, valuesAsStr, stringRepresent=True ):

        print( parameter.type.kind )

        associatedNames = []

        values = valuesAsStr.split( "%" )

        if "ENUMERATION" == parameter.type.kind:
            for value in values:
                name = self.getNameFromValue( parameter.type.enums, int(value) )
                associatedNames.append( name )
        elif ( "STR_ING" == parameter.type.kind ) and ( not stringRepresent ):
            for value in values:
                print( int(value) )
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
    # tcData = TestCaseData( "EXAMPLE", "example", "append", "append.001", dataApi )
    tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "manager", "Add_Party_To_Waiting_List", "OneName_char", dataApi )
    # tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "manager", "Place_Order", "FoolTheBill", dataApi )
    # tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "<<COMPOUND>>", "<<COMPOUND>>", "Asterix&Obelix", dataApi )
    # tcData = TestCaseData( "IO_WRAPPER_BUBEN", "<<COMPOUND>>", "<<COMPOUND>>", "Write&Read", dataApi )
    # tcData = TestCaseData( "ADVANCED", "advanced_stubbing", "temp_monitor", "Celsius_Stub", dataApi )
    print( tcData )

    print( tcData.getInputDataAsString() )
    # print( tcData.getExpectedDataAsString() )

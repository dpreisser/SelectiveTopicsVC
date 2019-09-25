
import os

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

            self.prepareData( testcase )

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
        value = self.getData( dataObjectCoords )

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

            if None == value:
                return dataAsString

            isArray = True

            parameterNameAsStr = "%s: <<ACCESS %s>>\n" % ( parameter.name, value )
            dataAsString += currentIndentAsStr + parameterNameAsStr
            numArrayElements = int(value)

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

            if "ACCE_SS" == element.kind or "AR_RAY" == element.kind or "REC_ORD" == element.kind:
                isBasicType = False
            else:
                isBasicType = True

            for arrayIdx in range( numArrayElements ):

                child_dataObjectCoords = deepcopy( dataObjectCoords )
                child_dataObjectCoords.append( arrayIdx )

                if isBasicType:

                    value = self.getData( child_dataObjectCoords )

                    print( isArray, isBasicType )
                    print( child_dataObjectCoords )
                    print( value )

                    if None != value:
                        elementAsStr = "[%s]: %s\n" % ( str(arrayIdx), value )
                        dataAsString += childIndentAsStr + elementAsStr
                    
                else:

                    print( isArray, isBasicType )
                    print( child_dataObjectCoords )
                    
                    elementAsStr = "[%s]\n" % str(arrayIdx)
                    dataAsString += childIndentAsStr + elementAsStr

                    for child in child_fields:

                        dataAsString += self.walkParameter( unit, function, child, testcase, \
                                                            child_dataObjectCoords, currentIndent+2, "" )

        else:

            child_dataObjectCoords = deepcopy( dataObjectCoords )
            child_dataObjectCoords.append( parameter.index )
                
            if isBasicType:

                value = self.getData( child_dataObjectCoords )

                print( isArray, isBasicType )
                print( child_dataObjectCoords )
                print( value )

                if None != value:
                    componentAsStr = "%s: %s\n" % ( parameter.name, value )
                    dataAsString += currentIndentAsStr + componentAsStr

            else:

                print( isArray, isBasicType )
                print( child_dataObjectCoords )
                print( value )

                for child in child_fields:

                    dataAsString += self.walkParameter( unit, function, child, testcase, \
                                                        child_dataObjectCoords, currentIndent+1, "" )

        return dataAsString

    
    def prepareData( self, testcase ):

        input = testcase.input

        for currentInput in input:

            data_oject_id = currentInput.data_object_id
            value = currentInput.value

            comp = data_oject_id.split( "." )

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

            inputData[data_oject_id] = value

            
    def getData( self, dataObjectCoords ):

        try:

            inputData = self.inputData[dataObjectCoords[0]][dataObjectCoords[1]][dataObjectCoords[2]]

            data_object_id = ".".join( [str(item) for item in dataObjectCoords] )

            value = inputData[data_object_id]

        except KeyError:

            value = None

        return value



if "__main__" == __name__:

    dataApi = DataAPI_Wrapper( "C:\Work\Training\V6.4\MinGW_WorkDir" )
    tcData = TestCaseData( "EXAMPLE", "example", "append", "append.001", dataApi )
    # tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "manager", "Add_Party_To_Waiting_List", "TwoNames", dataApi )
    # tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "manager", "Place_Order", "FoolTheBill", dataApi )
    # tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "<<COMPOUND>>", "<<COMPOUND>>", "Asterix&Obelix", dataApi )
    # tcData = TestCaseData( "IO_WRAPPER_BUBEN", "<<COMPOUND>>", "<<COMPOUND>>", "Write&Read", dataApi )
    # tcData = TestCaseData( "ADVANCED", "advanced_stubbing", "temp_monitor", "Celsius_Stub", dataApi )
    print( tcData )

    print( tcData.getInputDataAsString() )
    # print( tcData.getExpectedDataAsString() )

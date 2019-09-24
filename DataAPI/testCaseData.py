
import os

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

        currentIndentAsStr = ""
        for idx in range( currentIndent ):
            currentIndentAsStr += self.indentUnit

        envName = testcase.get_environment().name

        if 0 == currentIndent:

            tcIndent = currentIndent
            tcIndentAsStr = self.getIndentAsString( tcIndent )

            envIndent = currentIndent
            envIndentAsStr = self.getIndentAsString( envIndent )

            unitIndent = currentIndent + 1
            unitIndentAsStr = self.getIndentAsString( unitIndent )
            
            functionIndent = currentIndent + 2
            functionIndentAsStr = self.getIndentAsString( functionIndent )

            slotIndent = currentIndent + 3
            slotIndentAsStr = self.getIndentAsString( slotIndent )

            if testcase.is_compound_test:

                tcNameAsStr = testcase.name + " " + "(Compound)" + ":\n"
                dataAsString += tcIndentAsStr + tcNameAsStr

            elif testcase.is_unit_test:

                tcNameAsStr = testcase.name() + " " + "(Unit)" + ":\n"
                dataAsString += tcIndentAsStr + tcNameAsStr

            envNameAsStr = "Environment: %s\n" % envName
            dataAsString += envIndentAsStr + envNameAsStr

            unitName = testcase.unit_display_name
            unit = self.envApi[envName].Unit.get( unitName )

            if None != unit:
                unitNameAsStr = "UUT: %s\n" % unit.display_name
            else:
                unitNameAsStr = "UUT: %s\n" % unitName

            dataAsString += unitIndentAsStr + unitNameAsStr

            functionNameAsStr = "Subprogram: %s\n" % testcase.function_display_name
            dataAsString += functionIndentAsStr + functionNameAsStr

        else:

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

        return dataAsString



if "__main__" == __name__:

    dataApi = DataAPI_Wrapper( "C:\Work\Training\V6.4\MinGW_WorkDir" )
    # tcData = TestCaseData( "EXAMPLE", "example", "append", "append.001", dataApi )
    # tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "manager", "Add_Party_To_Waiting_List", "TwoNames", dataApi )
    # tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "manager", "Place_Order", "FoolTheBill", dataApi )
    # tcData = TestCaseData( "MANAGER_BUBENREUTH_W", "<<COMPOUND>>", "<<COMPOUND>>", "Asterix&Obelix", dataApi )
    tcData = TestCaseData( "IO_WRAPPER_BUBEN", "<<COMPOUND>>", "<<COMPOUND>>", "Write&Read", dataApi )
    # tcData = TestCaseData( "ADVANCED", "advanced_stubbing", "temp_monitor", "Celsius_Stub", dataApi )
    print( tcData )

    print( tcData.getInputDataAsString() )
    # print( tcData.getExpectedDataAsString() )


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


    def __str__( self ):

        msg = "TestCase:\n"
        msg += "Environment: %s\n" % self.envName
        msg += "Unit: %s\n" % self.unitName
        msg += "Function: %s\n" % self.functionName
        msg += "TestCase: %s\n" % self.tcName

        return msg


    def getInputDataAsString( self ):

        testcase = self.dataApi.getTestcase( self.envName, self.unitName, \
                                             self.functionName, self.tcName )

        self.inputDataAsString = ""

        self.inputDataAsString = self.dataApi.getInputDataAsString( testcase.input_tree, \
                                                                    self.inputDataAsString )


class DataAPI_Wrapper( object ):

    def __init__( self, workingDirVC ):

        self.workingDirVC = workingDirVC

        self.envApi = {}

        
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
                    return testcase

        return None

        
    def getInputDataAsString( self, input_tree, inputDataAsString ):

        currentIndent = int( input_tree["indent"] )
        currentIndentStr = ""
        for idx in range( currentIndent ):
            currentIndentStr += "  "

        label = input_tree["label"]
        value = input_tree["value"]

        if None != label:

            if None != value:
                newStr = label + ":"  + value + "\n"
            else:
                newStr = label + "\n"

            inputDataAsString += currentIndentStr + newStr

        children = input_tree["children"]

        for child in children:
            inputDataAsString += self.getInputDataAsString( child, "" )

        return inputDataAsString


if "__main__" == __name__:

    dataApi = DataAPI_Wrapper( "C:\Work\Training\V6.4\MinGW_WorkDir" )
    tcData = TestCaseData( "EXAMPLE", "example", "append", "append.001", dataApi )
    print( tcData )

    tcData.getInputDataAsString()
    print( tcData.inputDataAsString )

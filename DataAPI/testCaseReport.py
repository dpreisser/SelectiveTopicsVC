
import sys


class TestCaseReport( object ):

    def __init__( self, envName, unitName, functionName, tcName, dataApiReport ):

        self.envName = envName
        self.unitName = unitName
        self.functionName = functionName
        self.tcName = tcName

        self.dataApiReport = dataApiReport

        self.inputDataAsString = None
        self.expectedDataAsString = None
        self.inpExpDataAsString = None

        self.actualInputDataAsString = None
        self.actualExpectedDataAsString = None
        self.actualInpExpDataAsString = None

        self.initialize()


    def initialize( self ):

        self.dataApiReport.loadApi( self.envName )

        self.testcase = self.dataApiReport.getTestcase( self.envName, self.unitName, \
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
            self.inputDataAsString = self.dataApiReport.getDataAsString( self.testcase.input_tree )
        elif 2 == dataTypeControl:
            self.expectedDataAsString = self.dataApiReport.getDataAsString( self.testcase.expected_tree )
        elif 3 == dataTypeControl:
            self.inpExpDataAsString = self.dataApiReport.getDataAsString( self.testcase.input_tree )
            self.inpExpDataAsString += self.dataApiReport.getDataAsString( self.testcase.expected_tree )


    def buildInpExpDataAsString_explicit( self, dataTypeControl ):

        if 1 == dataTypeControl:
            self.inputDataAsString = self.dataApiReport.getDataAsString_explicit( self.testcase, dataTypeControl, True, 0 )
        elif 2 == dataTypeControl:
            self.expectedDataAsString = self.dataApiReport.getDataAsString_explicit( self.testcase, dataTypeControl, True, 0 )
        elif 3 == dataTypeControl:
            self.inpExpDataAsString = self.dataApiReport.getDataAsString_explicit( self.testcase, dataTypeControl, True, 0 )


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

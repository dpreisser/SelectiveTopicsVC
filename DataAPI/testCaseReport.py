
class TestCaseReport( object ):

    def __init__( self, envName, unitName, functionName, tcName, dataApiReport, traceHandler ):

        self.envName = envName
        self.unitName = unitName
        self.functionName = functionName
        self.tcName = tcName

        self.dataApiReport = dataApiReport
        self.traceHandler = traceHandler

        self.initialize()


    def initialize( self ):

        self.dataApiReport.loadApi( self.envName )

        self.testcase = self.dataApiReport.getTestcase( self.envName, self.unitName, \
                                                        self.functionName, self.tcName )

        if None == self.testcase:
            msg = "No testcase found for following input:"
            msg += self.__str__()
            self.traceHandler.addErrMessage( msg )


    def __str__( self ):

        msg = "TestCaseReport:\n"
        msg += "Environment: %s\n" % self.envName
        msg += "Unit: %s\n" % self.unitName
        msg += "Function: %s\n" % self.functionName
        msg += "TestCase: %s\n" % self.tcName

        return msg


    def getDataAsString( self, dataTypeControl ):

        if 1 == dataTypeControl:
            dataAsString = self.dataApiReport.getDataAsString( self.testcase.input_tree )
        elif 2 == dataTypeControl:
            dataAsString = self.dataApiReport.getDataAsString( self.testcase.expected_tree )
        elif 3 == dataTypeControl:
            dataAsString = self.dataApiReport.getDataAsString( self.testcase.input_tree )
            dataAsString += self.dataApiReport.getDataAsString( self.testcase.expected_tree )

        return dataAsString


    def getDataAsString_explicit( self, dataTypeControl, isInpExpData ):

        dataAsString = self.dataApiReport.getDataAsString_explicit( self.testcase, dataTypeControl, isInpExpData, 0 )

        return dataAsString

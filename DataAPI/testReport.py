
import sys
import argparse

from traceHandler import TraceHandler

from dataApiReportUtils import FormatHandler
from dataApiReport import DataAPI_Report


def initArgParser ():

    parser = argparse.ArgumentParser( description="RGW Report Script" )

    # Working Directory
    parser.add_argument ( "-w", dest="working_directory", action="store", default=".\\", \
                          required=False, help="Working Directory of VectorCAST. Optional. Default: .\\" )                   

    # Environment
    parser.add_argument ( "-e", dest="environment", action="store", default=None, \
                          required=True, help="Name of environment. Required. No Default." )

    # Unit 
    parser.add_argument( "-u", dest="unit", action="store", default=None, \
                         required=False, help="Name of unit. Optional." )

    # Subprogram
    parser.add_argument( "-s", dest="subprogram", action="store", default=None, \
                         required=False, help="Name of subprogram. Optional." )

    # TestCase
    parser.add_argument( "-t", dest="testcase", action="store", default=None, \
                         required=False, help="Name of TestCase. Optional." )

    # DTC
    dctChoices = [ 1, 2, 3 ]
    parser.add_argument( "-d", dest="dataTypeControl", action="store", type=int, default=3, \
                         required=False, choices=dctChoices, \
                         help="Datatype Control: 1: Input, 2: Expected, 3: Input&Expected. Optional. Default: 3" )

    # RGW
    parser.add_argument( "RGW", choices=[ "RGW" ], help="Fixed syntax." )

    # Report
    parser.add_argument( dest="report_type", action="store", default=None,
                         choices=[ "test", "actual" ], \
                         help="Type of report: test data or actual data." )

    return parser


def createReport( args ):

    workingDirVC = args.working_directory

    envName = args.environment
    unitName = args.unit
    functionName = args.subprogram
    tcName = args.testcase

    dataTypeControl = args.dataTypeControl
    reportType = args.report_type

    if "test" == reportType:
        isInpExpData = True
    elif "actual" == reportType:
        isInpExpData = False

    traceHandler = TraceHandler()

#    formatHandler = FormatHandler( traceHandler, \
#                                   indentUnit = "  ", \
#                                   widthLine = 72, \
#                                   widthGrp1 = 32, widthGrp2 = 32, \
#                                   adjustWidthGrp1 = False )

    formatHandler = FormatHandler( traceHandler, \
                                   indentUnit = "  ", \
                                   widthLine = 136, \
                                   widthGrp1 = 64, widthGrp2 = 64, \
                                   adjustWidthGrp1 = False )

    dataApiRep = DataAPI_Report( workingDirVC, formatHandler, traceHandler )
    api = dataApiRep.getApi( envName )

    # dataApiRep.setControlDTS( False, False, False )

    if None == unitName:

        testcases = api.TestCase.all()

        for testcase in testcases:

            dataAsString = dataApiRep.getDataAsString_explicit( testcase, dataTypeControl, isInpExpData, 0 )

            if not traceHandler.getStatus():
                print( traceHandler.getErrMessage() )
            else:
                print( dataAsString )

    elif None != unitName and None == functionName:

        unit = api.Unit.get( unitName )

        for testcase in unit.testcases:

            dataAsString = dataApiRep.getDataAsString_explicit( testcase, dataTypeControl, isInpExpData, 0 )

            if not traceHandler.getStatus():
                print( traceHandler.getErrMessage() )
            else:
                print( dataAsString )

    elif None != unitName and None != functionName and None == tcName:

        unit = api.Unit.get( unitName )

        for function in unit.functions:

            if function.display_name == functionName:

                for testcase in function.testcases:

                    dataAsString = dataApiRep.getDataAsString_explicit( testcase, dataTypeControl, isInpExpData, 0 )

                    if not traceHandler.getStatus():
                        print( traceHandler.getErrMessage() )
                    else:
                        print( dataAsString )

    elif None != unitName and None != functionName and None != tcName:

        testcase = dataApiRep.getTestcase( envName, unitName, \
                                           functionName, tcName )

        if not traceHandler.getStatus():
            print( traceHandler.getErrMessage() )
            return
        else:
            dataAsString = dataApiRep.getDataAsString_explicit( testcase, dataTypeControl, isInpExpData, 0 )

        if not traceHandler.getStatus():
            print( traceHandler.getErrMessage() )
        else:
            print( dataAsString )


if "__main__" == __name__:

    parser = initArgParser()

    # Read the aguments.
    try:
        args = parser.parse_args()
    except SystemExit:
        # exit on failure
        sys.exit() 

    createReport( args )

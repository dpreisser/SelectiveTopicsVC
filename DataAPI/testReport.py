
import sys
import argparse

from dataApiReport import DataAPI_Report
from testCaseReport import TestCaseReport

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



if "__main__" == __name__:

    parser = initArgParser()

    # Read the aguments.
    try:
        args = parser.parse_args()
    except SystemExit:
        # exit on failure
        sys.exit() 

    workingDirVC = args.working_directory

    envName = args.environment
    unitName = args.unit
    functionName = args.subprogram
    tcName = args.testcase

    dataTypeControl = args.dataTypeControl
    reportType = args.report_type

    dataApiRep = DataAPI_Report( workingDirVC )
    api = dataApiRep.getApi( envName )

    if None == unitName:

        testcases = api.TestCase.all()

        for testcase in testcases:

            inpExpDataAsString = dataApiRep.getDataAsString_explicit( testcase, dataTypeControl, True, 0 )
            print( inpExpDataAsString )

    elif None != unitName and None == functionName:

        unit = api.Unit.get( unitName )

        for testcase in unit.testcases:

            inpExpDataAsString = dataApiRep.getDataAsString_explicit( testcase, dataTypeControl, True, 0 )
            print( inpExpDataAsString )

    elif None != unitName and None != functionName and None == tcName:

        unit = api.Unit.get( unitName )

        for function in unit.functions:

            if function.name == functionName:

                for testcase in function.testcases:

                    inpExpDataAsString = dataApiRep.getDataAsString_explicit( testcase, dataTypeControl, True, 0 )
                    print( inpExpDataAsString )

    elif None != unitName and None != functionName and None != tcName:

        dataApiRep = DataAPI_Report( workingDirVC )
        tcRep = TestCaseReport( envName, unitName, functionName, tcName, dataApiRep )

        inpExpDataAsString = tcRep.getInpExpDataAsString( dataTypeControl  )
        print( inpExpDataAsString )


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
    parser.add_argument ( "-e", dest="environment", action="store", default="notset", \
                          required=True, help="Name of environment. Required. No Default." )

    # Unit 
    parser.add_argument( "-u", dest="unit", action="store", default="notset", \
                         required=False, help="Name of unit. Optional." )

    # Subprogram
    parser.add_argument( "-s", dest="subprogram", action="store", default="notset", \
                         required=False, help="Name of subprogram. Optional." )

    # TestCase
    parser.add_argument( "-t", dest="testcase", action="store", default="notset", \
                         required=False, help="Name of TestCase. Optional." )

    # DCT
    dctChoices = [ 1, 2, 3 ]
    parser.add_argument( '-d', dest="dataTypeControlArg", action="store", type=int, default=2, \
                         required=False, choices=dctChoices, \
                         help="Datatype Control: 1: Input, 2: Expected, 3: Input&Expected. Optional. Default: 2" )

    return parser



if "__main__" == __name__:

    parser = initArgParser()

    # Read the aguments.
    try:
        args = parser.parse_args()
    except SystemExit:
        # exit on failure
        sys.exit() 

    numParameters = len( sys.argv ) - 1

    workingDirVC = args.working_directory

    s = 1/0


    if 0 == numParameters:

        dataApiRep = DataAPI_Report( "C:\Work\Training\V6.4\MinGW_WorkDir" )
        tcRep = TestCaseReport( "EXAMPLE", "example", "append", "append.001", dataApiRep )
        # tcRep = TestCaseReport( "MANAGER_BUBENREUTH_W", "manager", "Add_Party_To_Waiting_List", "UserCode", dataApi )
        # tcRep = TestCaseReport( "MANAGER_BUBENREUTH_W", "manager", "Place_Order", "FoolTheBill", dataApi )
        # tcRep = TestCaseReport( "MANAGER_BUBENREUTH_W", "<<COMPOUND>>", "<<COMPOUND>>", "Asterix&Obelix", dataApi )
        # tcRep = TestCaseReport( "IO_WRAPPER_BUBEN", "<<COMPOUND>>", "<<COMPOUND>>", "Write&Read", dataApi )
        # tcRep = TestCaseReport( "ADVANCED", "advanced_stubbing", "temp_monitor", "Celsius_Stub", dataApi )

        print( tcRep.getInpExpDataAsString( 1 ) )
        print( tcRep.getInpExpDataAsString( 2 ) )

    elif 2 == numParameters:

        dataApiRep = DataAPI_Report( sys.argv[1] )
        api = dataApiRep.getApi( sys.argv[2] )

        testcases = api.TestCase.all()

        for testcase in testcases:

            inputDataAsString = dataApiRep.getDataAsString_explicit( testcase, 1, True, 0 )
            expectedDataAsString = dataApiRep.getDataAsString_explicit( testcase, 2, True, 0 )

            print( inputDataAsString )
            print( expectedDataAsString )

    elif 5 == numParameters:

        dataApiRep = DataAPI_Report( sys.argv[1] )
        tcRep = TestCaseReport( sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], dataApiRep )

        # print( tcRep.getInpExpDataAsString( 1 ) )
        # print( tcRep.getInpExpDataAsString( 2 ) )
        print( tcRep.getInpExpDataAsString( 3 ) )

    else:

        print( "Inappropriate number of parameters." )

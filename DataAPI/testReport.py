
import sys

from dataApiReport import DataAPI_Report
from testCaseReport import TestCaseReport


if "__main__" == __name__:

    numParameters = len( sys.argv ) - 1

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


import subprocess

from vector.apps.DataAPI.api import Api

class Link( object ):

    def __init__(self, envName ):
        super(Link, self).__init__()

        self.envName = envName
        self.init()


    def init( self ):

        self.api = Api( self.envName )

        self.testCases = self.api.TestCase.all()
        print( self.testCases )

        self.environment_name = self.api.environment.name


    def linkTestCase( self, tcName, reqKeys ):

        self.testCase_info = self.api.TestCase.get( tcName )
        self.testCase_name = self.testCase_info.name
        self.function_name = self.testCase_info.function_display_name
        self.unit_name = self.testCase_info.unit_display_name

        print( self.environment_name )
        print( self.unit_name )
        print( self.function_name )
        print( self.testCase_name )

        for key in reqKeys:

            # The requirement keys to which the test cases shall be linked must be known.
            # Example given for requirement key /item/1033.
            # One linkage at a time.

            # %VECTORCAST_DIR%\clicast -lc -e environment_name -u unit_name -s function_name -t testCase_name RGW Testcase Link /item/1033

            assocProc = subprocess.Popen( [ "C:\VCAST19\clicast", "-lc", \
                                            "-e", self.environment_name, \
                                            "-u", self.unit_name, \
                                            "-s", self.function_name, \
                                            "-t", self.testCase_name, \
                                            "RGW", "Testcase", "Link", key ], \
                                          stdout=subprocess.PIPE, \
                                          stderr=subprocess.PIPE )

            print( assocProc.stdout.read() )
            print( assocProc.stderr.read() )


if "__main__" == __name__:

    # Note:
    # For the example to work launch dataApi.py from the working directory
    # containing the folder corresponding to the chosen environment name, here "TEST".
    # Command to issue: %vectorcast_dir%\vpython Path\To\dataApi.py
    # You need to be licensed.

    envName = "TEST"
    reqKeys = [ "/item/1033" ]

    linkInstance = Link( envName )    
    linkInstance.linkTestCase( "Pie", reqKeys ) 

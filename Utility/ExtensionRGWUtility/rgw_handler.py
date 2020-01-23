
import os

import codecs

import xmltodict

import pprint

from vector.apps.RGWUtility import rgw_data
from vector.apps.RGWUtility import extension_rgw_data

class RGW_Handler( object ):

    def __init__( self, db_path ):

        self.db_path = db_path
        self.db_file = os.path.join( db_path, "requirements.db" )

        self.extension_repo_helper = extension_rgw_data.ExtensionRepoDataHelper( self.db_file )

        # These are the required keys with fixed names for each requirement.
        self.knownAttributes = [ "key", "id", "title", "description" ]


    def parseXmlFile( self, file ):

        fileStream = codecs.open( file, "rb", "utf-8" )
        xmlAsDict = xmltodict.parse( fileStream.read() )
        fileStream.close()

        return xmlAsDict


    def processRequirement( self, requirement ):

        for key,val in requirement.items():
            print( key,val )


    def processGroup( self, group ):

        print( group["@name"] )

        if isinstance( group["requirement"], list ):
            
            for requirement in group["requirement"]:
                self.processRequirement( requirement )

        else:

            requirement = group["requirement"]
            self.processRequirement( requirement )


    def processXmlAsDict( self, xmlAsDict ):

        if isinstance( xmlAsDict["req_data"]["group"], list ):

            for group in xmlAsDict["req_data"]["group"]:
                self.processGroup( group )
                
        else:
            
            group = xmlAsDict["req_data"]["group"]
            self.processGroup( group )


    def addReqToDatabase( self, file ):

        req_groups = self.extension_repo_helper.get_req_groups()

        self.req_groupNameToGroupId = {}
        
        for req_group in req_groups:
            groupId = req_group[0]
            groupName = req_group[1]
            self.req_groupNameToGroupId[groupName] = groupId

        xmlAsDict = self.parseXmlFile( file )

        self.processXmlAsDict( xmlAsDict )


if "__main__" == __name__:

    file = "C:\\Work\\GitHub\\FAE\\FAE\\products\\VectorCAST_Requirements_Gateway\\Polarion\\reqs_for_import.xml"
    db_path = "C:\\Work\\Training\\Demo\\MinGW_WorkDir\\RGW_Polarion"

    instance = RGW_Handler( db_path )
    instance.addReqToDatabase( file )




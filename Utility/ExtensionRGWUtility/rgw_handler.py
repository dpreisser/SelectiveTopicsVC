
import os

import codecs

import xmltodict

import time

import pprint

from vector.apps.RGWUtility import rgw_data
from vector.apps.RGWUtility import extension_rgw_data

class RGW_Handler( object ):

    def __init__( self, db_path ):

        self.db_path = db_path
        self.db_file = os.path.join( db_path, "requirements.db" )

        self.repo_helper = rgw_data.RepoDataHelper( self.db_file )
        self.extension_repo_helper = extension_rgw_data.ExtensionRepoDataHelper( self.db_file )

        # These are the required keys with fixed names for each requirement.
        self.knownAttributes = [ "key", "id", "title", "description" ]
        self.knownDataTypeNames = [ "External ID", "Title", "Description", "Test Status", "Needs Sync" ]

        self.attributeToDataTypeName = {}
        self.attributeToDataTypeName["id"] = "External ID"
        self.attributeToDataTypeName["title"] = "Title"
        self.attributeToDataTypeName["description"] = "Description"


    def parseXmlFile( self, file ):

        fileStream = codecs.open( file, "rb", "utf-8" )
        xmlAsDict = xmltodict.parse( fileStream.read() )
        fileStream.close()

        return xmlAsDict


    def processRequirement( self, requirement, groupId ):

        attribute_nameToValue = {}
        attribute_nameToId = {}

        for attributeName,attributeValue in requirement.items():

            attribute_nameToValue[attributeName] = attributeValue
            print( attributeName,attributeValue )

            if "key" == attributeName:

                reqKey = attributeValue
                objectTypeId = 1
                needsSync = 0

                reqRecord = self.extension_repo_helper.get_req_on_req_key( reqKey )
                print( reqRecord )
                reqId = reqRecord[0]

                if isinstance( reqId, type(None) ):
                    actionTypeName = "IMPORT"
                else:
                    actionTypeName = "UPDATE"

                actionTypeId = self.actionType_nameToId[actionTypeName]
                print( actionTypeName, actionTypeId )

                self.extension_repo_helper.create_req( objectTypeId, groupId, reqKey, needsSync )
                reqRecord = self.extension_repo_helper.get_req_on_req_key( reqKey )
                print( reqRecord )
                reqId = reqRecord[0]

                gmtime = time.gmtime()
                dts = time.strftime( "%Y-%m-%d %H:%M:%S", gmtime )
                self.extension_repo_helper.create_req_tracking( reqId, actionTypeId, dts )

                reqTrackingRecord = self.extension_repo_helper.get_req_tracking_on_req_id( reqId )
                print( reqTrackingRecord )
                reqTrackingId = reqTrackingRecord[0]

            # if attributeName in self.knownAttributes:
            #     dataTypeId = self.dataType_nameToId[key]

            # self.repo_helper.get_create_data_type_id(self, tcDataType):


    def processGroup( self, group ):

        groupName = group["@name"]

        if groupName in self.req_groupNameToGroupId.keys():
            groupId = self.req_groupNameToGroupId[groupName]
        else:
            self.extension_repo_helper.create_req_group( groupName )
            groupRecord = self.extension_repo_helper.get_req_group_on_name( groupName )
            groupId = groupRecord[0]
            groupName = groupRecord[1]
            self.req_groupNameToGroupId[groupName] = groupId

        if isinstance( group["requirement"], list ):
            
            for requirement in group["requirement"]:
                self.processRequirement( requirement, groupId )

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


    def addRequirementsToDatabase( self, file ):

        actionTypeRecords = self.extension_repo_helper.get_action_types()

        self.actionType_nameToId = {}

        for actionTypeRecord in actionTypeRecords:
            actionTypeId = actionTypeRecord[0]
            actionTypeName = actionTypeRecord[1]
            self.actionType_nameToId[actionTypeName] = actionTypeId

        groupRecords = self.extension_repo_helper.get_req_groups()

        self.req_groupNameToGroupId = {}
        
        for groupRecord in groupRecords:
            groupId = groupRecord[0]
            groupName = groupRecord[1]
            self.req_groupNameToGroupId[groupName] = groupId

        xmlAsDict = self.parseXmlFile( file )

        self.processXmlAsDict( xmlAsDict )


if "__main__" == __name__:

    file = "C:\\Work\\GitHub\\FAE\\FAE\\products\\VectorCAST_Requirements_Gateway\\Polarion\\reqs_for_import.xml"
    db_path = "C:\\Work\\Training\\Demo\\MinGW_WorkDir\\RGW_Polarion"

    instance = RGW_Handler( db_path )
    instance.addRequirementsToDatabase( file )




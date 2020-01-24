
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
        self.knownDataTypeNames = [ "External ID", "Title", "Description", "Test Status", "Needs Sync", "Last System Value" ]

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

        reqId = None
        reqTrackingId = None

        dataTypeInfoList = []

        gmtime = time.gmtime()
        dts = time.strftime( "%Y-%m-%d %H:%M:%S", gmtime )

        for attributeName,attributeValue in requirement.items():

            print( "Attribute: ", attributeName, attributeValue )

            if "key" == attributeName:

                reqKey = attributeValue
                objectTypeId = 1
                needsSync = 0

                reqRecord = self.extension_repo_helper.get_req_on_req_key( reqKey )
                print( "reqRecord: ", reqRecord )
                reqId = reqRecord[0]

                if reqId is None:
                    actionTypeName = "IMPORT"
                else:
                    actionTypeName = "UPDATE"

                actionTypeId = self.actionType_nameToId[actionTypeName]
                print( "Action: ", actionTypeName, actionTypeId )

                if "IMPORT" == actionTypeName:

                    self.extension_repo_helper.create_req( objectTypeId, groupId, reqKey, needsSync )
                    reqRecord = self.extension_repo_helper.get_req_on_req_key( reqKey )
                    print( "reqRecord: ", reqRecord )
                    reqId = reqRecord[0]

                else:

                    tcActionTypeName = "FLAG_FOR_REVIEW"
                    tcActionTypeId = self.actionType_nameToId[tcActionTypeName]

                    tcLinkRecords = self.extension_repo_helper.get_tc_links_on_req_id( reqId )
                    for tcLinkRecord in tcLinkRecords: 
                        tcId = tcLinkRecord[0]
                        if tcId is not None:
                            self.tcTrackingInfo[tcId] = ( tcId, tcActionTypeId, dts )

                self.extension_repo_helper.create_req_tracking( reqId, actionTypeId, dts )
                reqTrackingRecord = self.extension_repo_helper.get_req_tracking_on_req_id( reqId )
                print( "reqTrackingRecord: ", reqTrackingRecord )
                reqTrackingId = reqTrackingRecord[0]

            else:

                if attributeName in self.attributeToDataTypeName.keys():
                    dataTypeName = self.attributeToDataTypeName[attributeName]
                else:
                    dataTypeName = attributeName

                if dataTypeName in self.dataType_nameToId.keys():
                    dataTypeId = self.dataType_nameToId[dataTypeName]
                else:
                    self.extension_repo_helper.create_data_type( dataTypeName )
                    dataTypeRecord = self.extension_repo_helper.get_data_type_on_name( dataTypeName )
                    print( "reqTypeRecord: ", reqTypeRecord )
                    dataTypeId = reqTypeRecord[0]
                    self.dataType_nameToId[dataTypeName] = dataTypeId

                dataTypeInfoList.append( (dataTypeId,attributeValue) )

        if None != reqId and None != reqTrackingId:

            for dataTypeInfo in dataTypeInfoList:
                dataTypeId = dataTypeInfo[0]
                dataTypeValue = dataTypeInfo[1]
                self.extension_repo_helper.create_req_data( reqId, reqTrackingId, dataTypeId, dataTypeValue ) 


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

        self.tcTrackingInfo = {}

        if isinstance( xmlAsDict["req_data"]["group"], list ):

            for group in xmlAsDict["req_data"]["group"]:
                self.processGroup( group )
                
        else:
            
            group = xmlAsDict["req_data"]["group"]
            self.processGroup( group )


    def addRequirementsToDatabase( self, file ):

        actionTypeRecords = self.extension_repo_helper.get_action_types()

        self.actionType_nameToId = {}
        self.actionType_idToName = {}

        for actionTypeRecord in actionTypeRecords:
            actionTypeId = actionTypeRecord[0]
            actionTypeName = actionTypeRecord[1]
            self.actionType_nameToId[actionTypeName] = actionTypeId
            self.actionType_idToName[actionTypeId] = actionTypeName

        dataTypeRecords = self.extension_repo_helper.get_data_types()

        self.dataType_nameToId = {}

        for dataTypeRecord in dataTypeRecords:
            dataTypeId = dataTypeRecord[0]
            dataTypeName = dataTypeRecord[1]
            self.dataType_nameToId[dataTypeName] = dataTypeId

        groupRecords = self.extension_repo_helper.get_req_groups()

        self.req_groupNameToGroupId = {}
        
        for groupRecord in groupRecords:
            groupId = groupRecord[0]
            groupName = groupRecord[1]
            self.req_groupNameToGroupId[groupName] = groupId

        xmlAsDict = self.parseXmlFile( file )

        self.processXmlAsDict( xmlAsDict )

        for tcId, tcTrackingInfo in self.tcTrackingInfo.items():

            tcId = tcTrackingInfo[0]
            tcActionTypeId = tcTrackingInfo[1]
            dts = tcTrackingInfo[2]
            self.extension_repo_helper.create_tc_tracking( tcId, tcActionTypeId, dts )

            tcTrackingRecord = self.extension_repo_helper.get_tc_tracking_on_tc_id( tcId )
            print( "tcTrackingRecord: ", tcTrackingRecord )
            tcTrackingId = tcTrackingRecord[0]

            tcDataTypeName = "Test Status"
            tcDataTypeId = self.dataType_nameToId[tcDataTypeName]
            tcDataTypeValue = self.actionType_idToName[tcActionTypeId]
            self.extension_repo_helper.create_tc_data( tcId, tcTrackingId, tcDataTypeId, tcDataTypeValue )


if "__main__" == __name__:

    file = "C:\\Work\\GitHub\\FAE\\FAE\\products\\VectorCAST_Requirements_Gateway\\Polarion\\reqs_for_import.xml"
    db_path = "C:\\Work\\Training\\Demo\\MinGW_WorkDir\\RGW_Polarion"

    instance = RGW_Handler( db_path )
    instance.addRequirementsToDatabase( file )




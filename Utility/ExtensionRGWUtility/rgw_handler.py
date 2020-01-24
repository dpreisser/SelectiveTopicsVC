
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


    def getDataForExport( self ):

        export_req_data = {}
        export_tc_data = {}

        req_records = self.extension_repo_helper.get_req_export()

        for req_record in req_records:

            print( "req_record: ", req_record )

            lst_env_names = []
            lst_tc_names = []
            lst_tc_unique_ids = []        
            lst_tc_statuses = []

            req_id = req_record[0]
            req_key = req_record[1]

            export_req_data[req_key] = {}
            export_data = export_req_data[req_key]

            export_data["key"] = req_key
            export_data["modified"] = True

            last_update_dts = self.repo_helper.get_requirement_tracking_max_date_on_key( req_key )
            export_data["last_update_dts"] = last_update_dts

            req_data_type_records = self.repo_helper.get_data_types_on_req( req_id )

            for req_data_type_record in req_data_type_records:

                req_data_type_id = req_data_type_record[0]
                req_data_type_name = self.repo_helper.get_data_type_name_on_id( req_data_type_id )

                req_data_record = self.repo_helper.get_requirement_data_latest( req_id, req_data_type_id )
                req_data_type_content = req_data_record[2]

                print( req_data_type_id, req_data_type_name, req_data_type_content )

                if "External ID" == req_data_type_name:
                    export_data["id"] = req_data_type_content
                elif "Title" == req_data_type_name:
                    export_data["title"] = req_data_type_content
                elif "Description" == req_data_type_name:
                    export_data["description"] = req_data_type_content
                else:
                    export_data[req_data_type_name] = req_data_type_content

                tc_link_records = self.extension_repo_helper.get_tc_links_on_req_id( req_id )

                for tc_link_record in tc_link_records:

                    tc_id = tc_link_record[0]
                    tc_unique_id = tc_link_record[1]

                    if tc_unique_id in export_tc_data.keys():

                        env_name = export_tc_data[tc_unique_id]["environment_name"]
                        tc_name = export_tc_data[tc_unique_id]["test_name"]
                        tc_unique_id = export_tc_data[tc_unique_id]["test_unique_id"]
                        tc_status = export_tc_data[tc_unique_id]["test_status"]

                    else:

                        export_tc_data[tc_unique_id] = {}

                    tc_record = self.repo_helper.get_testcase_detail( tc_id )
                    print( "tc_record: ", tc_record )

                    env_name = tc_record[0]
                    tc_name = tc_record[3]

                    if tc_record[4] != tc_unique_id:
                        print( "Internal error." )
                        sys.exit()

                    tc_data_records = self.repo_helper.get_testcase_data_latest_all( tc_id )

                    tc_data_record = tc_data_records[-1]
                    print( "tc_data_record: ", tc_data_record )

                    tc_status = "none"

                    # 7 means action RUN
                    if 7 == tc_data_record[2]:
                        tc_status = tc_data_record[4]

                    export_tc_data[tc_unique_id]["environment_name"] = env_name
                    export_tc_data[tc_unique_id]["test_name"] = tc_name
                    export_tc_data[tc_unique_id]["test_unique_id"] = tc_unique_id
                    export_tc_data[tc_unique_id]["test_status"] = tc_status
                    export_tc_data[tc_unique_id]["test_req_keys"] = []

                    lst_env_names.append( env_name )
                    lst_tc_names.append( tc_name )
                    lst_tc_unique_ids.append( tc_unique_id )
                    lst_tc_statuses.append( tc_status )

                    export_tc_data[tc_unique_id]["test_req_keys"].append( req_key )

            export_data["environment_name"] = "\n".join( lst_env_names )
            export_data["test_name"] = "\n".join( lst_tc_names )
            export_data["test_unique_id"] = "\n".join( lst_tc_unique_ids )
            export_data["test_status"] = "\n".join( lst_tc_statuses )

        print( "export_req_data: " )
        pprint.pprint( export_req_data )

        print( "export_tc_data: " )
        pprint.pprint( export_tc_data )

        return export_req_data, export_tc_data


if "__main__" == __name__:

    db_path = "C:\\Work\\Training\\Demo\\MinGW_WorkDir\\RGW_Polarion"
    file = "C:\\Work\\GitHub\\FAE\\FAE\\products\\VectorCAST_Requirements_Gateway\\Polarion\\reqs_for_import.xml"

    instance = RGW_Handler( db_path )
    # instance.addRequirementsToDatabase( file )
    # instance.getDataForExport()

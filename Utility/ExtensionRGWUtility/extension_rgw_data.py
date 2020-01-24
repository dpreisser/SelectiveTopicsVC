
import sqlite3
import os.path

class ExtensionRepoDataHelper:

    def __init__( self, sqlite_file ):

        self.connection = None

        if ( not os.path.isfile(sqlite_file) ):
            raise IOError("Sqlite DB '" + sqlite_file + "' not found.")

        self.connection = sqlite3.connect( sqlite_file )
        self.use_max_counts = True
        self.cur = self.connection.cursor()

    # action types

    def _q_select_action_types( self ):
        return \
            ("SELECT "
             "id, "
             "text "
             "FROM action_types;")

    def get_action_types( self ):
        self.cur.execute( self._q_select_action_types() )
        return self.cur.fetchall()

    # data types

    def _q_select_data_types( self ):
        return \
            ("SELECT "
             "id, "
             "text "
             "FROM data_types;")

    def get_data_types( self ):
        self.cur.execute( self._q_select_data_types() )
        return self.cur.fetchall()

    def _q_select_data_type_on_name( self ):
        return \
            ("SELECT "
             "id, "
             "text "
             "FROM data_types "
             "WHERE text = ?;")

    def get_data_type_on_name( self, dataTypeName ):
        self.cur.execute( self._q_select_data_type_on_name(), (dataTypeName,) )
        return self.cur.fetchone()

    def _q_create_data_type( self ):
        return \
            ("INSERT INTO data_types "
             "(text) "
             "VALUES (?)")

    def create_data_type( self, dataTypeName ):
        self.cur.execute( self._q_create_data_type(), (dataTypeName,) )
        self.connection.commit()

    # requirement groups

    def _q_select_req_groups( self ):
        return \
            ("SELECT "
             "id, "
             "name "
             "FROM requirement_groups;")

    def get_req_groups( self ):
        self.cur.execute( self._q_select_req_groups() )
        return self.cur.fetchall()

    def _q_select_req_group_on_name( self ):
        return \
            ("SELECT "
             "id, "
             "name "
             "FROM requirement_groups "
             "WHERE name = ?;")

    def get_req_group_on_name( self, groupName ):
        self.cur.execute( self._q_select_req_group_on_name(), (groupName,) )
        return self.cur.fetchone()

    def _q_create_req_group( self ):
        return \
            ("INSERT INTO requirement_groups "
             "(name) "
             "VALUES (?)")

    def create_req_group( self, groupName ):
        self.cur.execute( self._q_create_req_group(), (groupName,) )
        self.connection.commit()

    # requirement

    def _q_select_req_on_req_key( self ):
        return \
            ("SELECT "
             "max(id), "
             "object_type_id, "
             "group_id, "
             "external_key, "
             "needs_sync "
             "FROM requirements "
             "WHERE external_key = ?;")

    def get_req_on_req_key( self, reqKey ):
        self.cur.execute( self._q_select_req_on_req_key(), (reqKey,) )
        return self.cur.fetchone()

    def _q_select_req_export( self ):
        return \
            ("SELECT "
             "requirements.id as id, "
             "requirements.external_key as key "
             "FROM requirements "
             "WHERE requirements.needs_sync = 1;")

    def get_req_export( self ):
        self.cur.execute( self._q_select_req_export() )
        return self.cur.fetchall()

    def _q_create_req( self ):
        return \
            ("INSERT INTO requirements "
             "(object_type_id, group_id, external_key, needs_sync) "
             "VALUES (?, ?, ?, ?)")

    def create_req( self, objectTypeId, groupId, reqKey, needsSync ):
        self.cur.execute( self._q_create_req(), (objectTypeId, groupId, reqKey, needsSync) )
        self.connection.commit()

    # requirement tracking

    def _q_select_req_tracking_on_req_id( self ):
        return \
            ("SELECT "
             "max(id), "
             "requirement_id, "
             "action_id, "
             "date_time "
             "FROM requirement_tracking "
             "WHERE requirement_id = ?;")

    def get_req_tracking_on_req_id( self, reqId ):
        self.cur.execute( self._q_select_req_tracking_on_req_id(), (reqId,) )
        return self.cur.fetchone()

    def _q_create_req_tracking( self ):
        return \
            ("INSERT INTO requirement_tracking "
             "(requirement_id, action_id, date_time) "
             "VALUES (?, ?, ?)")

    def create_req_tracking( self, reqId, actionTypeId, dts ):
        self.cur.execute( self._q_create_req_tracking(), (reqId, actionTypeId, dts) )
        self.connection.commit()

    # requirement data

    def _q_create_req_data( self ):
        return \
            ("INSERT INTO requirement_data "
             "(requirement_id, requirement_tracking_id, data_type_id, text) "
             "VALUES (?, ?, ?, ?)")

    def create_req_data( self, reqId, reqTrackingId, dataTypeId, dataTypeValue ):
        self.cur.execute( self._q_create_req_data(), (reqId, reqTrackingId, dataTypeId, dataTypeValue) )
        self.connection.commit()

    # requirements test_cases

    def _q_select_tc_links_on_req_id( self ):
        return \
            ("SELECT "
             "requirements_test_cases.test_case_id, "
             "test_cases.test_case_unique_id "
             "FROM requirements_test_cases "
             "INNER JOIN test_cases "
             "ON requirements_test_cases.test_case_id = test_cases.id "
             "WHERE requirements_test_cases.requirement_id = ?;")

    def get_tc_links_on_req_id( self, reqId ):
        self.cur.execute( self._q_select_tc_links_on_req_id(), (reqId,) )
        return self.cur.fetchall()

    def _q_select_req_links_on_tc_id( self ):
        return \
            ("SELECT "
             "requirements_test_cases.requirement_id, "
             "requirements.external_key "
             "FROM requirements_test_cases "
             "INNER JOIN requirements "
             "ON requirements_test_cases.requirement_id = requirements.id "
             "WHERE requirements_test_cases.test_case_id = ?;")

    def get_req_links_on_tc_id( self, tcId ):
        self.cur.execute( self._q_select_req_links_on_tc_id(), (tcId,) )
        return self.cur.fetchall()

    # test_case tracking

    def _q_select_tc_tracking_on_tc_id( self ):
        return \
            ("SELECT "
             "max(id), "
             "test_case_id, "
             "action_id, "
             "date_time "
             "FROM test_case_tracking "
             "WHERE test_case_id = ?;")

    def get_tc_tracking_on_tc_id( self, tcId ):
        self.cur.execute( self._q_select_tc_tracking_on_tc_id(), (tcId,) )
        return self.cur.fetchone()

    def _q_create_tc_tracking( self ):
        return \
            ("INSERT INTO test_case_tracking "
             "(test_case_id, action_id, date_time) "
             "VALUES (?, ?, ?)")

    def create_tc_tracking( self, tcId, actionTypeId, dts ):
        self.cur.execute( self._q_create_tc_tracking(), (tcId, actionTypeId, dts) )
        self.connection.commit()

    # test_case data

    def _q_create_tc_data( self ):
        return \
            ("INSERT INTO test_case_data "
             "(test_case_id, test_case_tracking_id, data_type_id, text) "
             "VALUES (?, ?, ?, ?)")

    def create_tc_data( self, tcId, tcTrackingId, dataTypeId, dataTypeValue ):
        self.cur.execute( self._q_create_tc_data(), (tcId, tcTrackingId, dataTypeId, dataTypeValue) )
        self.connection.commit()

    # deletion requirement

    def _q_delete_requirements_test_cases_on_req_id( self ):
        return \
            ("delete "
             "from requirements_test_cases "
             "where requirement_id = ?;")

    def _q_delete_requirement_tracking_on_req_id( self ):
        return \
            ("delete "
             "from requirement_tracking "
             "where requirement_id = ?;")

    def _q_delete_requirement_data_on_req_id( self ):
        return \
            ("delete "
             "from requirement_data "
             "where requirement_id = ?;")

    def _q_delete_requirements_on_req_id( self ):
        return \
            ("delete "
             "from requirements "
             "where id = ?;")

    def delete_requirement_on_req_id( self, req_id ):
        self.cur.execute( self._q_delete_requirements_test_cases_on_req_id(), (req_id,) )
        print ( "Removed %s requirements_test_cases records." % (self.cur.rowcount,) )
        self.cur.execute( self._q_delete_requirement_tracking_on_req_id(), (req_id,) )
        print ( "Removed %s requirement_tracking records." % (self.cur.rowcount,) )
        self.cur.execute( self._q_delete_requirement_data_on_req_id(), (req_id,) )
        print ( "Removed %s requirement_data records." % (self.cur.rowcount,) )
        self.cur.execute( self._q_delete_requirements_on_req_id(), (req_id,) )
        print ( "Removed %s requirements records." % (self.cur.rowcount,) )
        self.connection.commit()

    # deletion test case

    def _q_delete_requirements_test_cases_on_tc_ic( self ):
        return \
            ("delete "
             "from requirements_test_cases "
             "where test_case_id = ?;")

    def _q_delete_test_case_tracking_on_tc_id( self ):
        return \
            ("delete "
             "from test_case_tracking "
             "where test_case_id = ?;")

    def _q_delete_test_case_data_on_tc_id( self ):
        return \
            ("delete "
             "from test_case_data "
             "where test_case_id = ?;")

    def _q_delete_test_cases_on_tc_id( self ):
        return \
            ("delete "
             "from test_cases "
             "where id = ?;")

    def delete_testcase_on_req_id( self, tc_id ):
        self.cur.execute( self._q_delete_requirements_test_cases_on_tc_id(), (tc_id,) )
        print ( "Removed %s requirements_test_cases records." % (self.cur.rowcount,) )
        self.cur.execute( self._q_delete_test_case_tracking_on_tc_id(), (tc_id,) )
        print ( "Removed %s test_case_tracking records." % (self.cur.rowcount,) )
        self.cur.execute( self._q_delete_test_case_data_on_tc_id(), (tc_id,) )
        print ( "Removed %s test_case_data records." % (self.cur.rowcount,) )
        self.cur.execute( self._q_delete_test_cases_on_tc_id(), (tc_id,) )
        print ( "Removed %s test_cases records." % (self.cur.rowcount,) )
        self.connection.commit()

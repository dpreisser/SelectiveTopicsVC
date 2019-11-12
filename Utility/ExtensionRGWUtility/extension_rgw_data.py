
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


    def _q_select_req_links_for_tc( self ):
        return \
            ("SELECT "
             "requirements_test_cases.requirement_id, "
             "requirements.external_key "
             "FROM requirements_test_cases "
             "INNER JOIN requirements "
             "ON requirements_test_cases.requirement_id = requirements.id "
             "WHERE requirements_test_cases.test_case_id = ?;")

    def get_req_links_for_tc( self, tc_id ):
        self.cur.execute( self._q_select_req_links_for_tc(), (tc_id,) )
        return self.cur.fetchall()

    def _q_select_req_for_req( self ):
        return \
            ("SELECT "
             "id "
             "FROM requirements "
             "WHERE external_key = ?;")

    def get_req_from_req( self, req_key ):
        self.cur.execute( self._q_select_req_for_req(), (req_key,) )
        return self.cur.fetchall()

    # deletion requirement

    def _q_delete_requirements_test_cases_for_req( self ):
        return \
            ("delete "
             "from requirements_test_cases "
             "where requirement_id = ?;")

    def _q_delete_requirement_tracking_for_req( self ):
        return \
            ("delete "
             "from requirement_tracking "
             "where requirement_id = ?;")

    def _q_delete_requirement_data_for_req( self ):
        return \
            ("delete "
             "from requirement_data "
             "where requirement_id = ?;")

    def _q_delete_requirements_for_req( self ):
        return \
            ("delete "
             "from requirements "
             "where id = ?;")

    def delete_requirement( self, req_id ):
        self.cur.execute( self._q_delete_requirements_test_cases_for_req(), (req_id,) )
        print ( "Removed %s requirements_test_cases records." % (self.cur.rowcount,) )
        self.cur.execute( self._q_delete_requirement_tracking_for_req(), (req_id,) )
        print ( "Removed %s requirement_tracking records." % (self.cur.rowcount,) )
        self.cur.execute( self._q_delete_requirement_data_for_req(), (req_id,) )
        print ( "Removed %s requirement_data records." % (self.cur.rowcount,) )
        self.cur.execute( self._q_delete_requirements_for_req(), (req_id,) )
        print ( "Removed %s requirements records." % (self.cur.rowcount,) )
        self.connection.commit()

    # deletion test case

    def _q_delete_requirements_test_cases_for_tc( self ):
        return \
            ("delete "
             "from requirements_test_cases "
             "where test_case_id = ?;")

    def _q_delete_test_case_tracking_for_tc( self ):
        return \
            ("delete "
             "from test_case_tracking "
             "where test_case_id = ?;")

    def _q_delete_test_case_data_for_tc( self ):
        return \
            ("delete "
             "from test_case_data "
             "where test_case_id = ?;")

    def _q_delete_test_cases_for_tc( self ):
        return \
            ("delete "
             "from test_cases "
             "where id = ?;")

    def delete_testcase( self, tc_id ):
        self.cur.execute( self._q_delete_requirements_test_cases_for_tc(), (tc_id,) )
        print ( "Removed %s requirements_test_cases records." % (self.cur.rowcount,) )
        self.cur.execute( self._q_delete_test_case_tracking_for_tc(), (tc_id,) )
        print ( "Removed %s test_case_tracking records." % (self.cur.rowcount,) )
        self.cur.execute( self._q_delete_test_case_data_for_tc(), (tc_id,) )
        print ( "Removed %s test_case_data records." % (self.cur.rowcount,) )
        self.cur.execute( self._q_delete_test_cases_for_tc(), (tc_id,) )
        print ( "Removed %s test_cases records." % (self.cur.rowcount,) )
        self.connection.commit()

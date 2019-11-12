
import re
import sys
import os
import argparse

from copy import deepcopy
import pprint

from subprocess import call
from vector.apps.RGWUtility import rgw_data
from vector.apps.RGWUtility import extension_rgw_data

from gateway_repository import RepositoryDB

def report_coverage(file_name):
    repo_helper = rgw_data.RepoDataHelper(file_name)    
    req_covered = ""
    req_not_covered = ""
    # Get all requirements
    tbl_req = repo_helper.get_requirements()
    count_req = len(tbl_req)
    # Get Requirement IDs for Requirements that are assigned to test cases.
    tbl_req_covered = repo_helper.get_requirements_covered()
    count_req_covered = len(tbl_req_covered)
    for row_req_covered in tbl_req_covered:
        if len(req_covered) != 0: req_covered += ","
        req_covered += row_req_covered[0]
    # Get Requirement IDs for Requirements that are not assigned to test cases.
    tbl_req_not_covered = repo_helper.get_requirements_not_covered()
    for row_req_not_covered in tbl_req_not_covered:
        if len(req_not_covered) != 0: req_not_covered += ","
        req_not_covered += row_req_not_covered[0]
    
    # Output
    print "Requirements linked to Test Cases:  {}".format(req_covered,)
    print "Requirements not linked to Test Cases:  {}".format(req_not_covered,)
    print "Total: {} out of {} Requirements covered".format(count_req_covered, count_req)

def report_status(file_name):
    repo_helper = rgw_data.RepoDataHelper(file_name)
    test_cases = {}
    req_status_none = ""
    req_status_fail = ""
    req_status_pass = ""
    count_req_status_none = 0
    count_req_status_fail = 0
    count_req_status_pass = 0

    # Get the latest pass / fail statuses for all test cases.    
    tbl_tc = repo_helper.get_testcases()
    for row_tc in tbl_tc:
        curr_tc_id = row_tc[0]   

        repo_db = RepositoryDB( file_name )
        tc_unique_id = row_tc[5]
        tc_data_consolidated = repo_db.get_tc_data( tc_unique_id )
        print ("TC name is " + str( tc_data_consolidated.get('tc_name') )) 
        
        # For each testcase, find its last pass / fail state no later than 'date_time'.
        row_last_status = repo_helper.get_tc_last_result(curr_tc_id)
        # Populate the pass / fail state in memory
        last_status = rgw_data.RGW_STATUS_NONE
        if row_last_status != None:
            last_status = row_last_status[0]
        test_cases[curr_tc_id] = last_status

    # Work out what the compound pass / fail status is of each requirement.
    # Query all requirements
    tbl_req = repo_helper.get_requirements()
    count_req = len(tbl_req)
    for row_req in tbl_req:
        # For each requirement, find all linked testcases
        curr_req_id = row_req[0]
        curr_req_key = row_req[1]
        tbl_linked_tc = repo_helper.get_tc_links_on_req(curr_req_id)
        curr_req_status = rgw_data.RGW_STATUS_NONE
        for row_linked_tc in tbl_linked_tc:
            # For each linked testcase, get its status:
            curr_tc_status = rgw_data.RGW_STATUS_NONE
            curr_linked_tc = row_linked_tc[0]
            
            repo_db = RepositoryDB( file_name )
            tc_unique_id = row_linked_tc[5] 
            tc_data_consolidated = repo_db.get_tc_data( tc_unique_id )
            print ("TC name is " + str( tc_data_consolidated.get('tc_name') ))            
            
            # Does this testcase have a status?
            if curr_linked_tc in test_cases:
                curr_tc_status = test_cases[curr_linked_tc]
            curr_req_status = curr_tc_status
            # If any pass / fail state is fail or none, then the requirement is fail or none respectively,
            # so there is no point in any further updates.
            if (
                curr_req_status == rgw_data.RGW_STATUS_NONE or
                curr_req_status == rgw_data.RGW_STATUS_FAIL
               ):
                break;

        # Add requirement to one of the three strings.
        if curr_req_status == rgw_data.RGW_STATUS_NONE:
            if len(req_status_none) != 0: req_status_none += ","
            req_status_none += curr_req_key
            count_req_status_none += 1
        elif curr_req_status == rgw_data.RGW_STATUS_FAIL:
            if len(req_status_fail) != 0: req_status_fail += ","
            req_status_fail += curr_req_key
            count_req_status_fail += 1
        elif curr_req_status == rgw_data.RGW_STATUS_PASS:
            if len(req_status_pass) != 0: req_status_pass += ","
            req_status_pass += curr_req_key
            count_req_status_pass += 1

    # Output
    print "Requirements with NONE status:  {}".format(req_status_none,)
    print "Requirements with FAIL status:  {}".format(req_status_fail,)
    print "Requirements with PASS status:  {}".format(req_status_pass)
    print "Total: {} out of {} Requirements with NONE status".format(count_req_status_none, count_req)
    print "Total: {} out of {} Requirements with FAIL status".format(count_req_status_fail, count_req)
    print "Total: {} out of {} Requirements with PASS status".format(count_req_status_pass, count_req)

    
def report( file_name ):

    repo_helper = rgw_data.RepoDataHelper( file_name )
    repo_db = RepositoryDB( file_name )  

    tc_records_all = repo_helper.get_testcases()

    for tc_record in tc_records_all:

        tc_unique_id = tc_record[5]

        tc_data_consolidated = repo_db.get_tc_data( tc_unique_id )
        tc_data_consolidated["tc_unique_id"] = tc_unique_id

        print( tc_record )
        print( tc_data_consolidated )


def report_2( file_name ):

    tc_info = {}
    tc_info["tc_id"] = {}
    tc_info["tc_unique_id"] = {}

    repo_helper = rgw_data.RepoDataHelper( file_name )
    extension_repo_helper = extension_rgw_data.ExtensionRepoDataHelper( file_name )

    tc_records_all = repo_helper.get_testcases()

    # link_action_index = repo_helper.get_action_index( "link" )
    # print( link_action_index )

    for tc_record in tc_records_all:

        # tc_unique_id = tc_record[5]
        # tc_detail = repo_helper.get_testcase_detail_on_unique_id( tc_unique_id )

        tc_id = tc_record[0]
        # tc_data = repo_helper.get_testcase_data_latest_all( tc_id )
        req_links = extension_repo_helper.get_req_links_for_tc( tc_id )

        # print( tc_record )
        # print( tc_detail )
        # print( tc_data )
        # print( req_links )

        tc_id = tc_record[0]
        tc_unique_id = tc_record[5]

        theData = {}

        theData["tc_id"] = tc_record[0]
        theData["environment"] = tc_record[1]
        theData["unit"] = tc_record[2]
        theData["subprogram"] = tc_record[3]
        theData["tc_name"] = tc_record[4]
        theData["tc_unique_id"] = tc_record[5]

        theData["req_links"] = {}

        for tuple in req_links:
            req_id = tuple[0]
            theData["req_links"][req_id] = { "req_id" : tuple[0], "req_key" : tuple[1] }

        # We do not necessarily need deepcopy here.
        tc_info["tc_id"][tc_id] = deepcopy( theData )
        tc_info["tc_unique_id"][tc_unique_id] = deepcopy( theData )

    pprint.pprint( tc_info )


def delete_requirement( file_name, req_key ):

    extension_repo_helper = extension_rgw_data.ExtensionRepoDataHelper( file_name )

    req_ids = extension_repo_helper.get_req_from_req( req_key )

    for tuple in req_ids:
        req_id = tuple[0]
        extension_repo_helper.delete_requirement( req_id )


def delete_testcase( file_name, tc_id ):

    extension_repo_helper = extension_rgw_data.ExtensionRepoDataHelper( file_name )

    extension_repo_helper.delete_testcase( tc_id )


def rgw_cbt(file_name, dry_run):
    repo_helper = rgw_data.RepoDataHelper(file_name)
    # for all test-cases, select the most recent run date across the whole environment
    row_last_run = repo_helper.get_tc_last_result_all()
    last_date = row_last_run[1]
    # For all requirements changed between the most recent run date and now, find all associated test-cases
    tbl_testcases_rerun = repo_helper.get_testcases_since_req_changed(last_date)
    count_testcases = len(tbl_testcases_rerun)
    if not(count_testcases):
        print "-----------------"
        print "No Requirements have changed, there are no testcases to run."
        return
    if dry_run:
        print "-----------------"
        print "The following testcases will be run:"
    for row_testcase in tbl_testcases_rerun:
        if dry_run:
            testcase_detail = row_testcase[0]
            testcase_detail += "," + row_testcase[1]
            testcase_detail += "," + row_testcase[2]
            testcase_detail += "," + row_testcase[3]
            print testcase_detail
        else:
            # Then execute each.
            cmd_clicast = [os.environ["VECTORCAST_DIR"] + "\CLICAST"]
            cmd_clicast += ["-e" + row_testcase[0]]
            cmd_clicast += ["-u" + row_testcase[1]]
            cmd_clicast += ["-s" + row_testcase[2]]
            cmd_clicast += ["-t" + row_testcase[3]]
            cmd_clicast += ["Execute"]
            cmd_clicast += ["Run"]
            call(cmd_clicast)

    print "-----------------"
    if dry_run:
      print ("{} testcases will be run "
            "due to updated Requirements.".format(count_testcases,))
    else:
      print ("{} testcases were run "
            "due to updated Requirements.".format(count_testcases,))

def main(argv):
    # Parse arguments.
    parser = argparse.ArgumentParser(description=(
        "RGW CBT + Metrics demo script."))
    parser.add_argument(
        "--dry_run", "-d",
        help="CBT to be a dry run.",
        action="store_true")
    parser.add_argument(
        "operation",
        metavar="OPERATION",
        help="Specify the script operation.",
        choices = ["report","cbt"])
    parser.add_argument(
        "file_name",
        metavar="FILENAME",
        help="Specify the RGW Repository database file to operate on.")
    opts = parser.parse_args(sys.argv[1:])
    
    # Perform the specified operation.
    if opts.operation == "report":
        # report_coverage(opts.file_name)
        # report_status(opts.file_name)
        # report( opts.file_name )
        # report_2( opts.file_name )
        # delete_requirement( opts.file_name, "FR11" )
        # delete_testcase( opts.file_name, 10 )
    elif opts.operation == "cbt":
        rgw_cbt(opts.file_name, opts.dry_run)

    print "Done."

if __name__ == "__main__":
    main(sys.argv)

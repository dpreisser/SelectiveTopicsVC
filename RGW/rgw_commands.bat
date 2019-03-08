
setlocal

set subsystemName=Codebeamer
set envName=RGW_TESTS_CLICAST

REM call :create_subsystem

REM call :setup_connect
REM call :setup_import
REM call :setup_export
REM call :setup_exportAdvanced
REM call :report_setup

REM call :import
REM call :report_requirements

REM call :link_test_cases
REM call :report_test_cases
REM call :mark_as_reviewed
REM call :run_test_cases

REM call :export

endlocal

goto :eof

REM Outdated
REM %VECTORCAST_DIR%\clicast RGW Configure Set repo_setup mode sqlite

:create_subsystem
%VECTORCAST_DIR%\clicast RGW Configure Create_subsystem %subsystemName% codebeamer_gateway
exit /b 0

:setup_connect
%VECTORCAST_DIR%\clicast RGW Configure Interactive_setup %subsystemName% connect
exit /b 0

:setup_import
%VECTORCAST_DIR%\clicast RGW Configure Interactive_setup %subsystemName% import
exit /b 0

:setup_export
%VECTORCAST_DIR%\clicast RGW Configure Interactive_setup %subsystemName% export
exit /b 0

:setup_exportAdvanced
%VECTORCAST_DIR%\clicast RGW Configure Interactive_setup %subsystemName% exportAdvanced
exit /b 0

:report_setup
%VECTORCAST_DIR%\clicast RGW Configure Report
%VECTORCAST_DIR%\clicast RGW Configure Report %subsystemName%

exit /b 0


:import
%VECTORCAST_DIR%\clicast RGW Import %subsystemName%
exit /b 0


:report_requirements
%VECTORCAST_DIR%\clicast RGW Requirement Report All
%VECTORCAST_DIR%\clicast RGW Requirement Report Pending
%VECTORCAST_DIR%\clicast RGW Requirement Report Changed 2017-05-24_00:00:00 2017-05-24_23:00:00

exit /b 0


:link_test_cases
%VECTORCAST_DIR%\clicast -lc -e %envName% -s "<<COMPOUND>>" -t "Order&Clear" RGW Testcase Link /item/1942
%VECTORCAST_DIR%\clicast -lc -e %envName% -s "<<COMPOUND>>" -t "Order&Clear" RGW Testcase Link /item/1708
%VECTORCAST_DIR%\clicast -lc -e %envName% -s "<<COMPOUND>>" -t "Order&Clear" RGW Testcase Link /item/1710
%VECTORCAST_DIR%\clicast -lc -e %envName% -s "<<COMPOUND>>" -t "Order&Clear" RGW Testcase Link /item/1711

%VECTORCAST_DIR%\clicast -lc -e %envName% -s "<<COMPOUND>>" -t "Order&Clear" RGW Testcase Link /item/1033
%VECTORCAST_DIR%\clicast -lc -e %envName% -s "<<COMPOUND>>" -t "Order&Clear" RGW Testcase Link /item/1034
%VECTORCAST_DIR%\clicast -lc -e %envName% -s "<<COMPOUND>>" -t "Order&Clear" RGW Testcase Link /item/1035
%VECTORCAST_DIR%\clicast -lc -e %envName% -s "<<COMPOUND>>" -t "Order&Clear" RGW Testcase Link /item/1037
%VECTORCAST_DIR%\clicast -lc -e %envName% -s "<<COMPOUND>>" -t "Order&Clear" RGW Testcase Link /item/1038
%VECTORCAST_DIR%\clicast -lc -e %envName% -s "<<COMPOUND>>" -t "Order&Clear" RGW Testcase Link /item/1039

%VECTORCAST_DIR%\clicast -lc -e %envName% -u manager -s Place_Order -t Chicken RGW Testcase Link /item/1938
%VECTORCAST_DIR%\clicast -lc -e %envName% -u manager -s Place_Order -t Chicken RGW Testcase Link /item/1033
%VECTORCAST_DIR%\clicast -lc -e %envName% -u manager -s Place_Order -t Chicken RGW Testcase Link /item/1034
%VECTORCAST_DIR%\clicast -lc -e %envName% -u manager -s Place_Order -t Chicken RGW Testcase Link /item/1035
%VECTORCAST_DIR%\clicast -lc -e %envName% -u manager -s Place_Order -t Chicken RGW Testcase Link /item/1036

exit /b 0


:report_test_cases
%VECTORCAST_DIR%\clicast -lc -e %envName% -s "<<COMPOUND>>" -t "Order&Clear" RGW Testcase Report
%VECTORCAST_DIR%\clicast -lc -e %envName% -u manager -s Place_Order -t Chicken RGW Testcase Report

exit /b 0


:mark_as_reviewed
%VECTORCAST_DIR%\clicast -lc -e %envName% -s "<<COMPOUND>>" -t "Order&Clear" RGW Testcase mark_as_reviewed
%VECTORCAST_DIR%\clicast -lc -e %envName% -u manager -s Place_Order -t Chicken RGW Testcase mark_as_reviewed

exit /b 0


:run_test_cases
%VECTORCAST_DIR%\clicast -lc -e %envName% -s "<<COMPOUND>>" -t "Order&Clear" Execute Run
%VECTORCAST_DIR%\clicast -lc -e %envName% -u manager -s Place_Order -t Chicken Execute Run

exit /b 0


:export
%VECTORCAST_DIR%\clicast RGW Export %subsystemName%
exit /b 0

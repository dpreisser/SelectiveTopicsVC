
setlocal

del *.o
del *.exe

set std=
rem set std=-std=c99

if "%1" == "1" (
set INLINE1=inline
set INLINE2=inline
set INLINE3=inline
call :combo_1
goto :eof )

if "%1" == "2" (
set INLINE1=inline
set INLINE2=inline
set INLINE3=extern inline
call :combo_2
goto :eof )

endlocal

goto :eof

:combo_1

rem combo 1 for inline without warnings

gcc -c -o myMax.o myMax.c

gcc -DINLINE="%INLINE1%" -DDECLARATION -DDEFINITION %std% -c -o useMyMax.o useMyMax.c
gcc -DINLINE="%INLINE2%" -DDECLARATION -DDEFINITION %std% -c -o otherUse.o otherUse.c

gcc -DINLINE="%INLINE3%" -DDECLARATION -DDEFINITION %std% -c -o myMain.o myMain.c

gcc -o myMain.exe myMain.o useMyMax.o otherUse.o myMax.o

exit /b 0

:combo_2

rem combo 2 for no inline and inline as well as extern inline with warnings

gcc -DINLINE="%INLINE1%" -DDECLARATION -DDEFINITION %std% -c -o useMyMax.o useMyMax.c
gcc -DINLINE="%INLINE2%" -DDECLARATION -DDEFINITION %std% -c -o otherUse.o otherUse.c

gcc -DINLINE="%INLINE3%" -DDECLARATION -DDEFINITION %std% -c -o myMain.o myMain.c

gcc -o myMain.exe myMain.o useMyMax.o otherUse.o

exit /b 0

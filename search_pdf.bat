@echo off

mkdir all

REM Collect PDF file paths and save them to pdf_files.txt
for %%d in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    dir /s /b /a-d %%d:\*.pdf >> all\pdf_files.txt
)

REM Set the source file name and the prefix for the output parts
set "sourceFile=all\pdf_files.txt"
set "outputPrefix=pdf_part"

REM Count the lines in the source file
for /f %%A in ('type "%sourceFile%" ^| find /c /v ""') do set "totalLines=%%A"

REM Calculate the number of lines per part
set /a "linesPerPart=%totalLines% / 8"

REM Split the file into 8 equal parts
setlocal enabledelayedexpansion
set "partNum=1"
set "lineNum=0"
for /f "usebackq delims=" %%A in ("%sourceFile%") do (
    set /a "lineNum+=1"
    echo %%A>>"all\%outputPrefix%_!partNum!.txt"
    if !lineNum! geq !linesPerPart! (
        set /a "partNum+=1"
        set "lineNum=0"
    )
)
endlocal

echo File split into 8 equal parts.

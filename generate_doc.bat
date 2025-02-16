@echo off

REM Run the Sphinx build command using Python's -m flag
python -m sphinx -b html source/ build/

REM Check if the build was successful
if errorlevel 0 (
    echo Documentation build completed successfully.
) else (
    echo Documentation build failed. Check the output for errors.
    exit /b 1
)
@echo off
setlocal EnableExtensions EnableDelayedExpansion

title Expense Tracking App - Test Runner
color 0A
cls

if /I "%~1"=="--no-pause" set "NO_PAUSE=1"

echo ==================================================
echo   EXPENSE TRACKING APP - TEST RUNNER
echo ==================================================
echo.

set "ROOT=%~dp0"
set "PYTHON=%ROOT%\.venv\Scripts\python.exe"
set "BACKEND_TESTS=%ROOT%backend\tests"
set "FRONTEND_DIR=%ROOT%frontend"
set "REPORT_DIR=%BACKEND_TESTS%\reports"

if not exist "%PYTHON%" (
  color 0C
  echo [ERROR] Python virtual environment not found.
  echo         Expected: %PYTHON%
  echo.
  echo Create the venv first, then run this file again.
  goto :end
)

if not exist "%REPORT_DIR%" mkdir "%REPORT_DIR%" >nul 2>&1

echo [1/4] Checking backend test tools...
"%PYTHON%" -m pip show pytest >nul 2>&1
if errorlevel 1 (
  echo       Installing backend test dependencies...
  "%PYTHON%" -m pip install pytest pytest-cov pytest-html
)
echo       Backend test tools ready.
echo.

echo [2/4] Running BACKEND tests...
echo --------------------------------------------------
"%PYTHON%" -m pytest backend\tests\ -v --html="%REPORT_DIR%\backend-report.html" --self-contained-html --cov=backend --cov-report=html:"%REPORT_DIR%\coverage"
if errorlevel 1 (
  color 0C
  echo.
  echo [FAILED] Backend tests failed.
  goto :end
)
echo [PASSED] Backend tests completed successfully.
echo         HTML report: %REPORT_DIR%\backend-report.html
echo         Coverage:    %REPORT_DIR%\coverage\index.html
echo.

echo [3/4] Running FRONTEND tests...
echo --------------------------------------------------
cd /d "%FRONTEND_DIR%"
if exist "node_modules\.bin\vitest.cmd" (
  npx vitest run --reporter verbose
) else (
  npm install
  npx vitest run --reporter verbose
)
if errorlevel 1 (
  color 0C
  echo.
  echo [FAILED] Frontend tests failed.
  goto :end
)
echo [PASSED] Frontend tests completed successfully.
echo.

echo [4/4] Summary
echo ==================================================
color 0A
echo BACKEND : PASS
echo FRONTEND: PASS
echo.
echo All tests ran successfully.
echo.
echo Reports are saved in:
echo   %REPORT_DIR%
echo.

:end
if not defined NO_PAUSE (
  echo Press any key to close...
  pause >nul
)
endlocal

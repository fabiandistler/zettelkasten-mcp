@echo off
REM Start script for Zettelkasten MCP HTTP Server (Windows)

echo Starting Zettelkasten MCP HTTP Server...
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found!
    echo Please run: uv venv ^&^& uv sync
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo .env file not found, creating from .env.example
    copy .env.example .env
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Create data directories if they don't exist
echo Ensuring data directories exist...
if not exist "data\notes" mkdir data\notes
if not exist "data\db" mkdir data\db

REM Start the server
echo Starting HTTP server...
echo.
echo Server will be available at: http://127.0.0.1:8080
echo Press Ctrl+C to stop the server
echo.

python -m zettelkasten_mcp.http_server

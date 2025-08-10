@echo off
setlocal
cd /d %~dp0..

rem Ensure npm uses the public registry
call npm.cmd config set registry https://registry.npmjs.org/

rem Start backend (port 3000)
start "backend" cmd /c "cd backend && npm.cmd install --no-fund --no-audit && node server.js"

rem Give backend a moment
timeout /t 3 >nul

rem Start frontend (port 3001)
start "frontend" cmd /c "cd frontend && npm.cmd install --no-fund --no-audit && npm.cmd run dev"

rem Open browser
timeout /t 5 >nul
start "" http://localhost:3001

endlocal

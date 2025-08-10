@echo off
echo Setting up Git repository and pushing to GitHub...

REM Check if git is installed
git --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Git is not installed. Please install Git and try again.
    exit /b 1
)

REM Get GitHub username and repository name
set /p GITHUB_USERNAME=Enter your GitHub username: 
set /p REPO_NAME=Enter your repository name: 

REM Initialize Git repository if not already initialized
if not exist .git (
    echo Initializing Git repository...
    git init
) else (
    echo Git repository already initialized.
)

REM Add all files to Git
echo Adding files to Git...
git add .

REM Commit changes
set /p COMMIT_MESSAGE=Enter commit message (default: Initial commit): 
if "%COMMIT_MESSAGE%"=="" set COMMIT_MESSAGE=Initial commit
git commit -m "%COMMIT_MESSAGE%"

REM Set main branch
git branch -M main

REM Add remote origin
echo Adding remote origin...
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

REM Push to GitHub
echo Pushing to GitHub...
git push -u origin main

echo Done! Your code has been pushed to GitHub.
echo You can now deploy it to Render following the instructions in README_DEPLOYMENT.md

pause
@echo off
set /p MESSAGE=Enter content commit: 

echo Adding files...
git add .

echo Create commit with content: %MESSAGE%
git commit -m "%MESSAGE%"

echo Push to GitHub...
git push origin main

pause

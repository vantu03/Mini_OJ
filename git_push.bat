@echo off
set /p MESSAGE=Nhập nội dung commit: 

echo Đang thêm file...
git add .

echo Tạo commit với nội dung: %MESSAGE%
git commit -m "%MESSAGE%"

echo Push lên GitHub...
git push origin main

pause

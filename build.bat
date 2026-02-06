@echo off
echo Starting compilation...
pyinstaller --noconfirm --onefile --windowed ^
    --name "1024ImageCrawler" ^
    --icon "logo.ico" ^
    --add-data "logo.png;." ^
    --add-data "logo.ico;." ^
    --hidden-import "PyQt6" ^
    --hidden-import "requests" ^
    --hidden-import "bs4" ^
    main.py
echo Compilation finished.
exit

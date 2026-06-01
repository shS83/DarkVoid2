@echo off

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del *.spec 2>nul

uv run python -m PyInstaller ^
	--clean ^
	--onedir ^
	--name DarkVoid2 ^
	--add-data "assets;assets" ^
	--add-data "highscores.json;highscores.json" ^
	main.py

#!/bin/bash
rm -rf *.spec dist build
python -m PyInstaller --clean --onedir --name DarkVoid2 --add-data "highscores.json:highscores.json" --add-data "assets:assets" main.py

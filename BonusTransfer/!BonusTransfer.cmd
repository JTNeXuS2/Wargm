@echo off
title "Wargm.BonusTranfer"

:start
BonusTransfer.py
timeout /t 3
goto start
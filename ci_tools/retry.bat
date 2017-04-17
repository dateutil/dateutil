@echo off
REM This script takes a command and retries it a few times if it fails, with a
REM timeout between each retry.

setlocal EnableDelayedExpansion

REM Loop at most n_retries times, waiting sleep_time times between
set sleep_time=60
set n_retries=5

for /l %%x in (1, 1, %n_retries%) do (
  call %*
  if not ERRORLEVEL 1 EXIT /B 0
  timeout /t %sleep_time% /nobreak > nul
)

REM If it failed all n_retries times, we can give up at last.
EXIT /B 1

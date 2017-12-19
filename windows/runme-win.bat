@ECHO off

cd /d %~dp0

IF EXIST C:\\ProgramData\chocolatey\choco.exe ECHO Choco requirement met! && GOTO :smrtmon 
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

:smrtmon
IF EXIST "C:\\Program Files\smartmontools\bin\smartctl.exe" ECHO Smartmontools requirement met! && GOTO :python
choco install smartmontools
set PATH=%PATH%;C:\Program Files\smartmontools\bin\
set PATH=%PATH%;C:\Program Files\smartmontools\bin\smartctl.exe

:python
IF EXIST C:\\Python27\python.exe ECHO Python requirement met! && GOTO :pysmart
choco install python2
set PATH=%PATH%; C:\Python27
set PATH=%PATH%; C:\Python27\scripts


:pysmart
IF EXIST "C:\\Python27\Lib\site-packages\pySMART.smartx-0.3.7-py2.7.egg" ECHO pySMART requirement met! && GOTO :pip
cd ../lib/pySMART-master
python setup.py install

:pip
pip install postgres
pip install mysql-connector==2.1.4
pip install update mysql-connector

mkdir C:\\dbtshddtool\ 
mkdir C:\\dbtshddtool\lib

copy runhddtool.bat C:\\dbtshddtool\
cd ../src/
copy dbts-auto.py C:\\dbtshddtool\
cd ../lib/
copy dbts.config C:\\dbtshddtool\lib

schtasks /create /tn "DBTS-Auto" /tr "C:\\dbtshddtool\runhddtool.bat" /sc HOURLY /ru System

PAUSE
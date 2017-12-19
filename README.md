# Drivebase Toolset

Features List:
  - Automatic (*Hourly*) Tool, to check drive health and log it in a database.
  - Manual Diagnostics Console Tool, to quickly poll all the drives in the system and run tests on the drive of your choice.
  - Main SQL support.
  - Postgres support coming soon.
  - Generic config file
  - All 3 major platform support.

Notes:

-- Windows --
  Most of the install is automated for except the hourly tool. To get that to run on a schedule you have to set it up through Windows Task Scheduler. This is currently the development platform.
  
-- OSX --
  This is the platform that the tool is least tested on. Haven't got the hourly automatic tool to work properly with Launchd yet. The automated tool is still a work in progress.
  
-- Linux --
  The automated install will work on systems with apt and yum currently. The script also sets up a cron job to run hourly. This has been another system that was extensively tested.
  
-- Config --
  The config must be set up to run both manual and auto tools. For the automatic mode, all fields in the config must be set. If you wish to use the database functionality in the manual tool, the databse fields must be set in the config. 

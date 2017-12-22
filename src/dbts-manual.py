"""

AUTHOR: Tyler Angelo

This is meant to be a tool to quickly asses all storage devices on a machine. It's built with the pySMART API. Requires
smartmontools as well.

"""
import time
from sys import stdin

from mysql import connector
from pySMART import DeviceList
import platform
import socket
import psycopg2


# import keyboard as kb
# from pySMART import Device

def init():
    global textMods

    class textMods:
        CEND = '\033[0m'
        CBOLD = '\033[1m'
        CITALIC = '\033[3m'
        CURL = '\033[4m'
        CBLINK = '\033[5m'
        CBLINK2 = '\033[6m'
        CSELECTED = '\033[7m'

        CBLACK = '\033[30m'
        CRED = '\033[31m'
        CGREEN = '\033[32m'
        CYELLOW = '\033[33m'
        CBLUE = '\033[34m'
        CVIOLET = '\033[35m'
        CBEIGE = '\033[36m'
        CWHITE = '\033[37m'

        CBLACKBG = '\033[40m'
        CREDBG = '\033[41m'
        CGREENBG = '\033[42m'
        CYELLOWBG = '\033[43m'
        CBLUEBG = '\033[44m'
        CVIOLETBG = '\033[45m'
        CBEIGEBG = '\033[46m'
        CWHITEBG = '\033[47m'

        CGREY = '\033[90m'
        CRED2 = '\033[91m'
        CGREEN2 = '\033[92m'
        CYELLOW2 = '\033[93m'
        CBLUE2 = '\033[94m'
        CVIOLET2 = '\033[95m'
        CBEIGE2 = '\033[96m'
        CWHITE2 = '\033[97m'

        CGREYBG = '\033[100m'
        CREDBG2 = '\033[101m'
        CGREENBG2 = '\033[102m'
        CYELLOWBG2 = '\033[103m'
        CBLUEBG2 = '\033[104m'
        CVIOLETBG2 = '\033[105m'
        CBEIGEBG2 = '\033[106m'
        CWHITEBG2 = '\033[107m'

    global commandInfo
    commandInfo = {"assessment": "SMART health self-assessment as reported by the device.",
                   "all_attributes": "Prints the entire SMART attribute table",
                   "capacity": "Device's user capacity.",
                   "diags": "Contains parsed and processed diagnostic information extracted from the SMART information. Currently only populated for SAS and SCSI devices, since ATA/SATA SMART attributes are manufacturer proprietary.",
                   "firmware": "Device's firmware version.",
                   "interface": "Device's interface type (ATA, SATA, SCSI, SAS, SAT, CSMI)",
                   "is_ssd": "True if this device is a Solid State Drive. False otherwise.",
                   "messages": "Contains any SMART warnings or other error messages reported by the device",
                   "model": "Device's model number.",
                   "name": "Device's hardware ID, without the '/dev/' prefix.",
                   "serial": "Device's serial number.",
                   "supports_smart": "True if the device supports SMART (or SCSI equivalent) and has the feature set enabled. ",
                   "all_selftests": "Prints the entire SMART self-test log",
                   "get_selftest_result": "Refreshes a device's tests attribute to obtain the latest test results.",
                   "run_selftest": "Instructs a device to begin a SMART self-test. All tests are run in 'offline' / 'background' mode, allowing normal use of the device while it is being tested.",
                   "update": "Queries for device information using smartctl and updates all class members, including the SMART attribute table and self-test log.",
                   "refresh_list": "Refreshes and updates the drive list.",
                   "print_list": "Reprints drive list.",
                   "quit": "Quits the program.",
                   "short": "Brief elecrto-mechanical functionality check. Generally takes 2 minutes or less.",
                   "long": "Thorough electro-mechanical functionality check, including complete recording media scan. Generally takes several hours.",
                   "conveyance": "Brief test used to identify damage incurred in shipping. Generally takes 5 minutes or less. This test is not supported by SAS or SCSI devices.",
                   "help": "Prints the command list",
                   "db_records": "Prints all entries from the database of a given drive",
                   }


def printDrives():
    print '\nHere\'s your drive list:\n'
    print '{:<5} {:<8} {:<10}      {:<12} {:<15}'.format('ID', 'SMART?', 'PATH', 'INTERFACE', "MODEL")
    print '----------------------------------------------------------------------'
    for i in range(0, len(driveList.devices)):
        dev = driveList.devices[i]
        print '{:<5} {:<8} /dev/{:<10} {:<12} {:<15}'.format(i, dev.supports_smart, dev.name,
                                                             dev.interface.upper(), dev.model)


def collectDrives():
    print("Loading devices....")
    print("This might take a while.")

    global driveList
    driveList = DeviceList()
    printDrives()


def connectToDB():
    try:
        # conn = psycopg2.connect("dbname='' user='' host='' password=''")
        conn = connector.connect(user=_db_user, password=_db_password, host=_db_host,
                                 database=_db_name)
    except:
        print 'Cannot Connect to Database'
        menu()

    # Get the Hostname
    hostname = socket.gethostname().replace('-', '_')

    # Open Cursor Connection with DB
    cur = conn.cursor()

    return [hostname, cur, conn]


def executeCmd(cmd, driveId):
    dev = driveList.devices[driveId]
    print 'Command Output:'

    if cmd == 'model':
        print dev.model
        menu()
    elif cmd == 'name':
        print dev.name
        menu()
    elif cmd == 'firmware':
        print dev.firmware
        menu()
    elif cmd == 'interface':
        print dev.interface
        menu()
    elif cmd == 'supports_smart':
        print dev.supports_smart
        menu()

    if not dev.supports_smart:
        print textMods.CRED + 'This command requires SMART' + textMods.CEND
        print textMods.CRED + 'This drive unfortunately does not support SMART Technologies.' + textMods.CEND
        print textMods.CRED + 'Please select a different drive...' + textMods.CEND
        printDrives()
        menu()
    else:
        if cmd == 'assessment':
            if dev.assessment == 'PASS':
                print textMods.CGREEN + dev.assessment + textMods.CEND
            elif dev.assessment == 'WARN':
                print textMods.CYELLOW2 + dev.assessment + textMods.CEND
            else:
                print textMods.CRED + dev.assessment + textMods.CEND

        elif cmd == 'all_attributes':
            print dev.all_attributes()
        elif cmd == 'db_records':
            connection = connectToDB()
            hostname = connection[0]
            cur = connection[1]
            conn = connection[2]

            try:
                cur.execute(
                    "SELECT * FROM %s WHERE  path = %%s" % hostname, [dev.name]
                )

                # Save all the entries for safe keeping
                record = cur.fetchall()
                i = 1
                for r in record:
                    print "Entry %d:" % i,
                    print r[0],
                    print r[1],
                    print r[2],
                    print r[3],
                    print r[4]
                    i += 1
            except:
                print 'No records for this hostname exist.'


            cur.close()
            conn.close()
        elif cmd == 'capacity':
            print dev.capacity
        elif cmd == 'diags':
            print dev.diags
        elif cmd == 'is_ssd':
            print dev.is_ssd
        elif cmd == 'messages':
            for s in dev.messages:
                print s
        elif cmd == 'serial':
            print dev.serial
        elif cmd == 'all_selftests':
            print dev.all_selftests()
        elif cmd == 'run_selftest':

            print textMods.CRED + 'WARNING: You can only run a limited amount of selftests (around 21).' + textMods.CEND
            print textMods.CRED + 'Only run this test if you need to!' + textMods.CEND

            goodInput = False
            while not goodInput:
                cont = raw_input('\nWould you like to continue? (y or n): ')
                if cont.lower() == 'y':
                    goodInput = True
                    continue
                elif cont.lower() == 'n':
                    goodInput = True
                    menu()
                else:
                    goodInput = False

            print

            goodInput = False
            while not goodInput:
                print 'Test Types: short, long, conveyance'
                print '\nAdd \'?\' to the end of any test to find out what it does!'

                testType = raw_input('What kind of test would you like to run?: ')
                testTypeLen = len(testType)
                if '?' in testType and commandInfo.has_key(testType[0:testTypeLen - 1]):  # -1 to correct for the ?
                    print '\n' + testType[0:testTypeLen - 1] + ': ' + commandInfo.get(testType[0:testTypeLen - 1])
                    goodInput = False
                elif not commandInfo.has_key(testType[0:testTypeLen]):
                    print '\nInvalid Test Type. Try again.'
                    goodInput = False
                elif commandInfo.has_key(testType[0:testTypeLen]):
                    goodInput = True
                    print
                    if testType == 'long':
                        print 'The long test can take up to 2 hours to complete'
                        print 'Check all_selftests around the ETA for test results.\n'

                    test = dev.run_selftest(str(testType))
                    print test[1]
                    if test[2] is not None:
                        print 'ETA: ' + test[2]
                    else:
                        print 'ETA: N/A'
                        return

                    if cont is not None and testType == 'long':
                        menu()

                    print '\nWaiting for result . . .',

                    rslt = None
                    timeout = 0
                    while True:  # Do-while

                        if not dev.is_ssd:
                            time.sleep(10)  # Accounts for SUUUUUPER slow drives
                            timeout += 10
                        else:
                            time.sleep(2)  # SSDs dont need 10 seconds though
                            timeout += 2

                        try:
                            rslt = dev.get_selftest_result(str)
                        except:
                            # If we cant get results, attempt to restart the test

                            if timeout < 150:  # Only reattempt the test if not close to timeout
                                dev.run_selftest(str(testType))  # This avoids doing a double test
                                # The user will be unaware

                        # If the result returns a success
                        if (rslt is not None and (rslt[0] is 0)) or ((timeout >= 180) and (testType == 'short')):

                            if timeout >= 180:
                                print '\nWaiting for results timed out.'
                                print 'Check all_selftests for test results.'
                                menu()
                            break
                        print('.'),

                    print '\n\nID Test_Description Status                        Left Hours  1st_Error@LBA'
                    print rslt[1]

        elif cmd == 'update':
            print dev.update()

        menu()


def printCmds():
    print '\nHere\'s a list of commands: \nassessment, all_selftests, run_selftest,'
    print 'all_attributes, capacity, diags, firmware, interface,'
    print 'is_ssd, messages, model, name, serial, supports_smart,'
    print 'db_records, print_list, refresh_list, update, help, quit'
    print '\nAdd \'?\' to the end of any command to find out what it does!'

    print '\nUSAGE: [command][?] [drive_id]'


def menu():
    print
    cmdInput = raw_input('> ')

    # TODO: Get last command

    # if kb.is_pressed(key='up'):
    # sys.stdin = StringIO.StringIO('assessment 1')
    # Splits the input into command and target device
    cmdSplit = cmdInput.split(' ')
    cmd = cmdSplit[0].lower()
    targetDev = None
    if len(cmdSplit) > 1 and cmdSplit[1].isdigit():
        targetDev = int(cmdSplit[1])
    else:
        targetDev = ''

    # print cmdSplit[1]

    driveListLen = len(driveList.devices)
    cmdLength = len(cmd)

    # prints drive list
    if cmd == 'print_list':
        printDrives()
    elif cmd == 'refresh_list':
        collectDrives()
    elif cmd == 'quit':
        print '\nThanks for using The Drivebase Toolset!'
        exit()
    elif cmd == 'help':
        printCmds()
    # Handles an inquiry about a command
    elif '?' in cmd and commandInfo.has_key(cmd[0:cmdLength - 1]):  # -1 to correct for the ?
        print '\n' + cmd[0:cmdLength - 1] + ': ' + commandInfo.get(cmd[0:cmdLength - 1])
    elif not commandInfo.has_key(cmd[0:cmdLength]):
        print '\nInvalid command. See list for all available commands.'
        print 'USAGE: [command][?] [drive_id]'
    # Handles ID out of range
    elif targetDev is not None and (targetDev >= driveListLen or targetDev < 0):
        print '\nThat ID is out of range.'
    # elif not targetDev.isdigit():
    #    print '\nInvalid ID'
    #    print 'USAGE: [command] [drive_id]'
    # Success case
    elif commandInfo.has_key(cmd[0:cmdLength]) and targetDev is not None:
        executeCmd(cmd, targetDev)
    # Error cases
    elif not commandInfo.has_key(cmd[0:cmdLength]) and targetDev is None:
        print '\nInvalid command. See list for all available commands.'
        print 'No drive ID was found.'
        print 'USAGE: [command][?] [drive_id]'
    elif targetDev is None:
        print '\nNo drive ID was found.'
        print 'USAGE: [command][?] [drive_id]'

    menu()


if __name__ == '__main__':
    print("\nWelcome to The Drivebase Toolset!\n")

    if platform.system() == 'Windows' or platform.system() == 'Darwin' or platform.system() == 'Linux' or platform.system() == 'Linux2':

        config = open('lib/dbts.config', 'r')

        varTemp = []
        for l in config:
            varTemp.append(l.split('=')[1])

        _db_user = str(varTemp[5].replace('\n', ''))
        _db_password = str(varTemp[6].replace('\n', ''))
        _db_host = str(varTemp[7].replace('\n', ''))
        _db_name = str(varTemp[8].replace('\n', ''))

        config.close()

        init()
        collectDrives()
        printCmds()
        menu()
    else:
        print 'Sorry this platform isn\'t supported yet.'

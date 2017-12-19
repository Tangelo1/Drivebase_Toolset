"""

AUTHOR: Tyler Angelo

This is meant to be a tool to quickly asses all storage devices on a machine then store it in a database.
It's built with the pySMART API.

"""

import re
from mysql import connector
from pySMART import DeviceList
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import socket
import smtplib


# import psycopg2

# TODO: Refine the triggers a bit
# TODO: Set a threshold for each stat to email
# 5 > 4
# 187 > 0
# 188 > 13
# 197 > 0
# 198 > 0
# TODO: Delete old db records

def emailRecord(report, assessment=""):
    print 'Sending email...'

    msg = MIMEMultipart()
    msg['From'] = _from_address
    msg['To'] = ", ".join(_recipients)
    msg['Subject'] = "Drivebase Alert for " + _hostname + "!"

    if assessment is "SWAP":
        body = "One or more drives have been swapped since the last run!\n" \
               "\tHere is the report:\n\t\t " + str(report)

        for r in report:
            body += "\n\t\t" + assessment + ": " + str(r)
    elif assessment is "CONN":
        body = report
    else:
        body = "Some critical S.M.A.R.T. attributes have changed for one or more disk(s)!\n" \
               "\tHere is the report:\n"

        for r in report:
            body += "\n\t\t" + str(r)

    msg.attach(MIMEText(body, 'plain'))

    text = msg.as_string()

    server = smtplib.SMTP(_smtp_server, _smtp_port)
    server.starttls()
    server.login(_from_address, _from_password)
    server.sendmail(_from_address, _recipients, text)
    server.quit()


def setupReport(name, oldVals, newVals):
    return str(name + ":\n\t\t\t" + oldVals[0] + " " + oldVals[1] + ": " + oldVals[2] + " --> " + newVals[2])


def createReport(timeStamp, dev, currentAtts):
    print 'Creating report...'

    cur.execute(
        "SELECT * FROM %s WHERE path = %%s ORDER BY date DESC LIMIT 1" % _hostname, [dev.name]
    )

    lastEntry = cur.fetchall()

    # Given there's a last entry and the serial is not the same as the last
    if lastEntry and not lastEntry[0][1] == dev.serial and 'SWAP' not in lastEntry[0][1]:
        # Email a SWAP record
        emailRecord(report=str(dev.name.upper() + ": " + lastEntry[0][1] + " --> " + dev.serial), assessment="SWAP")
        # Insert a visual indication in the db that the drive has been swapped
        cur.execute(
            "INSERT INTO %s VALUES (%%s, %%s, %%s, %%s, %%s, %%s)" % _hostname,
            [timeStamp, '***** DRIVE SWAP *****', dev.name, None, None, None]
        )

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 1.5 hours to account for any fails and restarts off by one etc.
    lastHour = (datetime.now() - timedelta(hours=1.5)).strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(
        "SELECT * FROM %s WHERE date < %%s AND date >= %%s AND sn = %%s" % _hostname, [now, lastHour, dev.serial]
    )

    # Save all the entries for safe keeping
    record = cur.fetchall()


    if record:  # if not empty
        assessAppended = False
        # record [X][0] is timestamp
        # record [X][1] is serial
        # record [X][2] is path
        # record [X][3] is ssd boolean
        # record [X][4] is PASS, FAIL, WARN
        # record [X][5][0-6] are all the attributes
        max = len(record) - 1
        i = 0  # To iterate through the new attribute array

        # postgres
        # stats = record[max][5] # The oldest entry

        # mysql
        dbAtts = re.findall(r"'(.*?)'", record[max][5])  # The oldest entry.
        # RE needed because mySQL doesn't have array types

        for a in dbAtts:

            # Split looks like this vvv
            # [id, name, raw, when_failed]
            attSplitNew = currentAtts[i].split(' ')
            attSplitOld = dbAtts[i].split(' ')

            # Raw value of the current stat
            rawNew = int(attSplitNew[2])
            # Raw value of the old stat
            rawOld = int(attSplitOld[2])

            isFailing = attSplitNew[3]

            # THIS IS THE MAIN TRIGGER TO SEND AN EMAIL
            # filtering out temp warnings and bytes written
            if rawNew > rawOld and int(attSplitNew[0]) is not 241 and int(attSplitNew[0]) is not 194:
                report.append("[" + timeStamp + "] " + setupReport(dev.name.upper(), attSplitOld, attSplitNew) + "\n")

            # If drive assessment fails trigger email with drives messages
            if not assessAppended and record[max][4] == 'WARN' or record[max][4] == 'FAIL':
                if len(dev.messages) is not 1 and "Airflow" not in dev.messages[0]:
                    report.append(dev.name + " has a " + record[max][4] + " message: \n\t\t\t" + str(dev.messages))
                    assessAppended = True

            i += 1

        # Won't actually email util it's the last drive
        if report and driveCount is numDrives - 1:
            emailRecord(report=report)
            print 'Record reported!'


if __name__ == '__main__':
    config = open('lib/dbts.config', 'r')

    varTemp = []
    for l in config:
        varTemp.append(l.split('=')[1])

    _recipients = varTemp[0].replace('\n', '').split(", ")
    _from_address = str(varTemp[1].replace('\n', ''))
    _from_password = str(varTemp[2].replace('\n', ''))
    _smtp_server = str(varTemp[3].replace('\n', ''))
    _smtp_port = int(varTemp[4].replace('\n', ''))
    _db_user = str(varTemp[5].replace('\n', ''))
    _db_password = str(varTemp[6].replace('\n', ''))
    _db_host = str(varTemp[7].replace('\n', ''))
    _db_name = str(varTemp[8].replace('\n', ''))

    config.close()

    # Get the Hostname
    _hostname = socket.gethostname().split('.')[0].replace('-', '_')

    try:
        # Postgres config
        # conn = psycopg2.connect("dbname='' user='' host='' password=''")

        conn = connector.connect(user=_db_user, password=_db_password, host=_db_host, database=_db_name)
        print 'Connection to the database Successful!'
    except:
        print 'Couldn\'t connect to the database'
        emailRecord(report="Couldn't connect to database!", assessment="CONN")
        exit()

    # Open Cursor Connection with DB
    cur = conn.cursor()

    # Create a table for this host name if one doesn't already exist
    # MySQL
    cur.execute(
        "CREATE TABLE IF NOT EXISTS %s (date TIMESTAMP, sn TEXT, path TEXT, ssd BOOLEAN, status TEXT, atts TEXT)" % _hostname)

    # Postgres
    # cur.execute(
    #    "CREATE TABLE IF NOT EXISTS %s (date TIMESTAMP, sn TEXT, path TEXT, ssd BOOLEAN, status TEXT, atts TEXT[])" % _hostname)


    # Populate Critical Stats List
    criticalStats = [5, 187, 188, 194, 196, 197, 241]
    print 'Polling drives...'
    driveList = DeviceList()
    numDrives = len(driveList.devices)
    driveCount = 0
    report = []

    # Now  to poll the drives and save information
    for i in range(0, numDrives):
        # Load Current Drive
        dev = driveList.devices[i]

        # Collect static information
        timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        name = dev.name
        sn = dev.serial
        ssd = dev.is_ssd
        status = dev.assessment
        atts = []

        # Collect critical attributes
        for a in dev.attributes:
            if a is not None and int(a.num) in criticalStats:
                temp = a.num + " " + \
                       a.name + " " + \
                       a.raw + " " + \
                       a.when_failed

                atts.append(temp)

        createReport(timeStamp, dev, atts)

        # Postgres
        # Drop Information in the database
        # cur.execute(
        #   "INSERT INTO %s VALUES (%%s, %%s, %%s, %%s, %%s, %%s);" % _hostname, [timeStamp, sn, name, ssd, status, atts])

        #mySQL
        cur.execute(
            "INSERT INTO %s VALUES (%%s, %%s, %%s, %%s, %%s, %%s);" % _hostname,
            [timeStamp, sn, name, ssd, status, str(atts)])

        print 'Drive %d attributes logged in database...' % i

        # Clear Temp variables
        atts = []
        temp = ""
        driveCount += 1

    cur.execute("COMMIT")
    cur.close()
    conn.close()
    print 'Committed all records!'

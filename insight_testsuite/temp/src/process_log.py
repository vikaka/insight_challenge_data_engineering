from collections import Counter
import pandas as pd
from operator import itemgetter
from datetime import datetime as dt
import datetime
import sys
from os.path import splitext
from urllib.parse import urlparse

FILE_PATH = sys.argv[1]

"""Feature 1"""

# Need only the Host address to count number of accesses, use subscription after split to get host address
HOSTS = [line.split(" ")[0] for line in open(FILE_PATH, encoding='latin')]

# top 10 most common hosts sort by Lexicographical order in case of clash
COMMON = sorted(Counter(HOSTS).items(), key=lambda pair: (-pair[1], pair[0]))

# write to file
TARGET_1 = open(sys.argv[2], 'w')
for i in range(0, min(10, len(COMMON))):
    TARGET_1.write(COMMON[i][0] + ',%d\n' % (COMMON[i][1]))
TARGET_1.close()

"""Feature 2"""
# Require Resource name and number of bytes per request, Resource name is column 7 and size in bytes is always the last value in the log line
RESOURCE_BYTES = [[line.split(" ")[6], line.split(" ")[len(line.split(" "))-1].rstrip()] for line in open(FILE_PATH, encoding='latin')]

if not RESOURCE_BYTES:
    TARGET_2 = open(sys.argv[4], 'w')
    TARGET_2.write('Error : No log lines given')
    TARGET_2.close()
else:
    RESOURCE_BYTES_PD = pd.DataFrame(RESOURCE_BYTES)
    # assuming - as 0
    RESOURCE_BYTES_PD.loc[RESOURCE_BYTES_PD[1] == '-'] = 0
    # convert bytes column to numeric
    RESOURCE_BYTES_PD[1] = pd.to_numeric(RESOURCE_BYTES_PD[1])
    # Group by Resource, sum bytes values this give us most used resource by frequency and total bytes transmitted
    # Assign index to column to sort by lexicographic order in case of clash
    RESOURCE_BYTES_GROUP = RESOURCE_BYTES_PD.groupby(0).sum()
    RESOURCE_BYTES_GROUP[0] = RESOURCE_BYTES_GROUP.index
    RESOURCE_BYTES_GROUP = RESOURCE_BYTES_GROUP.sort_values([1, 0], ascending=[False, True])

    # write to files
    TARGET_2 = open(sys.argv[4], 'w')
    for i in range(0, min(10, len(RESOURCE_BYTES_GROUP))):
        TARGET_2.write(RESOURCE_BYTES_GROUP.index.values[i] + '\n')
    TARGET_2.close()

"""Feature 3"""
# Require only time of request made for this feature, time of request is always within [], converting to datetime object using strptime
TIMES = [[dt.strptime(line.split('[', 1)[1].split(']')[0], '%d/%b/%Y:%H:%M:%S %z'), 1]for line in open(FILE_PATH, encoding="latin")]

if not TIMES:
    TARGET_3 = open(sys.argv[3], 'w')
    TARGET_3.write('Error : No log lines given')
    TARGET_3.close()
else:
    TIMES_PD = pd.DataFrame(TIMES)
    TIMES_PD = TIMES_PD.set_index([0])


    def time_interval(start, end, delta):
        """To generate 60 minute time intervals.

        :param start: start time of log input.
        :param end: end time of log input.
        :param delta: time increments.
        """
        if start == end:
            yield start
        else:
            curr = start
            while curr < end:
                yield curr
                curr += delta

    # For each 60 minute window get count of accesses
    WINDOW_GROUP = []
    for result in time_interval(min(TIMES)[0], max(TIMES)[0], datetime.timedelta(seconds=1)):
        WINDOW_GROUP.append([result, len(TIMES_PD[result:result+datetime.timedelta(minutes=60)])])

    # sort by descending
    WINDOW_GROUP.sort(key=itemgetter(1), reverse=True)
    # write to file
    TARGET_3 = open(sys.argv[3], 'w')
    for i in range(0, min(10, len(WINDOW_GROUP))):
        TARGET_3.write(WINDOW_GROUP[i][0].strftime('%d/%b/%Y:%H:%M:%S %z') + ',%d\n' % (WINDOW_GROUP[i][1]))

    TARGET_3.close()


"""Feature 4"""

# Create two list, Failed login to track failed login attempts, Blocked_list to track the blocked attempts after three failed login
FAILED_LOGIN = {}
BLOCKED_LIST = []
# TIme to reset Invalid login attempts in Seconds
BLOCK_SECONDS = 20
# Number of failed attempts allowed, within reset window
BLOCK_TRY = 3
# Number of minutes to block, in minutes
BLOCK_MINUTES = 5

for line in open(FILE_PATH, encoding="latin"):
    # get host, time of access and server response
    HOST = line.split(" ")[0]
    TIME = dt.strptime(line.split('[', 1)[1].split(']')[0], '%d/%b/%Y:%H:%M:%S %z')
    SERVER_RESPONSE = line.split(" ")[len(line.split(" "))-2]
    # check if host has been blocked, do not need to check response if blocked
    if HOST in FAILED_LOGIN and FAILED_LOGIN[HOST][0] == BLOCK_TRY and TIME < FAILED_LOGIN[HOST][1] + datetime.timedelta(minutes=BLOCK_MINUTES):
            BLOCKED_LIST.append(line)
    # If not blocked, check response.
    # If successful login, reset counter and failed login attempts
    elif SERVER_RESPONSE == '200':
        if HOST in FAILED_LOGIN:
            FAILED_LOGIN.pop(HOST)
    # If failed login, four scenarios possible
    elif SERVER_RESPONSE == '401':
        if HOST in FAILED_LOGIN:
            # if more than 20 seconds since last failed login reset timer
            if TIME > FAILED_LOGIN[HOST][1] + datetime.timedelta(seconds=BLOCK_SECONDS):
                FAILED_LOGIN[HOST] = (1, TIME)
            # if failed login has exceeded three attempts, reset to 1
            elif FAILED_LOGIN[HOST][0] >= 3:
                FAILED_LOGIN[HOST] = (1, TIME)
            # if failed login is within 20 seconds window and less than 3, increment
            else:
                FAILED_LOGIN[HOST] = (FAILED_LOGIN[HOST][0]+1, TIME)
        else:
            FAILED_LOGIN[HOST] = (1, TIME)

# write blocked attempts to file
TARGET_4 = open(sys.argv[5], 'w')

if not BLOCKED_LIST:
    TARGET_4.write('No Attempts were Blocked')
    TARGET_4.close()
else:
    for i in BLOCKED_LIST:
        TARGET_4.write(i)
    TARGET_4.close()

'''Feature 5'''
# Get file extension from the resource file already loaded in feature 2
if not RESOURCE_BYTES:
    TARGET_5 = open(sys.argv[6], 'w')
    TARGET_5.write('Error : No log lines given')
    TARGET_5.close()
else:
    # Split file extension from end of Requested resource
    FILE_EXTENSION = []
    for url in RESOURCE_BYTES:
        path = urlparse(url[0]).path
        ext = splitext(path)[1]
        FILE_EXTENSION.append(ext)

    # get most commonly used file extensions
    MOST_COMMON_EXTENSIONS = sorted(Counter(FILE_EXTENSION).items(), key=lambda pair: (-pair[1], pair[0]))

    # write to file
    TARGET_5 = open(sys.argv[6], 'w')
    for i in range(0, min(10, len(MOST_COMMON_EXTENSIONS))):
        TARGET_5.write(MOST_COMMON_EXTENSIONS[i][0] + ',%d\n' % (MOST_COMMON_EXTENSIONS[i][1]))
    TARGET_5.close()

'''Feature 6'''
# get timestamp and response of code, timestamp is always between [] and processed using strptime, response code is always the penultimate object
TIMES_RESPONSE = [[dt.strptime(line.split('[', 1)[1].split(']')[0], '%d/%b/%Y:%H:%M:%S %z'), line.split(" ")[len(line.split(" "))-2].rstrip()]for line in open(FILE_PATH, encoding="latin")]
# Convert to data frame, change first column to date. Group by date and response code
if not TIMES_RESPONSE:
    TARGET_6 = open(sys.argv[7], 'w')
    TARGET_6.write('Error : No log lines given')
    TARGET_6.close()
else:

    TIMES_RESPONSE_PD = pd.DataFrame(TIMES_RESPONSE)
    TIMES_RESPONSE_PD[0] = TIMES_RESPONSE_PD[0].dt.date
    TIMES_RESPONSE_PD[1] = pd.to_numeric(TIMES_RESPONSE_PD[1])
    TIMES_RESPONSE_PD = TIMES_RESPONSE_PD.groupby([0, 1]).size()
    # Transform Data frame to readable format to display error code as column headers
    TIMES_RESPONSE_PD = pd.DataFrame(TIMES_RESPONSE_PD)
    TIMES_RESPONSE_PD.reset_index(level=1, inplace=True)
    TIMES_RESPONSE_PD = TIMES_RESPONSE_PD.pivot(columns=1, values=0)
    TIMES_RESPONSE_PD = TIMES_RESPONSE_PD.fillna(0)

    TIMES_RESPONSE_PD.index.rename('Date', inplace=True)

    # write to file
    TIMES_RESPONSE_PD.to_csv(sys.argv[7], sep=' ', mode='w')

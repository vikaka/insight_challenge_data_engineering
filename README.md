# Table of Contents
1. [Packages Used](README.md#packages-used)
2. [Feature Descriptions](README.md#feature-descriptions)
3. [Assumptions](README.md#assumptions)
4. [Testing](README.md#testing)
5. [Directory Structure](README.md#repo-directory-structure)


## Packages Used

**Python** version : Python 3.5.1

* collections(python standard)
* pandas(external package) -- needs to be downloaded
* operator(python standard)
* datetime(python standard)
* sys(python standard)
* OS(python standard)
* urllib(python standard)

run.sh contains the run command  
python [python file] [log input path] [Feature 1 output] [Feature 3 output] [Feature 2 output] [Feature 4 output] [Feature 5 output] [Feature 6 output]

Running time for the given log input:

For log with 4,400,644 events

Feature 1: ~1 minute  
Feature 2: ~1 minute  
Feature 3: ~9 minutes  
Feature 4: ~2 minutes  

Additional Features  
Feature 5: ~1 minute  
Feature 6: ~3 minutes  


## Feature Descriptions

### Feature 1: 
List the top 10 most active host/IP addresses that have accessed the site.

* To implement Feature 1, I've extracted the host address from the log file.
* This is done by using the split function on each line and getting the first element of the line
* The number of unique hosts is counted using the Counter function from package collections
* The result is then sorted first by most common hosts and order lexicographically in the case of a clash.

e.g., `log.txt`:

    199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "POST /login HTTP/1.0" 401 1420
	unicomp6.unicomp.net - - [01/Jul/1995:00:00:06 -0400] "GET /shuttle/countdown/ HTTP/1.0" 200 3985
	199.72.81.55 - - [01/Jul/1995:00:00:09 -0400] "POST /login HTTP/1.0" 401 1420
	burger.letters.com - - [01/Jul/1995:00:00:11 -0400] "GET /shuttle/countdown/liftoff.html HTTP/1.0" 304 0
	199.72.81.55 - - [01/Jul/1995:00:00:12 -0400] "POST /login HTTP/1.0" 401 1420
	199.72.81.55 - - [01/Jul/1995:00:00:13 -0400] "POST /login HTTP/1.0" 401 1420
	199.72.81.55 - - [01/Jul/1995:00:00:14 -0400] "POST /login HTTP/1.0" 401 1420
	burger.letters.com - - [01/Jul/1995:00:00:14 -0400] "GET /shuttle/countdown/ HTTP/1.0" 200 3985
	burger.letters.com - - [01/Jul/1995:00:00:15 -0400] "GET /shuttle/countdown/liftoff.html HTTP/1.0" 304 0
	199.72.81.55 - - [01/Jul/1995:00:00:15 -0400] "POST /login HTTP/1.0" 401 1420
…

The output is :

	199.72.81.55,6
	burger.letters.com,3
	unicomp6.unicomp.net,1
…

### Feature 2: 
Identify the 10 resources that consume the most bandwidth on the site

* For Feature 2, we require the resource that is being accessed and the number of bytes per resource.
* Similar to feature 1 the resource is extracted using string split and the corresponding byte size for the requested resource as a tuple for each log entry
* The tuple is then stored in a Pandas DataFrame.
* A group by is performed on the resource column, aggregating the sum of bytes for each resources. This gives us a table of resources and the total bytes requested by that resource
* The result of the group by is sorted by total size of resource requested, and the top 10 values are written to file.
* This feature details the most bandwidth intensive resources.

e.g., for the same log input as above we get the following result:

	/login
	/shuttle/countdown/
	/shuttle/countdown/liftoff.html
…


### Feature 3:
List the top 10 busiest (or most frequently visited) 60-minute periods 

* This Feature details the busiest time window based on number of server accesses. The time of access is extracted for this feature and stored in a Pandas DataFrame.
* Based on the starting time and ending time of the logs input,  a list containing all the possible 60 minute time windows is created
* For each possible time window, we check the number of accesses, the output of that is sorted by descending number of accesses per window and written to file.

e.g., for the same log input as feature1 example we get the following result:

	01/Jul/1995:00:00:01 -0400,10
	01/Jul/1995:00:00:02 -0400,9
	01/Jul/1995:00:00:03 -0400,9
	01/Jul/1995:00:00:04 -0400,9
	01/Jul/1995:00:00:05 -0400,9
	01/Jul/1995:00:00:06 -0400,9
	01/Jul/1995:00:00:07 -0400,8
	01/Jul/1995:00:00:08 -0400,8
	01/Jul/1995:00:00:09 -0400,8
	01/Jul/1995:00:00:10 -0400,7
...


### Feature 4: 
Detect patterns of three failed login attempts from the same IP address over 20 seconds so that all further attempts to the site can be blocked for 5 minutes. Log those possible security breaches.

* For feature 4, we require the host address, time of access, and the server response.
* For this feature I've used two additional data structures, a dictionary to store failed login attempts and keep track of three failed logins over a 20 second window from the first attempt.
* A list to store the server accesses that occur after three failed login attempts in 20 seconds for 5 minute window.
* The first condition checks if the host has triggered the condtion for blocking, if yes and the access is in the 5 minute window it is added to the blocked list even if it a succesful login.
* If the first condition is not satisfied and the users performs a succesful login, then the host is removed from failed login.
* The third condtion adds the user to failed login based on 4 scenarios - If more than 20 seconds since last failed login, reset counter. 
If user has already been blocked and 5 minute window is completed reset counter. If the failed login is within 20 seconds , increment counter. Other wise if user is not previously present in failed login add user to failed login list.
* write blocked list to file
* Here I've used a separate list to store Blocked Attempts. During implementation with this method we can directly print and identify blocked attempts as soon as they happen i.e in real time with little to no delay.

e.g., output for the example log.txt is:

	199.72.81.55 - - [01/Jul/1995:00:00:13 -0400] "POST /login HTTP/1.0" 401 1420
	199.72.81.55 - - [01/Jul/1995:00:00:14 -0400] "POST /login HTTP/1.0" 401 1420
	199.72.81.55 - - [01/Jul/1995:00:00:15 -0400] "POST /login HTTP/1.0" 401 1420
...



### Other considerations and optional features
With the available data i've added a few features which I think could be useful.

### Feature 5:
List the top 10 most used file types. 

* This feature lists the top 10 file extensions used. This feature works in tandem with feature 2.
* After extracting the resources, the files extension from the resources is extracted
* Now similar to Feature 1, Counter is used to count the occurance of each unique extension and sorted 
* The output file contains the top 10 most used file extensions and is written to file - extensions.txt

eg., the output of this feature is:

	,8
	.html,2
...

### Feature 6:  
HTTP error count by date.


* This feature lists the error count frequency by date
* First the timestamp and server response are extracted
* It is then stored as a Panda DataFrame
* The timestamp Column is converted to date column and grouped by Day and server response
* The dataframe is pivoted to make the response the column headers
* the output is written to file - http_errors 
* This table would be useful in visualizing error responses over day, to quickly spot any anomalies in server performance.

eg., the output of this feature is:

Date 200 304 401
1995-07-01 2 2 6
...

## Assumptions

Assume you receive as input, a file, `log.txt`, in ASCII format with one line per request, containing the following columns:

* **host** making the request. A hostname when possible, otherwise the Internet address if the name could not be looked up.

* **timestamp** in the format `[DD/MON/YYYY:HH:MM:SS -0400]`, where DD is the day of the month, MON is the abbreviated name of the month, YYYY is the year, HH:MM:SS is the time of day using a 24-hour clock. The timezone is -0400.

* **request** given in quotes.

* **HTTP reply code**

* **bytes** in the reply. Some lines in the log file will list `-` in the bytes field. For the purposes of this challenge, that should be interpreted as 0 bytes.


e.g., `log.txt`

    in24.inetnebr.com - - [01/Aug/1995:00:00:01 -0400] "GET /shuttle/missions/sts-68/news/sts-68-mcc-05.txt HTTP/1.0" 200 1839
    208.271.69.50 - - [01/Aug/1995:00:00:02 -400] “POST /login HTTP/1.0” 401 1420
    208.271.69.50 - - [01/Aug/1995:00:00:04 -400] “POST /login HTTP/1.0” 200 1420
    uplherc.upl.com - - [01/Aug/1995:00:00:07 -0400] "GET / HTTP/1.0" 304 0
    uplherc.upl.com - - [01/Aug/1995:00:00:08 -0400] "GET /images/ksclogo-medium.gif HTTP/1.0" 304 0
    ...
    
In the above example, the third line shows a failed login (HTTP reply code of 401) followed by a successful login (HTTP reply code of 200) two seconds later from the same IP address.


## Testing

Apart from the Provided test, Additional test inputs have been used to test the following cases:
* Test ordering of data in case of clashes
* Test blank input file
* Test implementation of basic features

Two test run files are present, one run_test.sh is provided already in the insight testsuite.  
Second file run_tests_additional.sh is modidifed run_tests.sh to include testing the additional features.  

For the user defined function in Feature 3, Unit test to check proper creation of time window start times is in file unit_test.py

## Repo directory structure

The directory structure for the repo is as follows:

    ├── README.md 
    ├── run.sh
    ├── src
    │   └── process_log.py
    │   └── unit_test.py
    ├── log_input
    │   └── log.txt
    ├── log_output
    |   └── hosts.txt
    |   └── hours.txt
    |   └── resources.txt
    |   └── blocked.txt
    |   └── extensions.txt
    |   └── http_errors.txt	
    ├── insight_testsuite
        └── run_tests.sh
        └── run_tests_additional.sh		
        └── tests
            └── test_features
            |   ├── log_input
            |   │   └── log.txt
            |   |__ log_output
            |       └── hosts.txt
            |       └── hours.txt
            |       └── resources.txt
            |       └── blocked.txt
            |       └── extensions.txt
            |       └── http_errors.txt
            ├── test_1
            |   ├── log_input
            |   │   └── log.txt
            |   |__ log_output
            |       └── hosts.txt
            |       └── hours.txt
            |       └── resources.txt
            |       └── blocked.txt
            |       └── extensions.txt
            |       └── http_errors.txt
            ├── test_2
            |   ├── log_input
            |   │   └── log.txt
            |   |__ log_output
            |       └── hosts.txt
            |       └── hours.txt
            |       └── resources.txt
            |       └── blocked.txt
            |       └── extensions.txt
            |       └── http_errors.txt
            ├── test_blank_file
                ├── log_input
                │   └── log.txt
                |__ log_output
                    └── hosts.txt
                    └── hours.txt
                    └── resources.txt
                    └── blocked.txt
                    └── extensions.txt
                    └── http_errors.txt



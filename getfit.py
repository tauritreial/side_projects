#! /usr/bin/env python
#-*- coding: utf-8 -*-

import time
import json
import httplib2
import matplotlib.pyplot as plt
from datetime import datetime
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow

# Copy your credentials from the Google Developers Console
CLIENT_ID = '963257660477-p6rm1i1mu3nkgfhlqol570lnla1sc9ha.apps.googleusercontent.com'
CLIENT_SECRET = 'w9gzmXpP-atkzS_6odR3-E6D'

# Check https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets/get
# for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/fitness.activity.read'


# DATA SOURCE
DATA_SOURCE = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"

# The ID is formatted like: "startTime-endTime" where startTime and endTime are
# 64 bit integers (epoch time with nanoseconds).
DATA_SET = "1581923297927862000-1582023297927862000"

# Constants to loop over each day
current_time_ns = int(time.time()*1e9)
one_day_ns = 86400000000000
ONE_DAY = current_time_ns - one_day_ns
DAY = current_time_ns

TOTAL_STEPS = []
DATE = []
# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


#Getting the credetials from Google to authorise my code
#Not using a function because user can allow it once
flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
authorize_url = flow.step1_get_authorize_url()
print ('Go to the following link in your browser:')
print (authorize_url)
code = input('Enter verification code: ').strip()
credentials = flow.step2_exchange(code)

#Looping over i days
for i in range(7):
    DAY = DAY - one_day_ns
    NEW_DATA_ID = (DAY, DAY - one_day_ns)

    #For the DATA_ID formatting
    TEST_ID = ("{}-{}".format(NEW_DATA_ID[0], NEW_DATA_ID[1]))

    def retrieve_data():
        # Create an httplib2.Http object and authorize it with our credentials
        http = httplib2.Http()
        http = credentials.authorize(http)

        fitness_service = build('fitness', 'v1', http=http)

        #Returns the database
        return fitness_service.users().dataSources(). \
                datasets(). \
                get(userId='me', dataSourceId=DATA_SOURCE, datasetId=TEST_ID). \
                execute()


    def nanoseconds(nanotime):
        """
        Convert epoch time with nanoseconds to human-readable.
        """
        dt = datetime.fromtimestamp(nanotime // 1000000000)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    if __name__ == "__main__":
        # Point of entry in execution mode:
        dataset = retrieve_data()
        with open('dataset.txt', 'w') as outfile:
            json.dump(dataset, outfile)
        last_point = dataset["point"][-1]

        #To determine the beginning and the end of the time of user request
        start_time = dataset["point"][1]
        end_time = dataset["point"][-1]

        #Calculates the sum of steps over one day
        N = len(dataset["point"])
        steps_list = []

        for x in list(dataset["point"]) [0:N]:
            steps = (x["value"][0].get("intVal", None))
            steps_list.append(int(steps))
        STEPS = (sum(steps_list))

        #To plot steps per day
        date = nanoseconds((int(start_time.get("startTimeNanos",0))))

        #Prints the results on the screen
        #print("Start time:", nanoseconds(int(start_time.get("startTimeNanos", 0))))
        #print("End time:", nanoseconds(int(end_time.get("endTimeNanos", 0))))
        #print("Data type:", last_point.get("dataTypeName", None))
        #print("Steps:", STEPS)

        TOTAL_STEPS.append(int(STEPS))
        DATE.append(date[5:10])


plt.plot(DATE, TOTAL_STEPS)
plt.xlabel("Date")
plt.ylabel("Number of steps")
plt.show()


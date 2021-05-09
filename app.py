import json
import requests
import datetime
import time
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import math
from twilio.rest import Client
from creds import ACCOUNT_SID, AUTH_TOKEN, HEADER, YOUR_PHONE_NO, TWILIO_ALLOTED_NUMBER

available = {}  # Initializing empty json object ,that gonna hold data of available slots
is_pin = False  # It will be used to check weather user input is Pin code or District name
working = False  # It will be used to stop user to give multiple inputs when script is still processing previous one
phone_no = ''  # Phone number of user ,Initially empty.
msg = ''  # Message send by the user ,Initially empty.

with open('district_data.json', 'r') as f:
    district_data = json.load(f)  # All district codes were already dumped in this file so no need to run API every time,revert back if you want code for getting this from SETU API.

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, Folks! \nNothing here, Just a Noob testing something."


def getDistrictCode(district_name):
    for states in data:
        for district in states['districts']:
            if district['district_name'] == district_name:
                return district['district_id']
    # district name not found in list ,so returning emtpy string.
    return ''


def getDates(i):
    today = datetime.datetime.today()
    waste_list = [today + datetime.timedelta(days=x) for x in range((i - 1) * 7)]
    date_list = [today + datetime.timedelta(days=x) for x in range(i * 7)]
    date_str = [x.strftime("%d-%m-%Y") for x in date_list]
    waste_str = [x.strftime("%d-%m-%Y") for x in waste_list]
    for waste in waste_str:
        date_str.remove(waste)
    # Here we are returning list of dates of either 1st or 2nd or 3rd or 4th week based on the value of i.
    return date_str


def getToday(date):
    if date == datetime.datetime.today().strftime("%d-%m-%Y"):
        # if current date is of today then rename it with Today instead of showing date( Just only for look result more nicer)
        return 'TODAY'
    elif date == (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y"):
        # if current date is of tomorrow then rename it with Tomorrow instead of showing date.
        return 'TOMORROW'
    else:
        # if current date is neither of today nor tomorrow then returning same date to be printed in output result.
        return date


def getAppointments(n, DIST_ID):
    date_str = getDates(
        n)  # Getting list of dates for nth week.(Not taking dates for full month initially just for efficient result.)
    if n == 5:
        # if value of n(week) exceeds 4, then returning no slots for this month and quiting the search process.
        return 'Sorry ,There is no vaccine available in your area for next 28 days.\n\nYou can try again after some time(Server data refresh every 30 min).'
    if is_pin:
        # If Pin boolean is on then search should be done by pin.
        search_type = 'calendarByPin?pincode'
    else:
        # If Pin boolean is off then search should be done by district_id.
        search_type = 'calendarByDistrict?district_id'
    global available
    date_ist = []
    try:
        for INP_DATE in date_str:  # Searching and retrieving data, date by date for given week.
            URL = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/{search_type}={DIST_ID}&date={INP_DATE}"
            response = requests.get(URL, headers=headers)
            if response.ok and ('centers' in json.loads(response.text)):
                response_json = json.loads(response.text)['centers']
                if response_json is not None:
                    for resp in response_json:  # Loading every response.
                        for data in resp['sessions']:  # Checking sessions for necessary information.
                            if data['available_capacity'] != 0:  # Setting Main Check ,If slots have available ,then only their data is loaded. Otherwise what is the purpose of empty slots :(
                                if data['date'] not in date_ist:  # Creating a list of dates ,for sorting result by dates
                                    date_ist.append(data['date'])
                                    available.update({f"{data['date']}": []})  # Creating entry of unique date in "Available" json object.
                                if resp['fee_type'] == '':  # This little 2 liner code if just for those case when data field returns nothing. Sometime happens (can be omitted)
                                    resp['fee_type'] = 'Paid'
                                #  Creating json data (only the important one) from the data we received from API
                                json_data = {"Hospital": resp['name'], "Fees": resp['fee_type'],
                                             "Age_Limit": data['min_age_limit'], "Vaccine": data['vaccine'],
                                             "Available": data['available_capacity']}
                                available['{}'.format(data['date'])].append(json_data)  # Feeding json data into json object date-wise.
            else:
                # Returning some common errors acc to their status code.
                if response.status_code == 400:
                    return 'Invalid Pin'
                elif response.status_code == 500:
                    return 'Internal Server Error'
                elif response.status_code == 403:
                    return 'Server quota limit reached.\nPlease try again after 5 min'
                else:
                    return "Error : (" + str(response.status_code) + ") " + str(response.text)
    except Exception as e:
        #  If above code fails to execute for some unknown reason then app owner should be informed.
        err_str = "Error : {}".format(e)
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        client.messages.create(
            body=err_str,
            from_=f'whatsapp:{TWILIO_ALLOTED_NUMBER}',
            to=f'whatsapp:{YOUR_PHONE_NO}'
        )
        return err_str
    if not date_ist:
        #  if date list remains empty (i.e : No slots in this week) then this function should re-run for next week (n+1 week,same district id).
        return getAppointments(n + 1, DIST_ID)
    else:
        #  sorting dates in ascending order
        dates = [datetime.datetime.strptime(ts, "%d-%m-%Y") for ts in date_ist]
        dates.sort()
        sorted_dates = [datetime.datetime.strftime(ts, "%d-%m-%Y") for ts in dates]
        msg_str = ''  # Initially empty message string.
        # Generating output reply date by date.
        for dts in sorted_dates:
            no = 0  # Just to track limits.
            msg_str = msg_str + f"*{getToday(dts)}* ({len(available['{}'.format(dts)])})\n"  # Creating Date entry in reply message(Heading).
            for list_name in available[f'{dts}']:  # Creating sub entry of available slots under above date.
                no += 1
                if no <= 20:  # Setting limit for 20 entry per date. Personally thinks its more than enough data to choose.
                    msg_str = msg_str + f"\n{no}) {list_name['Hospital']}\n    {list_name['Available']} {list_name['Vaccine']} Available\n    For {list_name['Age_Limit']}+ ({list_name['Fees']})\n"  # Format of message.
                else:
                    # Its unfair not to tell the reason for not showing other centers.
                    msg_str = msg_str + "\nCenter limit reached(20)\n"
                    break  # Breaking loop so that it will not run for remaining centers.
            msg_str = msg_str + '\n'  # Just for margin & spacing.
        return msg_str  # Returning list created above in form of message.


def is_Pin(message):
    global is_pin
    try:
        val = int(message)  # If successful then input is a PIN.
        is_pin = True
    except ValueError:
        is_pin = False  # If fails then surely its not a PIN.


@app.route("/sms", methods=['POST'])
def sms_reply():
    global working
    global phone_no
    global msg
    """Respond to incoming calls with a simple text message."""
    if working:  # If script is already working on previous input then give the user for atleast 5 second break( Hopefully ,meanwhile previous task should complete).
        time.sleep(5)
        reply = 'Try Again'
        resp = MessagingResponse()
        resp.message(reply)
        working = False  # Already make the user to wait ,so won't do it again.
        return str(resp)
    working = True  # Telling script that its started working on some input so please won't take other.
    msg = request.form.get('Body')
    phone_no = request.form.get('From')
    is_Pin(msg)  # Checking wether hte input is Pin code or District name.
    #  Sending input data to different function accordingly.
    if is_pin:
        #  If input is pin ,then sending input data directly to the function.
        reply = getAppointments(1, msg)
    else:
        #  If input is not a pin,then extracting district code first from input then sending it to function.
        code = getDistrictCode(msg.title())  # Here titled input message just to capitalize 1st letter ,as data in json file for reference is in same format.
        if code == '':
            #  If get code function doesn't reply anything then user input may be wrong or not in Govt search list.
            reply = "Invalid District Name"
        else:
            #  Starting function with district code.
            reply = getAppointments(1, code)
    # Create reply
    if len(reply) >= 1590:  # Twilio limit is 1600 characters/message ,so if our response message exceeds limits then sending it manually in parts under given limits.
        client = Client(ACCOUNT_SID, AUTH_TOKEN)  # As we only need to initialize client when limit exceeds, that's why we didn't initialized it above(starting).
        div = int(math.ceil(len(reply) / 1590))  # Getting how many parts can be possible of given message.
        if div >= 4:  # As no one needs that much amount of data (>1590*4)characters ,so setting upper limit of sending messages.
            div = 4
        for i in range(div):
            split = reply[:1590]  # Getting only first 1590 characters of message into temporary string.
            reply = reply.replace(split, '')  # As 1st part of msg is transfared in temp string so removing that part from main message.
            # Sending message in parts manually instead of replying in response.
            client.messages.create(
                body=split,
                from_=f'whatsapp:{TWILIO_ALLOTED_NUMBER}',
                to=phone_no
            )
        working = False  # As work is completed .
        return ''  # Returning empty response, As we already replied to that message query in chunks.
    resp = MessagingResponse()
    resp.message(reply)
    working = False
    return str(resp)  # Replying for input message


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)

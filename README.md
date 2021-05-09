
# cowin-whatsapp-cloud-bot
This bot works on free cloud server and provide vaccination center slots information on your whatsapp.
note : I've learned coding from internet ,So no doubt this code can be optimized more. Feel free to do so according to your needs. 

Software & Service's Used:
1) Python
2) AWS Cloud service
3) API Setu
4) Twilio
5) Flask
6) Gunicorn
7) Nginx
8) Other Python Libs(Json, Requests etc) 

Nothing to explain here, As i already added explaination of infact every line in code itself ,still have any doubts feel free to ask.

YOU JUST NEED TO CHANGE DATA OF CREDS.PY FILE WITH YOUR DATA . 

STEPS TO DEPLOY THE APP:

PART 1 (Creating ab account on cloud server)

  -> Any cloud service provider will work whose data servers are in India as this https://apisetu.gov.in/public/api/cowin API have geo-fencing , so if you try with any cloud service whose IP is of outside India then it gonna block your request. 
*HEROKU* will not work,already tried mostly everything.
AWS works fine.

1) Create a free acoount on Amazon AWS (https://portal.aws.amazon.com/billing/signup#/start) .
2) You have to verify your email, phone number and card details in order to create an account.
3) If you don't want to give them card details then you can also go with virtual debit cards (such as Airtel, Payzapp, IRCTC imudra etc).
4) They gonna charge you 2 rupee for verification .
5) [MOST IMPORTANT] : After verification change your region to (Asia Pacific (Mumbai)ap-south-1) option is at top right corner.
6) Then create a new EC2 instance with ubuntu (having free tier eligble).
7) Go to security groups ,open port 80 for inbound traffic.
8) Go to console,update macine & install python3,nginx,gunicorn3 and other important packages
9) clone project.
10) change directory to project directory.
11) create virtual envirnment and activate it.
12) Install remaining requirements (pip3 install -r requirements.txt).
13) create a new file at /etc/nginx/sites-enabled and put this in file.
14) server {
    listen 80;
    server_name YOUR_PUBLIC_DNS;
    location / {
        proxy_pass http://127.0.0.1:8080;
    }
  }
15) save everything ,restart nginx.
16) Now run,gunicorn3 app:app

PART 2

 1) Create an account at Twilio (https://www.twilio.com/try-twilio).
 2) Get Account Sid and Auth Token from homepage and paste it in creds file.
 3) Then go to Whatsapp (https://www.twilio.com/docs/autopilot/channels/whatsapp).
 4) Create your sandbox, go to sendbox page (https://www.twilio.com/console/sms/whatsapp/sandbox).
 5) At sendbox configuration ,put your Aws instance Public DNS at *when message comes in* feild.
 6) Add (/sms) after your public DNS in above feild.
 7) Save it

Now You are ready to go ,your own whatsapp cloud server cowin bot is up and running.
Anyone who sends Twilio code to Twilio number will be connected with your cloud bot and surely gets their query reply.

Feel free to give suggestions for Betterment.

Love You All ;)



SCREENSHOTS ATTACHED BELOW


![Screenshot_2021-05-09-16-47-03-420_com whatsapp w4b](https://user-images.githubusercontent.com/83899995/117570276-0bfd0f80-b0e7-11eb-87eb-c785dcc20159.jpg)
![Screenshot_2021-05-09-16-48-01-816_com whatsapp w4b](https://user-images.githubusercontent.com/83899995/117570280-0e5f6980-b0e7-11eb-9292-ddbeb7a08c07.jpg)
![Screenshot_2021-05-09-16-50-41-806_com whatsapp w4b](https://user-images.githubusercontent.com/83899995/117570282-0f909680-b0e7-11eb-9497-b2b60c25246e.jpg)

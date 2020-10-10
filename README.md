# Twilio Answering Machine
This program is a simple answering machine implementation in Python using Twilio. I used this program to replace my home phone line (costing ~ $40 per month) with a software answering machine that records a message from callers and forwards them my cellphone message. I was able to transfer the my home number to Twilio, and after switching, it cost me $2.50 the first month; this included all the program testing. I run the program on a raspberry pi as a cron job every 5 minutes. 

Setup:
    1) Download the helper library from https://www.twilio.com/docs/python/install
    2) Twilio account and phone number.
    3) Create a TwiML to answer coming calls:
       https://www.twilio.com/docs/wireless/tutorials/communications-guides/implement-voicemail
    4) Rename config_exmaple.py to config.py and add the needed information
    5) Run program
        a) text messages with a link to any recorded voicemail will be sent to    the cellphone 
        b) from cellphone: del 'id#' will delete the recording
    Enjoy
from googlevoice import Voice
from googlevoice.util import input
from time import sleep
import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service
import re, os
import getpass
from bs4 import BeautifulSoup

def start_crawl():
    """
        Run this to begin the crawl!
        Keep in mind participants form must have this format: Timestamp (google adds this automatically), Name, and phone number
        Keep in mind hosts form must have this format: Stop College, Location, Drink Name
        ** Also, your password to your google account will be echoed on the command line. **
        
        If you are not on Aaron's computer and are looking to get the necessary python packsages... you need:
            pygooglevoice
            gdata-python-client
            BeautifulSoup
        
        Happy crawling!
    """
    email = raw_input('What is your Google Account?') # voice and docs must be same acct
    password = getpass.getpass('What is your Google Password')
    hosts_name = raw_input('What is the name of your GoogleDocs Host Spreadsheet')
    participants_name = raw_input('What is the name of your GoogleDocs Participants Form')
    _organizer_number = raw_input('What is the phone number of the crawl organizer? (10 digit number)')
    organizer_number = '+1'+_organizer_number+':'
    num_stops = raw_input('What is the number of stops')
    
    gd_client = gdata.spreadsheet.service.SpreadsheetsService()
    gd_client.email = email
    gd_client.password = password
    gd_client.source = 'Insta-Crawl'
    gd_client.ProgrammaticLogin()
    
    hosts = _getSpreadsheetRows(hosts_name, gd_client)
    participants = _getSpreadsheetRows(participants_name, gd_client)
    
    voice = Voice()
    voice.login(email, password)
    
    _start_poll(organizer_number, hosts, participants, num_stops, voice)
    
def _getSpreadsheetRows(name, gd_client):
    """
        takes in name of spreadsheet from gd_client, queries the worksheet, and returns a 
        formatted list of lists, where each list represents each row, and each element of
        the interior lists represents each column.
    """
    # perform query
    q = gdata.spreadsheet.service.DocumentQuery()
    q['title'] = name
    q['title-exact'] = 'true'
    feed = gd_client.GetSpreadsheetsFeed(query=q)
    spreadsheet_id = feed.entry[0].id.text.rsplit('/',1)[1]
    feed = gd_client.GetWorksheetsFeed(spreadsheet_id)
    worksheet_id = feed.entry[0].id.text.rsplit('/',1)[1]
    # get the information
    rows = gd_client.GetListFeed(spreadsheet_id, worksheet_id).entry
    rowList = []
    for row in rows:
        rowData = []
        for key in row.custom:
            if key!='timestamp':
                rowData.append((key, row.custom[key].text))
        rowList.append(rowData)
    return rowList
    
def _start_poll(organizer_number, hosts, participants, num_stops, voice):
    """
        Begins polling loop for crawl 
        Input: the number of the crawl organizer, the hosts list, the participants list, the number of stops,
               and the voice object used (the open google voice session)
        Usage: text the organizer_number to activate the next stop
    """
    current = 0
    while current<=num_stops:
        count = 0
        voice.sms()
        for msg in _extractsms(voice.sms.html):
            if msg['from']==organizer_number:
                count+=1
        print('Current Stop Number: '+str(count))
        if count==int(num_stops)+1:
            for participant in participants:
                text = 'Hello, '+participant[0][1]+' the crawl is over!'
                voice.send_sms(participant[1][1], text)
                sleep(2)
        elif count>current:
            # send those sms's
            for participant in participants:
                text = 'Hello, '+participant[0][1]+' the next stop is at '+hosts[count-1][0][1]+' in '+hosts[count-1][1][1]+'. '+' They will be serving: '+hosts[count-1][2][1]
                voice.send_sms(participant[1][1], text)
                sleep(2)
            current=count
            
def _extractsms(htmlsms) :
    """
    extractsms  --  extract SMS messages from BeautifulSoup tree of Google Voice SMS HTML.

    Output is a list of dictionaries, one per message.
    """
    msgitems = []										# accum message items here
    #	Extract all conversations by searching for a DIV with an ID at top level.
    tree = BeautifulSoup(htmlsms)			# parse HTML into tree
    conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
    for conversation in conversations :
        #	For each conversation, extract each row, which is one SMS message.
        rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
        for row in rows :								# for all rows
            #	For each row, which is one message, extract all the fields.
            msgitem = {"id" : conversation["id"]}		# tag this message with conversation ID
            spans = row.findAll("span",attrs={"class" : True}, recursive=False)
            for span in spans :							# for all spans in row
                cl = span["class"][0].replace('gc-message-sms-', '')
                msgitem[cl] = (" ".join(span.findAll(text=True))).strip()	# put text in dict
            msgitems.append(msgitem)					# add msg dictionary to list
    return msgitems

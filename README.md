Insta-Crawl
-----------

Python script that utilizes Google Docs and Google Voice for next level crawls.

###Required Python Libraries
- pygooglevoice
- gdata-python-client
- BeautifulSoup

###Other Required Items
- A google account with a voice account/number and google docs
- A form/spreadsheet for participants on google docs in this format:
    * Timestamp (google adds this automatically), Name, and phone number
- A form/spreadsheet for hosts in this format:
    * Stop College, Location, Drink Name

###Notice
In the current way input is handled, your google account credentials will be
echoed in the terminal.
#Jpop_lyrics_scraper
#python 3

import requests, bs4, openpyxl, os, time, re, smtplib
from selenium import webdriver
from difflib import SequenceMatcher
from email.mime.text import MIMEText

def main_text(markup): #markup is the tag that has Kanji_1 or Translation_1 ID
	for tag in markup.find_all(True):
		tag.extract()
	try:
		return (markup.get_text()).encode('latin1').decode('utf-8') 
	except:
		return markup.get_text()
def delnum(text): #delete numbering for text
	spnum = text.index(' ')
	text = text[(spnum + 1):len(text)]
	return text
def song_vid(href): #find tags that are songs
    return href and (re.compile('/' + anamelink + '/lyrics/').search(href) or re.compile('/' + anamelink + '/videos/').search(href))
def trim(text): #trim unnessary parts
	text = text[5:(len(text)-5)]
	return text

print('\n\n\nWELCOME TO JPOP LYRICS SCRAPER!')
print('\n\n---------------------------------------------------------------------------------------------------------------\n\n')
print('''This is a script to pull all songs' lyrics with their translations (if available) of a Japanese artist from jpopasia.com to your email address. Each email will contain the song's lyric (in kanji) and its translation in English.\n''')
print('''WHY USE THIS SCRIPT?

This script is ideal if you want to learn songs' lyrics of a Japanese artist you are following, because all of their lyrics (in kanji) along with possilbe translations will be sent to your email, ready to be looked up whenever you want, even when offline, providing you use an email client that saves emails locally on your device (like a smartphone).
So that the next time you hear a song from that Japanese artist, you can search for the lyric directly in your inbox, saving you time and effort looking up online. Furthermore, you can manipulate the lyric just like a regular email (eg. mark as read, mark as unread, flag, star, move to folders, forward to your friends, etc.), which makes organizing your favourite Jpop artist's lyrics collections, sharing songs' lyrics, and many more actions become a convenient task.\n''')
print('''In short, with Jpop Lyric Scraper, you can save hundreds of Japanese songs lyrics for later use, in just a few minutes.''')
print('\n\n---------------------------------------------------------------------------------------------------------------\n\n')
print('HOW TO USE:')
print('1. Look for an artist to scrape lyrics and translations from\n2. Wait for the program to scrape all lyrics and translations from that artist \n3. Log in your gmail to send the scraped lyrics and translations to an email of your choice')
print('\n\n---------------------------------------------------------------------------------------------------------------\n\n')
artistquerry = input('First, please enter some keywords to find the one Japanese artist you are looking for (eg. akb48, sekai, kyary, etc.): ')
print('Searching....\nPlease allow up to two minutes for the program to search. Thank you for your patience!')
T1 = time.time()
qlink = 'http://www.jpopasia.com/search/?q=' + artistquerry
browser = webdriver.PhantomJS()
browser.get(qlink)
html = browser.page_source
qsoup = bs4.BeautifulSoup(html, "lxml")
ultag = qsoup.find('ul', class_="pretty size-xl upvoteable")
tags = ultag.find_all('b', class_="black")
alist = []
ainfo = []
i = 0
for tag in tags:
	i = i + 1
	ainfo.append(str(i)) #result number
	ainfo.append(tag.get_text(strip=True)) #artist name
	ainfo.append(tag.parent.get('href')) #artist discography's link
	alist.append(ainfo)
	ainfo = []
print('\n\n---------------------------------------------------------------------------------------------------------------\n\n')
print('SEARCH RESULT:	\n')
for ainfo in alist:
	print(ainfo[0] + '. ' + ainfo[1])
print('Took ', round((time.time() - T1), 2), 'seconds to search')
print('\n\n---------------------------------------------------------------------------------------------------------------\n\n')
while True:
	anum = input('Please enter the number next to the artist you are looking for: ')
	try: 
		anum = int(anum)
		if (anum > 0) and (anum <= len(alist)) :
			break
		else:
			print('Oops, your input is invalid, please try again!')
	except: 
		print('Oops, your input is invalid, please try again!')
ainfo = alist[anum-1]
aname = ainfo[1]
alink = 'http://www.jpopasia.com' + ainfo[2] + '/discography'
anamelink = (ainfo[2]).replace('/', '')
print ('\n\nYou have selected the following artist: ' + aname)
print('Please wait while we scrape all available lyrics and translations for this artist')
print('\n\n---------------------------------------------------------------------------------------------------------------\n\n')

#create excel
filefolder = '.\\lyrics_database\\'
filename = aname + '_lyrics.xlsx'
filepath = filefolder + filename
#create folder for the excel file
try:
	os.makedirs(filefolder)
except FileExistsError:
	pass
try: #If there is already a database
	wb = openpyxl.load_workbook(filepath)
	sheet = wb.active
	print('These are the song lyrics that have been scraped, ordered in their respective collection (duplicate songs in later collections will be omitted): ')
	row = 2
	while sheet['A' + str(row)].value != None:
		track = sheet['A' + str(row)].value
		sname = sheet['B' + str(row)].value
		body = sheet['D' + str(row)].value
		cname = sheet['E' + str(row)].value	
		if cname != sheet['E' + str(row-1)].value:
			print('Collection: ' + cname)
		print(track + '. ' + sname)
		row = row + 1
	print('\nA file entitled "' + filename + '" is available at: ' + os.path.abspath(filefolder))
except FileNotFoundError: #If there is no database, create one
	row = 2
	T1 = time.time()
	wb = openpyxl.Workbook()
	sheet = wb.active
	sheet['A1'] = '#'
	sheet['B1'] = 'Song name'
	sheet['C1'] = 'Link'
	sheet['D1'] = 'Body'
	sheet['E1'] = 'Collection'
	#Build database
	print('These are the song lyrics that have been scraped, ordered in their respective collection: ')
	row_attempt = 1
	res = requests.get(alink) #Request artist discography page
	dsoup = bs4.BeautifulSoup(res.text, "lxml") #parse it
	for ctag in dsoup.find_all(href=re.compile('/' + anamelink + '/album/')): #Find all the collection
		clink1 = ctag.get('href').encode('latin1').decode('utf-8') #fix font
		clink = 'http://www.jpopasia.com' + clink1 #get the link of the collection
		cname = ctag.getText().encode('latin1').decode('utf-8') #fix font + get the colletion name
		print('Collection: ' + cname)
		res = requests.get(clink) #Request the collection page
		csoup = bs4.BeautifulSoup(res.text, "lxml") #parse it
		songtaglist = csoup.find_all(href=song_vid, string = True ) #Lists of tags of songs of that collection
		for stag in songtaglist:
			slink1 = stag.get('href').encode('latin1').decode('utf-8') #fix font
			slink = 'http://www.jpopasia.com' + slink1 #get the link of the song
			res = requests.get(slink) 
			ssoup = bs4.BeautifulSoup(res.text, "lxml")
			try:
				kanji = trim(main_text(ssoup.find(id="kanji_1"))) #Retrieve Kanji 		
				if len(kanji) > 100: #1ST FILTER: ONLY TAKE SONGS THAT HAVE KANJI LYRICS
					row_attempt = row_attempt + 1		
					if row_attempt == 2: #If this is the first song to write
						sname = (delnum(stag.getText())).encode('latin1').decode('utf-8') 			
						row = 2 
						trans = trim(main_text(ssoup.find(id="translation_1"))) #Retrieve trans
						body = kanji + '\n\n----------------------------------------------\n\n' + trans #Create the body for the first song
						track = '1'
						sheet['A2'] = track
						sheet['B2'] = sname
						sheet['C2'] = slink
						sheet['D2'] = body
						sheet['E2'] = cname
						print(track + '. ' + sname)
					else: #If this is not the first song to write	
						uniquebody = True
						cb = kanji[:200].lower()
						for i in range(2, row + 1):
							pb = ((sheet['D' + str(i)].value)[:200]).lower()
							if SequenceMatcher(None, cb, pb).ratio() >= 0.5: #Criteria for unique body: More than 50% of the first 200 characters of the kanji lyric are different than that of the rest of the file
								uniquebody = False
								break
						if uniquebody == True: #4TH FILTER: ONLY TAKE SONGS THAT HAVE UNIQUE LYRICS	
							sname = (delnum(stag.getText())).encode('latin1').decode('utf-8')	
							trans = trim(main_text(ssoup.find(id="translation_1"))) #Retrieve trans
							body = kanji + '\n\n----------------------------------------------\n\n' + trans #Create the body for other songs							
							row = row + 1
							track = str(row - 1)
							sheet['A' + str(row)] = track
							sheet['B' + str(row)] = sname
							sheet['C' + str(row)] = slink
							sheet['D' + str(row)] = body
							sheet['E' + str(row)] = cname
							print(track + '. ' + sname)
			except AttributeError:		
				pass
	wb.save(filepath) #save the file
	print('\nA file entitled "' + filename + '" has been created at: ' + os.path.abspath(filefolder))
	print('It takes', round((time.time() - T1), 2), 'seconds to scrape lyrics')	
print('\n\n---------------------------------------------------------------------------------------------------------------\n\n')

print('Finally, please log in to your gmail account to send these lyrics and translations to an email of your choice. Each e-mail contains a lyric and a translation of a song.\nAll of the following information, including your gmail password, will not be saved and sent anywhere.')
sender = input('Please enter your gmail address: ')
password = input('Please enter your password (again, it will not be saved and sent anywhere): ')
to = input('Please enter a recipient email: ')
smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
smtpObj.ehlo()
smtpObj.starttls()
smtpObj.login(sender, password)
print('\n\n---------------------------------------------------------------------------------------------------------------\n\n')
#Send email
y = ' ' 
while (y != 'y') and (y != 'Y'):
	y = input('Please press "y" and then enter to start sending the scraped lyrics and translations to ' + to + ': ')
T1 = time.time()
mail_num = 0
row = 2
while sheet['A' + str(row)].value != None:
	track = sheet['A' + str(row)].value
	sname = sheet['B' + str(row)].value
	body = sheet['D' + str(row)].value
	title = aname + ''''s lyrics: ''' + track + '. ' + sname
	msg = MIMEText(body.encode('utf-8'), _charset='utf-8') #body
	msg['Subject'] = title #subject
	msg['From'] = sender
	msg['To'] = to
	smtpObj.sendmail(sender, to, msg.as_string())
	print('An email entitled: "' + title + '" has been sent')	
	mail_num = mail_num + 1
	row = row + 1
	if mail_num % 50 == 0:
		print('Resume sending emails after 30 seconds') #avoid being ban sending mails by gmail
		time.sleep(30)
smtpObj.quit()
print('\n\n' + str(mail_num) + ' mails have been sent in', round((time.time() - T1), 2), 'seconds' )
print('\n\n---------------------------------------------------------------------------------------------------------------\n\n')
print('THANK YOU FOR USING THIS SCRIPT!')
print('\n\nCREDITS:\nCreator: Phuoc Pham\nAll Jpop database comes from jpopasia.com')
wb.close()		

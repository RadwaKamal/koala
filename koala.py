import feedparser as fp
import tweepy as tp
import os
import csv
import time
from datetime import datetime
import psycopg2
import urllib.parse

def tweet(new_entries, publication_name):
	for new_entry in new_entries:
		tweet = new_entry[1] + " " + new_entry[0]
		try:
			api.update_status(tweet)
			cur = conn.cursor()
			cur.execute(insert_sql,(new_entry[0][21:], new_entry[2], publication_name))
			conn.commit()
			cur.close()
		except tp.error.TweepError as e:
			print(e.response.text)
			print(new_entry[0][21:])


def manipulate_entry_tags(tags):
	hashtags = ""
	for tag in tags:
		"""
		tag is in form : {'label': None, 'scheme': None, 'term': 'web-development'} 
		Extract term only and replace "-" if exists with "_"
		"""
		hashtag = tag.term
		if(hashtag.find('-') != -1):
			hashtag = str.replace(hashtag, "-", "_")
		hashtags += "#" + hashtag + " "
	return hashtags


def handle_entries(entries, publication_name):
	new_entries = []
	for entry in entries:
		cur = conn.cursor()
		entry_published_date = str.replace(entry.published, ' GMT', '')
		formated_publication_dt = datetime.strptime(entry_published_date, '%a, %d %b %Y %H:%M:%S')
		cur.execute(select_sql,(entry.id[21:],))
		row = cur.fetchone()
	
		if not row:
			entry_tags = manipulate_entry_tags(entry.tags)
			new_entries.append([entry.id, entry_tags, formated_publication_dt])
		cur.close()
	tweet(new_entries, publication_name)

if __name__ == '__main__':
	#Auth for tweepy 
	C_KEY = os.environ.get('C_KEY')
	C_SECRET = os.environ.get('C_SECRET')
	A_TOKEN = os.environ.get('A_TOKEN')
	A_TOKEN_SECRET = os.environ.get('A_TOKEN_SECRET')

	auth = tp.OAuthHandler(C_KEY, C_SECRET)
	auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)  
	api = tp.API(auth)

	urllib.parse.uses_netloc.append("postgres")
	url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
	insert_sql = "INSERT INTO medium_publications (publication_id, published_at, publication_name) VALUES (%s, %s, %s)"
	select_sql = "SELECT 1 FROM medium_publications WHERE publication_id=%s"

	conn = psycopg2.connect(
    	database=url.path[1:],
    	user=url.username,
    	password=url.password,
    	host=url.hostname,
    	port=url.port
	)

	while True:
		#Get feed
		
		urls = ["https://medium.freecodecamp.org/feed", 
		"https://medium.com/feed/javascript-scene", 
		"https://medium.com/feed/reloading", 
		"https://medium.com/feed/dev-channel", 
		"https://blog.prototypr.io/feed", 
		"https://uxdesign.cc/feed",
		"https://medium.com/fed-or-dead",
		"https://hackernoon.com/",
		"https://medium.com/the-vue-point"]

		for url in urls:
			rss = fp.parse(url)
			if "freecodecamp" in url:
				handle_entries(rss.entries, 'free code camp')
			elif "javascript" in url:
				handle_entries(rss.entries, 'javascript scene')
			elif "reloading" in url:
				handle_entries(rss.entries, 'reloading')
			elif "prototypr" in url:
				handle_entries(rss.entries, 'prototypr')
			elif "uxdesign" in url:
				handle_entries(rss.entries, 'uxdesign')
			elif "dev-channel" in url:
				handle_entries(rss.entries, 'dev channel')
			elif "dead" in url:
				handle_entries(rss.entries, 'dead')
			elif "hackernoon" in url:
				handle_entries(rss.entries, 'hackernoon')
			elif "vue-point" in url:
				handle_entries(rss.entries, 'vue point')

		time.sleep(43200)

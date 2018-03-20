import feedparser 
import tweepy 
import store
import time
from datetime import datetime
import psycopg2
import urllib.parse

def tweet(new_entries, publication_name):
	for new_entry in new_entries:

		entry_hashtags = new_entry[1]
		entry_url = new_entry[0] # e.g. https://medium.com/p/99099da313b5

		tweet_msg = entry_hashtags + " " + entry_url

		try:
			api.update_status(tweet_msg)

			# insert entry in db 
			entry_id = entry_url[21:] # e.g. 99099da313b5
			entry_published_date = new_entry[2]
			db_insert_entry(entry_id, entry_published_date, publication_name)
			
		except tweepy.error.TweepError as e:
			print(e.response.text)
			print(entry_id)

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
		cur = db_con.cursor()

		# cleaning date for db insert 
		entry_published_date = str.replace(entry.published, ' GMT', '')
		formated_publication_dt = datetime.strptime(entry_published_date, '%a, %d %b %Y %H:%M:%S')

		# check if entry retrieved already exists
		cur.execute(select_statment,(entry.id[21:],))
		entry_row = cur.fetchone()
		
		# entry is new
		if not entry_row:
			entry_tags = manipulate_entry_tags(entry.tags)
			new_entries.append([entry.id, entry_tags, formated_publication_dt])
		cur.close()

	# tweet new entries
	tweet(new_entries, publication_name)

def init(publication_name):
	rss = feedparser.parse(publications[publication_name])
	handle_entries(rss.entries, publication_name)

def db_insert_entry(entry_id, published_at, publication_name):
	cur = db_con.cursor()
	cur.execute(insert_statment,(entry_id, published_at, publication_name))
	db_con.commit()
	cur.close()

def db_queries():
	insert_statment = "INSERT INTO medium_publications (publication_id, published_at, publication_name) VALUES (%s, %s, %s)"
	select_statment = "SELECT 1 FROM medium_publications WHERE publication_id=%s"

	return (insert_statment, select_statment)

def db_connection_setup():
	""" 
	Setup database
	:return: database connection object
	"""
	# get db url
	urllib.parse.uses_netloc.append("postgres")
	db_url = urllib.parse.urlparse(keys['db_url'])

	# db connection
	try:
		con = psycopg2.connect(
			database=db_url.path[1:],
			user=db_url.username,
			password=db_url.password,
			host=db_url.hostname,
			port=db_url.port
		)
	except psycopg2.OperationalError as e:
		print('Unable to connect!\n{0}').format(e)
		sys.exit(1)
	else: 
		return con

def setup_twitter_api_connection():
	""" 
	Setup twitter api connection
	:return: tweepy api object, to be used for tweeting
	"""
	auth = tweepy.OAuthHandler(keys['cons_key'], keys['cons_secret'])
	auth.set_access_token(keys['access_token'], keys['access_secret'])  
	return tweepy.API(auth)


if __name__ == '__main__':
	publications = store.publications
	keys = store.keys
	
	api = setup_twitter_api_connection()

	db_con = db_connection_setup()
	insert_statment, select_statment = db_queries()

	while True:
		for publication_name in publications:
			init(publication_name)

		time.sleep(43200)

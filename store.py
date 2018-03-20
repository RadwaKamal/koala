import os
keys = {
	"cons_key": os.environ['CONS_KEY'],
	"cons_secret": os.environ['CONS_SECRET'],
	"access_token": os.environ['ACCESS_TOKEN'],
	"access_secret": os.environ['ACCESS_TOKEN_SECRET'],
	"db_url": os.environ['DATABASE_URL']
}

publications = {
	"free_code_camp": "https://medium.freecodecamp.org/feed",
	"javascript_scene": "https://medium.com/feed/javascript-scene",
	"reloading": "https://medium.com/feed/reloading",
	"prototypr": "https://blog.prototypr.io/feed",
	"uxdesign": "https://uxdesign.cc/feed",
	"dev_channel": "https://medium.com/feed/dev-channel",
	"hackernoon": "https://hackernoon.com/feed",
	"vue": "https://medium.com/feed/the-vue-point"
}
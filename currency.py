import json, feedparser, urllib2, urllib
from flask import Flask, render_template, request

DEFAULTS = { 'publication'  : 'f1',
             'city'         : 'London,UK',
             'currency_from': 'GBP',
             'currency_to'  : 'USD'}

RSS_FEEDS = {'bbc' : 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn' : 'http://rss.cnn.com/rss/edition.rss',
             'f1'  : 'http://feeds.bbci.co.uk/sport/formula1/rss.xml?edition=uk'}

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=e9d1da1d7e7e337e7b60d3f2c35e7c49"
CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=a21d13ccc8994973a001de2f74609631"

app = Flask(__name__)

@app.route("/")
def home():
    # get headlines based on user input or default
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)
    
    # get weather based on user inpput or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    
    # get currency based on user input of default
    currency_from = request.args.get('currency_from')
    if not currency_from:
        currency_from = DEFAULTS['currency_from']
    currency_to = request.args.get('currency_to')
    if not currency_to:
        currency_to = DEFAULTS['currency_to']
    rate, currencies = get_rate(currency_from, currency_to)

    return render_template('home.html', articles=articles, 
                                        weather=weather, 
                                        currency_from=currency_from,
                                        currency_to=currency_to,
                                        rate=rate,
                                        currencies=sorted(currencies))

def get_news(query):
    # check to see if the get is one of the rss feeds
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    # create the feed
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']

# function that gets the weather
def get_weather(query):
    # quote handels converting spaces etc.
    query = urllib.quote(query)
    # puts city name in url
    url = WEATHER_URL.format(query)
    # opens the url and gets the json
    data = urllib2.urlopen(url).read()
    # parses the json
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = { "description":parsed["weather"][0]["description"],
                    "tempature": "%.2f" % to_fahrenheit(parsed["main"]["temp"]),
                    "city": parsed["name"],
                    "country": parsed["sys"]["country"]}
    return weather

def get_rate(frm, to):
    all_currency = urllib2.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (("%.2f" % (to_rate/frm_rate)), parsed.keys())

def to_fahrenheit(tempature):
    return tempature * 1.8 + 32

# run app    
if __name__ == '__main__':
    app.run(port=5000, debug=True)

































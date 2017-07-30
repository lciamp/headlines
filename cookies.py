import datetime, json, feedparser, urllib2, urllib
from flask import Flask, render_template, request, make_response

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
    # publications logic
    publication = get_value_with_fallback("publication")
    articles = get_news(publication)
    
    # weather logic
    city = get_value_with_fallback("city")
    weather = get_weather(city)
    
    # currency logic
    currency_from = get_value_with_fallback('currency_from')
    currency_to = get_value_with_fallback('currency_to')
    # get_rate returns a tuple (rate, dict(keys))
    rate, currencies = get_rate(currency_from, currency_to)

    # making the response object for the cookie
    response = make_response(render_template('home.html', 
                                            articles=articles, 
                                            weather=weather, 
                                            currency_from=currency_from,
                                            currency_to=currency_to,
                                            rate=rate,
                                            currencies=sorted(currencies)))

    # date for cookie to expire
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    # set cookie
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    # return response object (template)
    return response
    
# function that gets the news
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

# function that gets currency
def get_rate(frm, to):
    all_currency = urllib2.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (("%.2f" % (to_rate/frm_rate)), parsed.keys())

# fallback function that checks GETS->Cookies->DEFAULTS
def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]



# function that converts C to F
def to_fahrenheit(tempature):
    return tempature * 1.8 + 32






# run app    
if __name__ == '__main__':
    app.run(port=5000, debug=True)

































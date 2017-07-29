import feedparser
from flask import Flask, render_template, request

app = Flask(__name__)

RSS_FEEDS = {'bbc' : 'http://feeds.bbci.co.uk/news/rss.xml',
            'cnn' : 'http://rss.cnn.com/rss/edition.rss',
            'f1' : 'http://feeds.bbci.co.uk/sport/formula1/rss.xml?edition=uk'}

@app.route("/")
def get_news():
    # get the get request
    query = request.args.get("publication")
    # check to see if the get is one of the rss feeds
    if not query or query.lower() not in RSS_FEEDS:
        publication = "f1"
    else:
        publication = query.lower()
    # create the feed
    feed = feedparser.parse(RSS_FEEDS[publication])
    ###first_article = feed['entries'][0]   
    return render_template("home.html", articles=feed['entries'])

# run app    
if __name__ == '__main__':
    app.run(port=5000, debug=True)
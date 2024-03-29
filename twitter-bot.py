import sqlite3
import feedparser
import tweepy
from auth import (consumer_key, consumer_secret, access_token, access_token_secret)

def getRss(twitterApi):
    rssFeeds = { "[NEW BLOG POST]" : "https://www.cadavre.co.uk/index.xml",
                 "[LATEST STRAVA ACTIVITY]" : "https://feedmyride.net/activities/72989925",}
    for postType in rssFeeds:
        url = rssFeeds[postType]
        rssFeed = feedparser.parse(url)
        if rssFeed:
            for item in rssFeed["items"]:
                url = item["link"]
                if "cadavre.co.uk" in url:
                    link = url.replace("cadavre.co.uk", "craigwilkinson.dev")
                    blogTitle = item["title"]
                else:
                    blogTitle = item["title"]
                    link = url
                if checkLink(link):
                    print("Already posted:", link)
                else:
                    twitterLengthTitle = (blogTitle[:160] + '...') if len(blogTitle) > 160 else blogTitle
                    message = postType + " " + twitterLengthTitle + " : " + link
                    saveLink(link)
                    print("Posted:", link)
                    twitterApi.update_status(message)
        else:
            print("Nothing found in feed", rssFeed)

def checkLink(link):
    conn = sqlite3.connect('rssFeed.sqlite')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS feed (link VARCHAR(100), UNIQUE(link));')
    cur.execute("SELECT link FROM feed WHERE link = ?;", (link,) )
    result = cur.fetchone()
    conn.commit()
    conn.close()
    if result is not None:
        return True
    return False

def saveLink(link):
    conn = sqlite3.connect('rssFeed.sqlite')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO feed (link) values (?);", (link,))
    conn.commit()
    conn.close()

def getTwitter():
    authenticationToken = tweepy.OAuthHandler(consumer_key,consumer_secret)
    authenticationToken.set_access_token(access_token,access_token_secret)
    twitter = tweepy.API(authenticationToken)
    return twitter

if __name__ == '__main__':
    twitterApi = getTwitter()
    getRss(twitterApi)

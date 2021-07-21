import sqlite3
import feedparser
import tweepy
from auth import (consumer_key, consumer_secret, access_token, access_token_secret)

def getRss(twitterApi):
    rssFeed = feedparser.parse("https://www.cadavre.co.uk/index.xml")
    if rssFeed:
        for item in rssFeed["items"]:
            # Links are expected to be 100 characters or less
            link = item["link"]
            if checkLink(link):
                print("Already posted:", link)
            else:
                blogTitle = item["title"]
                twitterLengthTitle = (blogTitle[:160] + '...') if len(blogTitle) > 160 else blogTitle
                message = "[NEW BLOG POST] " + twitterLengthTitle + " : " + link
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

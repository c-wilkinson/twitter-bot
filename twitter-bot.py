import sqlite3
import feedparser
import tweepy
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from auth import (consumer_key, consumer_secret, access_token, access_token_secret)

def getRss(twitterApi):
    rssFeeds = { "[NEW BLOG POST]" : "https://www.cadavre.co.uk/index.xml",
                 "[UPCOMING RACE]" : "https://rss.app/feeds/fSiPNAlJig7J4FR3.xml"}
    for type in rssFeeds:
        url = rssFeeds[type]
        rssFeed = feedparser.parse(url)
        if rssFeed:
            for item in rssFeed["items"]:
                url = item["link"]
                if "cadavre.co.uk" in url:
                    link = url.replace("cadavre.co.uk", "craigwilkinson.dev")
                    blogTitle = item["title"]
                else:
                    blogTitle = item["title"].replace(" | Book @ Findarace", "")
                    browser = webdriver.Chrome(ChromeDriverManager().install())
                    browser.get(url)
                    time.sleep(15)
                    link = browser.current_url
                if checkLink(link):
                    print("Already posted:", link)
                else:
                    twitterLengthTitle = (blogTitle[:160] + '...') if len(blogTitle) > 160 else blogTitle
                    message = type + " " + twitterLengthTitle + " : " + link
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

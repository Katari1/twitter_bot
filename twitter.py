__author__ = 'Katari1'

import tweepy
import MySQLdb as mdb
def get_creds(config_file):
    creds={}
    with open(config_file) as i:
        for line in i:
            if line == "\n":
                pass
            else:
                a = line.split()
                id = a[0]
                secret = a[1]
                creds[id] = secret
    return creds
def get_twitter_creds(creds):
    creds = get_creds('twitter_creds.txt')
    auth = tweepy.OAuthHandler(creds['consumer_key:'], creds['consumer_secret:'])
    auth.set_access_token(creds['access_token:'], creds['access_token_secret:'])
    return auth
def get_db_creds(creds):
    creds = get_creds(creds)
    user = creds['db_user:']
    password = creds['db_password:']
    return  user,password
def update_database(messageid,tweet_author,original_tweet_author,original_messageid,tweet_message):
    db_user,db_pass = get_db_creds('db_creds.txt')
    con = mdb.connect('localhost', db_user,db_pass,'twitterbot',use_unicode=True, charset="utf8")
    cur = con.cursor()
    query = "insert into tweets (messageid,tweet_author,original_tweet_author,original_messageid,tweet_message) VALUES (%s,%s,%s,%s,%s)"
    query1 = "insert into tweets (messageid,tweet_author,tweet_message) VALUES (%s,%s,%s)"
    if original_messageid and  original_tweet_author:
        params = (int(messageid),str(tweet_author),str(original_tweet_author),int(original_messageid),tweet_message.encode('utf-8'))
        cur.execute(query,params)
    else:
        params = (int(messageid),str(tweet_author),tweet_message.encode('utf-8'))
        cur.execute(query1,params)
    con.commit()
def find_tweets(searchterm):
    results={}
    search_results = api.search(searchterm)
    for s in search_results:
        try:
            results[s.id] = [s.user.screen_name,s.text,s.retweeted_status.user.screen_name,s.retweeted_status.id]
        except AttributeError:
            results[s.id] = [s.user.screen_name,s.text,None,None]
    return results
def update_status(status):
    api.update_status(str(status))



#Login to Twitter Account
auth = get_twitter_creds('twitter_creds.txt')
api = tweepy.API(auth)

#Search for GSD mentions
results = find_tweets('German Shepherd')

#Process Tweets
for i in results:
    print "Message id: ", i
    print "Author: ", results[i][0]
    print "Original Author: ",results[i][2]
    print "Original Message ID: " ,results[i][3]
    print "Text: ", results[i][1]
    messageid = i
    tweet_author = results[i][0]
    tweet_message = results[i][1]
    original_tweet_author = results[i][2]
    original_messageid = results[i][3]
    update_database(messageid,tweet_author,original_tweet_author,original_messageid,tweet_message)



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
    creds = get_creds('/home/pi/twitter_bot/twitter_creds.txt')
    auth = tweepy.OAuthHandler(creds['consumer_key:'], creds['consumer_secret:'])
    auth.set_access_token(creds['access_token:'], creds['access_token_secret:'])
    return auth
def get_db_creds(creds):
    creds = get_creds(creds)
    user = creds['db_user:']
    password = creds['db_password:']
    return  user,password
def update_database(messageid,tweet_author,original_tweet_author,original_messageid,tweet_message):
    db_user,db_pass = get_db_creds('/home/pi/twitter_bot/db_creds.txt')
    con = mdb.connect('localhost', db_user,db_pass,'twitterbot',use_unicode=True, charset="utf8mb4")
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
def find_tweets(searchterm,count,min_id):
    results={}
    search_results = api.search(searchterm,count = count,since_id = min_id)
    for s in search_results:
        try:
            results[s.id] = [s.user.screen_name,s.text,s.retweeted_status.user.screen_name,s.retweeted_status.id]
        except AttributeError:
            results[s.id] = [s.user.screen_name,s.text,None,None]
    return results
def update_status(status):
    api.update_status(str(status))
def check_duplicate(messageid):
    if messageid is None:
        return False
    db_user,db_pass = get_db_creds('/home/pi/twitter_bot/db_creds.txt')
    con = mdb.connect('localhost', db_user,db_pass,'twitterbot')
    cur = con.cursor()
    cur.execute("select * from tweets where messageid = %s or original_messageid = %s" %(messageid,messageid))
    results = cur.fetchone()
    if results:
        return True
    else:
        return False
def retweet(original_tweet_author,originalid,dbmessageid):
    db_user,db_pass = get_db_creds('/home/pi/twitter_bot/db_creds.txt')
    con = mdb.connect('localhost', db_user,db_pass,'twitterbot')
    cur = con.cursor()
    cur.execute("select tweet_message from messages where id = %s" %dbmessageid)
    message = cur.fetchone()[0]
    url = 'https://twitter.com/%s/status/%s' %(original_tweet_author,originalid)
    print '@%s %s  %s' %(original_tweet_author,message,url)
    update_status('@%s %s  %s' %(original_tweet_author,message,url))
def get_max_messageid():
    db_user,db_pass = get_db_creds('/home/pi/twitter_bot/db_creds.txt')
    con = mdb.connect('localhost', db_user,db_pass,'twitterbot')
    cur = con.cursor()
    cur.execute("select max(messageid) from tweets")
    results = cur.fetchone()[0]
    return results
#Login to Twitter Account
auth = get_twitter_creds('/home/pi/twitter_bot/twitter_creds.txt')
api = tweepy.API(auth)

#get max messageid
min_id = get_max_messageid()
count = 100
#Search for GSD mentions
results = find_tweets('German Shepherd',count,min_id)
results1 = find_tweets('lostdog',count,min_id)

#Process Tweets
for i in results:
    print "**********************************"
    print "Message id: ", i
    #print "Author: ", results[i][0]
    print "Original Author: ",results[i][2]
    print "Original Message ID: " ,results[i][3]
    print "Text: ", results[i][1].encode('utf-8')
    messageid = i
    tweet_author = results[i][0]
    tweet_message = results[i][1]
    original_tweet_author = results[i][2]
    original_messageid = results[i][3]
    #Check if duplicat of new message
    if check_duplicate(messageid) or check_duplicate(original_messageid):
        print "It is a duplicate....I am SKIPPING"
        continue
   #Check if retweet
    elif original_tweet_author is not None and original_messageid is not None:
        print "This is a retweet......Processing"
        if 'lost dog' in tweet_message or 'Lost Dog'in tweet_message or 'lostdog' in tweet_message or 'LostDog' in tweet_message:
            retweet(original_tweet_author,original_messageid,1)
            update_database(messageid,tweet_author,original_tweet_author,original_messageid,tweet_message)    
        else:
            retweet(original_tweet_author,original_messageid,2)
            update_database(messageid,tweet_author,original_tweet_author,original_messageid,tweet_message)    
    #Normal Tweet
    else:
        print "This is a normal tweet"
        #if 'lost dog' or 'Lost Dog' or 'lostdog' or 'LostDog' in tweet_message:
        if 'lost dog' in tweet_message or 'Lost Dog'in tweet_message or 'lostdog' in tweet_message or 'LostDog' in tweet_message:
            retweet(tweet_author,messageid,1)
            update_database(messageid,tweet_author,original_tweet_author,original_messageid,tweet_message)    
        else:
            retweet(tweet_author,messageid,2)
            update_database(messageid,tweet_author,original_tweet_author,original_messageid,tweet_message)    



#Process Tweets
for i in results1:
    print "**********************************"
    print "Message id: ", i
    #print "Author: ", results[i][0]
    print "Original Author: ",results1[i][2]
    print "Original Message ID: " ,results1[i][3]
    print "Text: ", results1[i][1].encode('utf-8')
    messageid = i
    tweet_author = results1[i][0]
    tweet_message = results1[i][1]
    original_tweet_author = results1[i][2]
    original_messageid = results1[i][3]
    #Check if duplicat of new message
    if check_duplicate(messageid) or check_duplicate(original_messageid):
        print "It is a duplicate....I am SKIPPING"
        continue
   #Check if retweet
    elif original_tweet_author is not None and original_messageid is not None:
        print "This is a retweet......Processing"
        if 'lost dog' in tweet_message or 'Lost Dog'in tweet_message or 'lostdog' in tweet_message or 'LostDog' in tweet_message:
            retweet(original_tweet_author,original_messageid,1)
            update_database(messageid,tweet_author,original_tweet_author,original_messageid,tweet_message)    
        else:
            retweet(original_tweet_author,original_messageid,2)
            update_database(messageid,tweet_author,original_tweet_author,original_messageid,tweet_message)    
    #Normal Tweet
    else:
        print "This is a normal tweet"
        #if 'lost dog' or 'Lost Dog' or 'lostdog' or 'LostDog' in tweet_message:
        if 'lost dog' in tweet_message or 'Lost Dog'in tweet_message or 'lostdog' in tweet_message or 'LostDog' in tweet_message:
            retweet(tweet_author,messageid,1)
            update_database(messageid,tweet_author,original_tweet_author,original_messageid,tweet_message)    
        else:
            retweet(tweet_author,messageid,2)

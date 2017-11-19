__author__ = 'vnagrani'

import tweepy
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
def loginwithcreds(creds):
    creds = get_creds('twitter_creds.txt')
    auth = tweepy.OAuthHandler(creds['consumer_key:'], creds['consumer_secret:'])
    auth.set_access_token(creds['access_token:'], creds['access_token_secret:'])
    return auth
def updatestatus(status):
    api.update_status(str(status))


auth = loginwithcreds('twitter_creds.txt')
api = tweepy.API(auth)

search_results = api.search('German Shepherd')
for s in search_results:
    print "***************************************"
    print s.text
    print s.user.screen_name
    print s.id
    print "***************************************"


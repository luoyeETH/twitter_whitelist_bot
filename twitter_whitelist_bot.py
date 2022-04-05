import tweepy
import time

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import random

# 创建数据库连接
engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/db?charset=utf8')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

consumer_key = '替换成你的consumer_key'
consumer_secret = '替换成你的consumer_secret'

key = '替换成你的key'
secret = 'secret'

auth = tweepy.OAuthHandler(consumer_key,
                           consumer_secret)
auth.set_access_token(key,
                      secret)

api = tweepy.API(auth)


class TwitterBot(Base):
    __tablename__ = "twitter_bot"  # 数据库中保存的表名字

    id = Column(Integer, index=True, primary_key=True)
    # Integer保存不了长ID,改用varchar类型
    tweet_id = Column(String(30), nullable=True)
    screen_name = Column(String(200), nullable=True)
    url = Column(String(300), nullable=True)
    updated_at = Column(DateTime, default=datetime.now)
  
  
# 创建数据库表，只需要执行一次
# Base.metadata.create_all(engine)


while True:
    print("@@@@@@@@@@@@@@@@@@@@Start@@@@@@@@@@@@@@@@@@@@@@")
    print(datetime.utcnow())

    public_tweets = []

    try:
        # public_tweets = api.home_timeline(count=50, tweet_mode='extended')
        # public_tweets = api.user_timeline(screen_name='reinkerte31', count=3, tweet_mode='extended')
        # 获取列表中的前100条推文保存到public_tweets中 list_id为推特列表
        public_tweets = api.list_timeline(list_id=1444116199432806401, count=100, tweet_mode='extended')

    except Exception as e:
        print(str(e))
        print("sleep 60s")
        time.sleep(60)
        continue

    for tweet in public_tweets:

        if session.query(TwitterBot).filter(TwitterBot.tweet_id == tweet.id).count() > 0:
            print(str(tweet.id) + "已存在。")
            continue

        print("id=" + str(tweet.id))
        print("created_at=" + str(tweet.created_at))

        p = tweet.full_text
        keywords = 'Follow,Like,RT,Tag,Retweet,FOLLOW,LIKE,RETWEET,TAG,关注,转推,喜欢'

        count = sum([1 if w in p and w else 0 for w in keywords.split(',')])
        if count > 1:
            print("---------------------Found 白名单推文")
            print(tweet.full_text)

            user_mentions = tweet.entities['user_mentions']
            for friend in user_mentions:
                screen_name = friend['screen_name']
                # 将zlexdl替换为自己的screen_name
                screen_names = ["zlexdl", screen_name]
                friendships = api.lookup_friendships(screen_name=screen_names)

                if len(friendships) > 1:

                    if not friendships[1].is_following:
                        print("Following <" + screen_name + "> ")
                        api.create_friendship(screen_name=screen_name)

                        print("Follow <" + screen_name + "> success!")
                    else:
                        print("Already following <" + screen_name + "> !")

            try:
                api.create_favorite(id=tweet.id_str)
            except Exception as e:
                print(str(e))
            
            # tweets中保存了转推的文案，修改成自己的，可以多添加几条
            tweets = [
                'It would be an honor to be a part of your project! You are frontrunners in the game, you have in me a loyal supporter who always gives. Keep it up, much love! @petechang1113 @abc_noName1 @kevinLiuA1110 @tastydogclub @Adidasshow78 @mike1021031',
                '@Tony34108142 @waynechen2032 @Macnotmc1 @sodassdf @Ro0dZz @chou22389047 @stone20213  if my luck could ever carry me now would be the time',
                '@itivitimonster @Malachi007 @Ivanyichen @SawadyQ @jayfans15 @RoyLiu68727021 @havel_wu Excited to be a part of it. Hopefully your first following will be WL and OGd for appreciation 🙏']

            message = random.choice(tweets)
            url = str("https://twitter.com/" + tweet.user.screen_name + "/status/" + tweet.id_str)
            print(url)
            re = api.update_status(message, attachment_url=url)
            print("转推结果：" + str(re.is_quote_status))

            twitterBot = TwitterBot(
                screen_name=tweet.user.screen_name,
                url=url,
                tweet_id=tweet.id)
            print(tweet.id)
            session.add(twitterBot)
            session.commit()

            print("time.sleep(300) start time=" + str(datetime.utcnow()))
            time.sleep(300)

    print("time.sleep(300) start time=" + str(datetime.utcnow()))
    time.sleep(300)
    print("@@@@@@@@@@@@@@@@@@@@END@@@@@@@@@@@@@@@@@@@@@@")


import sys
import json
import datetime
import tweepy
import urllib.request
import snscrape.modules.twitter as sntwitter
import pandas as pd
import settings
from requests_oauthlib import OAuth1Session
import identifies_image as idf
from requests_oauthlib import OAuth1Session
from urllib.parse import parse_qsl

base_url = 'https://api.twitter.com/'
request_token_url = base_url + 'oauth/request_token'
authenticate_url = base_url + 'oauth/authenticate'
access_token_url = base_url + 'oauth/access_token'
base_json_url = 'https://api.twitter.com/1.1/%s.json'

class TwiterGateway:
    # コンストラクタ
    def __init__(self):
        # フィールド

        # twitter認証
        auth = tweepy.OAuthHandler(
            settings.API_KEY, settings.API_SECRET_KEY)

        auth.set_access_token(settings.ACCESS_TOKEN,
                              settings.ACCESS_TOKEN_SECRET)

        # TODO 認証方式確立するまでは仮でaccesstokenを設定
        self.twitter = OAuth1Session(
            settings.API_KEY,
            settings.API_SECRET_KEY,
            settings.ACCESS_TOKEN,
            settings.ACCESS_TOKEN_SECRET)

        self.api = tweepy.API(auth)

    def get_twitter_request_token(self):

        try:
            # Twitter Application Management で設定したコールバックURLsのどれか
            oauth_callback = "http://localhost:3000/"

            twitter = OAuth1Session(settings.API_KEY, settings.API_SECRET_KEY)

            response = twitter.post(
                request_token_url,
                params={'oauth_callback': oauth_callback}
            )

            if response.status_code >400:
                raise Exception("twitterへのアクセスに失敗しました。")

            # responseからリクエストトークンを取り出す
            request_token = dict(parse_qsl(response.content.decode("utf-8")))

            # リクエストトークンから連携画面のURLを生成
            authenticate_url = "https://api.twitter.com/oauth/authenticate"
            authenticate_endpoint = '%s?oauth_token=%s' \
                % (authenticate_url, request_token['oauth_token'])


        except Exception as e:
            raise Exception(e)

        return authenticate_endpoint

    def get_twitter_access_token(self,request):

        oauth_token = request.params.get("oauth_token", "")
        oauth_verifier = request.params.get("oauth_verifier", "")

        twitter = OAuth1Session(
            settings.API_KEY,
            settings.API_SECRET_KEY,
            oauth_token,
            oauth_verifier,
        )

        response = twitter.post(
            access_token_url,
            params={'oauth_verifier': oauth_verifier}
        )

        access_token = dict(parse_qsl(response.content.decode("utf-8")))

        return access_token


    def get_user_favlist(self, user_id, max_count):
        ret_list = []
        try:
            url = "https://api.twitter.com/1.1/favorites/list.json?"
            params = {"screen_name": user_id,
                      "count": 5000}

            res = self.twitter.get(url, params=params)

            break_roop = False
            if res.status_code == 200:
                tweets = json.loads(res.text)
                for tweet in tweets:
                    # メディアなしツイートの場合
                    if ('extended_entities' not in tweet):
                        continue

                    # ファボ数フィルタ
                    if tweet["favorite_count"] < 5:
                        continue

                    entities = tweet["extended_entities"]
                    if 'media' in entities:
                        url_list = []

                        user_info = tweet["user"]
                        datetime_obj_utc = datetime.datetime.strptime(
                            tweet["created_at"], '%a %b %d %H:%M:%S %z %Y')

                        for media in entities['media']:
                            if media["type"] == 'photo':
                                media_url = media['media_url']
                                url_list.append(media_url)

                        ret_data = {
                            "ID": tweet["id"],
                            "UseID": user_info["screen_name"],
                            "DateTime": datetime_obj_utc.strftime('%Y-%m-%d %H:%M:%S'),
                            "Url": url_list
                        }
                        ret_list.append(ret_data)

                        if(len(ret_list) == max_count):
                            break_roop = True
                            break

                    if(break_roop):
                        break

            else:
                raise Exception("failed to access twitter.com")

        except Exception as e:
            raise Exception(e)

        return ret_list

    def get_identified_user_favlist(self, user_id, max_count, identifies_image_size):
        ret_list = []
        try:
            url = "https://api.twitter.com/1.1/favorites/list.json?"
            params = {"screen_name": user_id,
                      "count": 5000}

            res = self.twitter.get(url, params=params)

            break_roop = False
            if res.status_code == 200:
                tweets = json.loads(res.text)
                for tweet in tweets:
                    # メディアなしツイートの場合
                    if ('extended_entities' not in tweet):
                        continue

                    # ファボ数フィルタ
                    if tweet["favorite_count"] < 5:
                        continue

                    entities = tweet["extended_entities"]
                    if 'media' in entities:
                        illust_url_list = []
                        photo_url_list = []
                        is_photo_media = False

                        user_info = tweet["user"]
                        datetime_obj_utc = datetime.datetime.strptime(
                            tweet["created_at"], '%a %b %d %H:%M:%S %z %Y')

                        for media in entities['media']:
                            if media["type"] == 'photo':
                                is_photo_media = True
                                media_url = media['media_url']

                                if idf.do_identifiesImage(media_url + "?format=jpg&name=" + identifies_image_size) :
                                    illust_url_list.append(media_url)
                                else:
                                    photo_url_list.append(media_url)

                        # 画像ツイート以外はレスポンスしない
                        if is_photo_media :
                            ret_data = {
                                "ID": tweet["id"],
                                "UseID": user_info["screen_name"],
                                "DateTime": datetime_obj_utc.strftime('%Y-%m-%d %H:%M:%S'),
                                "illustUrlList": illust_url_list,
                                "PhotoUrlList" : photo_url_list
                            }
                            ret_list.append(ret_data)

                        if(len(ret_list) == max_count):
                            break_roop = True
                            break

                    if(break_roop):
                        break

            else:
                raise Exception("failed to access twitter.com")

        except Exception as e:
            raise Exception(e)

        return ret_list

    def get_timeline_image_tweets(self):
        """タイムライン画像取得メソッド
         ツイッターのユーザタイムラインの画像付きツイート
         を取得します

        Args:
            なし
        Returns:
           list[]: 取得したツイートのJsonオブジェクト
        Raises:
            Exception: tweepy実行に失敗した場合

        Note:
            リクエストしすぎるとtwitterのAPI制限に引っ掛かるため呼び出しは必要最小限とすること
        """

        ret_list = []

        try:
            for tweet in tweepy.Cursor(self.api.home_timeline).items(5):
                if 'media' in tweet.entities:
                    for media in tweet.extended_entities['media']:
                        if media["type"] == 'photo' and tweet.favorite_count > 5:
                            media_url = media['media_url']

                            tweetData = {
                                "ID": tweet.id,
                                "UseID": tweet.user.screen_name,
                                "DateTime": tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                                "Url": media_url
                            }
                            ret_list.append(tweetData)
        except Exception as e:
            raise Exception(e)

        return ret_list

    def get_list_timeline_image_tweets(self, max_count , req_list_id, req_since_id, req_max_id):
        """
         ツイッターのリストの画像付きツイート
         を取得します

        Args:
            req_list_id:取得対象のリストID
        Returns:
           list[]: 取得したツイートのJsonオブジェクト
        Raises:
            Exception: twitterへのアクセスエラー時

        Note:
            リクエストしすぎるとtwitterのAPI制限に引っ掛かるため呼び出しは必要最小限とすること
        """

        ret_list = []
        try:
            if req_since_id != '' and req_max_id != '':
                res = tweepy.Cursor(self.api.list_timeline, owner="watorin72", list_id=req_list_id,since_id = req_since_id ,max_id = req_max_id, include_rts = False).items(100)
            elif req_since_id != '':
                res = tweepy.Cursor(self.api.list_timeline, owner="watorin72", list_id=req_list_id,since_id = req_since_id , include_rts = False).items(100)
            elif req_max_id != '':
                res = tweepy.Cursor(self.api.list_timeline, owner="watorin72", list_id=req_list_id ,max_id = req_max_id, include_rts = False).items(100)
            else:
                res = tweepy.Cursor(self.api.list_timeline, owner="watorin72", list_id=req_list_id ,include_rts = False).items(100)

            for tweet in res:
                if 'media' in tweet.entities:
                    media_url_list = []
                    for media in tweet.extended_entities['media']:
                        if media["type"] == 'photo' and tweet.favorite_count > 0:
                            media_url_list.append(media['media_url'])

                    if len(media_url_list) > 0:
                        tweetData = {
                            "ID": tweet.id,
                            "UseID": tweet.user.screen_name,
                            "DateTime": tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            "Url": media_url_list
                        }
                        ret_list.append(tweetData)

                if (len(ret_list) == max_count):
                      break
        except Exception as e:
            raise Exception(e)

        return ret_list

    def get_user_image_tweets(self,
                              user_id,
                              opt_since,
                              opt_until,
                              max_count
                              ):
        # Creating list to append tweet data
        tweets_list = []

        # 取得上限件数
        if(max_count == 0):
            max_count = 1000

        search_option_list = []

        # ユーザ指定
        search_option_list.append('from:' + user_id)

        # 期間の指定
        if(opt_since == '' and opt_until == ''):
            d_today = datetime.date.today()

            td = datetime.timedelta(weeks=4)
            # 未指定の場合、検索範囲を1ヶ月以内に設定
            opt_since = (d_today - td).strftime('%Y-%m-%d')
            opt_until = d_today.strftime('%Y-%m-%d')

        search_option_list.append('since:' + opt_since)
        search_option_list.append('until:' + opt_until)

        # 取得メディアの指定
        search_option_list.append('filter:images')

        # 除外するツイート設定
        search_option_list.append('exclude:retweets')

        query = ' '.join(search_option_list)

        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i >= max_count:
                break
            tweets_list.append([tweet.date, tweet.id, tweet.content,
                                tweet.media, tweet.user.username])

        # Creating a dataframe from the tweets list above
        tweets_df = pd.DataFrame(tweets_list, columns=[
            'Datetime', 'Tweet Id', 'Text', 'Media', 'Username'])

        return tweets_df

    def conv_tweets_df_to_jsonList(self, tweets_df):
        # 検索対象のツイートを取得
        ret_list = []

        for datetime, tweetId, userName, media in zip(tweets_df['Datetime'], tweets_df['Tweet Id'], tweets_df['Username'], tweets_df['Media']):
            if media is not None:
                media_urls = []
                for mediaData in media:
                    if mediaData.type == 'photo':
                        media_urls.append(mediaData.fullUrl)

                tweetData = {
                    "id": tweetId,
                    "useID": userName,
                    "dateTime": datetime._repr_base,
                    "url": media_urls
                }
                ret_list.append(tweetData)
        return ret_list

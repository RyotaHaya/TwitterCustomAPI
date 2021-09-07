import responder
import json
import twitter
import urllib
import json
import re

api = responder.API()

class IndexController:
    async def on_get(self, req, resp):
        resp.content = api.template('index.html')

class LoginController:
    async def on_get(self, req, resp):
        resp.content = api.template('login.html')

class SampleClass:
    async def on_get(self, req, resp):
        # 何かしらの処理
        resp.text = "Hello root Page"


class SampleGet:
    async def on_get(self, req, resp):
        # 何かしらの処理
        resp.media = {
            "status": True,
            "result": "ss"
        }

class TwitterAuth:
    async def on_get(self, req, resp):
        try:
            gate = twitter.TwiterGateway()
            # 何かしらの処理
            token_url = gate.get_twitter_request_token()
            resp.media = {
                "url": token_url,
            }
        except Exception as e:
            resp.status_code = api.status_codes. HTTP_500

            resp.media = {
            "errors": [
            {
                "LocalizedMessage": str(e),
                "code": 500
            }
            ]
        }

class TwitterLogin:
    async def on_get(self, req, resp):
        # 何かしらの処理
        resp.media = {
            "status": True,
            "result": "ss"
        }


class TwitterListTimeLineImages:
    async def on_get(self, req, resp):
        # 何かしらの処理
        try:
            list_id = req.params.get("listId", "")

            if(list_id == ""):
                raise Exception("param ""listId"" is required.")

            #init = req.params.get("dispInit", True)
            max_count = int(req.params.get("maxCount", 100))

            # 取得範囲の指定(指定したIDと対応する)
            max_id = req.params.get("maxId", "")
            since_id = req.params.get("sinceId", "")

            gate = twitter.TwiterGateway()
            try:
                image_tweets = gate.get_list_timeline_image_tweets(max_count,list_id,since_id,max_id)
            except Exception as e:
                raise Exception(e)

            resp.headers["Content-Type"] = "application/json; charset=UTF-8"
            resp.status_code = 200

            resp.media = {
                "UserId": "",
                "TotalCount": len(image_tweets),
                "ImageTweetList": image_tweets
            }

        except Exception as e:
            resp.status_code = api.status_codes. HTTP_500

            resp.media = {
                "errors": [
                    {
                        "LocalizedMessage": str(e),
                        "StatusCode": resp.status_code
                    }
                ]
            }

class TwitterUserImages:
    async def on_get(self, req, resp):

        try:
            user_id = req.params.get("userId", "")
            if(user_id == ""):
                raise Exception("param ""userId"" is required.")

            date_since = req.params.get("since", "")
            date_until = req.params.get("until", "")
            max_cnt = int(req.params.get("maxCount", 0))

            gate = twitter.TwiterGateway()
            # 特定ユーザの画像ツイートIDを取得
            tweets_df = gate.get_user_image_tweets(
                user_id, date_since, date_until, max_cnt)

            image_tweets_id_list = gate.conv_tweets_df_to_jsonList(tweets_df)

            resp.headers["Content-Type"] = "application/json; charset=UTF-8"
            resp.status_code = 200

            resp.media = {
                "userId": user_id,
                "totalCount": len(image_tweets_id_list),
                "imageTweetId": image_tweets_id_list
            }

        except Exception as e:
            resp.status_code = api.status_codes. HTTP_500

            resp.media = {
                "errors": [
                    {
                        "message": str(e),
                        "code": 500
                    }
                ]
            }


class TwitterUserFavImages:
    async def on_get(self, req, resp):

        try:

            oauth = req.headers["Authorization"]
            token_list = re.split('\s', oauth)

            token_list = re.split('\s', oauth)
            token = token_list[1]
            token_secret = token_list[2]

            user_id = req.params.get("userId", "")

            if(user_id == ""):
                raise Exception("param ""userId"" is required.")

            max_cnt = int(req.params.get("maxCount", 100))

            exe_identifies_image = req.params.get("identifieImage", "")

            gate = twitter.TwiterGateway()
            # 特定ユーザの画像ツイートIDを取得
            if exe_identifies_image == "yes" :
                identifies_image_size = req.params.get("imageSIze", "small")
                image_tweets = gate.get_identified_user_favlist(user_id, max_cnt, identifies_image_size)
            else :
                image_tweets = gate.get_user_favlist(user_id, max_cnt)


            resp.media = {
                "userId": user_id,
                "totalCount": len(image_tweets),
                "imageTweetId": image_tweets
            }

        except Exception as e:
            resp.status_code = api.status_codes. HTTP_500

            resp.media = {
                "errors": [
                    {
                        "message": str(e),
                        "code": 500
                    }
                ]
            }

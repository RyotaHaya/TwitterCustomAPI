import responder
import handlers

api = responder.API(
    cors=True,
    cors_params={
        'allow_origins': ['*'],
        'allow_methods': ['*'],
        'allow_headers': ['*'],
    }
)


api.add_route('/', handlers.IndexController)
api.add_route('/hello', handlers.SampleClass)
api.add_route('/get', handlers.SampleGet)

api.add_route('/adminlogin', handlers.LoginController)

api.add_route('/api/twitter/requestToken', handlers.TwitterAuth)

# usering tweepy
api.add_route('/api/GetListTimeLineImages', handlers.TwitterListTimeLineImages)
api.add_route('/api/GetUserFavImages', handlers.TwitterUserFavImages)

# getOldtweet
api.add_route('/api/GetUserImageTweets', handlers.TwitterUserImages)

if __name__ == '__main__':
    api.run(address='0.0.0.0', port=5040, debug=False)

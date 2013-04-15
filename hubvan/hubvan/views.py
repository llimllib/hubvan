import datetime
from collections import namedtuple
from itertools import islice

import requests
import redis
from pygithub3 import Github

from django.shortcuts import render, redirect

from . import settings
from hubinterface import ShittyGithub, AllEventIterator

#hot or SUPER LAME?
REDIS = redis.StrictRedis(
            host = settings.REDIS_HOST,
            port = settings.REDIS_PORT,
            db   = settings.REDIS_DB
        )

def index(request):
    # View code here...
    return render(request, 'index.html')

def user(request, user):
    # First, get an oauth token.
    # 1. Look in the cache, if it's there, try it
    # 2. If not, enter oauth flow (or some such)
    access_token = REDIS.get("access_token-%s" % user)

    if not access_token:
        #probably ought to redirect to github oauth page
        return render(request, 'error.html', {'error': "No token for %s" % user})

    hub = ShittyGithub(token=access_token)
    user = hub.get_user()
    repos = map(lambda x: x["full_name"], hub.get_repos())
    events = list(islice(AllEventIterator(hub, repos), 20))

    return render(request, 'user.html', {'user':   user,
                                         'events': events,
                                        })

def oauth_callback(request):
    code = request.GET['code']
    res = requests.post("https://github.com/login/oauth/access_token", {
                            "client_id": settings.GITHUB_CLIENT_ID,
                            "client_secret": settings.GITHUB_CLIENT_SECRET,
                            "code": code,
                        },
                        headers={"Accept": "application/json"})
    resbody = res.json
    print "got: ", res, resbody

    if 'error' in resbody:
        #TODO: figure out logging
        return render(request, 'error.html', {'error': resbody["error"]})

    token = resbody['access_token']
    username = Github(token=token).users.get().login
    REDIS.set("access_token-%s" % username, token)
    return redirect('/%s?access_token=%s' % (username, token))

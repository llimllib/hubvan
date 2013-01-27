import time
from collections import namedtuple

import requests
import github
import redis

from django.shortcuts import render, redirect

from . import settings

#hot or SUPER LAME?
REDIS = redis.StrictRedis(
            host = settings.REDIS_HOST,
            port = settings.REDIS_PORT,
            db   = settings.REDIS_DB
        )

def index(request):
    # View code here...
    return render(request, 'index.html')

class DisplayEvent(object):
    def __init__(self, evt):
        self.evt = evt
        self.sortdate = evt.created_at

    def displayable(self):
        return len(str(self)) > 0

    def __str__(self):
        if   self.evt.type == 'WatchEvent':
            return '<a href="%s">%s</a> %s watching <a href="%s">%s</a>' % (
                    self.evt.actor.html_url,
                    self.evt.actor.login,
                    self.evt.payload['action'],
                    self.evt.repo.html_url,
                    self.evt.repo.name)

        elif self.evt.type == 'ForkEvent':
            return '<a href="%s">%s</a> forked <a href="%s">%s</a>' % (
                    self.evt.actor.html_url,
                    self.evt.actor.login,
                    self.evt.repo.html_url,
                    self.evt.repo.name)

        elif self.evt.type == 'PullRequestEvent':
            if not 'url' in self.evt.payload['pull_request']:
                #some old github pull requests don't include a URL. They do
                #have the pull request number, so follow that to a URL
                pull_url = self.evt.repo.get_pull(self.evt.payload["pull_request"]["number"]).html_url
            else:
                pull_url = self.evt.payload['pull_request']['html_url']

            return '<a href="%s">%s</a> %s <a href="%s">pull request %s</a> on <a href="%s">%s</a>' % (
                    self.evt.actor.html_url,
                    self.evt.actor.login,
                    self.evt.payload['action'],
                    pull_url,
                    self.evt.payload['number'],
                    self.evt.repo.html_url,
                    self.evt.repo.name)
        elif self.evt.type == 'IssuesEvent':
            return '<a href="%s">%s</a> %s <a href="%s">issue %s</a> on <a href="%s">%s</a>' % (
                    self.evt.actor.html_url,
                    self.evt.actor.login,
                    self.evt.payload['action'],
                    self.evt.payload['issue']['html_url'],
                    self.evt.payload['issue']['number'],
                    self.evt.repo.html_url,
                    self.evt.repo.name)
        elif self.evt.type == 'IssueCommentEvent':
            print self.evt.payload
            if 'action' not in self.evt.payload:
                #old IssueCommentEvents lack a whole bunch of crap. Here's the
                #entire payload of one such:
                # {u'repo': u'llimllib/bloomfilter-tutorial', u'comment_id': 1223476, u'issue_id': 939033, u'actor_gravatar': u'939848268c73b4049f90ee0703df7c68', u'actor': u'abachman'}
                #
                #For now, just toss it. Can't immediately see how to go from "issue_id"
                #to an issue with the github API.
                continue

            #TODO probably want to use a bit of the comment or some shit
            return '<a href="%s">%s</a> %s a comment on <a href="%s">issue %s</a> of <a href="%s">%s</a>' % (
                    self.evt.actor.html_url,
                    self.evt.actor.login,
                    self.evt.payload['action'],
                    self.evt.payload['issue']['html_url'],
                    self.evt.payload['issue']['number'],
                    self.evt.repo.html_url,
                    self.evt.repo.name)
        return ""


def user(request, user):
    # First, get an oauth token.
    # 1. Look in the cache, if it's there, try it
    # 2. If not, enter oauth flow (or some such)
    access_token = REDIS.get("access_token-%s" % user)

    if not access_token:
        #probably ought to redirect to github oauth page
        return render(request, 'error.html', {'error': "No token for %s" % user})

    # View code here...
    # 1. List user repos (and forks? Do I want to know if A forks
    #                     repo R and B forks/commits on A/R?)
    # 2. For each repo, get stars/forks/commits by other users
    # 3. merge all those lists
    # 4. Display the last x
    import github
    g = github.Github(access_token)
    u = g.get_user(user)
    repos = list(u.get_repos())

    #TODO: be much less wasteful in what events we grab! We'll murder our
    #      API rate limit VERY QUICKLY with this.
    eventlists = [list(r.get_events()) for r in repos]

    #TODO: cache some shit dude. Maybe create a custom github lib
    #      with caching? TOO RADICAL MAYBE WHOA

    #the list of events we care about
    events = []
    for eventlist in eventlists:
        for event in eventlist:
            #we don't want to see what we did.
            if event.actor.login == user: continue

            #if we don't know how to handle this event, just continue.
            e = DisplayEvent(event)
            if not e.displayable():
                print "don't know how to handle event type %s" % event.type
                continue

            events.append(e)

    events.sort(key=lambda x: x.sortdate)
    events.reverse()

    return render(request, 'user.html', {'user':   user,
                                         'events': events,
                                        })

# http://hubvan.com/oauth_callback?code=736be3911d761bcb91f2
def oauth_callback(request):
    code = request.GET['code']
    res = requests.post("https://github.com/login/oauth/access_token", {
                            "client_id": settings.GITHUB_CLIENT_ID,
                            "client_secret": settings.GITHUB_CLIENT_SECRET,
                            "code": code,
                        },
                        headers={"Accept": "application/json"})
    resbody = res.json()
    print "got: ", res, resbody

    if 'error' in resbody:
        #TODO: figure out logging
        return render(request, 'error.html', {'error': resbody["error"]})

    token = resbody['access_token']
    username = github.Github(token).get_user().login
    REDIS.set("access_token-%s" % username, token)
    return redirect('/%s?access_token=%s' % (username, token))

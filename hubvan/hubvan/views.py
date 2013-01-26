from django.shortcuts import render, redirect
import requests

from . import settings

def index(request):
    # View code here...
    return render(request, 'index.html')

def user(request, user):
    # First, get an oauth token.
    # 1. Look in the cache, if it's there, try it
    # 2. If not, enter oauth flow (or some such)

    # stick temp code here
    access_token = '6be5763c4cfe61a5996cbf6ce1ee706d32489a34'

    # View code here...
    # 1. List user repos (and forks? Do I want to know if A forks
    #                     repo R and B forks/commits on A/R?)
    # 2. For each repo, get stars/forks/commits by other users
    # 3. merge all those lists
    # 4. Display the last x
    import github
    g = github.Github()
    u = g.get_user(user)
    repos = list(u.get_repos())
    evs = [list(r.get_events()) for r in repos]

    #the list of events we care about
    events = []
    for eventlist in evs:
        events.extend(e for e in evs if e.actor.login != user)
    return render(request, 'user.html', {'user': user, 'events': events})

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

    #TODO: how the eff do I get a user's name here?
    return redirect('/wtfistheusername?access_token=' + resbody["access_token"])

# -*- coding: utf-8 -*-
from datetime import datetime

import requests

GITHUB_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

class DisplayEvent(object):
    def __init__(self, event_json):
        self.event_json = event_json

        self.dt = datetime.strptime(event_json["created_at"], GITHUB_DATE_FORMAT)

        #required attributes. All items will have actor and actor_url
        try:
            self.actor = event_json["actor"]["login"]
            self.actor_url = "https://github.com/{0}".format(self.actor)
            self.repo_name = event_json["repo"]["name"]
            self.repo_url = "https://github.com/{0}".format(self.repo_name)
        except KeyError:
            print event_json
            raise

    def __repr__(self): return str(self)

class ForkEvent(DisplayEvent):
    def __init__(self, event_json):
        DisplayEvent.__init__(self, event_json)

    def __str__(self):
        return '<a href="{0}">{1}</a> forked <a href="{2}">{3}</a>'.format(
                self.actor_url,
                self.actor,
                self.repo_url,
                self.repo_name)

class PullRequestEvent(DisplayEvent):
    def __init__(self, event_json):
        DisplayEvent.__init__(self, event_json)

        try:
            self.action = event_json["payload"]["action"]
            self.pull_number = event_json["payload"]["pull_request"]["number"]
        except KeyError:
            print event_json
            raise

        self.pull_url = "https://github.com/{0}/pull/{1}".format(self.repo_name, self.pull_number)

    def __str__(self):
        return '<a href="{0}">{1}</a> {2} <a href="{3}">pull request {4}</a> on <a href="{5}">{6}</a>'.format(
                self.actor_url,
                self.actor,
                self.action,
                self.pull_url,
                self.pull_number,
                self.repo_url,
                self.repo_name)

class IssuesEvent(DisplayEvent):
    def __init__(self, event_json):
        DisplayEvent.__init__(self, event_json)

        try:
            self.action = event_json["payload"]["action"]
            self.issue_url = event_json["payload"]["issue"]["html_url"]
            self.issue_num = event_json["payload"]["issue"]["number"]
        except KeyError:
            print event_json
            raise

    def __str__(self):
        return '<a href="{0}">{1}</a> {2} <a href="{3}">issue {4}</a> on <a href="{5}">{6}</a>'.format(
                self.actor_url,
                self.actor,
                self.action,
                self.issue_url,
                self.issue_num,
                self.repo_url,
                self.repo_name)

class IssueCommentEvent(DisplayEvent):
    def __init__(self, event_json):
        DisplayEvent.__init__(self, event_json)

        try:
            self.action = event_json["payload"]["action"]
            self.issue_url = event_json["payload"]["issue"]["html_url"]
            self.issue_num = event_json["payload"]["issue"]["number"]
        except KeyError:
            print event_json
            raise

    def __str__(self):
        return '<a href="{0}">{1}</a> {2} a comment on <a href="{3}">issue {4}</a> of <a href="{5}">{6}</a>'.format(
                self.actor_url,
                self.actor,
                self.action,
                self.issue_url,
                self.issue_num,
                self.repo_url,
                self.repo_name)

class WatchEvent(DisplayEvent):
    def __init__(self, event_json):
        DisplayEvent.__init__(self, event_json)

        try:
            self.action = event_json["payload"]["action"]
        except KeyError:
            print event_json
            raise

    def __str__(self):
        return '<a href="{0}">{1}</a> {2} watching <a href="{3}">{4}</a>'.format(
                self.actor_url,
                self.actor,
                self.action,
                self.repo_url,
                self.repo_name)

class ShittyGithub(object):
    """A shitty github wrapper"""

    def __init__(self, token):
        self.token = token
        self.headers = {"Authorization": "token {0}".format(self.token)}

    def get_user(self):
        """return the active user"""
        return requests.get("https://api.github.com/user",
                            headers=self.headers).json["login"]

    def get_repos(self):
        """get the current user's repositories"""
        return requests.get("https://api.github.com/user/repos",
                            headers=self.headers).json


    def repo_events(self, repo, page=1):
        url = "https://api.github.com/repos/{0}/events?page={1}".format(repo, page)
        return requests.get(url, headers=self.headers).json

class RepoEventIterator(object):
    def __init__(self, hub, repo):
        """repo: string, a repo name in "full name" format;
                 i.e. "username/reponame"
           hub:  ShittyGithub instance
        """
        self.repo = repo
        self.hub = hub
        self.page = 1
        self.events = self.hub.repo_events(self.repo)

    def next(self):
        if not self.events:
            self.page += 1
            self.events = self.hub.repo_events(self.repo, self.page)

        if self.events:
            return self.events.pop(0)

        raise StopIteration

    def __iter__(self): return self

class FilteredRepoEventIterator(object):
    """Filter out events by a user and make DisplayEvents out of them"""
    def __init__(self, hub, user, repo):
        self.user = user
        self.repo_events = RepoEventIterator(hub, repo)

    def filtered_next(self):
        n = self.repo_events.next()
        while n['actor']['login'] == self.user:
            n = self.repo_events.next()
        return n

    def next(self):
        event = self.make_display_event(self.filtered_next())
        while not event:
            event = self.make_display_event(self.filtered_next())

        return event

    def make_display_event(self, raw_event):
        """A static method, turns one event into a DisplayEvent"""
        event_type_display_map = {
            'WatchEvent': WatchEvent,
            'ForkEvent': ForkEvent,
            'PullRequestEvent': PullRequestEvent,
            'IssuesEvent': IssuesEvent,
            'IssueCommentEvent': IssueCommentEvent,
        }

        etype = raw_event["type"]
        if etype in event_type_display_map:
            try:
                event = event_type_display_map[etype](raw_event)
                return event
            except KeyError:
                print "Failed to parse event of type {0}".format(etype)
        else:
            print "ignoring event of type {0}".format(etype)

class AllEventIterator(object):
    def __init__(self, hub, user, repos):
        self.queue = []
        for repo in repos:
            evtiter = FilteredRepoEventIterator(hub, user, repo)

            try:
                first = evtiter.next()
            except StopIteration:
                continue

            self.queue.append((first, evtiter))

        #sort the queue earliest to latest
        self.queue.sort(key=lambda (item, it): item.dt)

    def next(self):
        if not self.queue:
            raise StopIteration

        item, iterator = self.queue.pop()

        try:
            newitem = iterator.next()
        except StopIteration:
            return item

        self.queue.append((newitem, iterator))
        #should just insert the item into the right place, but this is probably Good Enough™
        self.queue.sort(key=lambda (item, it): item.dt)

        return item

    def __iter__(self): return self

#import requests

#token='6be5763c4cfe61a5996cbf6ce1ee706d32489a34'
#hub = ShittyGithub(token)
#
#user = hub.get_user()
#
#print list(AllEventIterator(hub, ["llimllib/aiclass", "llimllib/bloomfilter-tutorial"]))

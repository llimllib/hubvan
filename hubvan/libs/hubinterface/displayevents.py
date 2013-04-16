from datetime import datetime

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

class PushEvent(DisplayEvent):
    def __init__(self, event_json):
        DisplayEvent.__init__(self, event_json)

        try:
            #TODO: most payloads have a commits array, containing 1 or more commits
            self.message = event_json["payload"]["commits"][0]['message'][:50]
        except KeyError:
            print event_json
            raise

    def __str__(self):
        return '<a href="{0}">{1}</a> pushed to <a href="{2}">{3}</a>: {4}'.format(
                self.actor_url,
                self.actor,
                self.repo_url,
                self.repo_name,
                self.message)

class CommitCommentEvent(DisplayEvent):
    def __init__(self, event_json):
        DisplayEvent.__init__(self, event_json)

    def __str__(self):
        return '<a href="{0}">{1}</a> commented on commit <a href="{4}"> <a href="{2}">{3}</a>: {4}'.format(
                self.actor_url,
                self.actor,
                self.repo_url,
                self.repo_name,
                self.message)

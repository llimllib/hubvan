from datetime import datetime

GITHUB_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

class DisplayEvent(object):
    def __init__(self, event_json):
        self.event_json = event_json

        self.dt = datetime.strptime(event_json["created_at"], GITHUB_DATE_FORMAT)

        #required attributes. All items will have actor and actor_url
        try:
            self.actor = event_json["actor"]["login"]
            self.repo_name = event_json["repo"]["name"]
        except KeyError:
            print event_json
            raise

        self.actor_url =  self.f('https://github.com/{actor}')
        self.actor_link = self.f('<a href="{actor_url}">{actor}</a>')

        self.repo_url =  self.f('https://github.com/{repo_name}')
        self.repo_link = self.f('<a href="{repo_url}">{repo_name}</a>')

    def f(self, template):
        return template.format(**self.__dict__)

    def __repr__(self): return str(self)

class ForkEvent(DisplayEvent):
    def __init__(self, event_json):
        DisplayEvent.__init__(self, event_json)

    def __str__(self):
        return self.f('{actor_link} forked {repo_link}')

class PullRequestEvent(DisplayEvent):
    def __init__(self, event_json):
        DisplayEvent.__init__(self, event_json)

        try:
            self.action = event_json["payload"]["action"]
            self.pull_number = event_json["payload"]["pull_request"]["number"]
        except KeyError:
            print event_json
            raise

        self.pull_url = self.f('https://github.com/{repo_name}/pull/{pull_number}')
        self.pull_link = self.f('<a href="{pull_url}">pull request {pull_number}</a>')

    def __str__(self):
        return self.f("{actor_link} {action} {pull_link} on {repo_link}")

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

        self.issue_link = self.f('<a href="{issue_url}">issue {issue_num}</a>')

    def __str__(self):
        return self.f('{actor_link} {action} {issue_link} on {repo_link}')

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

        self.issue_link = self.f('<a href="{issue_url}">issue {issue_num}</a>')

    def __str__(self):
        return self.f('{actor_link} {action} {issue_link} on {repo_link}')

class WatchEvent(DisplayEvent):
    def __init__(self, event_json):
        DisplayEvent.__init__(self, event_json)

        try:
            self.action = event_json["payload"]["action"]
        except KeyError:
            print event_json
            raise

    def __str__(self):
        return self.f('{actor_link} {action} watching {repo_link}')

class PushEvent(DisplayEvent):
    def __init__(self, event_json):
        DisplayEvent.__init__(self, event_json)

        try:
            self.message = event_json["payload"]["commits"][0]['message'][:50]
        except KeyError:
            print event_json
            raise

    def __str__(self):
        return self.f('{actor_link} pushed to {repo_link}: {message}')

class CommitCommentEvent(DisplayEvent):
    def __init__(self, event_json):
        DisplayEvent.__init__(self, event_json)
        try:
            self.message = event_json["payload"]["comment"]['body'][:50]
            self.html_url = event_json["payload"]["comment"]['html_url']
        except KeyError:
            print event_json
            raise

        self.html_link = self.f('<a href="{html_url}">commented on</a>')

    def __str__(self):
        return self.f('{actor_link} {html_link} {repo_link}: {message}')

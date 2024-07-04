from github import Github
import re

class GitHubAgent:
    def __init__(self, token):
        self.g = Github(token)

    def get_user_repos(self, username):
        try:
            user = self.g.get_user(username)
            repos = user.get_repos()
            return [repo.name for repo in repos]
        except Exception as e:
            return str(e)

    def _extract_repo_name(self, repo_url):
        match = re.match(r'https://github.com/([^/]+/[^/]+)', repo_url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid GitHub repository URL")

    def _get_all_contents(self, repo, contents, all_files=[]):
        for content_file in contents:
            if content_file.type == "dir":
                all_files = self._get_all_contents(repo, repo.get_contents(content_file.path), all_files)
            else:
                all_files.append(content_file.path)
        return all_files

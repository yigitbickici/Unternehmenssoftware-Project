from github import Github
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

GITHUB_TOKEN = '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'  # my GitHub access token

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



    def get_user_repos(self, username):
        try:
            user = self.g.get_user(username)
            repos = user.get_repos()
            repo_names = [repo.name for repo in repos]
            return repo_names
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


class LinkedInAgent:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        self.profile_url = 'https://api.linkedin.com/v2/me'
        self.token = None
        self._authenticate()

    def _authenticate(self):
        client = BackendApplicationClient(client_id=self.client_id)
        oauth = OAuth2Session(client=client)

        self.token = oauth.fetch_token(token_url=self.token_url, client_id=self.client_id,
                                       client_secret=self.client_secret)

    def get_profile(self):
        headers = {
            'Authorization': f'Bearer {self.token["access_token"]}',
            'Content-Type': 'application/json'
        }
        response = requests.get(self.profile_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Hata: {response.status_code}, {response.json()}")



client_id = '77bcz9g601kdmk' #linkedin DEYapp company application
client_secret = 'ORhcGqz8Ajd9tEwM'

agent = LinkedInAgent(client_id, client_secret)

try:
    profile_data = agent.get_profile()
    print("Profil Bilgileri:")
    print(profile_data)
except Exception as e:
    print(f"Hata oluştu: {e}")




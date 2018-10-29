
class MicrosoftConfiguration:
    AUTH_URL = "https://login.microsoftonline.com/consumers"
    AUTH_ENDPOINT = "/oauth2/v2.0/authorize"
    TOKEN_ENDPOINT = "/oauth2/v2.0/token"
    RESOURCE = "https://graph.microsoft.com"
    SCOPES = "Files.ReadWrite offline_access"

class OneDriveConfiguration:
    def __init__(self, data):
       self.data = data
    
    def get_auth_data(self, scopes, state):
        data = {
            'client_id':  self.get_client_id(),
            'scope': scopes,
            'redirect_uri': self.get_registered_redirect_url(),
            'response_type':'code',
            'response_mode':'query',
            'state':state
        }
        return data

    def get_token_request_data(self, code):
        data = {
            'grant_type':'authorization_code',
            'client_id': self.get_client_id(),
            'client_secret': self.get_client_secret(),
            'code': code,
            'redirect_uri': self.get_registered_redirect_url()
        }
        return data

    def get_refresh_token_request_data(self):
        data = {
            'client_id': self.get_client_id(),
            'refresh_token': self.get_refresh_token(),
            'grant_type': 'refresh_token',
            'client_secret': self.get_client_secret()
        }
        return data

    def get_token(self):
        if 'token' in self.data:
            return self.data['token']
        else:
            return None

    def set_token(self, token):
        self.data['token'] = token

    def get_refresh_token(self):
        if 'refresh_token' in self.data:
            return self.data['refresh_token']
        else:
            return None

    def set_refresh_token(self, refresh_token):
        self.data['refresh_token'] = refresh_token

    def get_token_type(self):
        if "token_type" in self.data:
            return self.data["token_type"]
        else:
            return None

    def set_token_type(self, ttype):
        self.data["token_type"] = ttype 
            
        
    def get_client_id(self):
        if "client_id" in self.data:
            return self.data["client_id"]
        else:
            return None

    def get_client_secret(self):
        if "client_secret" in self.data:
            return self.data["client_secret"]
        else:
            return None

    def get_registered_redirect_url(self):
        if "registered_redirect_url" in self.data:
            return self.data["registered_redirect_url"]
        else:
            return None

    def get_auth_header(self):
        return self.get_token_type() + " " +self.get_token()

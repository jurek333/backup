import urllib.parse
import uuid
import requests
import webbrowser
import json
from sys import platform
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing.pool import ThreadPool
import OneDrive

class MicrosoftAuthenticationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("<html><body><h2>You may close browser... <br/>Thank You!</h2></body></html>", "utf-8"))
        self.server.path = self.path

class Authentication:
    def __init__(self, onedrive_config: OneDrive.OneDriveConfiguration):
        self.onedrive = onedrive_config
        self.config = OneDrive.MicrosoftConfiguration()
        if platform == "linux" or platform == "linux2":
            self.web = webbrowser.get('x-www-browser')
        elif platform == "win32" or platform == "win64":
            self.web = webbrowser.get('windows-default')
        else:
            print("MicrosoftAuthentication.Authentication does not support %s"%(platform))
            exit(1)

    def run_http_server(self) -> HTTPServer:
        redirect_url = self.onedrive.get_registered_redirect_url()
        parts = urllib.parse.urlparse(redirect_url)
        address = ('',parts.port)
        httpd = HTTPServer(address, MicrosoftAuthenticationHandler)
        httpd.handle_request()
        httpd.server_close()
        query = urllib.parse.urlparse(httpd.path)
        queryData = urllib.parse.parse_qs(query.query)
        return queryData

    def open_browser(self) -> str:
        state = str(uuid.uuid4())
        params = self.onedrive.get_auth_data(self.config.SCOPES, state)
        url = self.config.AUTH_URL + self.config.AUTH_ENDPOINT + "?" \
                + urllib.parse.urlencode(params)
        self.web.open(url)
        return state

    def run_authentication(self):
        pool = ThreadPool(processes=1)
        asyncFun = pool.apply_async(self.run_http_server, ())
        status = self.open_browser()
        data = asyncFun.get()
        code = data["code"]
        
        url = self.config.AUTH_URL + self.config.TOKEN_ENDPOINT
        body = self.onedrive.get_token_request_data(code[0])
        response = requests.post(url, data=body)
        print(response.text)
            
        token_data = json.loads(response.text)
        if "error" in token_data:
            print("nieudane logowanie %s"%(token_data["error_description"]))
            exit(1)

        self.onedrive.set_token(token_data["access_token"])
        self.onedrive.set_refresh_token(token_data["refresh_token"])
        self.onedrive.set_token_type(token_data["token_type"])

        return self.onedrive.get_auth_header()

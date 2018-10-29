import urllib.parse
import uuid
import requests
import webbrowser
import json
import logging
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
            logging.critical("MicrosoftAuthentication.Authentication does not support %s"%(platform))
            exit(1)

    def _run_http_server(self) -> HTTPServer:
        redirect_url = self.onedrive.get_registered_redirect_url()
        parts = urllib.parse.urlparse(redirect_url)
        logging.debug("running server on localhost:%d"%(parts.port))
        address = ('',parts.port)
        httpd = HTTPServer(address, MicrosoftAuthenticationHandler)
        httpd.handle_request()
        httpd.server_close()
        query = urllib.parse.urlparse(httpd.path)
        queryData = urllib.parse.parse_qs(query.query)
        return queryData

    def _open_browser(self) -> str:
        state = str(uuid.uuid4())
        params = self.onedrive.get_auth_data(self.config.SCOPES, state)
        url = self.config.AUTH_URL + self.config.AUTH_ENDPOINT + "?" \
                + urllib.parse.urlencode(params)
        logging.debug("make POST request to: %s"%(url))
        self.web.open(url)
        return state

    def get_authentication_header(self):
        token = self.onedrive.get_token()
        if token is None:
            return self._make_whole_auth()
        return self.onedrive.get_auth_header()
        
    def authentication_error(self):
        if self._refresh_token():                    #if it fails try to refresh token
            return self.onedrive.get_auth_header()
        if self._make_whole_auth():
            return self.onedrive.get_auth_header()
        return None

    def _save_token_data(self, http_response):
        self.onedrive.set_token(http_response["access_token"])
        self.onedrive.set_refresh_token(http_response["refresh_token"])
        self.onedrive.set_token_type(http_response["token_type"])

    def _refresh_token(self) -> bool:
        logging.debug("zostanie przprowadzone odświeżenie tokenu")
        refresh_token = self.onedrive.get_refresh_token()
        if refresh_token is None or refresh_token == "":
            return False
        url = self.config.AUTH_URL + self.config.TOKEN_ENDPOINT
        body = self.onedrive.get_refresh_token_request_data()
        print(body)
        response = requests.post(url, data=body)
            
        token_data = json.loads(response.text)
        if "error" in token_data:
            logging.error("nieudane logowanie %s"%(token_data["error_description"]))
            return False
        self._save_token_data(token_data)
        return True

    def _make_whole_auth(self):
        logging.debug("zostanie przeprowadzona autoryzacja")
        pool = ThreadPool(processes=1)
        asyncFun = pool.apply_async(self._run_http_server, ())
        status = self._open_browser()
        data = asyncFun.get()
        code = data["code"]
        logging.debug("received code %s"%(code))
        
        url = self.config.AUTH_URL + self.config.TOKEN_ENDPOINT
        body = self.onedrive.get_token_request_data(code[0])
        response = requests.post(url, data=body)
            
        token_data = json.loads(response.text)
        if "error" in token_data:
            logging.error("nieudane logowanie %s"%(token_data["error_description"]))
            exit(1)
        self._save_token_data(token_data)
        return self.onedrive.get_auth_header()

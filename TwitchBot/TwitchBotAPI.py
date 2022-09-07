import TwitchBotConfigs, requests

class TwitchAPI(object):
    _TTV_STREAMS_URL = "https://api.twitch.tv/helix/streams?user_login={}"
    _TTV_AUTH_URL    = "https://id.twitch.tv/oauth2/token"

    def __init__(self, ClientID: str, ClientSecret: str) -> None:
        self.ClientID     = ClientID
        self.ClientSecret = ClientSecret 
        self.AccessBeaver = 'Bearer ' + self.GetAccessToken()
        self.AuthenticationHeaders = {
            "Client-ID"     : self.ClientID,
            "Authorization" : self.AccessBeaver   
        }
    
    def CheckUserIsLive(self, BroadcasterNickname : str) -> bool:
        RequestURL = TwitchAPI._TTV_STREAMS_URL.format(BroadcasterNickname)
        try:
            Request  = requests.Session().get(RequestURL, headers=self.AuthenticationHeaders).json()
            return True if len(Request["data"]) == 1 else False
        except Exception as e:
            return False
    
    def GetAccessToken(self) -> str:
        TwitchAuthenticationParameters = {
            'client_id'    : self.ClientID,
            'client_secret': self.ClientSecret,
            'grant_type'   : "client_credentials"
        }
        return requests.post(url=TwitchAPI._TTV_AUTH_URL, params=TwitchAuthenticationParameters).json()['access_token']
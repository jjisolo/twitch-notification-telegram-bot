import TwitchBotConfigs, requests, logging

class TwitchAPI(object):
    """
    Holds various methods for working with Twitch API.
    """

    _TTV_STREAMS_URL = "https://api.twitch.tv/helix/streams?user_login={}"
    _TTV_AUTH_URL    = "https://id.twitch.tv/oauth2/token"

    def __init__(self, ClientID: str, ClientSecret: str) -> None:
        """
        Initialize the object. Get access beaver token.

        :param ClientID(string): Client ID of the Twitch Application.
        :param ClientSecret(string): Secret client ID of the Twitch Application.
        """

        self.ClientID     = ClientID
        self.ClientSecret = ClientSecret 
        self.AccessBeaver = 'Bearer ' + self.__GetAccessToken()
        self.AuthenticationHeaders = {
            "Client-ID"     : self.ClientID,
            "Authorization" : self.AccessBeaver   
        }
    
    def __GetAccessToken(self) -> str:
        """
        Get API access token.

        :returns string: API Access token.
        """
        TwitchAuthenticationParameters = {
            'client_id'    : self.ClientID,
            'client_secret': self.ClientSecret,
            'grant_type'   : "client_credentials"
        }
        return requests.post(url=TwitchAPI._TTV_AUTH_URL, params=TwitchAuthenticationParameters).json()['access_token']
    
    def CheckUserIsLive(self, BroadcasterNickname : str) -> bool:
        """
        Check if the streamer is live.

        :param BroadcasterNickname(string): Broadcaster nickname of Twitch.
        :returns boolean: True if broadcaster is live, false if he's not.
        """
        RequestURL = TwitchAPI._TTV_STREAMS_URL.format(BroadcasterNickname)
        try:
            Request  = requests.Session().get(RequestURL, headers=self.AuthenticationHeaders).json()
            return True if len(Request["data"]) == 1 else False
        except Exception as e:
            return False
    

import sqlite3, typing, dataclasses, logging

@dataclasses.dataclass
class Notification(object):
    """
    Base Notification class
    """
    TelegramUserID        : typing.Union[str, int]
    TwitchBroadcasterName : str 

class TwitchBotDataBase(object):
    """
    Base twitch database class, that aggregates
    different methods for working with sqlite databse.
    """

    def __init__(self, DatabaseFilename : str) -> None:
        """
        Connect to the database.

        :param DatabaseFilename(string): Filename of the database. 
        """
        logging.info("[db] Initializing database")
        self.Connection = sqlite3.connect(DatabaseFilename)
        self.Cursor     = self.Connection.cursor()
    
    def __GetUserID(self, UserID : typing.Union[str, int]) -> str:
        """
        Get User database ID from user Telegram ID.

        :param UserID(union: string, integer): User Telegram ID.
        :returns string: Database ID.
        """
        Result = self.Cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (UserID,))
        return Result.fetchone()[0]

    def __GetUserTelegramID(self, UserTelegramID : typing.Union[str, int]) -> str:
        """
        Get user Telegram ID from user database ID.

        :param UserTelegramID(union: string, integer): database ID of the User.
        :returns string: Telegram ID
        """        
        Result = self.Cursor.execute("SELECT `user_id` FROM `users` WHERE `id` = ?", (UserTelegramID,))
        return Result.fetchone()[0]

    def GetDistinctAccounts(self) -> typing.Tuple[str]: 
        """
        Get distinct twitch accounts from database

        :returns tuple[str]: Distinct twitch accounts.
        """
        Result = self.Cursor.execute("SELECT DISTINCT followed_account FROM linked_accounts")
        return Result.fetchall()

    def GetDistinctUsers(self) -> typing.Tuple[str]:
       """
       Get distinct users from database.

       :returns tuple[str]: Distinct users.
       """
       Result = self.Cursor.execute("SELECT DISTINCT user_id FROM users")
       return Result.fetchall()

    def UsertExists(self, UserID : typing.Union[str, int]) -> bool:
        """
        Check if user exists in the database.

        :param UserID(union: string, integer): Telegram ID of the user.
        :returns boolean: True if the user exists in the databse, false if he's not.
        """
        Result = self.Cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (UserID,))
        return bool(len(Result.fetchall()))

    def AddUser(self, UserID : typing.Union[str, int]) -> None:
        """
        Add new user to the database

        :param UserID(union: string, integer): Telegram ID of the user.
        """
        logging.info("[db] Adding new user to the database --> ID:" + str(UserID))        
        self.Cursor.execute("INSERT INTO 'users' ('user_id') VALUES (?)", (UserID,))
        return self.Connection.commit()

    def RemoveLinkedAccount(self, UserID : typing.Union[str, int], LinkedAccountName : str) -> None:
        """
        Remove followed account from database.

        :param UserID(union: string, integer): Telegram ID of the user.
        :param LinkedAccountName(string): Twitch account name of the broadcaster.
        """
        logging.info("[db] Adding new linked accout to the database --> ID: {}, NAME: {}".format(UserID, LinkedAccountName))        
        self.Cursor.execute("DELETE FROM linked_accounts WHERE users_id = ? AND followed_account = '"+LinkedAccountName+"'", (self.__GetUserID(UserID),))
        return self.Connection.commit()
    
    def GetPendingNotifies(self) -> typing.List[Notification]:
        """
        Get all (user_id's, boardcaster name's) <-- As Notification() class.

        :returns List[class Notification]: List of notifications, that are needed to be processed.
        """
        Notifications = []
        
        DataBaseExecutionResult = self.Cursor.execute("SELECT followed_account, users_id FROM linked_accounts WHERE notified=0")
        DataBaseExecutionResult = DataBaseExecutionResult.fetchall()

        for FollowedAccountPendingNotify in DataBaseExecutionResult:
            Notifications.append(Notification(
                self.__GetUserTelegramID(FollowedAccountPendingNotify[1]),
                FollowedAccountPendingNotify[0]
            ))

        return (Notifications)

    def SetNotifyStatus(self, UserID : typing.Union[str, int], LinkedAccountName : str, NotifyStatus : bool) -> None:
        """
        Set notification flags to Users.
        
        :param UserID(union: string, integer): Telegram ID of the user.
        :param LinkedAccountName(string): Twitch account name of the broadcaster.
        :param NotifyStatus(bool): 0 means do not notify, 1 means notify.
        """
        NotifyValue = "1" if NotifyStatus else "0"
        logging.info("[db] Setting notify status --> ID: {}, NAME: {}, STATUS: {}".format(UserID, LinkedAccountName, NotifyStatus))        
        self.Cursor.execute("UPDATE linked_accounts SET notified="+NotifyValue+" WHERE followed_account='"+LinkedAccountName+"'")
        return self.Connection.commit()

    def GetNotifyStatus(self, UserID : typing.Union[str, int], LinkedAccountName : str) -> bool:
        """
        Set notification flags to Users.
        
        :param UserID(union: string, integer): Telegram ID of the user.
        :param LinkedAccountName(string): Twitch account name of the broadcaster.
        :param boolean: 0 means not notified, 1 means notified indeed.
        """
        Result = self.Cursor.execute("SELECT notified FROM linked_accounts WHERE users_id=? AND followed_account=?", (self.__GetUserID(UserID), LinkedAccountName))
        try:
            return Result.fetchone()[0]
        except:
            return False

    def AddLinkedAccount(self, UserID : typing.Union[str, int], LinkedAccountName : str) -> None:
        """
        Add followed Twitch account to the linked_accounts table

        :param UserID(union: string, integer): Telegram ID of the user.
        :param LinkedAccountName(string): Twitch account name of the broadcaster.
        """
        logging.info("[db] Adding new account to the database --> ID: {}, NAME: {}".format(UserID, LinkedAccountName))        
        self.Cursor.execute("INSERT INTO 'linked_accounts' ('users_id', 'followed_account') VALUES (?, ?)", (self.__GetUserID(UserID), LinkedAccountName))
        return self.Connection.commit()

    def GetLinkedTwitchAccounts(self, UserID : typing.Union[str, int]) -> typing.Tuple[str]:
        """
        Get followed Twitch account of the user.

        :param UserID(union: string, integer): Telegram ID of the user.
        :returns Tuple[string]: Followed Twitch accounts. 
        """
        Result = self.Cursor.execute("SELECT * FROM 'linked_accounts' WHERE `users_id` = ?", (self.__GetUserID(UserID),))
        return Result.fetchall()

    def Close(self) -> None:
        """
        Close the connection to the database.
        """
        self.Connection.close()


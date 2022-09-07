import sqlite3

class TwitchBotDataBase(object):
    def __init__(self, DatabaseFilename : str) -> None:
        self.Connection = sqlite3.connect(DatabaseFilename)
        self.Cursor = self.Connection.cursor()
    
    def UsertExists(self, UserID : str) -> bool:
        Result = self.Cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (UserID,))
        return bool(len(Result.fetchall()))

    def GetUserID(self, UserID : str) -> str:
        Result = self.Cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (UserID,))
        return Result.fetchone()[0]

    def AddUser(self, UserID : str) -> None:
        self.Cursor.execute("INSERT INTO 'users' ('user_id') VALUES (?)", (UserID,))
        return self.Connection.commit()

    def RemoveLinkedAccount(self, UserID : str, LinkedAccountName : str) -> None:
        self.Cursor.execute("DELETE FROM linked_accounts WHERE users_id = ? AND followed_account = '"+LinkedAccountName+"'", (self.GetUserID(UserID),))
        return self.Connection.commit()
    
    def GetDistinctAccounts(self) -> str:
        Result = self.Cursor.execute("SELECT DISTINCT followed_account FROM linked_accounts")
        return Result.fetchall()

    def AddLinkedAccount(self, UserID : str, LinkedAccountName : str) -> bool:
        self.Cursor.execute("INSERT INTO 'linked_accounts' ('users_id', 'followed_account') VALUES (?, ?)", (self.GetUserID(UserID), LinkedAccountName))
        return self.Connection.commit()

    def GetLinkedTwitchAccounts(self, UserID : str) -> str:
        Result = self.Cursor.execute("SELECT * FROM 'linked_accounts' WHERE `users_id` = ?", (self.GetUserID(UserID),))
        return Result.fetchall()

    def Close(self) -> None:
        self.Connection.close()


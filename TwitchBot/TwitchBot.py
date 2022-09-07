from email.message import Message
from aiogram                         import types, executor
from TwitchBotDatabase               import TwitchBotDataBase
from TwitchBotBase                   import TelegramBot, TelegramBotDispatcher, UsersDatabase, TwitchApi
from Handlers.PersonalMessageHandler import TELEGRAM_DP_BROADCASTER_TURNED_ON_LIST

import asyncio, itertools, random

async def DispatcherStartPolling() -> None:
    """
    Start polling of the bot dispatcher in async loop.
    """
    await TelegramBotDispatcher.start_polling()

async def ParseBroadcasters() -> None:
    """
    Parse active broadcasters, notify users, that are followed them.
    """
    while True:
        DistinctBroadcasters = UsersDatabase.GetDistinctAccounts()
        DistinctUsers        = UsersDatabase.GetDistinctUsers()
        ActiveBroadcasters   = []
        InActiveBroadcasters = []

        for BroadcasterName in  DistinctBroadcasters:
            BroadcasterTranslatedName = BroadcasterName[0]
            if TwitchApi.CheckUserIsLive(BroadcasterTranslatedName):
                ActiveBroadcasters.append(BroadcasterTranslatedName)
            else:
                InActiveBroadcasters.append(BroadcasterTranslatedName)

        Notifications = UsersDatabase.GetPendingNotifies()
        for Notification in Notifications:
            if not UsersDatabase.GetNotifyStatus(Notification.TelegramUserID, Notification.TwitchBroadcasterName):
                MessageChoosed = random.choice(TELEGRAM_DP_BROADCASTER_TURNED_ON_LIST)
                MessageChoosed = MessageChoosed.format(Notification.TwitchBroadcasterName)
                UsersDatabase.SetNotifyStatus(Notification.TelegramUserID, Notification.TwitchBroadcasterName, False)
                await TelegramBot.send_message(Notification.TelegramUserID, MessageChoosed)
        
        for (ActiveBroadcaster, InActiveBroadcaster) in zip(ActiveBroadcasters, InActiveBroadcasters):
            for DistinctUser in DistinctUsers:
                DistincUserTranslated = DistinctUser[0]
                if(not UsersDatabase.GetNotifyStatus(DistincUserTranslated, ActiveBroadcaster)):
                    UsersDatabase.SetNotifyStatus(DistincUserTranslated, ActiveBroadcaster, True)
                else:
                    DistincUserTranslated = DistinctUser[0]
                    UsersDatabase.SetNotifyStatus(DistincUserTranslated, InActiveBroadcaster, False)
    
        await asyncio.sleep(20)

async def Main() -> None:
    await asyncio.gather(
        DispatcherStartPolling(),
        ParseBroadcasters()
    )

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(Main())


from email.message import Message
from aiogram                         import types, executor
from TwitchBotDatabase               import TwitchBotDataBase
from TwitchBotBase                   import TelegramBot, TelegramBotDispatcher, UsersDatabase, TwitchApi
from Handlers.PersonalMessageHandler import TELEGRAM_DP_BROADCASTER_TURNED_ON_LIST

import asyncio, itertools, random

async def DispatcherStartPolling() -> None:
    await TelegramBotDispatcher.start_polling()

async def ParseBroadcasters() -> None:
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

        for ActiveBroadcaster in ActiveBroadcasters:
            for DistinctUser in DistinctUsers:
                DistincUserTranslated = DistinctUser[0]
                UsersDatabase.SetNotifyStatus(DistincUserTranslated, ActiveBroadcaster, True)

        for InActiveBroadcaster in InActiveBroadcasters:
            for DistinctUser in DistinctUsers:
                DistincUserTranslated = DistinctUser[0]
                UsersDatabase.SetNotifyStatus(DistincUserTranslated, InActiveBroadcaster, False)

        Notifications = UsersDatabase.GetPendingNotifies()
        for Notification in Notifications:
            MessageChoosed = random.choice(TELEGRAM_DP_BROADCASTER_TURNED_ON_LIST)
            MessageChoosed = MessageChoosed.format(Notification.TwitchBroadcasterName)
            await TelegramBot.send_message(Notification.TelegramUserID, MessageChoosed)
        
        await asyncio.sleep(600)

async def Main() -> None:
    await asyncio.gather(
        DispatcherStartPolling(),
        ParseBroadcasters()
    )

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(Main())


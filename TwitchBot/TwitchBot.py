from xml.etree.ElementTree import TreeBuilder
from aiogram           import types, executor
from TwitchBotDatabase import TwitchBotDataBase
from Handlers          import PersonalMessageHandler
from TwitchBotBase     import TelegramBot, TelegramBotDispatcher, UsersDatabase, TwitchApi

import asyncio, itertools

async def DispatcherStartPolling() -> None:
    await TelegramBotDispatcher.start_polling()

async def ParseBroadcasters() -> None:
    while True:
        DistinctBroadcasters = UsersDatabase.GetDistinctAccounts()
        ActiveBroadcasters   = []
        for BroadcasterName in  DistinctBroadcasters:
            if TwitchApi.CheckUserIsLive(BroadcasterName):
                ActiveBroadcasters += BroadcasterName
        
        await asyncio.sleep(600)

async def Main() -> None:
    await asyncio.gather(
        DispatcherStartPolling(),
        ParseBroadcasters()
    )

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(Main())


from aiogram           import Bot, Dispatcher, types
from TwitchBotDatabase import TwitchBotDataBase
from TwitchBotAPI      import TwitchAPI

import TwitchBotConfigs, logging

logging.basicConfig(level=logging.INFO)


TelegramBot           = Bot(token=TwitchBotConfigs.BOT_TOKEN, parse_mode="HTML")
TelegramBotDispatcher = Dispatcher(TelegramBot)
UsersDatabase         = TwitchBotDataBase("telegram_users.db")
TwitchApi             = TwitchAPI(TwitchBotConfigs.TTV_CLIENT_ID, TwitchBotConfigs.TTV_CLIENT_SECRET)
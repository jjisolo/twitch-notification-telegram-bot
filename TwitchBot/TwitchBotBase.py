from aiogram                            import Bot, Dispatcher, types
from TwitchBotDatabase                  import TwitchBotDataBase
from TwitchBotAPI                       import TwitchAPI
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher                 import FSMContext
from aiogram.dispatcher.filters.state   import State, StatesGroup

import TwitchBotConfigs, logging

class AddBroadcasterForm(StatesGroup):
    BroadcasterNickname = State()

class RemBroadcasterForm(StatesGroup):
    BroadcasterNickname = State()

logging.basicConfig(level=logging.INFO)

TelegramBot           = Bot(token=TwitchBotConfigs.BOT_TOKEN, parse_mode="HTML")
TelegramBotDispatcher = Dispatcher(TelegramBot, storage=MemoryStorage())
UsersDatabase         = TwitchBotDataBase("telegram_users.db")
TwitchApi             = TwitchAPI(TwitchBotConfigs.TTV_CLIENT_ID, TwitchBotConfigs.TTV_CLIENT_SECRET)
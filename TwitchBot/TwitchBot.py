from aiogram           import types, executor
from TwitchBotBase     import TelegramBot, TelegramBotDispatcher
from TwitchBotDatabase import TwitchBotDataBase
from Handlers          import PersonalMessageHandler

if __name__ == "__main__":
    executor.start_polling(TelegramBotDispatcher, skip_updates=True)

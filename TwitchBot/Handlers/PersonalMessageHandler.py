from aiogram          import types, Bot
from TwitchBotBase    import TelegramBotDispatcher, TelegramBot
from TwitchBotBase    import UsersDatabase
from TwitchBotBase    import TwitchApi

_TELEGRAM_DP_STARTMESSAGE           = "🍄Привет, {}! Теперь ты будешь получать уведомления, когда один из моих любимых стримеров начнет трансляцию!🍄"
_TELEGRAM_DP_NO_BROADCASTERS        = "{}, ты не выбрал ни одного стримера, попробуй использовать команду !ttv [имя стримера]!"
_TELEGRAM_DP_CURRENT_BROADCASTS     = "{}, вот список стримеров которых ты смотришь, и их live-статус: " 
_TELEGRAM_DP_NOT_STREAMING_TEMPLATE = "❌ <b>{}</b>({}) - Оффлайн"
_TELEGRAM_DP_IS_STREAMING_TEMPLATE  = "✅ <b>{}</b>({}) - Онлайн"
_TELEGRAM_DP_BROADCASTER_REMOVED    = "Стример <b>{}</b> был успешно удален из списка отслеживаемых"
_TELEGRAM_DP_BROADCASTER_ADDED      = "Вы теперь отслеживаете стримера <b>{}</b>"
_TELEGRAM_DP_BROADCASTER_EXISTS     = "Стример {} уже был добавлен в список отслеживаемых"

@TelegramBotDispatcher.message_handler(commands=["start"])
async def Start(MessageIn : types.Message) -> None:
    if not UsersDatabase.UsertExists(MessageIn.from_user.id):
        UsersDatabase.AddUser(MessageIn.from_user.id)
    await MessageIn.answer(_TELEGRAM_DP_STARTMESSAGE.format(MessageIn.from_user.first_name))    
    
@TelegramBotDispatcher.message_handler(commands=["remove_ttv_sreamer"], commands_prefix="!")
async def RemoveFollowedAccount(MessageIn : types.Message) -> None:
    BroadcasterName = MessageIn.text.split()[1]
    UsersDatabase.RemoveLinkedAccount(MessageIn.from_user.id, BroadcasterName)
    await MessageIn.answer(_TELEGRAM_DP_BROADCASTER_REMOVED.format(BroadcasterName))

@TelegramBotDispatcher.message_handler(commands=["add_ttv_streamer"], commands_prefix="!")
async def AddFollowedAccount(MessageIn : types.Message) -> None:
    BroadcasterName = MessageIn.text.split()[1]
    LinkedTwitchAccounts = UsersDatabase.GetLinkedTwitchAccounts(MessageIn.from_user.id)
    if(len(LinkedTwitchAccounts)):
        for TwitchAccount in LinkedTwitchAccounts:
            if TwitchAccount[2] == BroadcasterName:
                await MessageIn.answer(_TELEGRAM_DP_BROADCASTER_EXISTS.format(BroadcasterName)) 
                return
    UsersDatabase.AddLinkedAccount(MessageIn.from_user.id, BroadcasterName)
    await MessageIn.answer(_TELEGRAM_DP_BROADCASTER_ADDED.format(BroadcasterName))   

@TelegramBotDispatcher.message_handler(commands=['get_linked_accounts'])
async def CurrentBroadCasts(MessageIn : types.Message) -> None:
    LinkedTwitchAccounts = UsersDatabase.GetLinkedTwitchAccounts(MessageIn.from_user.id)
    if(len(LinkedTwitchAccounts)):
        MessageAnswer = _TELEGRAM_DP_CURRENT_BROADCASTS.format(MessageIn.from_user.first_name)
        for TwitchAccount in LinkedTwitchAccounts:
            TwitchAccountName = TwitchAccount[2]
            MessageAnswer    += "\n"
            if TwitchApi.CheckUserIsLive(TwitchAccountName):
                MessageAnswer += "\n" + _TELEGRAM_DP_IS_STREAMING_TEMPLATE.format(TwitchAccountName, "twitch")
            else:
                MessageAnswer += "\n" + _TELEGRAM_DP_NOT_STREAMING_TEMPLATE.format(TwitchAccountName, "twitch")
    else:
        MessageAnswer = _TELEGRAM_DP_NO_BROADCASTERS.format(MessageIn.from_user.first_name)
    await MessageIn.answer(MessageAnswer)    
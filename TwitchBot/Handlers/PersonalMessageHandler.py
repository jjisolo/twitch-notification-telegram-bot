from aiogram          import types, Bot
from TwitchBotBase    import TelegramBotDispatcher, TelegramBot, AddBroadcasterForm, RemBroadcasterForm, FSMContext
from TwitchBotBase    import UsersDatabase
from TwitchBotBase    import TwitchApi

import TwitchBotBase, logging

_TELEGRAM_DP_STARTMESSAGE           = "Привет, {}! Теперь ты будешь получать уведомления, когда один из моих любимых стримеров начнет трансляцию!"
_TELEGRAM_DP_CHOOSE_VARIANT         = "Пожалуйста выбери одну из опций ниже"
_TELEGRAM_DP_NO_BROADCASTERS        = "{}, ты не выбрал ни одного стримера, попробуй использовать команду !ttv [имя стримера]!"
_TELEGRAM_DP_CURRENT_BROADCASTS     = "Вот список стримеров которых ты смотришь, и их live-статус: " 
_TELEGRAM_DP_NOT_STREAMING_TEMPLATE = "💤 <b>{}</b>({}) - Оффлайн"
_TELEGRAM_DP_IS_STREAMING_TEMPLATE  = "💢 <b>{}</b>({}) - Онлайн"
_TELEGRAM_DP_BROADCASTER_REMOVED    = "Стример <b>{}</b> был успешно удален из списка отслеживаемых"
_TELEGRAM_DP_BROADCASTER_ADDED      = "Вы теперь отслеживаете стримера <b>{}</b>"
_TELEGRAM_DP_BROADCASTER_EXISTS     = "Стример {} уже был добавлен в список отслеживаемых"

_TELEGRAM_DP_BROADCASTER_TURNED_ON_1 = "<b>{}</b> Подрубил, скорее заходи на его стрим!"
_TELEGRAM_DP_BROADCASTER_TURNED_ON_2 = "Псс... тут <b>{}</b> начал стримить"
_TELEGRAM_DP_BROADCASTER_TURNED_ON_3 = "Это что стрим <b>{}</b>?? Заходи скорее!"
_TELEGRAM_DP_BROADCASTER_TURNED_ON_4 = "<b>{}</b> Сейчас стримит, не пропусти!"
_TELEGRAM_DP_BROADCASTER_TURNED_ON_5 = "Подрубка от <b>{}</b>!"
_TELEGRAM_DP_BROADCASTER_TURNED_ON_6 = "Поток от <b>{}</b>, заходи скорее!"
_TELEGRAM_DP_BROADCASTER_TURNED_ON_7 = "<b>{}</b> Подрубил! Не пропусти!"
_TELEGRAM_DP_BROADCASTER_TURNED_ON_8 = "<b>{}</b> Начал трансляцию!"

TELEGRAM_DP_BROADCASTER_TURNED_ON_LIST = [
    _TELEGRAM_DP_BROADCASTER_TURNED_ON_1,
    _TELEGRAM_DP_BROADCASTER_TURNED_ON_2,
    _TELEGRAM_DP_BROADCASTER_TURNED_ON_3,
    _TELEGRAM_DP_BROADCASTER_TURNED_ON_4,
    _TELEGRAM_DP_BROADCASTER_TURNED_ON_5,
    _TELEGRAM_DP_BROADCASTER_TURNED_ON_6,
    _TELEGRAM_DP_BROADCASTER_TURNED_ON_7,
    _TELEGRAM_DP_BROADCASTER_TURNED_ON_8
]

StartFollowBroadcasterInlineButton = types.InlineKeyboardButton('Начать отслеживать стримера', callback_data='!add_ttv_streamer')
EndFollowBroadcasterInlineButton   = types.InlineKeyboardButton('Прекратить отслеживать стримера', callback_data='!remove_ttv_streamer')
WatchFollowBroadcasterInlineButton = types.InlineKeyboardButton('Отслеживаемые стримеры', callback_data='!get_followed_accounts')
StartInlineKeyboard = types.InlineKeyboardMarkup()
StartInlineKeyboard.add(StartFollowBroadcasterInlineButton)
StartInlineKeyboard.add(EndFollowBroadcasterInlineButton)
StartInlineKeyboard.add(WatchFollowBroadcasterInlineButton)

@TelegramBotDispatcher.callback_query_handler(lambda c: c.data and c.data.startswith("!"))
async def process_inline_buttons_callbacks(callback_query: types.CallbackQuery):
    """
    Process querry for the inline buttons, such as remove followed broadcastrer etc.
    """
    if callback_query.data[1:] == "add_ttv_streamer":
        await AddBroadcasterForm.BroadcasterNickname.set()
        logging.info("[pm-handler] Starting 'Add broadcaster' action --> ID:" + str(callback_query.from_user.id))        
        await TelegramBot.send_message(callback_query.from_user.id, text="Введи ник стримера на твиче которого ты хочешь отслеживать")
    if callback_query.data[1:] == "remove_ttv_streamer":
        await RemBroadcasterForm.BroadcasterNickname.set()   
        logging.info("[pm-handler] Starting 'Remove broadcaster' action --> ID:" + str(callback_query.from_user.id))             
        await TelegramBot.send_message(callback_query.from_user.id, text="Введи ник стримера на твиче которого ты хочешь прекратить отслеживать")
    if callback_query.data[1:] == "get_followed_accounts":
        logging.info("[pm-handler] Starting 'Get followed accounts' action --> ID:" + str(callback_query.from_user.id))             
        LinkedTwitchAccounts = UsersDatabase.GetLinkedTwitchAccounts(callback_query.from_user.id)
        MessageAnswer = _TELEGRAM_DP_CURRENT_BROADCASTS
        if(len(LinkedTwitchAccounts)):
            for TwitchAccount in LinkedTwitchAccounts:
                TwitchAccountName = TwitchAccount[2]
                MessageAnswer    += "\n"
                if TwitchApi.CheckUserIsLive(TwitchAccountName):
                    MessageAnswer += "\n" + _TELEGRAM_DP_IS_STREAMING_TEMPLATE.format(TwitchAccountName, "twitch")
                else:
                    MessageAnswer += "\n" + _TELEGRAM_DP_NOT_STREAMING_TEMPLATE.format(TwitchAccountName, "twitch")
        logging.info("[pm-handler] Sending message --> " + str(callback_query.from_user.id))             
        await TelegramBot.send_message(callback_query.from_user.id, text=MessageAnswer)    

@TelegramBotDispatcher.message_handler(state=AddBroadcasterForm.BroadcasterNickname)
async def process_name(MessageIn: types.Message, state: FSMContext):
    """
    Process broadcaster name form end(means when user already sended broadcaster's name).
    *Add following
    """
    logging.info("[pm-handler] Ending 'Add broadcaster' action --> ID: " + str(MessageIn.from_user.id))             
    await state.finish()
    BroadcasterName = MessageIn.text
    LinkedTwitchAccounts = UsersDatabase.GetLinkedTwitchAccounts(MessageIn.from_user.id)
    if(len(LinkedTwitchAccounts)):
        for TwitchAccount in LinkedTwitchAccounts:
            if TwitchAccount[2] == BroadcasterName:
                logging.info("[pm-handler] Sending message --> ID: " + str(MessageIn.from_user.id))             
                await MessageIn.answer(_TELEGRAM_DP_BROADCASTER_EXISTS.format(BroadcasterName)) 
                return
    UsersDatabase.AddLinkedAccount(MessageIn.from_user.id, BroadcasterName)
    logging.info("[pm-handler] Send message --> ID: " + str(MessageIn.from_user.id))             
    await MessageIn.reply(_TELEGRAM_DP_BROADCASTER_ADDED.format(BroadcasterName))

@TelegramBotDispatcher.message_handler(state=RemBroadcasterForm.BroadcasterNickname)
async def process_name(MessageIn: types.Message, state: FSMContext):
    """
    Process broadcaster name form end(means when user already sended broadcaster's name).
    *Remove following
    """
    logging.info("[pm-handler] Ending 'Remove broadcaster' action --> ID: " + str(MessageIn.from_user.id))             
    await state.finish()
    BroadcasterName = MessageIn.text
    UsersDatabase.RemoveLinkedAccount(MessageIn.from_user.id, BroadcasterName)
    logging.info("[pm-handler] Sending message --> ID: " + str(MessageIn.from_user.id))             
    await MessageIn.answer(_TELEGRAM_DP_BROADCASTER_REMOVED.format(BroadcasterName), reply_markup=types.ReplyKeyboardRemove())

@TelegramBotDispatcher.message_handler(commands=["menu"])
async def Menu(MessageIn : types.Message) -> None:
    """
    Send menu form to the user.
    """
    logging.info("[pm-handler] Sending menu form to --> ID: " + str(MessageIn.from_user.id))             
    await MessageIn.answer(_TELEGRAM_DP_CHOOSE_VARIANT, reply_markup=StartInlineKeyboard)

@TelegramBotDispatcher.message_handler(commands=["start"])
async def Start(MessageIn : types.Message) -> None:
    """
    Send start form to the user.
    """
    logging.info("[pm-handler] Send start form --> ID: " + str(MessageIn.from_user.id))             
    if not UsersDatabase.UsertExists(MessageIn.from_user.id):
        logging.info("[pm-handler] Registered new user --> ID: " + str(MessageIn.from_user.id))             
        UsersDatabase.AddUser(MessageIn.from_user.id)
    logging.info("[pm-handler] Sending message --> ID: " + str(MessageIn.from_user.id))             
    await MessageIn.answer(_TELEGRAM_DP_STARTMESSAGE.format(MessageIn.from_user.first_name), reply_markup=types.ReplyKeyboardRemove())    
    await MessageIn.answer(_TELEGRAM_DP_CHOOSE_VARIANT, reply_markup=StartInlineKeyboard)

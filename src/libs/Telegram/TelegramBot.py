import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class TelegramBot:
    
    def __init__(self, token, handler):
        
        self.handler = handler
        self.token = token
        self.bot = telepot.Bot(token)
        
        MessageLoop(self.bot, self.handler).run_as_thread()
        
    def getBot(self):
        return self.bot
    
    def getHandler(self):
        return self.handler
        
    def sendMessage(self, chat_id, text, reply_markup=None):
        return self.bot.sendMessage(chat_id, text=text, reply_markup=reply_markup)
    
    def answerCallbackQuery(self, query_id, text):
        self.bot.answerCallbackQuery(query_id, text)
    
    def editMessageText(self, msg_identifier, text, reply_markup=None):
        self.bot.editMessageText(msg_identifier, text, reply_markup)
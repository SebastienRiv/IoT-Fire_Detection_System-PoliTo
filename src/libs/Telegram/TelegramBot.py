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
        self.bot.sendMessage(chat_id, text=text, reply_markup=reply_markup)
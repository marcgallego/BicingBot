import telegram
from telegram.ext import Updater, CommandHandler

#textos
startText = "Hola! Soc un bot de bicicletes"
helpText = "Coses que puc fer i presentacio i ajuda i tal i cual"
authorsText = "Marc Gallego i Marc Vernet i blablabla"

#funcions
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=startText)

def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=helpText)

def authors(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=authorsText)

def graph(bot, update, args):
    bot.send_message(chat_id=update.message.chat_id, text="algo")

def nodes(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="algo")

def edges(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="algo")

def components(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="algo")

def plotgraph(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="algo")

def route(bot, update, args):
    bot.send_message(chat_id=update.message.chat_id, text="algo")


# declara una constant amb el access token que llegeix de token.txt
TOKEN = open('token.txt').read().strip()

# crea objectes per treballar amb Telegram
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

# indica que quan el bot rebi la comanda  s'executi la funció
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('authors', authors))
dispatcher.add_handler(CommandHandler('graph', graph, pass_args=True))
dispatcher.add_handler(CommandHandler('nodes', nodes))
dispatcher.add_handler(CommandHandler('edges', edges))
dispatcher.add_handler(CommandHandler('components', components))
dispatcher.add_handler(CommandHandler('plotgraph', plotgraph))
dispatcher.add_handler(CommandHandler('route', route, pass_args=True))

# engega el bot
updater.start_polling()

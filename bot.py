import telegram
from telegram.ext import Updater, CommandHandler
import networkx as nx
import os

from dataBasic import dibuixaMapa, creaGraf

'''
Coses que falten a fer:
    --funcio components i route
    --comprovar que funciona per més d'un usuari a la vegada (caldrà canviar el nom de les fotos)
    --acabar d'arreglar els textos
    --fer alguna cosa extra per anar de sobrats(amb la capacitat de cada estacio o la altitud)
    --posar algun easteregg aixi fino per las risas

Comentaris:
    -- segons la documentacio el graf per defecte ha de ser de mida 1000.
            Ara es crea a /start pero no entenc molt be com va la cosa
    --Hi ha un diccionari per relacionar cada id d'usuari amb el seu graf, nose si funciona
'''

#textos
startText = "Hola! Sóc un bot del Bicing de Barcelona. \nPer més informació escriu /help."
helpText = "Coses que puc fer i presentacio i ajuda i tal i cual"
authorsText = "Els meus autors són: \nMarc Gallego: marc.gallego.asin@est.fib.upc.edu \nMarc Vernet:marc.vernet@est.fib.upc.edu"

usuaris = dict()

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=startText)
    usuaris[update.message.chat_id] = creaGraf(1)

def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=helpText)

def authors(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=authorsText)

def graph(bot, update, args):
    usuaris[update.message.chat_id] = creaGraf(int(args[0])/1000)
    bot.send_message(chat_id=update.message.chat_id, text="graf fet")

def nodes(bot, update):
    n = usuaris[update.message.chat_id].number_of_nodes()
    bot.send_message(chat_id=update.message.chat_id, text=n)

def edges(bot, update):
    n = usuaris[update.message.chat_id].number_of_edges()
    bot.send_message(chat_id=update.message.chat_id, text=n)

def components(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="algo")

def plotgraph(bot, update):
    dibuixaMapa(usuaris[update.message.chat_id])
    bot.send_photo(chat_id=update.message.chat_id, photo=open('map.png', 'rb'))
    os.remove("map.png")

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

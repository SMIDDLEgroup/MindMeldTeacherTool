from datetime import datetime

from telebot import TeleBot

from provider_bot.__init__ import app
from mindmeld.components.dialogue import Conversation
from provider_bot.bot_db import create_database
from provider_bot.utils.state_logger import timestamp, LOGEND

with open(f'loggs/{timestamp()}.txt', 'w') as logger:
    bot = TeleBot(__name__)

    conversations = {}

    @bot.route('/start')
    def reply(message):
        try:
            username = message['chat']['username'].lower()
        except:
            return

        conversations[username] = {}
        conversations[username]['data'] = {'username': username}
        conversations[username]['conversation'] = Conversation(app=app, context=conversations[username]['data'])

        print(f"{username} has new session")
        print("==========================")
        bot.send_message(message['chat']['id'], "")

    @bot.route('.*')
    def reply(message):
        try:
            request_text = message['text']
            username = message['chat']['username'].lower()
        except:
            return

        if username not in conversations:
            conversations[username] = {}
            conversations[username]['data'] = {'username': username}
            conversations[username]['conversation'] = Conversation(app=app, context=conversations[username]['data'])

        resps = conversations[username]['conversation'].say(request_text)

        for resp in resps:
            print(username)
            print(request_text)
            history = conversations[username]['conversation'].history
            if history:
                intent = history[0]['request']['intent']
                resp += f"\n[{intent}]"
                if history[0]['request']['entities']:
                    resp += "\nEntities"
                    for e in history[0]['request']['entities']:
                         resp += f"\n{e}"
            logger.write(":::\n".join(str(l) for l in [timestamp(), username, request_text, resp, LOGEND]))
            print(resp)
            print(LOGEND, end='')
            bot.send_message(message['chat']['id'], resp)


    create_database()
    bot.config['api_key'] = '1690556509:AAEejV2fvqsexl8KgWbtLsb1IjRbTujzHo0'
    bot.poll(debug=True)


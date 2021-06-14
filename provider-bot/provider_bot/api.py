from flask import Flask, request, jsonify
from provider_bot.__init__ import app
from mindmeld.components.dialogue import Conversation
from provider_bot.bot_db import create_database

api = Flask(__name__)
conversation = Conversation(app=app, context={'username': 'inmost_light'})

def simplify_entity(e):
    if e is None:
        return None
    if e['type'] == 'sys_time':
        if e['role'] == 'day':
            return str(e['value'][0]['value'])[:10]
        if e['role'] == 'hour':
            return str(e['value'][0]['value'])[11:16]
        else:
            raise NotImplementedError('Unknown sys_time role')
    if e['type'] == 'service_plan':
        return e['value'][0]['cname']
    if e['type'] == 'sys_number':
        return e['value'][0]['value']
    else:
        raise NotImplementedError('Unknown entity type')

@api.route('/api',methods = ['POST'])
def endpoint():
    message = request.json['message']
    conversation.say(message)
    history = conversation.history
    e1 = history[0]['request']['entities'][0] if len(history[0]['request']['entities']) > 0 else None
    e2 = history[0]['request']['entities'][1] if len(history[0]['request']['entities']) > 1 else None

    return jsonify({"intent": history[0]['request']['intent'],
                    "entity1": simplify_entity(e1),
                    "entity2": simplify_entity(e2)})

api.run(host= '0.0.0.0',debug=True)

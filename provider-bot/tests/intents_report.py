import json
from collections import Counter, defaultdict

from provider_bot.__init__ import app
from mindmeld.components.dialogue import Conversation

with open('./ intents.json') as intents_file:
    intents = json.loads(intents_file.read())

actual_intents_count = Counter(intents.values())
intents_count = defaultdict(lambda: 0)

true_positive = defaultdict(lambda: 0)
false_positive = defaultdict(lambda: 0)
false_negative = defaultdict(lambda: 0)
for prompt, actual_intent in intents.items():
    conversation = Conversation(app=app, context={'username': 'inmost_light'})
    conversation.say(prompt)
    intent = conversation.history[0]['request']['intent']
    if intent == actual_intent:
        true_positive[intent] += 1
    else:
        false_positive[intent] += 1
        false_negative[actual_intent] += 1

for intent in actual_intents_count:
    if intent not in true_positive:
        print(f'{intent} is absent!')
    else:
        print(f'{intent}: p:{true_positive[intent] / (true_positive[intent] + false_positive[intent])}' +
              f' r:{true_positive[intent] / (true_positive[intent] + false_negative[intent])}')



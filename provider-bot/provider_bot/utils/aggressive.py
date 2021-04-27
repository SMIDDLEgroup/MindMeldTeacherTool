import re

with open('./provider_bot/utils/aggressive.txt') as f:
    words = {w.lower().strip() for w in f.readlines()}


def is_aggressive(text):
    text = re.sub('\!\?\,\;\.', '', text).lower().split(' ')
    for w in text:
        if w in words:
            return True
    return False

def aggressive_filter(state):
    def _state(request, responder):
        if not is_aggressive(request.text):
            state(request, responder)
        else:
            responder.frame["aggressive_count"] = responder.frame.get("aggressive_count", 0) + 1
            if responder.frame["aggressive_count"] > 2:
                responder.frame["aggressive_count"] = 0
                responder.reply("Заспокойтесь, ми з'єднаємо вас з оператором!")
            else:
                responder.reply("Заспокойтеся, будь ласка, ми вирішимо вашу проблему.")
    _state.__name__ = state.__name__
    return _state
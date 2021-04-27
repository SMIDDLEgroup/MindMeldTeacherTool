from datetime import datetime

LOGEND = "==========================\n"


def timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")


logger = open(f'loggs/states{timestamp()}.txt', 'w')


def logged(state):
    def _state(request, responder):
        state_name = state.__name__
        username = request.context.get('username')
        intent = request.intent
        request_text = request.text
        entities = request.entities
        state(request, responder)
        directives = responder.directives
        logger.write(":::\n".join(
            str(l) for l in [timestamp(), username, state_name, f"[{intent}]", entities, request_text, directives, LOGEND]))
        logger.flush()

    _state.__name__ = state.__name__
    return _state

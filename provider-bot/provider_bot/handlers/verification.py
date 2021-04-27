from provider_bot.root import app
from provider_bot.bot_db import get_user_data
from provider_bot.handlers.general import default
from provider_bot.utils.state_logger import logged
from provider_bot.utils.aggressive import aggressive_filter


def create_dialog(dialog_name, steps, target_flag):
    dialog_lock = dialog_name + '_lock'

    def step_builder(entity_params):
        lock_name = entity_params['name'] + '_count'

        def _dialog_step(request, responder):
            # if request.intent == 'abort':
            #     responder.reply('Зрозуміло. Чим ще можемо вам допомогти?')
            #     return
            responder.frame['user'] = get_user_data(request.context['username'])
            entity = None
            for e in request.entities:
                if e['type'] == entity_params['type'] and e['role'] == entity_params['role']:
                    entity = entity_params['converter'](e['value'][0]['value'])
            if not entity:
                responder.frame[lock_name] = responder.frame.get(lock_name, 0) + 1
                if responder.frame[lock_name] < 3:
                    responder.params.target_dialogue_state = entity_params['name']
                    responder.reply(entity_params['prompt'])
                    return
                else:
                    responder.frame[lock_name] = 0
                    responder.reply(entity_params['enter_fail_message'])
                    return
            responder.frame[lock_name] = 0
            if entity_params['validator'](responder.frame, entity):
                responder.frame[dialog_lock] = 0
                if 'final' in entity_params:
                    responder.frame[target_flag] = True
                    if 'return_to' in responder.frame and responder.frame['return_to']:
                        responder.frame['return_to'](request, responder)
                    else:
                        default(request, responder)
                else:
                    responder.params.target_dialogue_state = entity_params['next_step']
                    responder.reply(entity_params['next_step_prompt'])
            else:
                responder.frame[dialog_lock] = responder.frame.get(dialog_lock, 0) + 1
                if responder.frame[dialog_lock] > 3:
                    responder.frame[dialog_lock] = 0
                    responder.reply(entity_params['validation_fail_message'])
                else:
                    responder.params.target_dialogue_state = entity_params['name']
                    responder.reply(entity_params['validation_retry_message'])

        return _dialog_step

    for i in range(len(steps) - 1):
        steps[i]['next_step'] = steps[i + 1]['name']
        steps[i]['next_step_prompt'] = steps[i + 1]['prompt']

    steps_handlers = []
    for step in steps:
        handler = step_builder(step)
        handler.__name__ = step['name']
        steps_handlers.append(handler)

    #steps_handlers[0] = app.handle(intent=dialog_name)(steps_handlers[0])
    steps_handlers[0] = app.handle(targeted_only=True)(aggressive_filter(logged(steps_handlers[0])))
    for i in range(len(steps_handlers) - 1):
        i = i + 1
        steps_handlers[i] = app.handle(targeted_only=True)(aggressive_filter(logged(steps_handlers[i])))

    return steps_handlers


verify_handlers = create_dialog('verification', [
    {
        'name': 'verify_service_number',
        'type': 'sys_number',
        'role': 'service_number',
        'converter': lambda e: e,
        'prompt': "Введіть 8 цифр вашого договору.",
        'enter_fail_message': "Не вдалося розпізнати номер договору. З'єдную з оператором.",
        'validator': lambda frame, e: frame['user']['id'] == e,
        'validation_fail_message': "Номер договору не дійсний. З'єдную з оператором.",
        'validation_retry_message': "Номер договору не дійсний. Спробуйте ще.",
    },
    {
        'name': 'verify_house_number',
        'type': 'sys_number',
        'role': 'house_number',
        'converter': str,
        'prompt': "Введіть номер вашого будинку.",
        'enter_fail_message': "Не вдалося розпізнати номер будинку. З'єдную з оператором.",
        'validator': lambda frame, e: frame['user']['house_number'] == e,
        'final': True,
        'validation_fail_message': "Номер будинку не співпадає. З'єдную з оператором.",
        'validation_retry_message': "Номер будинку не дійсний. Спробуйте ще.",
    }
], 'verified')

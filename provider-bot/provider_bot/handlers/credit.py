from datetime import datetime, timedelta

from provider_bot.root import app
from provider_bot.bot_db import get_user_data, get_service_plan, set_credit_flag
from provider_bot.utils.state_logger import logged
from provider_bot.utils.aggressive import aggressive_filter


@app.handle(intent='get_credit')
@logged
@aggressive_filter
def get_credit(request, responder):
    responder.frame['user'] = get_user_data(request.context['username'])
    if responder.frame['user']['credit']:
        responder.reply('Послугу "Кредит довіри" уже підключено. Чим ще можемо вам допомогти?')
        return
    if request.intent == 'abort':
        responder.reply('Можливо у вас є ще якісь питання?')
        return
    if request.intent in ['confirmation', 'get_credit', 'repeat', 'clarify']:
        responder.params.target_dialogue_state = 'turn_on_credit'
        responder.reply('З послугою "Кредит довіри" ви можете відновити постачання інтернету одразу, '
                        'а заплатити протягом 10 днів. Бажаєте підключити цю послугу зараз?')
        return
    else:
        responder.reply('Перепрошую, я вас не зрозуміла. Чим ще можемо вам допомогти?')
        return


@app.handle(targeted_only=True)
@logged
@aggressive_filter
def turn_on_credit(request, responder):
    if request.intent == 'abort':
        responder.reply('Зрозуміло. Чим ще можемо вам допомогти?')
        return
    if request.intent in ['confirmation', 'clarify']:
        if not responder.frame.get('verified', False):
            responder.params.target_dialogue_state = 'verify_service_number'
            responder.frame['return_to'] = turn_on_credit_continue
            responder.reply(f"Спочатку пройдіть верифікацію. Введіть 8 цифр вашого договору.")
            return
        else:
            turn_on_credit_continue(request, responder)
            return
    if request.intent == 'repeat':
        get_credit(request, responder)
        return
    else:
        responder.frame['credit_count'] = responder.frame.get('credit_count', 0) + 1
        if responder.frame['credit_count'] < 3:
            responder.params.target_dialogue_state = 'turn_on_credit'
            responder.reply('Перепрошую, я вас не зрозуміла.')
            return
        else:
            responder.frame['credit_count'] = 0
            responder.reply('Перепрошую, я вас не зрозуміла. Чим ще можемо вам допомогти?')
            return


@app.handle(targeted_only=True)
@logged
@aggressive_filter
def turn_on_credit_continue(request, responder):
    responder.frame['user'] = get_user_data(request.context['username'])
    responder.frame['service_plan'] = get_service_plan(responder.frame['user']['service_plan_id'])
    responder.params.target_dialogue_state = 'turn_on_credit_processing'
    responder.reply(f'Ми можемо внести вам кредит довіри на суму {responder.frame["service_plan"]["price"]}' +
                    f' до {str(datetime.now() + timedelta(days=10))[:10]}.' +
                    f'Сплатити {abs(responder.frame["user"]["balance"]) + responder.frame["service_plan"]["price"]} грн '
                    f'потрібно протягом 10 днів. ' +
                    f'Вас влаштовують такі умови?')


@app.handle(targeted_only=True)
@logged
@aggressive_filter
def turn_on_credit_processing(request, responder):
    if request.intent == 'confirmation':
        set_credit_flag(responder.frame['user']['id'], True)
        responder.reply('Послугу "Кредит довіри" підключено.')
        return
    if request.intent == 'abort':
        responder.reply('Зрозуміло. Чим іще ми можемо вам допомогти?')
        return
    if request.intent == 'repeat':
        turn_on_credit_continue(request, responder)
        return
    else:
        responder.frame['credit_process_count'] = responder.frame.get('credit_process_count', 0) + 1
        if responder.frame['credit_process_count'] < 3:
            responder.frame['user'] = get_user_data(request.context['username'])
            responder.frame['service_plan'] = get_service_plan(responder.frame['user']['service_plan_id'])
            responder.params.target_dialogue_state = 'turn_on_credit_processing'
            responder.reply('Перепрошую, я вас не зрозуміла.\n' +
                            f'Ми можемо внести вам кредит довіри на суму {responder.frame["service_plan"]["price"]}' +
                            f' до {str(datetime.now() + timedelta(days=10))[:10]}.' +
                            f'Сплатити {abs(responder.frame["user"]["balance"]) + responder.frame["service_plan"]["price"]} грн '
                            f'потрібно протягом 10 днів. ' +
                            f'Вас влаштовують такі умови?')
            return
        else:
            responder.frame['credit_process_count'] = 0
            responder.reply('Перепрошую, я вас не зрозуміла. Чим ще можемо вам допомогти?')
            return

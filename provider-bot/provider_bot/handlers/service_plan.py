from provider_bot.root import app
from provider_bot.bot_db import get_user_data, get_service_plan
from provider_bot.vocalizer import vocalized_name
from provider_bot.utils.state_logger import logged
from provider_bot.utils.aggressive import aggressive_filter


@app.handle(intent='change_service_plan')
@logged
@aggressive_filter
def change_service_plan(request, responder):
    for e in request.entities:
        if e['type'] == 'service_plan':
            selected_plan = e['value'][0]
    if not responder.frame.get('verified', False):
        responder.params.target_dialogue_state = 'verify_service_number'
        responder.frame['return_to'] = change_service_plan
        responder.reply(f"Спочатку пройдіть верифікацію. Введіть 8 цифр вашого договору.")
    else:
        responder.frame['user'] = get_user_data(request.context['username'])
        responder.frame['service_plan'] = get_service_plan(responder.frame['user']['service_plan_id'])
        responder.params.target_dialogue_state = 'change_service_plan_selection'
        responder.reply(f"Зараз ваш тарифний план {responder.frame['service_plan']['name']}." +
                        f" На який тарифний план ви бажаєте перейти?")


@app.handle(targeted_only=True)
@logged
@aggressive_filter
def change_service_plan_selection(request, responder):
    if request.intent == 'abort':
        responder.reply("Зрозуміло. Чим ще ми можемо вам допомогти?")
        return
    if request.intent == 'clarify':
        responder.reply("- Смідл Спорт HD Pro +100\n- Смідл Power Time Pro +200\n- Premium HD +200")
        responder.params.target_dialogue_state = 'change_service_plan_selection'
        return
    if request.intent == 'specify_service_plan':
        selected_plan = None
        for e in request.entities:
            if e['type'] == 'service_plan':
                selected_plan = e['value'][0]
        if selected_plan and selected_plan['id'] != responder.frame['service_plan']['id']:
            responder.frame['selected_service_plan'] = get_service_plan(selected_plan['id'])
            responder.params.target_dialogue_state = 'change_service_plan_confirm'
            responder.reply("Ви бажаєте змінити ваш тарифний план з " +
                            f"{responder.frame['service_plan']['name']} на " +
                            f"{responder.frame['selected_service_plan']['name']}?")
            return
    responder.frame['change_service_plan_selection_count'] = responder.frame.get('change_service_plan_selection_count', 0) + 1
    if responder.frame['change_service_plan_selection_count'] < 3:
        responder.params.target_dialogue_state = 'change_service_plan_selection'
        responder.reply(f"Зараз ваш тарифний план {responder.frame['service_plan']['name']}." +
                        f" На який тарифний план ви бажаєте перейти?")
        return
    else:
        responder.frame['change_service_plan_selection_count'] = 0
        responder.reply(f"{vocalized_name(request.context['username'])},  зачекайте на з'єднання, будь ласка.")


@app.handle(targeted_only=True)
@logged
@aggressive_filter
def change_service_plan_confirm(request, responder):
    if request.intent == 'abort':
        responder.reply('Зрозуміло. Чим ще ми можемо вам допомогти?')
        return
    if request.intent == 'confirmation':
        responder.params.target_dialogue_state = 'change_service_plan_changed'
        responder.reply(f"Вартість нового тарифного плану складатиме" +
                        f" {responder.frame['selected_service_plan']['price']}. " +
                        f"Ви підтверджуєте перехід на тарифний план " +
                        f"{responder.frame['selected_service_plan']['name']}?")
        return
    else:
        responder.frame['change_service_plan_confirm_count'] = responder.frame.get('change_service_plan_confirm_count', 0) + 1
        if responder.frame['change_service_plan_confirm_count'] < 3:
            responder.params.target_dialogue_state = 'change_service_plan_confirm'
            responder.reply("Ви бажаєте змінити ваш тарифний план з " +
                            f"{responder.frame['service_plan']['name']} на " +
                            f"{responder.frame['selected_service_plan']['name']}?")
            return
        else:
            responder.frame['change_service_plan_confirm_count'] = 0
            responder.reply(f"{vocalized_name(request.context['username'])},  зачекайте на з'єднання, будь ласка.")


@app.handle(targeted_only=True)
@logged
@aggressive_filter
def change_service_plan_changed(request, responder):
    if request.intent == 'abort':
        responder.reply('Зрозуміло. Чим ще ми можемо вам допомогти?')
        return
    if request.intent == 'confirmation':
        responder.reply("Ваш тарифний план змінено. Чим ще ми можемо вам допомогти?")
        return
    else:
        responder.frame['change_service_plan_changed_count'] = responder.frame.get('change_service_plan_changed_count', 0) + 1
        if responder.frame['change_service_plan_changed_count'] < 3:
            responder.params.target_dialogue_state = 'change_service_plan_changed'
            responder.reply(f"Вартість нового тарифного плану складатиме" +
                            f" {responder.frame['selected_service_plan']['price']}. " +
                            f"Ви підтверджуєте перехід на тарифний план " +
                            f"{responder.frame['selected_service_plan']['name']}?")
            return
        else:
            responder.frame['change_service_plan_confirm_count'] = 0
            responder.reply(f"{vocalized_name(request.context['username'])},  зачекайте на з'єднання, будь ласка.")
        return


@app.handle(intent='stop_service')
@logged
@aggressive_filter
def stop_service(request, responder):
    responder.reply("Зачекайте, ми з'єднаємо вас зі спеціалістом з подібних запитів.")


@app.handle(intent='service_plan_description')
@logged
@aggressive_filter
def service_plan_description(request, responder):
    responder.frame['user'] = get_user_data(request.context['username'])
    responder.frame['service_plan'] = get_service_plan(responder.frame['user']['service_plan_id'])
    responder.reply(f"Ваш тарифний план {responder.frame['service_plan']['name']}.\n" +
                    f"{responder.frame['service_plan']['description']}\n" +
                    f"Вартість складає {responder.frame['service_plan']['price']} "
                    f"гривень на місяць.")

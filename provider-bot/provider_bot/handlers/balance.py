from provider_bot.root import app
from provider_bot.bot_db import get_user_data
from provider_bot.utils.state_logger import logged
from provider_bot.utils.aggressive import aggressive_filter


@app.handle(intent='check_balance')
@logged
@aggressive_filter
def check_balance(request, responder):
    if not responder.frame.get('verified', False):
        responder.params.target_dialogue_state = 'verify_service_number'
        responder.frame['return_to'] = check_balance
        responder.reply(f"Спочатку пройдіть верифікацію. Введіть 8 цифр вашого договору.")
    else:
        balance = get_user_data(request.context['username'])['balance']
        responder.reply(f"Ваш баланс: {balance}")

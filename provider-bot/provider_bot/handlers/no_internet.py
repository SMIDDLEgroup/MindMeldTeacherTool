from provider_bot.root import app
from provider_bot.bot_db import get_user_data
from provider_bot.utils.state_logger import logged
from provider_bot.utils.aggressive import aggressive_filter


@app.handle(intent='no_internet')
@logged
@aggressive_filter
def no_internet(request, responder):
    if not responder.frame.get('verified', False):
        responder.params.target_dialogue_state = 'verify_service_number'
        responder.frame['return_to'] = no_internet
        responder.reply(f"Спочатку пройдіть верифікацію. Введіть 8 цифр вашого договору.")
    else:
        user = get_user_data(request.context['username'])
        balance = user['balance']
        repair = user['repair']
        if balance < 0:
            reply = f'Остання оплата на ваш рахунок була здійснена' + \
                    f' {user["last_payment_date"]} у розмірі {user["last_payment_amount"]} грн.' + \
                    f'Наразі ваша заборгованість складає {abs(balance)} грн.' \
                    f'Сплатіть, будь ласка, {abs(balance)} грн, щоб відновити послугу інтернету.\n\n'
            if not user['credit']:
                reply += f'Чи бажаєте ви дізнатися про послугу "Кредит довіри"?'
                responder.params.target_dialogue_state = 'get_credit'
            responder.reply(reply)
        elif repair:
            responder.reply('Через технічні несправності інтернет у вас не працює.'
                            ' Наші спеціалісти вирішать цю проблему якомога швидше.'
                            ' Чи можемо ми вам ще чимось допомогти?')
        else:
            responder.reply("Зачекайте, ми з'єднаємо вас з оператором!")

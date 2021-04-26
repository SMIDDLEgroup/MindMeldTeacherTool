from provider_bot.root import app
from provider_bot.bot_db import get_user_data
from provider_bot.vocalizer import vocalized_name
from provider_bot.utils.state_logger import logged
from provider_bot.utils.aggressive import aggressive_filter

@app.handle(default=True)
@logged
@aggressive_filter
def default(request, responder):
    """This is a default handler."""
    responder.reply('Перепрошую?')


@app.handle(intent='thanks')
@logged
@aggressive_filter
def thanks(request, responder):
    responder.reply(['Прошу.', 'Завжди рада допомогти.'])


@app.handle(intent='small_talk')
@logged
@aggressive_filter
def small_talk(request, responder):
    responses = ['Я би з задоволенням з вами поспілкувалася, але можу допомогти лише з послугами компанії "Смідл".',
                 'Я можу допомогти вам з такими питаннями:\n- перевірити баланс\n- виклик майстра додому\n- зміна тарифного плану\n- опис вашого тарифного плану\n- послуга "Кредит довіри"\n- перевірка проблем з роботою інтернету.',
                 'На жаль, на це відповісти я не зможу.',
                 'Я розумію, що вам цікаво зі мною погратися, але я не найкращий співбесідник, якщо справа не стосується послуг компанії "Смідл"',
                 'Що ж, якщо будуть питання щодо послуг компанії "Смідл" - звертайтесь.']
    responder.frame['small_talk_cycle'] = responder.frame.get('small_talk_cycle', 0)
    responder.reply(responses[responder.frame['small_talk_cycle']])
    responder.frame['small_talk_cycle'] += 1
    if responder.frame['small_talk_cycle'] >= len(responses):
        responder.frame['small_talk_cycle'] = 0

@app.handle(intent='competence')
@logged
@aggressive_filter
def competence(request, responder):
    responder.reply('Я можу допомогти вам з такими питаннями:\n- перевірити баланс\n- виклик майстра додому\n- зміна тарифного плану\n- опис вашого тарифного плану\n- послуга "Кредит довіри"\n- перевірка проблем з роботою інтернету.')

@app.handle(intent='confirmation')
@logged
@aggressive_filter
def confirmation(request, responder):
    responder.reply(['Чим саме я можу вам допомогти?',
                     'Сформулюйте, будь ласка, ваш запит.'])


@app.handle(intent='greet')
@logged
@aggressive_filter
def welcome(request, responder):
    responder.frame['greeted'] = responder.frame.get('greeted', False)
    username = get_user_data(request.context.get('username'))['username']
    if not responder.frame['greeted']:
        responder.frame['greeted'] = True
        if username:
            responder.reply(f'Вітаю, {vocalized_name(username)}!')
        else:
            responder.reply('Вітаю!')
    else:
        responder.reply([f'Слухаю вас',
                         f'Так-так, я вас слухаю',
                         f'Так, {vocalized_name(username)}, чим можу допомогти?'])


@app.handle(intent='abort')
@logged
@aggressive_filter
def abort(request, responder):
    responder.reply("Буду рада вам допомогти, якщо виникнуть проблеми.")


@app.handle(intent='goodbye')
@logged
@aggressive_filter
def goodbye(request, responder):
    responder.reply(['До побачення!', 'До зустрічі!', "На зв'язку!", "Бувайте!"])


@app.handle(intent='suicide')
@logged
@aggressive_filter
def suicide(request, responder):
    responder.reply("Ми готові вас вислухати, зачекайте хвилинку.")

@app.handle(intent='clarify')
@logged
@aggressive_filter
def clarify(request, responder):
    responder.reply(['Що саме вас цікавить?',
                     'Сформулюйте, будь ласка, ваш запит.',
                     'Чим саме я можу вам допомогти?'])
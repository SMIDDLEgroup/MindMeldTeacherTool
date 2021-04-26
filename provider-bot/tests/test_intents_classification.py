from provider_bot.__init__ import app
from mindmeld.components.dialogue import Conversation
import unittest

class TestIntents(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.conversation = Conversation(app=app, context={'username': 'inmost_light'})

    def test_hello(self):
        message = "Привітулі!"
        self.conversation.say(message)
        intent = self.conversation.history[0]['request']['intent']
        self.assertEqual(intent, "greet")

    def test_check_balance(self):
        message = "Скільки грошей у мене на рахунку?"
        self.conversation.say(message)
        intent = self.conversation.history[0]['request']['intent']
        self.assertEqual(intent, "check_balance")
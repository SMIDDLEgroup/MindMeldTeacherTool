# -*- coding: utf-8 -*-
from provider_bot.root import app
from provider_bot.bot_db import get_user_data, get_service_plan, set_credit_flag, call_home_service
from provider_bot import custom_features
from provider_bot.vocalizer import vocalized_name

from provider_bot.handlers import general, verification, balance, credit, no_internet, service_plan, balance_and_home_service

__all__ = ['app']

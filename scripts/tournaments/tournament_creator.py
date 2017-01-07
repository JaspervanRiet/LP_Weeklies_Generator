#!/usr/bin/python
# -*- coding: utf-8  -*-
from forex_python.converter import CurrencyRates

import pywikibot
from pywikibot import config, Bot, i18n
import datetime

"""

Contains functions that turn the tournament templates into proper pages

"""
class TournamentCreator:
    def __init__(self, edition, date):
        self.edition = int(edition)
        self.date = date
        self.date_match = (datetime.datetime
            .strptime(date, "%Y-%m-%d")
            .strftime("%B %d, %Y"))

    def create_tournament(self, contents):
        contents = contents.replace("VOGANBOT_DATE_TOURNAMENT", self.date)
        contents = contents.replace("VOGANBOT_DATE_MATCH", self.date_match)
        contents = contents.replace("VOGANBOT_EDITION_PREV",
                str(self.edition - 1))
        contents = contents.replace("VOGANBOT_EDITION_NEXT",
                str(self.edition+ 1))
        contents = contents.replace("VOGANBOT_EDITION",
                str(self.edition))

    def create_europe_gfinity_friday(self, contents):
        self.create_tournament(contents)
        currency_converter = CurrencyRates()
        gbp_exchange_rate = currency_converter.get_rate('GBP', 'USD')

        contents = contents.replace(
                "VOGANBOT_PRIZE_1", str(200*gbp_exchange_rate))
        contents = contents.replace(
                "VOGANBOT_PRIZE_2", str(50*gbp_exchange_rate))
        contents = contents.replace(
                "VOGANBOT_TOTAL_PRIZE", str(250*gbp_exchange_rate))

        return contents

    def create_europe_gfinity_monday(self, contents):
        self.create_tournament(contents)

        currency_converter = CurrencyRates()
        gbp_exchange_rate = currency_converter.get_rate('GBP', 'USD')

        contents = contents.replace(
                "VOGANBOT_PRIZE_1", str(100*gbp_exchange_rate))
        contents = contents.replace(
                "VOGANBOT_PRIZE_2", str(50*gbp_exchange_rate))
        contents = contents.replace(
                "VOGANBOT_TOTAL_PRIZE", str(150*gbp_exchange_rate))

        return contents

    def create_overwatch_go4(self, contents):
        # self.create_tournament(contents)
        contents = contents.replace("VOGANBOT_DATE_TOURNAMENT", self.date)
        contents = contents.replace("VOGANBOT_DATE_MATCH", self.date_match)
        contents = contents.replace("VOGANBOT_EDITION_PREV",
                str(self.edition - 1))
        contents = contents.replace("VOGANBOT_EDITION_NEXT",
                str(self.edition+ 1))
        contents = contents.replace("VOGANBOT_EDITION",
                str(self.edition))

        currency_converter = CurrencyRates()
        exchange_rate = currency_converter.get_rate('EUR', 'USD')

        contents = contents.replace(
                "VOGANBOT_PRIZE_1", str(150*exchange_rate))
        contents = contents.replace(
                "VOGANBOT_TOTAL_PRIZE", str(150*exchange_rate))

        return contents


#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Bot that automatically creates certain weekly tournament for the Liquipedia wikis. Based on the pagefromfile.py bot created by Andre Engels. Adapted by Jasper van Riet.

"""
#
# (C) Jasper van Riet, 2017
# (C) Andre Engels, 2004
# (C) Pywikibot team, 2005-2014
#
# Distributed under the terms of the MIT license.
#
from __future__ import unicode_literals

__version__ = '$Id$'
#

from tournaments.tournament_creator import TournamentCreator
import os
import re
import codecs
import time
import datetime

import pywikibot
from pywikibot import config, Bot, i18n

tournament_type = 0
tournament_edition = 0
tournament_date = ""

class TournamentType(object):
    GFINITY_EU_FRIDAY = 1
    GFINITY_EU_MONDAY = 2
    NEXUS_NA_SATURDAY = 3
    SPL_NA_FRIDAY = 4 
    OVERWATCH_GO4 = 5

class NoTitle(Exception):

    """No title found."""

    def __init__(self, offset):
        """Constructor."""
        self.offset = offset


class PageFromFileRobot(Bot):

    """
    Responsible for writing pages to the wiki.

    Titles and contents are given by a PageFromFileReader.

    """

    def __init__(self, reader, **kwargs):
        """Constructor."""
        self.availableOptions.update({
            'always': True,
            'force': False,
            'append': None,
            'summary': None,
            'minor': False,
            'autosummary': False,
            'nocontent': '',
            'redirect': True,
        })

        super(PageFromFileRobot, self).__init__(**kwargs)
        self.reader = reader

    def run(self):
        """Start file processing and upload content."""
        for title, contents in self.reader.run():
            self.save(title, contents)

    def save(self, title, contents):
        """Upload page content."""
        mysite = pywikibot.Site()

        page = pywikibot.Page(mysite, title)
        self.current_page = page

        if self.getOption('summary'):
            comment = self.getOption('summary')
        else:
            comment = i18n.twtranslate(mysite, 'pagefromfile-msg')

        comment_top = comment + " - " + i18n.twtranslate(
            mysite, 'pagefromfile-msg_top')
        comment_bottom = comment + " - " + i18n.twtranslate(
            mysite, 'pagefromfile-msg_bottom')
        comment_force = "%s *** %s ***" % (
            comment, i18n.twtranslate(mysite, 'pagefromfile-msg_force'))

        # Remove trailing newlines (cause troubles when creating redirects)
        contents = re.sub('^[\r\n]*', '', contents)

        creator = TournamentCreator(tournament_edition, tournament_date)
        if tournament_type == TournamentType.GFINITY_EU_FRIDAY:
            contents = creator.create_europe_gfinity_friday(contents)
        elif tournament_type == TournamentType.GFINITY_EU_MONDAY:
            contents = creator.create_europe_gfinity_monday(contents)
        elif tournament_type == TournamentType.NEXUS_NA_SATURDAY:
            contents = creator.create_na_tournament(contents)
	elif tournament_type == TournamentType.SPL_NA_FRIDAY:
            contents = creator.create_na_tournament(contents)
        elif tournament_type == TournamentType.OVERWATCH_GO4:
            contents = creator.create_overwatch_go4(contents)

        if page.exists():
            if not self.getOption('redirect') and page.isRedirectPage():
                pywikibot.output(u"Page %s is redirect, skipping!" % title)
                return
            pagecontents = page.get(get_redirect=True)
            if self.getOption('nocontent') != u'':
                if pagecontents.find(self.getOption('nocontent')) != -1 or \
                pagecontents.find(self.getOption('nocontent').lower()) != -1:
                    pywikibot.output(u'Page has %s so it is skipped' % self.getOption('nocontent'))
                    return
            if self.getOption('append') == 'top':
                pywikibot.output(u"Page %s already exists, appending on top!"
                                     % title)
                contents = contents + pagecontents
                comment = comment_top
            elif self.getOption('append') == 'bottom':
                pywikibot.output(u"Page %s already exists, appending on bottom!"
                                     % title)
                contents = pagecontents + contents
                comment = comment_bottom
            elif self.getOption('force'):
                pywikibot.output(u"Page %s already exists, ***overwriting!"
                                 % title)
                comment = comment_force
            else:
                pywikibot.output(u"Page %s already exists, not adding!" % title)
                return
        else:
            if self.getOption('autosummary'):
                comment = ''
                config.default_edit_summary = ''

        self.userPut(page, page.text, contents,
                     summary=comment,
                     minor=self.getOption('minor'),
                     show_diff=False,
                     ignore_save_related_errors=True)

"""

Checks if given date is within the next 3 days
        
"""
def date_within_three_days(date):
    today = datetime.date.today()
    margin = datetime.timedelta(days = 3)
    return today - margin <= date.date() <= today + margin

class PageFromFileReader:

    """
    Responsible for reading the file.

    The run() method yields a (title, contents) tuple for each found page.

    """

    def __init__(self, filename, pageStartMarker, pageEndMarker,
                 titleStartMarker, titleEndMarker, include, notitle):
        """Constructor.

        Check if self.file name exists. If not, ask for a new filename.
        User can quit.

        """
        self.filename = filename
        self.pageStartMarker = pageStartMarker
        self.pageEndMarker = pageEndMarker
        self.titleStartMarker = titleStartMarker
        self.titleEndMarker = titleEndMarker
        self.include = include
        self.notitle = notitle

    def run(self):
        """Read file and yield page title and content."""
        pywikibot.output('\n\nReading \'%s\'...' % self.filename)

        edition = "" 
        date = "" 

        try:
            with open(self.filename, 'U') as f:
                edition = f.readline()
                date = f.readline()
                text = f.read()

        except IOError as err:
            pywikibot.output(str(err))
            raise IOError
        
        edition = int(edition)
        global tournament_edition
        tournament_edition = edition

        global tournament_date
        date = date.replace('\n', '')
        current_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        if not date_within_three_days(current_date):
            pywikibot.output('\nThis tournament takes place more than 3 days from now!')
            pywikibot.output('Cancelling...')
            quit()

        tournament_date = date

        # Set correct edition for next run
        edition += 1

        # Set next occurence to next week
        next_week = current_date + datetime.timedelta(days=7)
        next_week = next_week.strftime("%Y-%m-%d")
        text = str(edition) + '\n' + next_week + '\n'+ text

        try:
            with open(self.filename, 'w') as f:
                f.writelines(text)
        except IOError as err:
            pywikibot.output(str(err))
            raise IOError

        position = 0
        length = 0
        while True:
            try:
                length, title, contents = self.findpage(text[position:])
                title = title.replace('VOGANBOT_EDITION', str(tournament_edition))
            except AttributeError:
                if not length:
                    pywikibot.output(u'\nStart or end marker not found.')
                else:
                    pywikibot.output(u'End of file.')
                break
            except NoTitle as err:
                pywikibot.output(u'\nNo title found - skipping a page.')
                position += err.offset
                continue

            position += length
            yield title, contents

    def findpage(self, text):
        """Find page to work on."""
        pageR = re.compile(re.escape(self.pageStartMarker) + "(.*?)" +
                           re.escape(self.pageEndMarker), re.DOTALL)
        titleR = re.compile(re.escape(self.titleStartMarker) + "(.*?)" +
                            re.escape(self.titleEndMarker))

        location = pageR.search(text)
        if self.include:
            contents = location.group()
        else:
            contents = location.group(1)
        try:
            title = titleR.search(contents).group(1)
            if self.notitle:
                # Remove title (to allow creation of redirects)
                contents = titleR.sub('', contents, count=1)
        except AttributeError:
            raise NoTitle(location.end())
        else:
            return location.end(), title, contents

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_tournament_type():
    global tournament_type
    list_tournament = [
            "EU - Gfinity Friday",
            "EU - Gfinity Monday",
            "NA - Nexus Saturday",
            "NA - SPL Friday",
            "Overwatch - Go4"]
    user_choice = pywikibot.bot.input_list_choice(
            u"Enter the number of the desired tournament:",
            list_tournament,
            force=False,
            default='0'
            )

    tournament_type = list_tournament.index(user_choice) + 1

def get_filename():
    filename = "scripts/tournaments/"
    if tournament_type == TournamentType.GFINITY_EU_FRIDAY:
        filename += "gfinity_eu_3v3_friday.txt"
    elif tournament_type == TournamentType.GFINITY_EU_MONDAY:
        filename += "gfinity_eu_3v3_monday.txt"
    elif tournament_type == TournamentType.NEXUS_NA_SATURDAY:
        filename += "nexus_na_3v3_saturday.txt"
    elif tournament_type == TournamentType.SPL_NA_FRIDAY:
        filename += "spl_na_3v3_friday.txt"
    elif tournament_type == TournamentType.OVERWATCH_GO4:
        filename += "Go4Overwatch.txt"

    return filename

def main(*args):
    """
    Process command line arguments and invoke bot.

    If args is an empty list, sys.argv is used.

    @param args: command line arguments
    @type args: list of unicode
    """
    # Adapt these to the file you are using. 'pageStartMarker' and
    # 'pageEndMarker' are the beginning and end of each entry. Take text that
    # should be included and does not occur elsewhere in the text.

    # TODO: make config variables for these.
    filename = "dict.txt"
    pageStartMarker = "{{-start-}}"
    pageEndMarker = "{{-stop-}}"
    titleStartMarker = u"'''"
    titleEndMarker = u"'''"
    options = {}
    include = False
    notitle = False

    get_tournament_type()
    filename = get_filename()

    for arg in pywikibot.handle_args(args):
        if arg.startswith("-start:"):
            pageStartMarker = arg[7:]
        elif arg.startswith("-end:"):
            pageEndMarker = arg[5:]
        elif arg.startswith("-file:"):
            filename = arg[6:]
        elif arg == "-include":
            include = True
        elif arg.startswith('-append') and arg[7:] in ('top', 'bottom'):
            options['append'] = arg[7:]
        elif arg == "-force":
            options['force'] = True
        elif arg == "-safe":
            options['force'] = False
            options['append'] = None
        elif arg == "-noredirect":
            options['redirect'] = False
        elif arg == '-notitle':
            notitle = True
        elif arg == '-minor':
            options['minor'] = True
        elif arg.startswith('-nocontent:'):
            options['nocontent'] = arg[11:]
        elif arg.startswith("-titlestart:"):
            titleStartMarker = arg[12:]
        elif arg.startswith("-titleend:"):
            titleEndMarker = arg[10:]
        elif arg.startswith("-summary:"):
            options['summary'] = arg[9:]
        elif arg == '-autosummary':
            options['autosummary'] = True
        else:
            pywikibot.output(u"Disregarding unknown argument %s." % arg)

    failed_filename = False
    while not os.path.isfile(filename):
        pywikibot.output('\nFile \'%s\' does not exist. ' % filename)
        _input = pywikibot.input(
            'Please enter the file name [q to quit]:')
        if _input == 'q':
            failed_filename = True
            break
        else:
            filename = _input

    # show help text from the top of this file if reader failed
    # or User quit.
    if failed_filename:
        pywikibot.showHelp()
    else:
        reader = PageFromFileReader(
                filename, pageStartMarker, pageEndMarker,
                titleStartMarker, titleEndMarker, include,
                notitle)
        bot = PageFromFileRobot(reader, **options)
        bot.run()

if __name__ == "__main__":
    main()

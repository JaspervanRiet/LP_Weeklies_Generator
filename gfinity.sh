#!/bin/bash
cd /home/jaspervanriet/pywikibot
python pwb.py weekly_tournament_generator -notitle -summary:Create <<< '1'
python pwb.py weekly_tournament_generator -notitle -summary:Create <<< '2'
python pwb.py weekly_tournament_generator -notitle -summary:Create <<< '3'
python pwb.py weekly_tournament_generator -notitle -summary:Create <<< '4'
python pwb.py weekly_tournament_generator -notitle -summary:Create <<< '5'


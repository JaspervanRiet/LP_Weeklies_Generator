#!/bin/bash
cd /home/jaspervanriet/pywikibot
python pwb.py weekly_tournament_generator -notitle -summary:Create <<< '1' # Gfinity EU Friday
python pwb.py weekly_tournament_generator -notitle -summary:Create <<< '2' # Gfinity EU Monday
python pwb.py weekly_tournament_generator -notitle -summary:Create <<< '3' # ESL EU Sunday
python pwb.py weekly_tournament_generator -notitle -summary:Create <<< '4' # Nexus NA Saturday
python pwb.py weekly_tournament_generator -notitle -summary:Create <<< '5' # SPL NA Friday
python pwb.py weekly_tournament_generator -notitle -summary:Create <<< '6' # PRL NA Monday


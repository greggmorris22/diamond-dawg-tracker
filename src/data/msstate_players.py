"""
Complete list of Mississippi State University alumni drafted into professional
baseball from 2013 through 2025. Each entry is a (display_name, mlb_id) tuple.

Because IDs are known up front, the app bypasses name-search entirely —
no wrong-player mismatches possible.

The app dynamically filters this list at runtime: only players with active
2026 regular-season stats (at any level) are displayed. Players who are
retired, injured, or otherwise inactive return no stats and are silently
skipped.

Source: MLB Stats API draft endpoint, school = Mississippi State University.
Last updated: 2026-04-04.
"""

MSU_PLAYERS = [
    # 2013
    ("Hunter Renfroe",      592669),
    ("Adam Frazier",        624428),
    ("Kendall Graveman",    608665),
    ("Chad Girodo",         643325),
    ("Evan Mitchell",       641887),
    ("Daryl Norris",        643470),
    ("Luis Pollorena",      643490),
    # 2014
    ("Jacob Lindgren",      605338),
    ("Jonathan Holder",     656547),
    ("Brandon Woodruff",    605540),
    ("Brett Pirtle",        657720),
    # 2015 — no MSU picks found in API
    # 2016
    ("Dakota Hudson",       641712),
    ("Reid Humphreys",      641714),
    ("Daniel Brown",        667681),
    ("Jacob Robson",        615699),
    ("Zac Houston",         667677),
    ("Nathaniel Lowe",      663993),
    ("Gavin Collins",       641468),
    ("Vance Tatum",         667673),
    ("Austin Sexton",       642063),
    ("Jack Kruger",         667674),
    ("Brent Rooker",        667670),
    # 2017
    ("Ryan Gridley",        667667),
    ("Jake Mangum",         663968),
    # 2018
    ("Konnor Pilkington",   663455),
    ("J.P. France",         641585),
    ("Hunter Stovall",      667663),
    ("Ethan Small",         663629),
    ("Zach Neff",           679820),
    ("Jacob Billingsley",   667679),
    # 2019
    ("Colby White",         686831),
    ("Trysten Barlow",      663679),
    ("Dustin Skelton",      670236),
    ("Jared Liebelt",       679823),
    ("Keegan James",        667669),
    ("Peyton Plumlee",      690183),
    ("Cole Gordon",         656478),
    ("Tanner Allen",        669327),
    # 2020
    ("Justin Foscue",       679822),
    ("Jordan Westburg",     676059),
    ("J.T. Ginn",           669372),
    # 2021
    ("Will Bednar",         687218),
    ("Eric Cerantola",      672021),
    ("Christian MacLeod",   681306),
    ("Rowdey Jordan",       679821),
    # 2022
    ("Landon Sims",         683085),
    ("Logan Tanner",        683091),
    ("Preston Johnson",     699980),
    ("K.C. Hunt",           687268),
    ("Jackson Fristoe",     690977),
    ("Kamren James",        687553),
    # 2023
    ("Colton Ledbetter",    807742),
    ("Cade Smith",          694696),
    ("Kellum Clark",        690969),
    # 2024
    ("Jurrangelo Cijntje",  701388),
    ("Khal Stephen",        701590),
    ("Nate Dohm",           702296),
    ("Dakota Jordan",       702607),
    ("Brooks Auger",        824624),
    ("Colby Holcombe",      802418),
    ("Tyson Hardin",        824620),
    ("Connor Hujsak",       824615),
    ("Tyler Davis",         824623),
    ("David Mershon",       702574),
    ("Cam Schuelke",        807575),
    # 2025
    ("Pico Kohn",           695560),
    ("Evan Siary",          804905),
    ("Karson Ligon",        695704),
    ("Hunter Hines",        702309),
    ("Luke Dotson",         806060),
    ("Nate Williams",       802699),
    ("Jacob Pruitt",        809131),
]

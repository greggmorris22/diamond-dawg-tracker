"""
Mississippi State University alumni drafted into professional baseball
from 2013 through 2025, filtered to players with confirmed activity in
2023 or later (plus all 2025 draft picks who may begin playing in 2026).

Players confirmed retired (no stats since 2022) have been removed to
reduce API calls at load time. If a player returns to active play, add
them back here with their MLB Stats API player ID.

Source: MLB Stats API draft endpoint, school = Mississippi State University.
Last updated: 2026-04-04.
"""

MSU_PLAYERS = [
    # 2013
    ("Hunter Renfroe",      592669),  # 2025 MLB
    ("Adam Frazier",        624428),  # 2025 MLB
    ("Kendall Graveman",    608665),  # 2025 MLB
    # Chad Girodo, Evan Mitchell, Daryl Norris, Luis Pollorena — no stats since 2022
    # 2014
    ("Jonathan Holder",     656547),  # 2023 AAA
    ("Brandon Woodruff",    605540),  # 2025 MLB
    # Jacob Lindgren, Brett Pirtle — no stats since 2022
    # 2015 — no MSU picks found in API
    # 2016
    ("Dakota Hudson",       641712),  # 2025 AAA
    ("Jacob Robson",        615699),  # 2024 WIN
    ("Zac Houston",         667677),  # 2024 AAA
    ("Nathaniel Lowe",      663993),  # 2025 MLB
    ("Gavin Collins",       641468),  # 2025 AAA
    ("Brent Rooker",        667670),  # 2025 MLB
    # Reid Humphreys, Daniel Brown, Vance Tatum, Austin Sexton, Jack Kruger — no stats since 2022
    # 2017
    ("Jake Mangum",         663968),  # 2025 MLB
    # Ryan Gridley — no stats since 2022
    # 2018
    ("Konnor Pilkington",   663455),  # 2025 MLB
    ("J.P. France",         641585),  # 2025 MLB
    ("Hunter Stovall",      667663),  # 2025 AAA
    ("Ethan Small",         663629),  # 2025 AAA
    ("Zach Neff",           679820),  # 2023 ROK
    # Jacob Billingsley — no stats since 2022
    # 2019
    ("Colby White",         686831),  # 2025 AA
    ("Keegan James",        667669),  # 2023 A+
    ("Peyton Plumlee",      690183),  # 2023 AA
    ("Tanner Allen",        669327),  # 2024 AA
    # Trysten Barlow, Dustin Skelton, Jared Liebelt, Cole Gordon — no stats since 2022
    # 2020
    ("Justin Foscue",       679822),  # 2025 MLB
    ("Jordan Westburg",     676059),  # 2025 MLB
    ("J.T. Ginn",           669372),  # 2025 MLB
    # 2021
    ("Will Bednar",         687218),  # 2025 AAA
    ("Eric Cerantola",      672021),  # 2025 AAA
    ("Christian MacLeod",   681306),  # 2025 AAA
    ("Rowdey Jordan",       679821),  # 2025 AAA
    # 2022
    ("Landon Sims",         683085),  # 2025 AA
    ("Logan Tanner",        683091),  # 2025 A+
    ("Preston Johnson",     699980),  # 2025 AAA
    ("K.C. Hunt",           687268),  # 2025 AA
    ("Jackson Fristoe",     690977),  # 2025 A
    ("Kamren James",        687553),  # 2025 AA
    # 2023
    ("Colton Ledbetter",    807742),  # 2025 AA
    ("Cade Smith",          694696),  # 2025 A+
    ("Kellum Clark",        690969),  # 2024 A+
    # 2024
    ("Jurrangelo Cijntje",  701388),  # 2025 AA
    ("Khal Stephen",        701590),  # 2025 AA
    ("Nate Dohm",           702296),  # 2025 A+
    ("Dakota Jordan",       702607),  # 2025 A
    ("Brooks Auger",        824624),  # 2025 A+
    ("Colby Holcombe",      802418),  # 2025 A+
    ("Tyson Hardin",        824620),  # 2025 AA
    ("Connor Hujsak",       824615),  # 2025 A
    ("Tyler Davis",         824623),  # 2025 A+
    ("David Mershon",       702574),  # 2025 AAA
    ("Cam Schuelke",        807575),  # 2025 A
    # 2025 — newly drafted, may begin playing in 2026
    ("Pico Kohn",           695560),
    ("Evan Siary",          804905),  # 2025 A
    ("Karson Ligon",        695704),
    ("Hunter Hines",        702309),
    ("Luke Dotson",         806060),
    ("Nate Williams",       802699),
    ("Jacob Pruitt",        809131),
]

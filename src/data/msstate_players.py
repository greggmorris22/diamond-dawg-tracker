"""
Static list of Mississippi State University alumni who were drafted into
professional baseball (2018-2025). Each entry is a (display_name, mlb_id)
tuple. Because IDs are known up front, the app bypasses name search entirely
— no wrong-player mismatches possible.

Players who have since reached MLB or retired will return no MiLB stats
and are silently skipped by the app.

Source: MLB Stats API draft endpoint, school = Mississippi State University.
Last updated: 2026-04-03.
"""

MSU_PLAYERS = [
    # 2018
    ("Konnor Pilkington",   663455),
    ("J.P. France",         641585),
    ("Hunter Stovall",      667663),
    ("Ethan Small",         663629),
    ("Zach Neff",           679820),
    ("Jake Mangum",         663968),
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

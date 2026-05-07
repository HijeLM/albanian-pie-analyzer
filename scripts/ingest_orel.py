#!/usr/bin/env python3
"""
Data ingestion script: parse Orel 1998 Albanian Etymological Dictionary PDF
and insert entries into PostgreSQL.

Usage:
    python ingest_orel.py --pdf /path/to/orel1998.pdf
    python ingest_orel.py --seed   # Insert built-in sample dataset only
"""

import argparse
import re
import sys
import os
import unicodedata
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db
from app.models import Word, Source, Entry, Cognate, Evolution


# ---------------------------------------------------------------------------
# Built-in sample dataset (200 Albanian words with PIE roots, cognates, etc.)
# ---------------------------------------------------------------------------
SAMPLE_DATA = [
    {
        "word": "atë", "meaning": "father", "pos": "noun",
        "root": "*ph₂tḗr", "confidence": 0.95, "notes": "Core PIE kinship term",
        "cognates": [
            ("Latin", "pater", "father"), ("Greek", "πατήρ", "father"),
            ("Sanskrit", "pitā", "father"), ("English", "father", "father"),
            ("German", "Vater", "father"),
        ],
        "evolutions": [("PIE", "*ph₂tḗr"), ("Proto-Albanian", "*pater"), ("Albanian", "atë")],
    },
    {
        "word": "nënë", "meaning": "mother", "pos": "noun",
        "root": "*méh₂tēr", "confidence": 0.90,
        "cognates": [
            ("Latin", "mater", "mother"), ("Greek", "μήτηρ", "mother"),
            ("Sanskrit", "mātā", "mother"), ("English", "mother", "mother"),
        ],
        "evolutions": [("PIE", "*méh₂tēr"), ("Proto-Albanian", "*māter"), ("Albanian", "nënë")],
    },
    {
        "word": "bir", "meaning": "son", "pos": "noun",
        "root": "*bʰer-", "confidence": 0.80, "notes": "Related to 'bear' (to carry)",
        "cognates": [
            ("Sanskrit", "bhr̥tá", "carried"), ("Greek", "φέρω", "to carry"),
        ],
        "evolutions": [("PIE", "*bʰer-"), ("Proto-Albanian", "*ber-"), ("Albanian", "bir")],
    },
    {
        "word": "motër", "meaning": "sister", "pos": "noun",
        "root": "*méh₂tēr", "confidence": 0.75,
        "cognates": [
            ("Latin", "māter", "mother/matrix"), ("Slavic", "*mati", "mother"),
        ],
        "evolutions": [("PIE", "*méh₂tēr"), ("Albanian", "motër")],
    },
    {
        "word": "vëlla", "meaning": "brother", "pos": "noun",
        "root": "*bʰréh₂tēr", "confidence": 0.90,
        "cognates": [
            ("Latin", "frater", "brother"), ("Sanskrit", "bhrātā", "brother"),
            ("English", "brother", "brother"), ("German", "Bruder", "brother"),
        ],
        "evolutions": [("PIE", "*bʰréh₂tēr"), ("Proto-Albanian", "*brāter"), ("Albanian", "vëlla")],
    },
    {
        "word": "djep", "meaning": "cradle", "pos": "noun",
        "root": "*dʰeubʰ-", "confidence": 0.65,
        "cognates": [("Greek", "θύπτω", "to beat"), ("Latin", "foveo", "to warm")],
        "evolutions": [("PIE", "*dʰeubʰ-"), ("Albanian", "djep")],
    },
    {
        "word": "ujk", "meaning": "wolf", "pos": "noun",
        "root": "*wĺ̥kʷos", "confidence": 0.95,
        "cognates": [
            ("Latin", "lupus", "wolf"), ("Greek", "λύκος", "wolf"),
            ("Sanskrit", "vṛka", "wolf"), ("Russian", "волк", "wolf"),
            ("English", "wolf", "wolf"),
        ],
        "evolutions": [("PIE", "*wĺ̥kʷos"), ("Proto-Albanian", "*ulkos"), ("Albanian", "ujk")],
    },
    {
        "word": "ari", "meaning": "bear", "pos": "noun",
        "root": "*h₂ŕ̥tḱos", "confidence": 0.90,
        "cognates": [
            ("Greek", "ἄρκτος", "bear"), ("Latin", "ursus", "bear"),
            ("Welsh", "arth", "bear"), ("Sanskrit", "ṛkṣa", "bear"),
        ],
        "evolutions": [("PIE", "*h₂ŕ̥tḱos"), ("Proto-Albanian", "*artos"), ("Albanian", "ari")],
    },
    {
        "word": "dem", "meaning": "bull, ox", "pos": "noun",
        "root": "*dʰewbʰ-", "confidence": 0.72,
        "cognates": [("Greek", "θεμός", "pile"), ("Latvian", "dumps", "deep")],
        "evolutions": [("PIE", "*dʰewbʰ-"), ("Albanian", "dem")],
    },
    {
        "word": "dele", "meaning": "sheep", "pos": "noun",
        "root": "*dʰelH-", "confidence": 0.68,
        "cognates": [("Latin", "fēlāre", "to suckle"), ("Greek", "θηλή", "nipple")],
        "evolutions": [("PIE", "*dʰelH-"), ("Albanian", "dele")],
    },
    {
        "word": "lopë", "meaning": "cow", "pos": "noun",
        "root": "*h₁loup-", "confidence": 0.60,
        "cognates": [("Slavic", "*lopa", "large flat thing"), ("Lithuanian", "lopa", "paw")],
        "evolutions": [("PIE", "*h₁loup-"), ("Albanian", "lopë")],
    },
    {
        "word": "gomar", "meaning": "donkey", "pos": "noun",
        "root": "*gʷou-", "confidence": 0.45, "notes": "Possibly borrowed from Greek",
        "cognates": [("Greek", "γόμαρος", "donkey")],
        "evolutions": [("Albanian", "gomar")],
    },
    {
        "word": "peshk", "meaning": "fish", "pos": "noun",
        "root": "*peisk-", "confidence": 0.88,
        "cognates": [
            ("Latin", "piscis", "fish"), ("English", "fish", "fish"),
            ("German", "Fisch", "fish"), ("Gothic", "fisks", "fish"),
        ],
        "evolutions": [("PIE", "*peisk-"), ("Proto-Albanian", "*pisk-"), ("Albanian", "peshk")],
    },
    {
        "word": "zog", "meaning": "bird, chick", "pos": "noun",
        "root": "*gʰwesdʰ-", "confidence": 0.55,
        "cognates": [("Greek", "ζωός", "living"), ("Latin", "fastus", "disdain")],
        "evolutions": [("PIE", "*gʰwesdʰ-"), ("Albanian", "zog")],
    },
    {
        "word": "pemë", "meaning": "tree, fruit", "pos": "noun",
        "root": "*pomo-", "confidence": 0.70,
        "cognates": [("Latin", "pomum", "fruit"), ("French", "pomme", "apple")],
        "evolutions": [("PIE", "*pomo-"), ("Albanian", "pemë")],
    },
    {
        "word": "dru", "meaning": "wood, tree", "pos": "noun",
        "root": "*dóru", "confidence": 0.95,
        "cognates": [
            ("Greek", "δόρυ", "spear, wood"), ("Sanskrit", "dāru", "wood"),
            ("English", "tree", "tree"), ("Russian", "дерево", "tree"),
        ],
        "evolutions": [("PIE", "*dóru"), ("Proto-Albanian", "*deru"), ("Albanian", "dru")],
    },
    {
        "word": "gur", "meaning": "stone", "pos": "noun",
        "root": "*gʷr̥H-", "confidence": 0.82,
        "cognates": [
            ("Greek", "βαρύς", "heavy"), ("Sanskrit", "guru", "heavy"),
            ("Latin", "gravis", "heavy"),
        ],
        "evolutions": [("PIE", "*gʷr̥H-"), ("Proto-Albanian", "*gur-"), ("Albanian", "gur")],
    },
    {
        "word": "ujë", "meaning": "water", "pos": "noun",
        "root": "*wed-", "confidence": 0.90,
        "cognates": [
            ("English", "water", "water"), ("German", "Wasser", "water"),
            ("Russian", "вода", "water"), ("Greek", "ὕδωρ", "water"),
        ],
        "evolutions": [("PIE", "*wed-"), ("Proto-Albanian", "*uda"), ("Albanian", "ujë")],
    },
    {
        "word": "zjarr", "meaning": "fire", "pos": "noun",
        "root": "*ǵʰwer-", "confidence": 0.78,
        "cognates": [
            ("Sanskrit", "gharmá", "heat"), ("Greek", "θερμός", "warm"),
            ("Latin", "formus", "warm"),
        ],
        "evolutions": [("PIE", "*ǵʰwer-"), ("Proto-Albanian", "*dzer-"), ("Albanian", "zjarr")],
    },
    {
        "word": "diell", "meaning": "sun", "pos": "noun",
        "root": "*dyew-", "confidence": 0.85,
        "cognates": [
            ("Latin", "dies", "day"), ("Sanskrit", "dyaus", "sky/heaven"),
            ("Greek", "Ζεύς", "Zeus"), ("English", "day", "day"),
        ],
        "evolutions": [("PIE", "*dyew-"), ("Proto-Albanian", "*diwel"), ("Albanian", "diell")],
    },
    {
        "word": "hënë", "meaning": "moon, Monday", "pos": "noun",
        "root": "*mḗh₁n̥s", "confidence": 0.88,
        "cognates": [
            ("English", "moon", "moon"), ("German", "Mond", "moon"),
            ("Latin", "mensis", "month"), ("Greek", "μήνη", "moon"),
        ],
        "evolutions": [("PIE", "*mḗh₁n̥s"), ("Proto-Albanian", "*mēn-"), ("Albanian", "hënë")],
    },
    {
        "word": "natë", "meaning": "night", "pos": "noun",
        "root": "*nókʷts", "confidence": 0.92,
        "cognates": [
            ("Latin", "nox", "night"), ("Greek", "νύξ", "night"),
            ("English", "night", "night"), ("Sanskrit", "naktam", "at night"),
        ],
        "evolutions": [("PIE", "*nókʷts"), ("Proto-Albanian", "*nakts"), ("Albanian", "natë")],
    },
    {
        "word": "ditë", "meaning": "day", "pos": "noun",
        "root": "*dyew-", "confidence": 0.83,
        "cognates": [
            ("Latin", "dies", "day"), ("Sanskrit", "divas", "day"),
            ("Greek", "Διός", "of Zeus"),
        ],
        "evolutions": [("PIE", "*dyew-"), ("Proto-Albanian", "*dita"), ("Albanian", "ditë")],
    },
    {
        "word": "verë", "meaning": "summer, wine", "pos": "noun",
        "root": "*wes-r̥", "confidence": 0.75,
        "cognates": [
            ("Latin", "ver", "spring"), ("Greek", "ἔαρ", "spring"),
            ("Sanskrit", "vasantá", "spring"),
        ],
        "evolutions": [("PIE", "*wes-r̥"), ("Proto-Albanian", "*wer-"), ("Albanian", "verë")],
    },
    {
        "word": "dimër", "meaning": "winter", "pos": "noun",
        "root": "*ǵʰéyōm", "confidence": 0.80,
        "cognates": [
            ("Greek", "χειμών", "winter"), ("Latin", "hiems", "winter"),
            ("Sanskrit", "hima", "snow, winter"),
        ],
        "evolutions": [("PIE", "*ǵʰéyōm"), ("Proto-Albanian", "*džim-"), ("Albanian", "dimër")],
    },
    {
        "word": "mal", "meaning": "mountain", "pos": "noun",
        "root": "*molH-", "confidence": 0.65,
        "cognates": [("Slavic", "*molu", "sandbank"), ("Latin", "moles", "mass")],
        "evolutions": [("PIE", "*molH-"), ("Albanian", "mal")],
    },
    {
        "word": "lumë", "meaning": "river", "pos": "noun",
        "root": "*plew-", "confidence": 0.70,
        "cognates": [
            ("Latin", "pluo", "to rain"), ("Greek", "πλέω", "to sail"),
            ("English", "flow", "to flow"),
        ],
        "evolutions": [("PIE", "*plew-"), ("Proto-Albanian", "*lum-"), ("Albanian", "lumë")],
    },
    {
        "word": "det", "meaning": "sea", "pos": "noun",
        "root": "*dʰewbʰ-", "confidence": 0.62,
        "cognates": [("Lithuanian", "dubùs", "deep"), ("English", "deep", "deep")],
        "evolutions": [("PIE", "*dʰewbʰ-"), ("Albanian", "det")],
    },
    {
        "word": "tokë", "meaning": "earth, land, soil", "pos": "noun",
        "root": "*dʰeǵʰom", "confidence": 0.85,
        "cognates": [
            ("Latin", "humus", "earth"), ("Greek", "χθών", "earth"),
            ("Sanskrit", "kṣam", "earth"),
        ],
        "evolutions": [("PIE", "*dʰeǵʰom"), ("Proto-Albanian", "*toga"), ("Albanian", "tokë")],
    },
    {
        "word": "re", "meaning": "cloud", "pos": "noun",
        "root": "*h₃nebʰ-", "confidence": 0.73,
        "cognates": [
            ("Latin", "nebula", "mist"), ("Greek", "νέφος", "cloud"),
            ("German", "Nebel", "fog"), ("Sanskrit", "nábhas", "sky"),
        ],
        "evolutions": [("PIE", "*h₃nebʰ-"), ("Proto-Albanian", "*neb-"), ("Albanian", "re")],
    },
    {
        "word": "borë", "meaning": "snow", "pos": "noun",
        "root": "*gʷʰorH-", "confidence": 0.68,
        "cognates": [("Slavic", "*bura", "storm"), ("Lithuanian", "burà", "sail")],
        "evolutions": [("PIE", "*gʷʰorH-"), ("Albanian", "borë")],
    },
    {
        "word": "erë", "meaning": "wind, smell", "pos": "noun",
        "root": "*h₂ewH-", "confidence": 0.77,
        "cognates": [
            ("Greek", "ἄημι", "to blow"), ("Latin", "aura", "breeze"),
            ("English", "air", "air"),
        ],
        "evolutions": [("PIE", "*h₂ewH-"), ("Proto-Albanian", "*aura"), ("Albanian", "erë")],
    },
    {
        "word": "shpirt", "meaning": "spirit, soul", "pos": "noun",
        "root": "*spiro-", "confidence": 0.55, "notes": "Possibly Latin loan",
        "cognates": [("Latin", "spiritus", "spirit"), ("English", "spirit", "spirit")],
        "evolutions": [("Latin", "spiritus"), ("Albanian", "shpirt")],
    },
    {
        "word": "zemër", "meaning": "heart", "pos": "noun",
        "root": "*ǵʰr̥dʰ-", "confidence": 0.78,
        "cognates": [
            ("Latin", "cor", "heart"), ("Greek", "καρδία", "heart"),
            ("English", "heart", "heart"),
        ],
        "evolutions": [("PIE", "*ǵʰr̥dʰ-"), ("Proto-Albanian", "*dzer-"), ("Albanian", "zemër")],
    },
    {
        "word": "gojë", "meaning": "mouth", "pos": "noun",
        "root": "*gʷel-", "confidence": 0.72,
        "cognates": [("Latin", "gula", "throat"), ("English", "gullet", "throat")],
        "evolutions": [("PIE", "*gʷel-"), ("Proto-Albanian", "*gola"), ("Albanian", "gojë")],
    },
    {
        "word": "dorë", "meaning": "hand", "pos": "noun",
        "root": "*dʰers-", "confidence": 0.65,
        "cognates": [("Sanskrit", "dharṣati", "to be bold"), ("Gothic", "gadars", "to dare")],
        "evolutions": [("PIE", "*dʰers-"), ("Albanian", "dorë")],
    },
    {
        "word": "këmbë", "meaning": "leg, foot", "pos": "noun",
        "root": "*gombʰo-", "confidence": 0.70,
        "cognates": [("Greek", "γόμφος", "nail, bolt"), ("Sanskrit", "gambhá", "tooth")],
        "evolutions": [("PIE", "*gombʰo-"), ("Proto-Albanian", "*kamba"), ("Albanian", "këmbë")],
    },
    {
        "word": "sy", "meaning": "eye", "pos": "noun",
        "root": "*h₃okʷ-", "confidence": 0.93,
        "cognates": [
            ("Latin", "oculus", "eye"), ("Greek", "ὄψ", "eye"),
            ("English", "eye", "eye"), ("Sanskrit", "akṣi", "eye"),
        ],
        "evolutions": [("PIE", "*h₃okʷ-"), ("Proto-Albanian", "*ok-"), ("Albanian", "sy")],
    },
    {
        "word": "vesh", "meaning": "ear", "pos": "noun",
        "root": "*h₂ous-", "confidence": 0.88,
        "cognates": [
            ("Latin", "auris", "ear"), ("Greek", "οὖς", "ear"),
            ("English", "ear", "ear"), ("Sanskrit", "ā́vi", "ear"),
        ],
        "evolutions": [("PIE", "*h₂ous-"), ("Proto-Albanian", "*aus-"), ("Albanian", "vesh")],
    },
    {
        "word": "dhëmb", "meaning": "tooth", "pos": "noun",
        "root": "*h₁dónt-", "confidence": 0.91,
        "cognates": [
            ("Latin", "dens", "tooth"), ("Greek", "ὀδούς", "tooth"),
            ("English", "tooth", "tooth"), ("Sanskrit", "danta", "tooth"),
        ],
        "evolutions": [("PIE", "*h₁dónt-"), ("Proto-Albanian", "*dant-"), ("Albanian", "dhëmb")],
    },
    {
        "word": "gjuhë", "meaning": "tongue, language", "pos": "noun",
        "root": "*dʰn̥ǵʰwéh₂s", "confidence": 0.87,
        "cognates": [
            ("Latin", "lingua", "tongue"), ("English", "tongue", "tongue"),
            ("Sanskrit", "jihvā", "tongue"), ("Old Irish", "tengae", "tongue"),
        ],
        "evolutions": [("PIE", "*dʰn̥ǵʰwéh₂s"), ("Proto-Albanian", "*glug-"), ("Albanian", "gjuhë")],
    },
    {
        "word": "hundë", "meaning": "nose", "pos": "noun",
        "root": "*h₂ens-", "confidence": 0.80,
        "cognates": [
            ("Latin", "nasus", "nose"), ("English", "nose", "nose"),
            ("Sanskrit", "nāsā", "nose"), ("German", "Nase", "nose"),
        ],
        "evolutions": [("PIE", "*h₂ens-"), ("Proto-Albanian", "*nas-"), ("Albanian", "hundë")],
    },
    {
        "word": "qime", "meaning": "hair, fur", "pos": "noun",
        "root": "*kes-", "confidence": 0.60,
        "cognates": [("Latin", "caesaries", "hair"), ("Greek", "κόμη", "hair")],
        "evolutions": [("PIE", "*kes-"), ("Albanian", "qime")],
    },
    {
        "word": "gjak", "meaning": "blood", "pos": "noun",
        "root": "*yekʷ-", "confidence": 0.82,
        "cognates": [
            ("Greek", "ἧπαρ", "liver"), ("Latin", "iecur", "liver"),
            ("Sanskrit", "yákṛt", "liver"),
        ],
        "evolutions": [("PIE", "*yekʷ-"), ("Proto-Albanian", "*dzak-"), ("Albanian", "gjak")],
    },
    {
        "word": "kockë", "meaning": "bone", "pos": "noun",
        "root": "*kost-", "confidence": 0.75,
        "cognates": [
            ("Latin", "costa", "rib"), ("Russian", "кость", "bone"),
            ("Polish", "kość", "bone"),
        ],
        "evolutions": [("PIE", "*kost-"), ("Albanian", "kockë")],
    },
    {
        "word": "lëkurë", "meaning": "skin, leather", "pos": "noun",
        "root": "*lep-", "confidence": 0.67,
        "cognates": [("Greek", "λέπω", "to peel"), ("Lithuanian", "lupti", "to peel")],
        "evolutions": [("PIE", "*lep-"), ("Albanian", "lëkurë")],
    },
    {
        "word": "nam", "meaning": "name, fame", "pos": "noun",
        "root": "*h₁nómn̥", "confidence": 0.93,
        "cognates": [
            ("Latin", "nomen", "name"), ("Greek", "ὄνομα", "name"),
            ("English", "name", "name"), ("Sanskrit", "nāman", "name"),
        ],
        "evolutions": [("PIE", "*h₁nómn̥"), ("Proto-Albanian", "*naman"), ("Albanian", "nam")],
    },
    {
        "word": "numër", "meaning": "number", "pos": "noun",
        "root": "*nem-", "confidence": 0.70, "notes": "Possibly via Latin numerus",
        "cognates": [("Latin", "numerus", "number"), ("Greek", "νέμω", "to distribute")],
        "evolutions": [("PIE", "*nem-"), ("Latin", "numerus"), ("Albanian", "numër")],
    },
    {
        "word": "mjaltë", "meaning": "honey", "pos": "noun",
        "root": "*melid", "confidence": 0.88,
        "cognates": [
            ("Greek", "μέλι", "honey"), ("Latin", "mel", "honey"),
            ("English", "mead", "honey drink"), ("Welsh", "mêl", "honey"),
        ],
        "evolutions": [("PIE", "*melid"), ("Proto-Albanian", "*melita"), ("Albanian", "mjaltë")],
    },
    {
        "word": "kripë", "meaning": "salt", "pos": "noun",
        "root": "*sal-", "confidence": 0.80,
        "cognates": [
            ("Latin", "sal", "salt"), ("Greek", "ἅλς", "salt"),
            ("English", "salt", "salt"), ("Russian", "соль", "salt"),
        ],
        "evolutions": [("PIE", "*sal-"), ("Proto-Albanian", "*kripa"), ("Albanian", "kripë")],
    },
    {
        "word": "bukë", "meaning": "bread, food", "pos": "noun",
        "root": "*bʰóHgos", "confidence": 0.72,
        "cognates": [("English", "bake", "to bake"), ("German", "backen", "to bake")],
        "evolutions": [("PIE", "*bʰóHgos"), ("Proto-Albanian", "*buka"), ("Albanian", "bukë")],
    },
    {
        "word": "vaj", "meaning": "oil", "pos": "noun",
        "root": "*h₂eyg-", "confidence": 0.55, "notes": "May be from Latin oleum",
        "cognates": [("Latin", "oleum", "oil"), ("Greek", "ἔλαιον", "olive oil")],
        "evolutions": [("Latin/Greek", "oleum"), ("Albanian", "vaj")],
    },
    {
        "word": "verë", "meaning": "wine (also summer)", "pos": "noun",
        "root": "*wóyh₁nom", "confidence": 0.78,
        "cognates": [
            ("Latin", "vinum", "wine"), ("Greek", "οἶνος", "wine"),
            ("English", "wine", "wine"),
        ],
        "evolutions": [("PIE", "*wóyh₁nom"), ("Proto-Albanian", "*wina"), ("Albanian", "verë")],
    },
    {
        "word": "qumësht", "meaning": "milk", "pos": "noun",
        "root": "*gʷen-", "confidence": 0.60,
        "cognates": [("Greek", "γάλα", "milk"), ("Latin", "lac", "milk")],
        "evolutions": [("PIE", "*gʷen-"), ("Albanian", "qumësht")],
    },
    {
        "word": "fëmijë", "meaning": "child", "pos": "noun",
        "root": "*dʰeh₁-", "confidence": 0.63,
        "cognates": [("Latin", "filius", "son"), ("Sanskrit", "dhīta", "daughter")],
        "evolutions": [("PIE", "*dʰeh₁-"), ("Albanian", "fëmijë")],
    },
    {
        "word": "plak", "meaning": "old man, elder", "pos": "noun",
        "root": "*pḷth₂-", "confidence": 0.68,
        "cognates": [("Greek", "πλατύς", "broad, flat"), ("Sanskrit", "pṛthu", "broad")],
        "evolutions": [("PIE", "*pḷth₂-"), ("Albanian", "plak")],
    },
    {
        "word": "grua", "meaning": "woman, wife", "pos": "noun",
        "root": "*gʷen-", "confidence": 0.88,
        "cognates": [
            ("Greek", "γυνή", "woman"), ("English", "queen", "queen"),
            ("Gothic", "qino", "woman"), ("Sanskrit", "jáni", "woman"),
        ],
        "evolutions": [("PIE", "*gʷen-"), ("Proto-Albanian", "*guna"), ("Albanian", "grua")],
    },
    {
        "word": "burrë", "meaning": "man, husband", "pos": "noun",
        "root": "*gʷr̥H-", "confidence": 0.70,
        "cognates": [("Sanskrit", "guru", "heavy, venerable"), ("Greek", "βαρύς", "heavy")],
        "evolutions": [("PIE", "*gʷr̥H-"), ("Proto-Albanian", "*burra"), ("Albanian", "burrë")],
    },
    {
        "word": "mbret", "meaning": "king", "pos": "noun",
        "root": "*h₃reǵ-", "confidence": 0.85,
        "cognates": [
            ("Latin", "rex", "king"), ("Sanskrit", "rājan", "king"),
            ("Celtic", "*rīx", "king"), ("Old Irish", "rí", "king"),
        ],
        "evolutions": [("PIE", "*h₃reǵ-"), ("Latin", "imperator"), ("Albanian", "mbret")],
    },
    {
        "word": "zot", "meaning": "lord, god, master", "pos": "noun",
        "root": "*gʰosti-", "confidence": 0.65,
        "cognates": [("Latin", "hostis", "enemy, stranger"), ("Gothic", "gasts", "guest")],
        "evolutions": [("PIE", "*gʰosti-"), ("Proto-Albanian", "*dzot"), ("Albanian", "zot")],
    },
    {
        "word": "shtëpi", "meaning": "house, home", "pos": "noun",
        "root": "*stā-", "confidence": 0.72,
        "cognates": [("Latin", "stabilis", "stable"), ("English", "stand", "to stand")],
        "evolutions": [("PIE", "*stā-"), ("Latin", "stabulum"), ("Albanian", "shtëpi")],
    },
    {
        "word": "derë", "meaning": "door, gate", "pos": "noun",
        "root": "*dʰwer-", "confidence": 0.90,
        "cognates": [
            ("English", "door", "door"), ("Greek", "θύρα", "door"),
            ("Latin", "foris", "door"), ("Sanskrit", "dvār", "door"),
        ],
        "evolutions": [("PIE", "*dʰwer-"), ("Proto-Albanian", "*dver-"), ("Albanian", "derë")],
    },
    {
        "word": "rrugë", "meaning": "road, way, street", "pos": "noun",
        "root": "*h₃reǵ-", "confidence": 0.62, "notes": "Possibly from Latin ruga",
        "cognates": [("Latin", "ruga", "wrinkle, road"), ("French", "rue", "street")],
        "evolutions": [("Latin", "ruga"), ("Albanian", "rrugë")],
    },
    {
        "word": "urë", "meaning": "bridge", "pos": "noun",
        "root": "*plh₂-", "confidence": 0.58,
        "cognates": [("Latin", "pons", "bridge"), ("Greek", "πόρος", "passage")],
        "evolutions": [("PIE", "*plh₂-"), ("Albanian", "urë")],
    },
    {
        "word": "qiell", "meaning": "sky, heaven", "pos": "noun",
        "root": "*kel-", "confidence": 0.73,
        "cognates": [("Latin", "caelum", "sky"), ("Welsh", "caer", "fort")],
        "evolutions": [("PIE", "*kel-"), ("Latin", "caelum"), ("Albanian", "qiell")],
    },
    {
        "word": "dhe", "meaning": "and, earth", "pos": "conjunction",
        "root": "*dʰeǵʰom", "confidence": 0.80,
        "cognates": [("Greek", "χθών", "earth"), ("Latin", "humus", "earth")],
        "evolutions": [("PIE", "*dʰeǵʰom"), ("Albanian", "dhe")],
    },
    {
        "word": "jam", "meaning": "I am", "pos": "verb",
        "root": "*h₁es-", "confidence": 0.95,
        "cognates": [
            ("Latin", "sum", "I am"), ("Greek", "εἰμί", "I am"),
            ("Sanskrit", "asmi", "I am"), ("English", "am", "am"),
        ],
        "evolutions": [("PIE", "*h₁es-"), ("Proto-Albanian", "*esmi"), ("Albanian", "jam")],
    },
    {
        "word": "kam", "meaning": "I have", "pos": "verb",
        "root": "*kap-", "confidence": 0.75,
        "cognates": [("Latin", "capio", "to take"), ("Greek", "κάπτω", "to grab")],
        "evolutions": [("PIE", "*kap-"), ("Proto-Albanian", "*kap-"), ("Albanian", "kam")],
    },
    {
        "word": "bie", "meaning": "to fall, to bring", "pos": "verb",
        "root": "*bʰer-", "confidence": 0.82,
        "cognates": [
            ("Latin", "fero", "to carry"), ("Greek", "φέρω", "to carry"),
            ("Sanskrit", "bhárati", "carries"), ("English", "bear", "to carry"),
        ],
        "evolutions": [("PIE", "*bʰer-"), ("Proto-Albanian", "*ber-"), ("Albanian", "bie")],
    },
    {
        "word": "vdes", "meaning": "to die", "pos": "verb",
        "root": "*dʰewbʰ-", "confidence": 0.65,
        "cognates": [("Greek", "θάνατος", "death"), ("Sanskrit", "dhūpāyati", "to fumigate")],
        "evolutions": [("PIE", "*dʰewbʰ-"), ("Albanian", "vdes")],
    },
    {
        "word": "ha", "meaning": "to eat", "pos": "verb",
        "root": "*h₁ed-", "confidence": 0.88,
        "cognates": [
            ("Latin", "edo", "to eat"), ("Greek", "ἔδω", "to eat"),
            ("English", "eat", "to eat"), ("Sanskrit", "admi", "I eat"),
        ],
        "evolutions": [("PIE", "*h₁ed-"), ("Proto-Albanian", "*ad-"), ("Albanian", "ha")],
    },
    {
        "word": "pi", "meaning": "to drink", "pos": "verb",
        "root": "*peh₃-", "confidence": 0.90,
        "cognates": [
            ("Latin", "bibo", "to drink"), ("Greek", "πίνω", "to drink"),
            ("Sanskrit", "pibati", "drinks"), ("Russian", "пить", "to drink"),
        ],
        "evolutions": [("PIE", "*peh₃-"), ("Proto-Albanian", "*pi-"), ("Albanian", "pi")],
    },
    {
        "word": "fle", "meaning": "to sleep", "pos": "verb",
        "root": "*slep-", "confidence": 0.78,
        "cognates": [("English", "sleep", "to sleep"), ("German", "schlafen", "to sleep")],
        "evolutions": [("PIE", "*slep-"), ("Proto-Albanian", "*flep-"), ("Albanian", "fle")],
    },
    {
        "word": "shoh", "meaning": "to see", "pos": "verb",
        "root": "*sekʷ-", "confidence": 0.73,
        "cognates": [
            ("Latin", "sequor", "to follow"), ("Greek", "ἕπομαι", "to follow"),
            ("Sanskrit", "sácate", "follows"),
        ],
        "evolutions": [("PIE", "*sekʷ-"), ("Albanian", "shoh")],
    },
    {
        "word": "dëgjoj", "meaning": "to hear, to listen", "pos": "verb",
        "root": "*dʰwer-", "confidence": 0.62,
        "cognates": [("Latin", "audio", "to hear"), ("Greek", "ἀκούω", "to hear")],
        "evolutions": [("PIE", "*dʰwer-"), ("Albanian", "dëgjoj")],
    },
    {
        "word": "them", "meaning": "to say, to tell", "pos": "verb",
        "root": "*dʰeh₁-", "confidence": 0.75,
        "cognates": [("Greek", "θέσις", "position"), ("Sanskrit", "dhārayati", "holds")],
        "evolutions": [("PIE", "*dʰeh₁-"), ("Albanian", "them")],
    },
    {
        "word": "jap", "meaning": "to give", "pos": "verb",
        "root": "*gʷʰen-", "confidence": 0.68,
        "cognates": [("Greek", "βαίνω", "to go"), ("Sanskrit", "gam", "to go")],
        "evolutions": [("PIE", "*gʷʰen-"), ("Albanian", "jap")],
    },
    {
        "word": "marr", "meaning": "to take, to get", "pos": "verb",
        "root": "*mer-", "confidence": 0.70,
        "cognates": [("Latin", "mereo", "to earn"), ("Greek", "μείρομαι", "to receive")],
        "evolutions": [("PIE", "*mer-"), ("Albanian", "marr")],
    },
    {
        "word": "vij", "meaning": "to come", "pos": "verb",
        "root": "*gʷem-", "confidence": 0.83,
        "cognates": [
            ("Latin", "venio", "to come"), ("Sanskrit", "gam", "to go"),
            ("English", "come", "to come"), ("Greek", "βαίνω", "to walk"),
        ],
        "evolutions": [("PIE", "*gʷem-"), ("Proto-Albanian", "*wen-"), ("Albanian", "vij")],
    },
    {
        "word": "shkoj", "meaning": "to go", "pos": "verb",
        "root": "*skewd-", "confidence": 0.72,
        "cognates": [("English", "shoot", "to shoot"), ("German", "schießen", "to shoot")],
        "evolutions": [("PIE", "*skewd-"), ("Albanian", "shkoj")],
    },
    {
        "word": "rri", "meaning": "to stay, to sit, to remain", "pos": "verb",
        "root": "*sed-", "confidence": 0.78,
        "cognates": [
            ("Latin", "sedeo", "to sit"), ("English", "sit", "to sit"),
            ("Greek", "ἕζομαι", "to sit"),
        ],
        "evolutions": [("PIE", "*sed-"), ("Albanian", "rri")],
    },
    {
        "word": "bëj", "meaning": "to do, to make", "pos": "verb",
        "root": "*bʰuH-", "confidence": 0.65,
        "cognates": [("English", "be", "to be"), ("Latin", "fui", "I was")],
        "evolutions": [("PIE", "*bʰuH-"), ("Albanian", "bëj")],
    },
    {
        "word": "di", "meaning": "to know", "pos": "verb",
        "root": "*weyd-", "confidence": 0.85,
        "cognates": [
            ("Latin", "video", "to see"), ("Greek", "οἶδα", "I know"),
            ("Sanskrit", "veda", "knowledge"), ("English", "wit", "to know"),
        ],
        "evolutions": [("PIE", "*weyd-"), ("Proto-Albanian", "*wid-"), ("Albanian", "di")],
    },
    {
        "word": "dua", "meaning": "to want, to love", "pos": "verb",
        "root": "*dʰewH-", "confidence": 0.70,
        "cognates": [("Greek", "θυμός", "spirit, desire"), ("Sanskrit", "dhūman", "smoke")],
        "evolutions": [("PIE", "*dʰewH-"), ("Albanian", "dua")],
    },
    {
        "word": "mund", "meaning": "to be able to, can", "pos": "verb",
        "root": "*men-", "confidence": 0.68,
        "cognates": [("Latin", "mens", "mind"), ("Greek", "μένος", "spirit, force")],
        "evolutions": [("PIE", "*men-"), ("Albanian", "mund")],
    },
    {
        "word": "ndaj", "meaning": "to divide, to separate", "pos": "verb",
        "root": "*dʰeh₁i-", "confidence": 0.65,
        "cognates": [("Greek", "δαίομαι", "to divide"), ("Sanskrit", "dayate", "divides")],
        "evolutions": [("PIE", "*dʰeh₁i-"), ("Albanian", "ndaj")],
    },
    {
        "word": "lë", "meaning": "to leave, to let", "pos": "verb",
        "root": "*leykʷ-", "confidence": 0.77,
        "cognates": [
            ("Latin", "linquo", "to leave"), ("Greek", "λείπω", "to leave"),
            ("Sanskrit", "riṇakti", "leaves"), ("English", "loan", "loan"),
        ],
        "evolutions": [("PIE", "*leykʷ-"), ("Proto-Albanian", "*lek-"), ("Albanian", "lë")],
    },
    {
        "word": "gjej", "meaning": "to find", "pos": "verb",
        "root": "*ǵʰey-", "confidence": 0.63,
        "cognates": [("Sanskrit", "jáyati", "conquers"), ("Greek", "γήθω", "rejoice")],
        "evolutions": [("PIE", "*ǵʰey-"), ("Albanian", "gjej")],
    },
    {
        "word": "hap", "meaning": "to open", "pos": "verb",
        "root": "*keh₂p-", "confidence": 0.72,
        "cognates": [("Latin", "capio", "to take"), ("Greek", "κάπτω", "to grasp")],
        "evolutions": [("PIE", "*keh₂p-"), ("Albanian", "hap")],
    },
    {
        "word": "mbyll", "meaning": "to close, to shut", "pos": "verb",
        "root": "*mel-", "confidence": 0.60,
        "cognates": [("Latin", "mollis", "soft"), ("Greek", "μαλακός", "soft")],
        "evolutions": [("PIE", "*mel-"), ("Albanian", "mbyll")],
    },
    {
        "word": "i", "meaning": "one (numeral)", "pos": "numeral",
        "root": "*óynos", "confidence": 0.90,
        "cognates": [
            ("Latin", "unus", "one"), ("Greek", "οἶνος", "one on a die"),
            ("English", "one", "one"), ("German", "ein", "one"),
        ],
        "evolutions": [("PIE", "*óynos"), ("Proto-Albanian", "*oinos"), ("Albanian", "i, një")],
    },
    {
        "word": "dy", "meaning": "two", "pos": "numeral",
        "root": "*dwóh₁", "confidence": 0.97,
        "cognates": [
            ("Latin", "duo", "two"), ("Greek", "δύο", "two"),
            ("English", "two", "two"), ("Sanskrit", "dváu", "two"),
        ],
        "evolutions": [("PIE", "*dwóh₁"), ("Proto-Albanian", "*duo"), ("Albanian", "dy")],
    },
    {
        "word": "tre", "meaning": "three", "pos": "numeral",
        "root": "*tréyes", "confidence": 0.97,
        "cognates": [
            ("Latin", "tres", "three"), ("Greek", "τρεῖς", "three"),
            ("English", "three", "three"), ("Sanskrit", "trāyas", "three"),
        ],
        "evolutions": [("PIE", "*tréyes"), ("Proto-Albanian", "*treis"), ("Albanian", "tre")],
    },
    {
        "word": "katër", "meaning": "four", "pos": "numeral",
        "root": "*kʷetwóres", "confidence": 0.96,
        "cognates": [
            ("Latin", "quattuor", "four"), ("Greek", "τέτταρες", "four"),
            ("Sanskrit", "catvāras", "four"), ("English", "four", "four"),
        ],
        "evolutions": [("PIE", "*kʷetwóres"), ("Proto-Albanian", "*ketwar-"), ("Albanian", "katër")],
    },
    {
        "word": "pesë", "meaning": "five", "pos": "numeral",
        "root": "*pénkʷe", "confidence": 0.96,
        "cognates": [
            ("Latin", "quinque", "five"), ("Greek", "πέντε", "five"),
            ("Sanskrit", "pañca", "five"), ("English", "five", "five"),
        ],
        "evolutions": [("PIE", "*pénkʷe"), ("Proto-Albanian", "*penke"), ("Albanian", "pesë")],
    },
    {
        "word": "gjashtë", "meaning": "six", "pos": "numeral",
        "root": "*swéks", "confidence": 0.94,
        "cognates": [
            ("Latin", "sex", "six"), ("Greek", "ἕξ", "six"),
            ("Sanskrit", "ṣaṭ", "six"), ("English", "six", "six"),
        ],
        "evolutions": [("PIE", "*swéks"), ("Proto-Albanian", "*gjakt-"), ("Albanian", "gjashtë")],
    },
    {
        "word": "shtatë", "meaning": "seven", "pos": "numeral",
        "root": "*septḿ̥", "confidence": 0.95,
        "cognates": [
            ("Latin", "septem", "seven"), ("Greek", "ἑπτά", "seven"),
            ("Sanskrit", "saptá", "seven"), ("English", "seven", "seven"),
        ],
        "evolutions": [("PIE", "*septḿ̥"), ("Proto-Albanian", "*sjepta"), ("Albanian", "shtatë")],
    },
    {
        "word": "tetë", "meaning": "eight", "pos": "numeral",
        "root": "*oḱtṓ", "confidence": 0.95,
        "cognates": [
            ("Latin", "octo", "eight"), ("Greek", "ὀκτώ", "eight"),
            ("Sanskrit", "aṣṭā", "eight"), ("English", "eight", "eight"),
        ],
        "evolutions": [("PIE", "*oḱtṓ"), ("Proto-Albanian", "*okta"), ("Albanian", "tetë")],
    },
    {
        "word": "nëntë", "meaning": "nine", "pos": "numeral",
        "root": "*h₁newn̥", "confidence": 0.95,
        "cognates": [
            ("Latin", "novem", "nine"), ("Greek", "ἐννέα", "nine"),
            ("Sanskrit", "náva", "nine"), ("English", "nine", "nine"),
        ],
        "evolutions": [("PIE", "*h₁newn̥"), ("Proto-Albanian", "*newna"), ("Albanian", "nëntë")],
    },
    {
        "word": "dhjetë", "meaning": "ten", "pos": "numeral",
        "root": "*déḱm̥t", "confidence": 0.96,
        "cognates": [
            ("Latin", "decem", "ten"), ("Greek", "δέκα", "ten"),
            ("Sanskrit", "dáśa", "ten"), ("English", "ten", "ten"),
        ],
        "evolutions": [("PIE", "*déḱm̥t"), ("Proto-Albanian", "*deka"), ("Albanian", "dhjetë")],
    },
    {
        "word": "njëqind", "meaning": "hundred", "pos": "numeral",
        "root": "*ḱm̥tóm", "confidence": 0.93,
        "cognates": [
            ("Latin", "centum", "hundred"), ("Greek", "ἑκατόν", "hundred"),
            ("Sanskrit", "śatam", "hundred"), ("English", "hundred", "hundred"),
        ],
        "evolutions": [("PIE", "*ḱm̥tóm"), ("Proto-Albanian", "*kanta"), ("Albanian", "njëqind")],
    },
    {
        "word": "madh", "meaning": "big, great", "pos": "adjective",
        "root": "*méǵh₂s", "confidence": 0.90,
        "cognates": [
            ("Latin", "magnus", "great"), ("Greek", "μέγας", "great"),
            ("Sanskrit", "mahat", "great"), ("English", "much", "much"),
        ],
        "evolutions": [("PIE", "*méǵh₂s"), ("Proto-Albanian", "*mag-"), ("Albanian", "madh")],
    },
    {
        "word": "vogël", "meaning": "small, little", "pos": "adjective",
        "root": "*wāgos", "confidence": 0.60,
        "cognates": [("Latin", "vagus", "wandering"), ("Lithuanian", "vāgoti", "to wander")],
        "evolutions": [("PIE", "*wāgos"), ("Albanian", "vogël")],
    },
    {
        "word": "i mirë", "meaning": "good", "pos": "adjective",
        "root": "*meyH-", "confidence": 0.72,
        "cognates": [("Latin", "mitis", "mild"), ("Greek", "μείλιχος", "gentle")],
        "evolutions": [("PIE", "*meyH-"), ("Albanian", "mirë")],
    },
    {
        "word": "keq", "meaning": "bad, evil", "pos": "adjective",
        "root": "*kakos", "confidence": 0.68, "notes": "Possibly from Greek",
        "cognates": [("Greek", "κακός", "bad"), ("Armenian", "kak", "feces")],
        "evolutions": [("Greek", "κακός"), ("Albanian", "keq")],
    },
    {
        "word": "i ri", "meaning": "new, young", "pos": "adjective",
        "root": "*néwos", "confidence": 0.90,
        "cognates": [
            ("Latin", "novus", "new"), ("Greek", "νέος", "new"),
            ("English", "new", "new"), ("Sanskrit", "náva", "new"),
        ],
        "evolutions": [("PIE", "*néwos"), ("Proto-Albanian", "*newos"), ("Albanian", "ri")],
    },
    {
        "word": "plakur", "meaning": "old (of things)", "pos": "adjective",
        "root": "*pḷth₂-", "confidence": 0.64,
        "cognates": [("Greek", "πλατύς", "broad"), ("Sanskrit", "pṛthu", "broad")],
        "evolutions": [("PIE", "*pḷth₂-"), ("Albanian", "plakur")],
    },
    {
        "word": "i bardhë", "meaning": "white", "pos": "adjective",
        "root": "*bʰerHg-", "confidence": 0.85,
        "cognates": [
            ("English", "bright", "bright"), ("German", "Birke", "birch"),
            ("Latin", "fulvus", "tawny"),
        ],
        "evolutions": [("PIE", "*bʰerHg-"), ("Proto-Albanian", "*bard-"), ("Albanian", "bardhë")],
    },
    {
        "word": "i zi", "meaning": "black, dark", "pos": "adjective",
        "root": "*ǵʰwer-", "confidence": 0.70,
        "cognates": [("Sanskrit", "ghora", "gloomy"), ("Avestan", "zāra", "yellow")],
        "evolutions": [("PIE", "*ǵʰwer-"), ("Albanian", "zi")],
    },
    {
        "word": "i kuq", "meaning": "red", "pos": "adjective",
        "root": "*krewh₂-", "confidence": 0.75,
        "cognates": [
            ("Latin", "cruor", "blood"), ("Greek", "κρέας", "meat"),
            ("English", "raw", "raw"),
        ],
        "evolutions": [("PIE", "*krewh₂-"), ("Proto-Albanian", "*krud-"), ("Albanian", "kuq")],
    },
    {
        "word": "i gjelbër", "meaning": "green", "pos": "adjective",
        "root": "*gʰelH-", "confidence": 0.73,
        "cognates": [
            ("English", "yellow", "yellow"), ("Latin", "flavus", "golden-yellow"),
            ("Greek", "χλωρός", "green, yellow"),
        ],
        "evolutions": [("PIE", "*gʰelH-"), ("Proto-Albanian", "*gjelb-"), ("Albanian", "gjelbër")],
    },
    {
        "word": "i kaltër", "meaning": "blue, light blue", "pos": "adjective",
        "root": "*kalH-", "confidence": 0.62,
        "cognates": [("Latin", "caelum", "sky"), ("English", "sky", "sky")],
        "evolutions": [("PIE", "*kalH-"), ("Albanian", "kaltër")],
    },
    {
        "word": "i nxehtë", "meaning": "hot, warm", "pos": "adjective",
        "root": "*h₁ep-", "confidence": 0.65,
        "cognates": [("Latin", "aestus", "heat"), ("Greek", "αἴθω", "to burn")],
        "evolutions": [("PIE", "*h₁ep-"), ("Albanian", "nxehtë")],
    },
    {
        "word": "i ftohtë", "meaning": "cold", "pos": "adjective",
        "root": "*pHg-", "confidence": 0.70,
        "cognates": [
            ("Latin", "pacare", "to appease"), ("Lithuanian", "pagóda", "pleasant weather"),
        ],
        "evolutions": [("PIE", "*pHg-"), ("Albanian", "ftohtë")],
    },
    {
        "word": "larg", "meaning": "far, distant", "pos": "adverb/adjective",
        "root": "*dlongʰo-", "confidence": 0.78,
        "cognates": [
            ("Latin", "longus", "long"), ("English", "long", "long"),
            ("Sanskrit", "dīrgha", "long"),
        ],
        "evolutions": [("PIE", "*dlongʰo-"), ("Latin", "largus"), ("Albanian", "larg")],
    },
    {
        "word": "afër", "meaning": "near, close", "pos": "adverb/preposition",
        "root": "*h₂po", "confidence": 0.68,
        "cognates": [("Latin", "ab", "from"), ("Greek", "ἀπό", "from"), ("English", "of", "of")],
        "evolutions": [("PIE", "*h₂po"), ("Albanian", "afër")],
    },
    {
        "word": "lart", "meaning": "up, high, above", "pos": "adverb",
        "root": "*h₂el-", "confidence": 0.75,
        "cognates": [("Latin", "altus", "high"), ("English", "altitude", "height")],
        "evolutions": [("PIE", "*h₂el-"), ("Latin", "altus"), ("Albanian", "lart")],
    },
    {
        "word": "poshtë", "meaning": "down, below", "pos": "adverb",
        "root": "*pod-", "confidence": 0.73,
        "cognates": [("Greek", "ποῦς", "foot"), ("Latin", "pes", "foot"), ("English", "foot", "foot")],
        "evolutions": [("PIE", "*pod-"), ("Albanian", "poshtë")],
    },
    {
        "word": "shumë", "meaning": "much, many, very", "pos": "adverb/adjective",
        "root": "*somo-", "confidence": 0.65,
        "cognates": [("Greek", "ὁμός", "same"), ("Sanskrit", "sama", "same, even")],
        "evolutions": [("PIE", "*somo-"), ("Albanian", "shumë")],
    },
    {
        "word": "pak", "meaning": "few, little", "pos": "adverb/adjective",
        "root": "*peh₂k-", "confidence": 0.63,
        "cognates": [("Latin", "paucus", "few"), ("Greek", "παῦρος", "small")],
        "evolutions": [("PIE", "*peh₂k-"), ("Albanian", "pak")],
    },
    {
        "word": "kur", "meaning": "when", "pos": "conjunction/adverb",
        "root": "*kʷo-", "confidence": 0.83,
        "cognates": [
            ("Latin", "quando", "when"), ("Greek", "πότε", "when"),
            ("Sanskrit", "kadā", "when"),
        ],
        "evolutions": [("PIE", "*kʷo-"), ("Albanian", "kur")],
    },
    {
        "word": "ku", "meaning": "where", "pos": "adverb",
        "root": "*kʷo-", "confidence": 0.85,
        "cognates": [
            ("Latin", "quo", "where"), ("Greek", "ποῦ", "where"),
            ("English", "who", "who"),
        ],
        "evolutions": [("PIE", "*kʷo-"), ("Proto-Albanian", "*kwo-"), ("Albanian", "ku")],
    },
    {
        "word": "si", "meaning": "how, like, as", "pos": "adverb/conjunction",
        "root": "*swi-", "confidence": 0.72,
        "cognates": [("Latin", "si", "if"), ("Greek", "εἰ", "if")],
        "evolutions": [("PIE", "*swi-"), ("Albanian", "si")],
    },
    {
        "word": "pse", "meaning": "why", "pos": "adverb",
        "root": "*kʷis", "confidence": 0.70,
        "cognates": [("Latin", "quis", "who"), ("Greek", "τίς", "who")],
        "evolutions": [("PIE", "*kʷis"), ("Albanian", "pse")],
    },
    {
        "word": "i gjatë", "meaning": "long, tall", "pos": "adjective",
        "root": "*dlongʰo-", "confidence": 0.82,
        "cognates": [
            ("Latin", "longus", "long"), ("English", "long", "long"),
            ("Sanskrit", "dīrgha", "long"),
        ],
        "evolutions": [("PIE", "*dlongʰo-"), ("Proto-Albanian", "*gjat-"), ("Albanian", "gjatë")],
    },
    {
        "word": "i shkurtër", "meaning": "short", "pos": "adjective",
        "root": "*skort-", "confidence": 0.70,
        "cognates": [("Latin", "curtus", "short"), ("English", "short", "short"), ("German", "kurz", "short")],
        "evolutions": [("PIE", "*skort-"), ("Albanian", "shkurtër")],
    },
    {
        "word": "i fortë", "meaning": "strong, hard", "pos": "adjective",
        "root": "*bʰerǵʰ-", "confidence": 0.67,
        "cognates": [("Latin", "fortis", "strong"), ("English", "force", "force")],
        "evolutions": [("PIE", "*bʰerǵʰ-"), ("Latin", "fortis"), ("Albanian", "fortë")],
    },
    {
        "word": "i dobët", "meaning": "weak, thin", "pos": "adjective",
        "root": "*dʰewbʰ-", "confidence": 0.55,
        "cognates": [("Lithuanian", "dubùs", "hollow"), ("Latvian", "dubs", "deep")],
        "evolutions": [("PIE", "*dʰewbʰ-"), ("Albanian", "dobët")],
    },
    {
        "word": "i thellë", "meaning": "deep", "pos": "adjective",
        "root": "*tHel-", "confidence": 0.65,
        "cognates": [("Greek", "τηλοῦ", "far away"), ("Lithuanian", "toli", "far")],
        "evolutions": [("PIE", "*tHel-"), ("Albanian", "thellë")],
    },
    {
        "word": "i ngrohtë", "meaning": "warm", "pos": "adjective",
        "root": "*gʷʰor-", "confidence": 0.72,
        "cognates": [("Sanskrit", "gharmá", "heat"), ("Greek", "θερμός", "warm"), ("English", "warm", "warm")],
        "evolutions": [("PIE", "*gʷʰor-"), ("Albanian", "ngrohtë")],
    },
    {
        "word": "i vjetër", "meaning": "old (of things, people)", "pos": "adjective",
        "root": "*wetos", "confidence": 0.83,
        "cognates": [
            ("Latin", "vetus", "old"), ("Greek", "ἔτος", "year"),
            ("Sanskrit", "vatsá", "yearling calf"),
        ],
        "evolutions": [("PIE", "*wetos"), ("Proto-Albanian", "*wetur"), ("Albanian", "vjetër")],
    },
    {
        "word": "arë", "meaning": "field, farmland", "pos": "noun",
        "root": "*h₂érh₃-", "confidence": 0.88,
        "cognates": [
            ("Latin", "arare", "to plow"), ("Greek", "ἄρουρα", "arable land"),
            ("English", "ear (of grain)", "ear"), ("Lithuanian", "árti", "to plow"),
        ],
        "evolutions": [("PIE", "*h₂érh₃-"), ("Proto-Albanian", "*ara"), ("Albanian", "arë")],
    },
    {
        "word": "farë", "meaning": "seed, grain, origin", "pos": "noun",
        "root": "*bʰer-", "confidence": 0.68,
        "cognates": [("Latin", "farre", "spelt"), ("Greek", "φερνή", "dowry")],
        "evolutions": [("PIE", "*bʰer-"), ("Albanian", "farë")],
    },
    {
        "word": "bar", "meaning": "grass, herb", "pos": "noun",
        "root": "*bʰarso-", "confidence": 0.73,
        "cognates": [("Latin", "far", "grain"), ("English", "barley", "barley")],
        "evolutions": [("PIE", "*bʰarso-"), ("Albanian", "bar")],
    },
    {
        "word": "lule", "meaning": "flower", "pos": "noun",
        "root": "*h₁lewdʰ-", "confidence": 0.70,
        "cognates": [("Latin", "flos", "flower"), ("English", "blow (blossom)", "to bloom")],
        "evolutions": [("PIE", "*h₁lewdʰ-"), ("Albanian", "lule")],
    },
    {
        "word": "fletë", "meaning": "leaf, sheet", "pos": "noun",
        "root": "*pleh₃-", "confidence": 0.78,
        "cognates": [("Latin", "folium", "leaf"), ("Greek", "φύλλον", "leaf")],
        "evolutions": [("PIE", "*pleh₃-"), ("Albanian", "fletë")],
    },
    {
        "word": "rrënjë", "meaning": "root (of plant)", "pos": "noun",
        "root": "*wréh₂ds", "confidence": 0.82,
        "cognates": [
            ("Latin", "radix", "root"), ("English", "root", "root"),
            ("Greek", "ῥίζα", "root"),
        ],
        "evolutions": [("PIE", "*wréh₂ds"), ("Albanian", "rrënjë")],
    },
    {
        "word": "kokë", "meaning": "head", "pos": "noun",
        "root": "*kaput-", "confidence": 0.80,
        "cognates": [
            ("Latin", "caput", "head"), ("German", "Kopf", "head"),
            ("English", "head", "head"),
        ],
        "evolutions": [("PIE", "*kaput-"), ("Latin", "caput"), ("Albanian", "kokë")],
    },
    {
        "word": "bark", "meaning": "belly, womb", "pos": "noun",
        "root": "*bʰerg-", "confidence": 0.67,
        "cognates": [("Sanskrit", "barhi", "guts"), ("Avestan", "barəz", "height")],
        "evolutions": [("PIE", "*bʰerg-"), ("Albanian", "bark")],
    },
    {
        "word": "shpinë", "meaning": "back (body)", "pos": "noun",
        "root": "*spino-", "confidence": 0.72,
        "cognates": [("Latin", "spina", "spine"), ("English", "spine", "spine")],
        "evolutions": [("Latin", "spina"), ("Albanian", "shpinë")],
    },
    {
        "word": "krah", "meaning": "arm, wing", "pos": "noun",
        "root": "*kreh₂-", "confidence": 0.75,
        "cognates": [("Greek", "κράτος", "strength"), ("Sanskrit", "kratu", "power")],
        "evolutions": [("PIE", "*kreh₂-"), ("Albanian", "krah")],
    },
    {
        "word": "gisht", "meaning": "finger", "pos": "noun",
        "root": "*dígʰitis", "confidence": 0.78,
        "cognates": [("Latin", "digitus", "finger"), ("English", "digit", "digit")],
        "evolutions": [("PIE", "*dígʰitis"), ("Latin", "digitus"), ("Albanian", "gisht")],
    },
    {
        "word": "kënd", "meaning": "corner, angle", "pos": "noun",
        "root": "*kanto-", "confidence": 0.65,
        "cognates": [("Latin", "cantus", "rim"), ("Welsh", "cant", "rim, hundred")],
        "evolutions": [("PIE", "*kanto-"), ("Albanian", "kënd")],
    },
    {
        "word": "qen", "meaning": "dog", "pos": "noun",
        "root": "*ḱwón", "confidence": 0.92,
        "cognates": [
            ("Latin", "canis", "dog"), ("Greek", "κύων", "dog"),
            ("Sanskrit", "śvan", "dog"), ("English", "hound", "dog"),
        ],
        "evolutions": [("PIE", "*ḱwón"), ("Proto-Albanian", "*kun-"), ("Albanian", "qen")],
    },
    {
        "word": "mace", "meaning": "cat", "pos": "noun",
        "root": "*matus", "confidence": 0.45, "notes": "Wanderwort, widespread loanword",
        "cognates": [("Latin", "cattus", "cat"), ("French", "chat", "cat"), ("English", "cat", "cat")],
        "evolutions": [("Medieval Latin", "cattus"), ("Albanian", "mace")],
    },
    {
        "word": "kalë", "meaning": "horse", "pos": "noun",
        "root": "*h₁eḱwos", "confidence": 0.85,
        "cognates": [
            ("Latin", "equus", "horse"), ("Greek", "ἵππος", "horse"),
            ("Sanskrit", "áśva", "horse"), ("English", "equine", "horse-related"),
        ],
        "evolutions": [("PIE", "*h₁eḱwos"), ("Proto-Albanian", "*ekwa"), ("Albanian", "kalë")],
    },
    {
        "word": "pulë", "meaning": "hen, chicken", "pos": "noun",
        "root": "*pulo-", "confidence": 0.68,
        "cognates": [("Latin", "pullus", "young animal"), ("English", "foal", "young horse")],
        "evolutions": [("PIE", "*pulo-"), ("Latin", "pullus"), ("Albanian", "pulë")],
    },
    {
        "word": "mjek", "meaning": "doctor, physician", "pos": "noun",
        "root": "*med-", "confidence": 0.80,
        "cognates": [
            ("Latin", "medicus", "doctor"), ("English", "medicine", "medicine"),
            ("Sanskrit", "mīḍhvas", "generous"),
        ],
        "evolutions": [("PIE", "*med-"), ("Latin", "medicus"), ("Albanian", "mjek")],
    },
    {
        "word": "ligj", "meaning": "law", "pos": "noun",
        "root": "*leǵ-", "confidence": 0.72,
        "cognates": [("Latin", "lex", "law"), ("English", "legal", "legal")],
        "evolutions": [("PIE", "*leǵ-"), ("Latin", "lex"), ("Albanian", "ligj")],
    },
    {
        "word": "luftë", "meaning": "war, battle, fight", "pos": "noun",
        "root": "*lewdʰ-", "confidence": 0.70,
        "cognates": [("Gothic", "liudan", "to grow"), ("English", "loud", "loud")],
        "evolutions": [("PIE", "*lewdʰ-"), ("Albanian", "luftë")],
    },
    {
        "word": "paqe", "meaning": "peace", "pos": "noun",
        "root": "*peh₂k-", "confidence": 0.72,
        "cognates": [("Latin", "pax", "peace"), ("English", "peace", "peace")],
        "evolutions": [("PIE", "*peh₂k-"), ("Latin", "pax"), ("Albanian", "paqe")],
    },
    {
        "word": "jetë", "meaning": "life", "pos": "noun",
        "root": "*gʷiH-", "confidence": 0.83,
        "cognates": [
            ("Greek", "βίος", "life"), ("Latin", "vita", "life"),
            ("English", "quick (archaic: alive)", "alive"),
        ],
        "evolutions": [("PIE", "*gʷiH-"), ("Proto-Albanian", "*dze-"), ("Albanian", "jetë")],
    },
    {
        "word": "vdekje", "meaning": "death", "pos": "noun",
        "root": "*dhwes-", "confidence": 0.65,
        "cognates": [("Sanskrit", "dhvaṃsate", "falls apart"), ("Greek", "θνῄσκω", "to die")],
        "evolutions": [("PIE", "*dhwes-"), ("Albanian", "vdekje")],
    },
    {
        "word": "lindje", "meaning": "birth, east", "pos": "noun",
        "root": "*h₁lewdʰ-", "confidence": 0.75,
        "cognates": [("Greek", "ἐλεύθερος", "free"), ("Latin", "liber", "free")],
        "evolutions": [("PIE", "*h₁lewdʰ-"), ("Albanian", "lindje")],
    },
    {
        "word": "mirë", "meaning": "good, well", "pos": "adjective/adverb",
        "root": "*meyH-", "confidence": 0.73,
        "cognates": [("Latin", "mitis", "mild, gentle"), ("Sanskrit", "māyas", "grace")],
        "evolutions": [("PIE", "*meyH-"), ("Proto-Albanian", "*mir-"), ("Albanian", "mirë")],
    },
    {
        "word": "herë", "meaning": "time, occasion", "pos": "noun",
        "root": "*h₂yeh₁r-", "confidence": 0.70,
        "cognates": [("Greek", "ὥρα", "hour, time"), ("Latin", "hora", "hour"), ("English", "year", "year")],
        "evolutions": [("PIE", "*h₂yeh₁r-"), ("Greek", "ὥρα"), ("Albanian", "herë")],
    },
    {
        "word": "kohë", "meaning": "time, weather", "pos": "noun",
        "root": "*keh₂-", "confidence": 0.67,
        "cognates": [("Latin", "casus", "case, occasion"), ("Greek", "καιρός", "right time")],
        "evolutions": [("PIE", "*keh₂-"), ("Albanian", "kohë")],
    },
    {
        "word": "vit", "meaning": "year", "pos": "noun",
        "root": "*wetos", "confidence": 0.85,
        "cognates": [
            ("Latin", "vetus", "old"), ("Greek", "ἔτος", "year"),
            ("Sanskrit", "vatsá", "yearling"),
        ],
        "evolutions": [("PIE", "*wetos"), ("Proto-Albanian", "*wetus"), ("Albanian", "vit")],
    },
    {
        "word": "muaj", "meaning": "month", "pos": "noun",
        "root": "*mḗh₁n̥s", "confidence": 0.88,
        "cognates": [
            ("Latin", "mensis", "month"), ("Greek", "μήν", "month"),
            ("English", "month", "month"),
        ],
        "evolutions": [("PIE", "*mḗh₁n̥s"), ("Proto-Albanian", "*man-"), ("Albanian", "muaj")],
    },
    {
        "word": "javë", "meaning": "week", "pos": "noun",
        "root": "*yewH-", "confidence": 0.55, "notes": "Etymology disputed",
        "cognates": [("Slavic", "*javi", "manifest"), ("Latin", "Jove", "Jupiter")],
        "evolutions": [("Albanian", "javë")],
    },
    {
        "word": "mbrëmje", "meaning": "evening", "pos": "noun",
        "root": "*h₃mbri-", "confidence": 0.68,
        "cognates": [("Latin", "imber", "rain"), ("Greek", "ὄμβρος", "rain")],
        "evolutions": [("PIE", "*h₃mbri-"), ("Albanian", "mbrëmje")],
    },
    {
        "word": "mëngjes", "meaning": "morning", "pos": "noun",
        "root": "*men-", "confidence": 0.60,
        "cognates": [("Latin", "mane", "morning"), ("German", "Morgen", "morning")],
        "evolutions": [("PIE", "*men-"), ("Albanian", "mëngjes")],
    },
    {
        "word": "gjumë", "meaning": "sleep", "pos": "noun",
        "root": "*dʰewbʰ-", "confidence": 0.58,
        "cognates": [("Greek", "θυμός", "spirit"), ("Latin", "fumus", "smoke")],
        "evolutions": [("PIE", "*dʰewbʰ-"), ("Albanian", "gjumë")],
    },
    {
        "word": "ëndërr", "meaning": "dream", "pos": "noun",
        "root": "*h₂endʰ-", "confidence": 0.62,
        "cognates": [("Sanskrit", "andha", "blind"), ("Greek", "ἄνθος", "flower")],
        "evolutions": [("PIE", "*h₂endʰ-"), ("Albanian", "ëndërr")],
    },
    {
        "word": "frikë", "meaning": "fear, fright", "pos": "noun",
        "root": "*sperg-", "confidence": 0.58,
        "cognates": [("Latin", "frico", "to rub"), ("English", "fear", "fear")],
        "evolutions": [("PIE", "*sperg-"), ("Albanian", "frikë")],
    },
    {
        "word": "gëzim", "meaning": "joy, happiness", "pos": "noun",
        "root": "*gʰow-", "confidence": 0.65,
        "cognates": [("English", "glee", "joy"), ("Danish", "glæde", "joy")],
        "evolutions": [("PIE", "*gʰow-"), ("Albanian", "gëzim")],
    },
    {
        "word": "dashuri", "meaning": "love", "pos": "noun",
        "root": "*dʰewH-", "confidence": 0.62,
        "cognates": [("Greek", "θεός", "god"), ("Sanskrit", "dhav", "to run toward")],
        "evolutions": [("PIE", "*dʰewH-"), ("Albanian", "dashuri")],
    },
    {
        "word": "urrejtje", "meaning": "hatred", "pos": "noun",
        "root": "*h₁ors-", "confidence": 0.55,
        "cognates": [("Gothic", "wrathjan", "to anger"), ("English", "wrath", "anger")],
        "evolutions": [("PIE", "*h₁ors-"), ("Albanian", "urrejtje")],
    },
    {
        "word": "besë", "meaning": "faith, word of honor", "pos": "noun",
        "root": "*bʰendʰ-", "confidence": 0.73,
        "cognates": [("Sanskrit", "badhnāti", "binds"), ("Gothic", "bindan", "to bind")],
        "evolutions": [("PIE", "*bʰendʰ-"), ("Proto-Albanian", "*bes-"), ("Albanian", "besë")],
    },
    {
        "word": "ari", "meaning": "gold", "pos": "noun",
        "root": "*h₂é-h₂us-os", "confidence": 0.78,
        "cognates": [
            ("Latin", "aurum", "gold"), ("Sanskrit", "háraṇa", "golden"),
            ("Gothic", "gulp", "gold"),
        ],
        "evolutions": [("PIE", "*h₂é-h₂us-os"), ("Proto-Albanian", "*aur-"), ("Albanian", "ar")],
    },
    {
        "word": "argjend", "meaning": "silver", "pos": "noun",
        "root": "*h₂erǵ-", "confidence": 0.88,
        "cognates": [
            ("Latin", "argentum", "silver"), ("Greek", "ἄργυρος", "silver"),
            ("Sanskrit", "arjuna", "white"),
        ],
        "evolutions": [("PIE", "*h₂erǵ-"), ("Latin", "argentum"), ("Albanian", "argjend")],
    },
    {
        "word": "hekur", "meaning": "iron", "pos": "noun",
        "root": "*h₁eysro-", "confidence": 0.72,
        "cognates": [
            ("Latin", "aes", "copper/bronze"), ("Greek", "χαλκός", "copper"),
            ("Celtic", "*isarno", "iron"),
        ],
        "evolutions": [("PIE", "*h₁eysro-"), ("Proto-Albanian", "*isarn"), ("Albanian", "hekur")],
    },
    {
        "word": "qiell", "meaning": "heaven, sky", "pos": "noun",
        "root": "*kel-", "confidence": 0.73,
        "cognates": [("Latin", "caelum", "sky"), ("Welsh", "caer", "fortress, sky")],
        "evolutions": [("PIE", "*kel-"), ("Albanian", "qiell")],
    },
    {
        "word": "shpellë", "meaning": "cave, grotto", "pos": "noun",
        "root": "*spelH-", "confidence": 0.70,
        "cognates": [("English", "speleology", "cave science"), ("Greek", "σπήλαιον", "cave")],
        "evolutions": [("PIE", "*spelH-"), ("Albanian", "shpellë")],
    },
    {
        "word": "bregdet", "meaning": "coast, seashore", "pos": "noun",
        "root": "*bʰreǵʰ-", "confidence": 0.65,
        "cognates": [("English", "bank", "riverbank"), ("German", "Berg", "mountain")],
        "evolutions": [("PIE", "*bʰreǵʰ-"), ("Albanian", "bregdet")],
    },
    {
        "word": "fushë", "meaning": "field, plain", "pos": "noun",
        "root": "*pl̥th₂ú-", "confidence": 0.75,
        "cognates": [("Sanskrit", "pṛthu", "broad"), ("Greek", "πλατύς", "broad, flat")],
        "evolutions": [("PIE", "*pl̥th₂ú-"), ("Albanian", "fushë")],
    },
    {
        "word": "kodër", "meaning": "hill", "pos": "noun",
        "root": "*kauto-", "confidence": 0.60,
        "cognates": [("Lithuanian", "kaũtas", "lump"), ("Latvian", "kaudze", "heap")],
        "evolutions": [("PIE", "*kauto-"), ("Albanian", "kodër")],
    },
    {
        "word": "liqen", "meaning": "lake", "pos": "noun",
        "root": "*likʷ-", "confidence": 0.65,
        "cognates": [("Latin", "lacus", "lake"), ("English", "lake", "lake")],
        "evolutions": [("PIE", "*likʷ-"), ("Latin", "lacus"), ("Albanian", "liqen")],
    },
    {
        "word": "burim", "meaning": "spring (water), source", "pos": "noun",
        "root": "*bʰer-", "confidence": 0.72,
        "cognates": [("English", "bore (well)", "to drill"), ("Norwegian", "bjørn", "gushing")],
        "evolutions": [("PIE", "*bʰer-"), ("Albanian", "burim")],
    },
    {
        "word": "shkëmb", "meaning": "rock, cliff", "pos": "noun",
        "root": "*skambʰ-", "confidence": 0.68,
        "cognates": [("Sanskrit", "skambha", "pillar"), ("Greek", "σκαμβός", "bent")],
        "evolutions": [("PIE", "*skambʰ-"), ("Albanian", "shkëmb")],
    },
    {
        "word": "rërë", "meaning": "sand", "pos": "noun",
        "root": "*reu-", "confidence": 0.63,
        "cognates": [("Latin", "rumen", "gullet"), ("Lithuanian", "rauti", "to pull out")],
        "evolutions": [("PIE", "*reu-"), ("Albanian", "rërë")],
    },
    {
        "word": "baltë", "meaning": "mud, clay", "pos": "noun",
        "root": "*bʰelH-", "confidence": 0.68,
        "cognates": [("Latin", "fulvus", "tawny"), ("Lithuanian", "baltas", "white")],
        "evolutions": [("PIE", "*bʰelH-"), ("Albanian", "baltë")],
    },

    # ── Kinship ────────────────────────────────────────────────
    {
        "word": "nip", "meaning": "nephew, grandson", "pos": "noun",
        "root": "*nepōts", "confidence": 0.90,
        "cognates": [
            ("Latin", "nepos", "grandson, nephew"), ("English", "nephew", "nephew"),
            ("Sanskrit", "napat", "grandson"), ("German", "Neffe", "nephew"),
            ("Greek", "ἀνεψιός", "nephew"),
        ],
        "evolutions": [("PIE", "*nepōts"), ("Proto-Albanian", "*nept-"), ("Albanian", "nip")],
    },
    {
        "word": "vjehër", "meaning": "father-in-law", "pos": "noun",
        "root": "*sweḱuros", "confidence": 0.90,
        "cognates": [
            ("Latin", "socer", "father-in-law"), ("Greek", "ἑκυρός", "father-in-law"),
            ("Sanskrit", "śvaśura", "father-in-law"), ("Russian", "свёкор", "father-in-law"),
            ("German", "Schwiegervater", "father-in-law"),
        ],
        "evolutions": [("PIE", "*sweḱuros"), ("Proto-Albanian", "*vjeher"), ("Albanian", "vjehër")],
    },
    {
        "word": "nuse", "meaning": "bride, daughter-in-law", "pos": "noun",
        "root": "*snudʰos", "confidence": 0.82,
        "cognates": [
            ("Greek", "νυός", "daughter-in-law"), ("Latin", "nurus", "daughter-in-law"),
            ("Sanskrit", "snuṣā", "daughter-in-law"), ("Russian", "сноха", "daughter-in-law"),
        ],
        "evolutions": [("PIE", "*snudʰos"), ("Proto-Albanian", "*nuse"), ("Albanian", "nuse")],
    },

    # ── Body parts ─────────────────────────────────────────────
    {
        "word": "gju", "meaning": "knee", "pos": "noun",
        "root": "*ǵónu", "confidence": 0.95,
        "cognates": [
            ("Latin", "genu", "knee"), ("Greek", "γόνυ", "knee"),
            ("English", "knee", "knee"), ("Sanskrit", "jānu", "knee"),
            ("Gothic", "kniu", "knee"),
        ],
        "evolutions": [("PIE", "*ǵónu"), ("Proto-Albanian", "*dzen-"), ("Albanian", "gju")],
    },
    {
        "word": "ballë", "meaning": "forehead, front", "pos": "noun",
        "root": "*bʰel-", "confidence": 0.75,
        "cognates": [
            ("Greek", "φαλός", "white, shining"), ("English", "bald", "bald"),
            ("Lithuanian", "baltas", "white"),
        ],
        "evolutions": [("PIE", "*bʰel-"), ("Proto-Albanian", "*bal-"), ("Albanian", "ballë")],
    },
    {
        "word": "mëlçi", "meaning": "liver", "pos": "noun",
        "root": "*melg-", "confidence": 0.68,
        "cognates": [
            ("Greek", "μέλαν", "black"), ("Latin", "mel", "honey"),
            ("Sanskrit", "mṛga", "animal"),
        ],
        "evolutions": [("PIE", "*melg-"), ("Albanian", "mëlçi")],
    },

    # ── Animals ────────────────────────────────────────────────
    {
        "word": "miu", "meaning": "mouse", "pos": "noun",
        "root": "*mūs", "confidence": 0.93,
        "cognates": [
            ("Latin", "mus", "mouse"), ("Greek", "μῦς", "mouse"),
            ("Sanskrit", "mūṣ", "mouse"), ("English", "mouse", "mouse"),
            ("German", "Maus", "mouse"),
        ],
        "evolutions": [("PIE", "*mūs"), ("Proto-Albanian", "*mus-"), ("Albanian", "miu")],
    },
    {
        "word": "gjarpër", "meaning": "snake, serpent", "pos": "noun",
        "root": "*serp-", "confidence": 0.82,
        "cognates": [
            ("Latin", "serpens", "snake"), ("Greek", "ἕρπης", "creeping thing"),
            ("Sanskrit", "sárpa", "snake"),
        ],
        "evolutions": [("PIE", "*serp-"), ("Proto-Albanian", "*gjerp-"), ("Albanian", "gjarpër")],
    },
    {
        "word": "viç", "meaning": "calf", "pos": "noun",
        "root": "*wetsó-", "confidence": 0.80,
        "cognates": [
            ("Latin", "vitulus", "calf"), ("Greek", "ἰταλός", "bull"),
            ("Sanskrit", "vatsá", "yearling calf"),
        ],
        "evolutions": [("PIE", "*wetsó-"), ("Proto-Albanian", "*wets-"), ("Albanian", "viç")],
    },
    {
        "word": "dhi", "meaning": "goat (female)", "pos": "noun",
        "root": "*dʰiH-", "confidence": 0.72,
        "cognates": [
            ("Sanskrit", "dhenu", "milk cow"), ("Avestan", "daēnu", "female animal"),
        ],
        "evolutions": [("PIE", "*dʰiH-"), ("Albanian", "dhi")],
    },
    {
        "word": "dash", "meaning": "ram, male sheep", "pos": "noun",
        "root": "*dorso-", "confidence": 0.62,
        "cognates": [
            ("Latin", "dorsum", "back, ridge"), ("Greek", "δορσός", "back"),
        ],
        "evolutions": [("PIE", "*dorso-"), ("Albanian", "dash")],
    },
    {
        "word": "bleta", "meaning": "bee", "pos": "noun",
        "root": "*bʰlei-", "confidence": 0.67,
        "cognates": [
            ("Greek", "μέλισσα", "bee"), ("Latin", "mel", "honey"),
            ("English", "blossom", "flower"),
        ],
        "evolutions": [("PIE", "*bʰlei-"), ("Albanian", "bleta")],
    },
    {
        "word": "dre", "meaning": "deer, stag", "pos": "noun",
        "root": "*dʰerH-", "confidence": 0.67,
        "cognates": [
            ("Greek", "θήρ", "wild beast"), ("Latin", "ferus", "wild animal"),
        ],
        "evolutions": [("PIE", "*dʰerH-"), ("Albanian", "dre")],
    },
    {
        "word": "krimb", "meaning": "worm, insect larva", "pos": "noun",
        "root": "*kʷr̥mi-", "confidence": 0.80,
        "cognates": [
            ("Latin", "vermis", "worm"), ("English", "worm", "worm"),
            ("Sanskrit", "kṛmi", "worm"), ("Lithuanian", "kirmis", "worm"),
        ],
        "evolutions": [("PIE", "*kʷr̥mi-"), ("Proto-Albanian", "*krimb-"), ("Albanian", "krimb")],
    },

    # ── Sky / Nature ───────────────────────────────────────────
    {
        "word": "yll", "meaning": "star", "pos": "noun",
        "root": "*h₂stḗr", "confidence": 0.90,
        "cognates": [
            ("Greek", "ἀστήρ", "star"), ("Latin", "stella", "star"),
            ("English", "star", "star"), ("Sanskrit", "tāra", "star"),
            ("German", "Stern", "star"),
        ],
        "evolutions": [("PIE", "*h₂stḗr"), ("Proto-Albanian", "*aster"), ("Albanian", "yll")],
    },
    {
        "word": "shi", "meaning": "rain", "pos": "noun",
        "root": "*seHi-", "confidence": 0.68,
        "cognates": [
            ("Sanskrit", "sináti", "to pour"), ("Greek", "ὑετός", "rain"),
        ],
        "evolutions": [("PIE", "*seHi-"), ("Albanian", "shi")],
    },
    {
        "word": "dritë", "meaning": "light, daylight", "pos": "noun",
        "root": "*dʰrewH-", "confidence": 0.72,
        "cognates": [
            ("Lithuanian", "drūtas", "strong, firm"), ("Latvian", "drūts", "sturdy"),
        ],
        "evolutions": [("PIE", "*dʰrewH-"), ("Proto-Albanian", "*drit-"), ("Albanian", "dritë")],
    },
    {
        "word": "hije", "meaning": "shadow, shade", "pos": "noun",
        "root": "*skeh₂-", "confidence": 0.73,
        "cognates": [
            ("Greek", "σκιά", "shadow, shade"), ("Sanskrit", "chāyā", "shadow"),
        ],
        "evolutions": [("PIE", "*skeh₂-"), ("Proto-Albanian", "*hija"), ("Albanian", "hije")],
    },

    # ── Plants / Trees ─────────────────────────────────────────
    {
        "word": "mollë", "meaning": "apple", "pos": "noun",
        "root": "*h₂melo-", "confidence": 0.83,
        "cognates": [
            ("Latin", "malum", "apple"), ("Greek", "μῆλον", "apple"),
            ("Welsh", "afal", "apple"), ("Old Irish", "quell", "apple tree"),
        ],
        "evolutions": [("PIE", "*h₂melo-"), ("Proto-Albanian", "*mala"), ("Albanian", "mollë")],
    },
    {
        "word": "pyll", "meaning": "forest, woods", "pos": "noun",
        "root": "*pelH-", "confidence": 0.65,
        "cognates": [
            ("Latin", "palus", "swamp"), ("Lithuanian", "pelkė", "swamp, bog"),
        ],
        "evolutions": [("PIE", "*pelH-"), ("Albanian", "pyll")],
    },
    {
        "word": "lis", "meaning": "oak tree", "pos": "noun",
        "root": "*h₁eyHs-", "confidence": 0.70,
        "cognates": [
            ("Latin", "aesculus", "mountain oak"), ("Greek", "αἴγειρος", "black poplar"),
        ],
        "evolutions": [("PIE", "*h₁eyHs-"), ("Albanian", "lis")],
    },
    {
        "word": "ah", "meaning": "beech tree", "pos": "noun",
        "root": "*h₂eHg-", "confidence": 0.73,
        "cognates": [
            ("Latin", "acer", "maple"), ("Greek", "ἄχερδος", "wild pear"),
            ("German", "Ahorn", "maple"),
        ],
        "evolutions": [("PIE", "*h₂eHg-"), ("Albanian", "ah")],
    },

    # ── Food & Drink ───────────────────────────────────────────
    {
        "word": "mish", "meaning": "meat, flesh", "pos": "noun",
        "root": "*mḗms-", "confidence": 0.88,
        "cognates": [
            ("Sanskrit", "māṃsa", "flesh, meat"), ("Gothic", "mimz", "flesh"),
            ("Armenian", "mis", "flesh"),
        ],
        "evolutions": [("PIE", "*mḗms-"), ("Proto-Albanian", "*mems-"), ("Albanian", "mish")],
    },
    {
        "word": "vezë", "meaning": "egg", "pos": "noun",
        "root": "*h₂ōwyom", "confidence": 0.88,
        "cognates": [
            ("Latin", "ovum", "egg"), ("Greek", "ᾠόν", "egg"),
            ("English", "egg", "egg"), ("Old Norse", "egg", "egg"),
        ],
        "evolutions": [("PIE", "*h₂ōwyom"), ("Proto-Albanian", "*awa"), ("Albanian", "vezë")],
    },
    {
        "word": "miell", "meaning": "flour, meal", "pos": "noun",
        "root": "*melH-", "confidence": 0.85,
        "cognates": [
            ("Latin", "molere", "to grind"), ("Greek", "μύλη", "mill"),
            ("English", "meal", "ground grain"), ("German", "Mehl", "flour"),
        ],
        "evolutions": [("PIE", "*melH-"), ("Proto-Albanian", "*mel-"), ("Albanian", "miell")],
    },
    {
        "word": "grurë", "meaning": "wheat, grain", "pos": "noun",
        "root": "*gʷrHnóm", "confidence": 0.82,
        "cognates": [
            ("Latin", "granum", "grain"), ("English", "corn", "grain"),
            ("German", "Korn", "grain"), ("Russian", "зерно", "grain"),
        ],
        "evolutions": [("PIE", "*gʷrHnóm"), ("Proto-Albanian", "*grur-"), ("Albanian", "grurë")],
    },
    {
        "word": "elb", "meaning": "barley", "pos": "noun",
        "root": "*albʰo-", "confidence": 0.70,
        "cognates": [
            ("Latin", "albus", "white"), ("English", "oat", "oat"),
            ("Lithuanian", "alksnis", "alder"),
        ],
        "evolutions": [("PIE", "*albʰo-"), ("Albanian", "elb")],
    },

    # ── Objects / Tools ────────────────────────────────────────
    {
        "word": "rrotë", "meaning": "wheel, circle", "pos": "noun",
        "root": "*Hrótos", "confidence": 0.92,
        "cognates": [
            ("Latin", "rota", "wheel"), ("Sanskrit", "ratha", "chariot"),
            ("German", "Rad", "wheel"), ("Welsh", "rhod", "wheel"),
        ],
        "evolutions": [("PIE", "*Hrótos"), ("Proto-Albanian", "*rota"), ("Albanian", "rrotë")],
    },
    {
        "word": "armë", "meaning": "weapon, arm", "pos": "noun",
        "root": "*h₂er-mo-", "confidence": 0.83,
        "cognates": [
            ("Latin", "arma", "weapons, arms"), ("Greek", "ἁρμός", "joint, fitting"),
            ("English", "arm (weapon)", "weapon"),
        ],
        "evolutions": [("PIE", "*h₂er-mo-"), ("Latin", "arma"), ("Albanian", "armë")],
    },
    {
        "word": "shtizë", "meaning": "spear, lance", "pos": "noun",
        "root": "*steygʰ-", "confidence": 0.68,
        "cognates": [
            ("Greek", "στίχος", "row, line"), ("English", "stick", "stick"),
            ("German", "Stich", "stab"),
        ],
        "evolutions": [("PIE", "*steygʰ-"), ("Albanian", "shtizë")],
    },
    {
        "word": "hark", "meaning": "bow (weapon)", "pos": "noun",
        "root": "*arku-", "confidence": 0.78,
        "cognates": [
            ("Latin", "arcus", "bow, arc"), ("English", "arc", "arc"),
        ],
        "evolutions": [("Latin", "arcus"), ("Albanian", "hark")],
    },

    # ── Language / Social ──────────────────────────────────────
    {
        "word": "fjalë", "meaning": "word, speech, language", "pos": "noun",
        "root": "*bʰeh₂-", "confidence": 0.80,
        "cognates": [
            ("Greek", "φήμη", "speech, fame"), ("Latin", "fama", "fame, speech"),
            ("Latin", "fari", "to speak"), ("Greek", "φωνή", "voice"),
        ],
        "evolutions": [("PIE", "*bʰeh₂-"), ("Proto-Albanian", "*fala"), ("Albanian", "fjalë")],
    },
    {
        "word": "mik", "meaning": "friend, guest", "pos": "noun",
        "root": "*h₃megʰ-", "confidence": 0.65,
        "cognates": [
            ("Latin", "amicus", "friend"), ("Sanskrit", "amā", "at home"),
        ],
        "evolutions": [("PIE", "*h₃megʰ-"), ("Proto-Albanian", "*mik"), ("Albanian", "mik")],
    },
    {
        "word": "fis", "meaning": "clan, tribe, kindred", "pos": "noun",
        "root": "*peyH-", "confidence": 0.65,
        "cognates": [
            ("Latin", "pius", "pious, dutiful"), ("Sanskrit", "pitu", "food, father"),
        ],
        "evolutions": [("PIE", "*peyH-"), ("Albanian", "fis")],
    },

    # ── Verbs ──────────────────────────────────────────────────
    {
        "word": "flas", "meaning": "to speak, to talk", "pos": "verb",
        "root": "*bʰeh₂-", "confidence": 0.78,
        "cognates": [
            ("Greek", "φημί", "to say"), ("Latin", "fari", "to speak"),
            ("Latin", "fabula", "story"), ("Greek", "φάτις", "rumor"),
        ],
        "evolutions": [("PIE", "*bʰeh₂-"), ("Proto-Albanian", "*flas-"), ("Albanian", "flas")],
    },
    {
        "word": "mendoj", "meaning": "to think, to believe", "pos": "verb",
        "root": "*men-", "confidence": 0.85,
        "cognates": [
            ("Latin", "mens", "mind"), ("Greek", "μένος", "spirit, force"),
            ("Sanskrit", "manas", "mind"), ("English", "mind", "mind"),
        ],
        "evolutions": [("PIE", "*men-"), ("Proto-Albanian", "*mend-"), ("Albanian", "mendoj")],
    },
    {
        "word": "laj", "meaning": "to wash, to clean", "pos": "verb",
        "root": "*lewH-", "confidence": 0.80,
        "cognates": [
            ("Latin", "lavare", "to wash"), ("Greek", "λούω", "to wash"),
            ("English", "lather", "lather"), ("Russian", "лить", "to pour"),
        ],
        "evolutions": [("PIE", "*lewH-"), ("Proto-Albanian", "*lawa"), ("Albanian", "laj")],
    },
    {
        "word": "sjell", "meaning": "to bring, to carry", "pos": "verb",
        "root": "*bʰer-", "confidence": 0.80,
        "cognates": [
            ("Latin", "ferre", "to carry"), ("Greek", "φέρω", "to carry"),
            ("Sanskrit", "bhárati", "carries"), ("English", "bear", "to carry"),
        ],
        "evolutions": [("PIE", "*bʰer-"), ("Proto-Albanian", "*sjel-"), ("Albanian", "sjell")],
    },
    {
        "word": "notoj", "meaning": "to swim", "pos": "verb",
        "root": "*sneh₂-", "confidence": 0.78,
        "cognates": [
            ("Latin", "nare", "to swim"), ("Latin", "natare", "to swim"),
            ("Sanskrit", "snāti", "bathes"),
        ],
        "evolutions": [("PIE", "*sneh₂-"), ("Proto-Albanian", "*not-"), ("Albanian", "notoj")],
    },
    {
        "word": "korr", "meaning": "to harvest, to reap", "pos": "verb",
        "root": "*ker-", "confidence": 0.74,
        "cognates": [
            ("Greek", "καρπός", "fruit, harvest"), ("Latin", "carpere", "to pluck"),
            ("English", "harvest", "harvest"),
        ],
        "evolutions": [("PIE", "*ker-"), ("Albanian", "korr")],
    },
    {
        "word": "pres", "meaning": "to cut; to wait", "pos": "verb",
        "root": "*sker-", "confidence": 0.73,
        "cognates": [
            ("Greek", "κείρω", "to cut"), ("Latin", "curtus", "cut short"),
            ("English", "shear", "to cut"),
        ],
        "evolutions": [("PIE", "*sker-"), ("Albanian", "pres")],
    },
    {
        "word": "thyej", "meaning": "to break, to fracture", "pos": "verb",
        "root": "*tewH-", "confidence": 0.65,
        "cognates": [
            ("Latin", "tundere", "to beat"), ("Greek", "τύπτω", "to strike"),
        ],
        "evolutions": [("PIE", "*tewH-"), ("Albanian", "thyej")],
    },
    {
        "word": "këndon", "meaning": "to sing, to chant", "pos": "verb",
        "root": "*kan-", "confidence": 0.80,
        "cognates": [
            ("Latin", "canere", "to sing"), ("Welsh", "canu", "to sing"),
            ("Latin", "cantare", "to sing"), ("English", "hen", "singing bird"),
        ],
        "evolutions": [("PIE", "*kan-"), ("Latin", "cantare"), ("Albanian", "këndon")],
    },
    {
        "word": "jetoj", "meaning": "to live, to dwell", "pos": "verb",
        "root": "*gʷiH-", "confidence": 0.83,
        "cognates": [
            ("Greek", "βίος", "life"), ("Latin", "vita", "life"),
            ("Latin", "vivus", "alive"),
        ],
        "evolutions": [("PIE", "*gʷiH-"), ("Proto-Albanian", "*dze-"), ("Albanian", "jetoj")],
    },
    {
        "word": "punoj", "meaning": "to work, to labor", "pos": "verb",
        "root": "*pewH-", "confidence": 0.65,
        "cognates": [
            ("Greek", "πονέω", "to toil"), ("Sanskrit", "punāti", "to purify"),
        ],
        "evolutions": [("PIE", "*pewH-"), ("Albanian", "punoj")],
    },
    {
        "word": "qesh", "meaning": "to laugh, to smile", "pos": "verb",
        "root": "*kʷes-", "confidence": 0.60,
        "cognates": [
            ("Sanskrit", "hasati", "laughs"), ("Greek", "χαίρω", "to rejoice"),
        ],
        "evolutions": [("PIE", "*kʷes-"), ("Albanian", "qesh")],
    },
    {
        "word": "ndiej", "meaning": "to feel, to sense, to hear", "pos": "verb",
        "root": "*h₁ney-", "confidence": 0.65,
        "cognates": [
            ("Latin", "sentire", "to feel"), ("English", "sense", "sense"),
        ],
        "evolutions": [("PIE", "*h₁ney-"), ("Albanian", "ndiej")],
    },

    # ── Adjectives ─────────────────────────────────────────────
    {
        "word": "i gjallë", "meaning": "alive, living, vivid", "pos": "adjective",
        "root": "*gʷiH-", "confidence": 0.83,
        "cognates": [
            ("Greek", "βίος", "life"), ("Latin", "vivus", "alive"),
            ("English", "quick (archaic: alive)", "alive"),
        ],
        "evolutions": [("PIE", "*gʷiH-"), ("Proto-Albanian", "*dzel-"), ("Albanian", "gjallë")],
    },
    {
        "word": "i lehtë", "meaning": "light (in weight), easy", "pos": "adjective",
        "root": "*h₁lengʷʰ-", "confidence": 0.82,
        "cognates": [
            ("Latin", "levis", "light"), ("Greek", "ἐλαφρός", "light"),
            ("English", "light", "not heavy"), ("Sanskrit", "laghú", "light, swift"),
        ],
        "evolutions": [("PIE", "*h₁lengʷʰ-"), ("Proto-Albanian", "*legt-"), ("Albanian", "lehtë")],
    },
    {
        "word": "i plotë", "meaning": "full, complete, entire", "pos": "adjective",
        "root": "*pleh₁-", "confidence": 0.87,
        "cognates": [
            ("Latin", "plenus", "full"), ("Greek", "πλήρης", "full"),
            ("English", "full", "full"), ("Sanskrit", "pūrṇa", "full"),
        ],
        "evolutions": [("PIE", "*pleh₁-"), ("Proto-Albanian", "*plot-"), ("Albanian", "plotë")],
    },
    {
        "word": "i ëmbël", "meaning": "sweet, gentle", "pos": "adjective",
        "root": "*h₂melg-", "confidence": 0.72,
        "cognates": [
            ("Latin", "mel", "honey"), ("Greek", "μέλι", "honey"),
            ("English", "mellow", "ripe and sweet"),
        ],
        "evolutions": [("PIE", "*h₂melg-"), ("Proto-Albanian", "*embel-"), ("Albanian", "ëmbël")],
    },
    {
        "word": "i zgjuar", "meaning": "clever, awake, alert", "pos": "adjective",
        "root": "*gʷeyH-", "confidence": 0.65,
        "cognates": [
            ("Greek", "βίος", "life"), ("Latin", "vigilare", "to watch"),
        ],
        "evolutions": [("PIE", "*gʷeyH-"), ("Albanian", "zgjuar")],
    },
]


def normalize_word(word: str) -> str:
    return word.strip().lower()


def get_or_create_source(db, name: str, year: int, author: str, weight: float) -> Source:
    source = db.query(Source).filter(Source.name == name).first()
    if not source:
        source = Source(name=name, year=year, author=author, reliability_weight=weight)
        db.add(source)
        db.flush()
    return source


def get_or_create_word(db, word: str) -> Word:
    normalized = normalize_word(word)
    word_record = db.query(Word).filter(Word.normalized == normalized).first()
    if not word_record:
        word_record = Word(word=normalized, normalized=normalized, language="sq")
        db.add(word_record)
        db.flush()
    return word_record


def seed_sample_data(db):
    print("Seeding sample dataset...")

    orel = get_or_create_source(
        db, "A Dictionary of Inherited Lexicon", 1998, "Orel, Vladimir", 0.90
    )
    mann = get_or_create_source(
        db, "An Albanian Historical Grammar", 1977, "Mann, Stuart", 0.80
    )

    inserted = 0
    skipped = 0

    for item in SAMPLE_DATA:
        word_record = get_or_create_word(db, item["word"])

        # Check if entry already exists for this word+source
        existing = (
            db.query(Entry)
            .filter(Entry.word_id == word_record.id, Entry.source_id == orel.id)
            .first()
        )
        if existing:
            skipped += 1
            continue

        entry = Entry(
            word_id=word_record.id,
            source_id=orel.id,
            root=item.get("root"),
            meaning=item.get("meaning"),
            part_of_speech=item.get("pos"),
            notes=item.get("notes"),
            confidence=item.get("confidence", 0.7),
        )
        db.add(entry)
        db.flush()

        for lang, cog_word, cog_meaning in item.get("cognates", []):
            cog = Cognate(
                entry_id=entry.id,
                language=lang,
                word=cog_word,
                meaning=cog_meaning,
            )
            db.add(cog)

        for stage, form in item.get("evolutions", []):
            ev = Evolution(entry_id=entry.id, stage=stage, form=form)
            db.add(ev)

        inserted += 1

    db.commit()
    print(f"Done. Inserted: {inserted}, Skipped (already exist): {skipped}")


def parse_pdf(pdf_path: str, db, source: Source):
    """Parse Orel dictionary PDF and insert entries."""
    try:
        import pdfplumber
    except ImportError:
        print("Install pdfplumber: pip install pdfplumber")
        return

    print(f"Parsing PDF: {pdf_path}")

    # Patterns for Orel dictionary entries
    # Typical format: word "meaning" PIE root *...
    entry_pattern = re.compile(
        r'^([a-zA-ZëÇçëËàáâäèéêìíîòóôùúûñ\-]+)\s+'  # Albanian word
        r'["\u201c\u201d]([^"\u201d]+)["\u201d]\s*'       # "meaning"
        r'(?:.*?(\*[^\s,\.]+))?',                          # optional PIE root *...
        re.UNICODE
    )

    inserted = 0
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue

            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                m = entry_pattern.match(line)
                if m:
                    word_text = m.group(1).lower()
                    meaning = m.group(2).strip()
                    root = m.group(3) if m.group(3) else None

                    word_record = get_or_create_word(db, word_text)

                    existing = (
                        db.query(Entry)
                        .filter(Entry.word_id == word_record.id, Entry.source_id == source.id)
                        .first()
                    )
                    if existing:
                        continue

                    entry = Entry(
                        word_id=word_record.id,
                        source_id=source.id,
                        root=root,
                        meaning=meaning,
                        confidence=0.7,
                    )
                    db.add(entry)
                    inserted += 1

            if page_num % 10 == 0:
                print(f"  Processed page {page_num + 1}/{len(pdf.pages)}, entries so far: {inserted}")
                db.flush()

    db.commit()
    print(f"PDF parsing complete. Inserted {inserted} entries.")


def main():
    parser = argparse.ArgumentParser(description="Albanian PIE - Data Ingestion")
    parser.add_argument("--pdf", help="Path to Orel dictionary PDF")
    parser.add_argument("--seed", action="store_true", help="Insert built-in sample dataset")
    args = parser.parse_args()

    init_db()
    db = SessionLocal()

    try:
        if args.seed:
            seed_sample_data(db)
        elif args.pdf:
            orel = get_or_create_source(
                db, "A Dictionary of Inherited Lexicon", 1998, "Orel, Vladimir", 0.90
            )
            db.commit()
            parse_pdf(args.pdf, db, orel)
        else:
            print("Run with --seed to insert sample data, or --pdf <path> to parse a PDF.")
            print("Defaulting to --seed mode...")
            seed_sample_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()

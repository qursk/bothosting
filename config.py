# config.py
# ---------
# Zentrale Konfiguration für IDs, Dateipfade & Konstanten

# ---- CHANNEL IDs ----
ROLE_CHANNEL_ID = 1436384612476649493  # Embed mit Rollen-Roaster
ROLE_MESSAGE_ID = 1442644466438639777

WEEKLY_CHANNEL_ID = 1437497948236808307  # Wochenabgaben Kanal
WEEKLY_MESSAGE_ID = None

TEXT_CHANNEL_ID = 1442649242714767380  # Kanal für add/remove Kommandos

VOICE_DELETE_ID = 1442474461247963136  # Auto-Delete Voice Channel

# ---- DATEIPFADE ----
ROLES_FILE = "data/roles_data.json"
WEEKLY_FILE = "data/weekly_state.json"

# ---- ROLLEN-MAPPING ----
ROLE_MAPPING = {
    "12": "➜CEO",
    "11": "➜Stellvertretender CEO",
    "10": "➜Direktor",
    "9": "➜Operationsleiter",
    "8": "➜Koordinator",
    "7": "➜Trainingsleiter",
    "6": "➜Leitender Truppführer",
    "5": "➜Truppführer",
    "4": "➜Läufer",
    "3": "➜Anwärter",
    "2": "➜Rekrut",
    "1": "➜Lockvogel"
}

ROLE_IDS = {
    "12": 1436103567185416322,
    "11": 1436103577394221088,
    "10": 1436103578480803940,
    "9": 1436103580615708712,
    "8": 1436103581206839366,
    "7": 1436103581936910487,
    "6": 1436103583253659669,
    "5": 1436103583585276098,
    "4": 1436103583983730759,
    "3": 1436103584763744347,
    "2": 1436104038235246722,
    "1": 1436104041158676490
}

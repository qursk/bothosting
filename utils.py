# utils.py
import json
import os
import discord
from datetime import datetime


async def load_json(path: str, fallback: dict):
    if not os.path.exists(path):
        return fallback
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] load_json({path}): {e}")
        return fallback


async def save_json(path: str, data: dict):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"[INFO] Saved: {path}")
    except Exception as e:
        print(f"[ERROR] save_json({path}): {e}")


def embed(title, description="", color=discord.Color.blue()):
    em = discord.Embed(title=title,
                       description=description,
                       color=color,
                       timestamp=datetime.utcnow())
    return em

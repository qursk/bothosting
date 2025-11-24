import os
import discord
from discord.ext import commands
import webserver

# Allowed guild (server) ID
ALLOWED_GUILD_ID = 1436101095276675174
# Allowed channel ID
ALLOWED_CHANNEL_ID = 1442474461247963136
# Target message and channel for !add command
TARGET_MESSAGE_ID = 1442212690880626953
TARGET_CHANNEL_ID = 1436384612476649493

# Role mapping
ROLE_MAPPING = {
    "ceo": "CEO",
    "sv": "Stellvertretend",
    "dk": "Direktor",
    "opl": "Operationsleiter",
    "kd": "Koordinator",
    "tl": "Trainingsleiter",
    "ltf": "Leitender Truppenführer",
    "tf": "Truppenführer",
    "lf": "Läufer",
    "aw": "Anwärter",
    "rk": "Rekrut",
    "lv": "Lockvogel"
}

# Intents are required for certain events and functionalities
intents = discord.Intents.default()
intents.message_content = True  # Enable if you want to read message content
intents.members = True  # Enable to access guild members list

# Create bot instance with command prefix "!"
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user} (ID: {bot.user.id})")


# Decorator to block commands on other servers and channels
def guild_and_channel_only(ctx):
    return ctx.guild and ctx.guild.id == ALLOWED_GUILD_ID and ctx.channel.id == ALLOWED_CHANNEL_ID

@bot.command(name="hello")
@commands.check(guild_and_channel_only)
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}! I'm your bot running on **your server**.")

@hello.error
async def hello_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return  # Ignoriert, falls Command nicht im erlaubten Server/Kanal ausgeführt wird

# ...existing code...

@bot.command(name="add")
@commands.check(guild_and_channel_only)
async def add_member(ctx, *, args: str):
    """
    Fügt einen Benutzer zur Organisationsnachricht hinzu und vergibt die Discord-Rolle.
    Verwendung: !add <@User oder Name> <Rolle>
    """
    parts = args.strip().split()
    if len(parts) < 2:
        await ctx.send("❌ Verwendung: `!add <@User oder Name> <Rolle>`\nBeispiel: `!add @Max ceo` oder `!add Max Mustermann ceo`")
        return

    role_lower = parts[-1].lower()
    member_str = " ".join(parts[:-1])

    if role_lower not in ROLE_MAPPING:
        await ctx.send(f"❌ Ungültige Rolle! Verfügbare Rollen: {', '.join(ROLE_MAPPING.keys())}")
        return

    try:
        member = await commands.MemberConverter().convert(ctx, member_str)
    except Exception as e:
        await ctx.send(f"❌ Benutzer '{member_str}' nicht auf dem Server gefunden!")
        return

    try:
        target_channel = bot.get_channel(TARGET_CHANNEL_ID)
        if not target_channel:
            await ctx.send("❌ Zielkanal nicht gefunden!")
            return

        target_message = await target_channel.fetch_message(TARGET_MESSAGE_ID)
        if not target_message:
            await ctx.send("❌ Zielnachricht nicht gefunden!")
            return

        current_content = target_message.content or ""
        role_name = ROLE_MAPPING[role_lower]
        member_mention = member.mention

        # Wenn Rolle in Nachricht existiert => füge unter dieser Sektion hinzu (wenn nicht schon vorhanden)
        if role_name in current_content:
            lines = current_content.split('\n')
            new_lines = []
            i = 0
            added = False

            while i < len(lines):
                line = lines[i]
                new_lines.append(line)
                # Wenn wir auf die Rollen-Überschrift stoßen
                if line.strip().startswith("**") and role_name in line and not added:
                    i += 1
                    # Sammle die Sektion
                    section_lines = []
                while i < len(lines) and not (lines[i].strip().startswith("**")):
                    section_lines.append(lines[i])
                    i += 1

                    # Prüfe, ob der Member schon in der Sektion ist
                    if any(member_mention in s or member.display_name in s or member.name in s for s in section_lines):
                        await ctx.send(f"ℹ️ {member.display_name} ist bereits unter '{role_name}' eingetragen.")
                        return

                    # Füge den Member an den Anfang der Sektion
                    if section_lines and section_lines[0].strip() == "":
                        section_lines[0] = f"{member_mention}"
                    else:
                        section_lines.insert(0, f"{member_mention}")

                    new_lines.extend(section_lines)
                    added = True
                    continue
                else:
                    i += 1

            new_content = '\n'.join(new_lines)
        else:
            # Rolle existiert noch nicht in Nachricht -> neue Sektion anhängen
            new_content = f"{current_content}\n\n**{role_name}**\n{member_mention}"



        # Aktualisiere die Nachricht
        await target_message.edit(content=new_content)

        # Versuche, die Discord-Rolle zu finden oder zu erstellen und dem Member zu geben
        role_obj = discord.utils.get(ctx.guild.roles, name=role_name)
        if role_obj is None:
            try:
                role_obj = await ctx.guild.create_role(name=role_name, reason="Erstellt durch Bot für Organisationsrollen")
            except discord.Forbidden:
                await ctx.send(f"✅ {member.display_name} wurde unter '{role_name}' hinzugefügt! ⚠️ Rolle konnte nicht erstellt werden (fehlende Berechtigung).")
                return
            except Exception as e:
                await ctx.send(f"✅ {member.display_name} wurde unter '{role_name}' hinzugefügt! ⚠️ Fehler beim Erstellen der Rolle: {e}")
                return

        try:
            await member.add_roles(role_obj, reason="Rolle vergeben durch Bot via !add")
            await ctx.send(f"✅ {member.display_name} wurde unter '{role_name}' hinzugefügt und Rolle '{role_name}' vergeben.")
        except discord.Forbidden:
            await ctx.send(f"✅ {member.display_name} wurde unter '{role_name}' hinzugefügt! ⚠️ Rolle konnte nicht zugewiesen werden (fehlende Berechtigung).")
        except Exception as e:
            await ctx.send(f"✅ {member.display_name} wurde unter '{role_name}' hinzugefügt! ⚠️ Fehler beim Zuweisen der Rolle: {e}")

    except discord.Forbidden:
        await ctx.send("❌ Keine Berechtigung, die Nachricht zu bearbeiten!")
    except discord.NotFound:
        await ctx.send("❌ Nachricht oder Kanal nicht gefunden!")
    except Exception as e:
        await ctx.send(f"❌ Fehler: {str(e)}")
        print(f"Error in add command: {e}")

@add_member.error
async def add_member_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return  # Ignoriert, falls Command nicht im erlaubten Server/Kanal ausgeführt wird
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Verwendung: `!add <@User oder Name> <Rolle>`\nBeispiel: `!add @Max ceo` oder `!add Max Mustermann ceo`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Fehlerhafte Eingabe! Verwende: `!add <@User oder Name> <Rolle>`")

# Neues Kommando: remove
@bot.command(name="remove")
@commands.check(guild_and_channel_only)
async def remove_member(ctx, *, args: str):
    """
    Entfernt einen Benutzer aus der Organisationsnachricht und nimmt ihm die Discord-Rolle weg.
    Verwendung: !remove <@User oder Name> <Rolle>
    """
    parts = args.strip().split()
    if len(parts) < 2:
        await ctx.send("❌ Verwendung: `!remove <@User oder Name> <Rolle>`\nBeispiel: `!remove @Max ceo` oder `!remove Max Mustermann ceo`")
        return

    role_lower = parts[-1].lower()
    member_str = " ".join(parts[:-1])

    if role_lower not in ROLE_MAPPING:
        await ctx.send(f"❌ Ungültige Rolle! Verfügbare Rollen: {', '.join(ROLE_MAPPING.keys())}")
        return

    try:
        member = await commands.MemberConverter().convert(ctx, member_str)
    except Exception as e:
        await ctx.send(f"❌ Benutzer '{member_str}' nicht auf dem Server gefunden!")
        return

    try:
        target_channel = bot.get_channel(TARGET_CHANNEL_ID)
        if not target_channel:
            await ctx.send("❌ Zielkanal nicht gefunden!")
            return

        target_message = await target_channel.fetch_message(TARGET_MESSAGE_ID)
        if not target_message:
            await ctx.send("❌ Zielnachricht nicht gefunden!")
            return

        current_content = target_message.content or ""
        role_name = ROLE_MAPPING[role_lower]
        member_mention = member.mention
        member_names = {member_mention, member.display_name, member.name}

        lines = current_content.split('\n')
        new_lines = []
        i = 0
        removed = False

        while i < len(lines):
            line = lines[i]
            # Wenn wir auf die Role-Überschrift stoßen
            if line.strip().startswith("**") and role_name in line:
                new_lines.append(line)
                i += 1
                # Sammle alle Zeilen der Rolle (bis nächste Rolle-Überschrift oder EOF)
                section_lines = []
                while i < len(lines) and not (lines[i].strip().startswith("**")):
                    section_lines.append(lines[i])
                    i += 1

                # Filtere die Zeilen: entferne Zeilen, die den Benutzer enthalten
                filtered_section = []
                for sline in section_lines:
                    if any(name in sline for name in member_names):
                        removed = True
                        continue
                    filtered_section.append(sline)

                # Wenn nach Entfernen keine Einträge mehr in der Sektion sind (nur leere/whitespace), entferne auch die Überschrift
                if any(l.strip() for l in filtered_section):
                    new_lines.extend(filtered_section)
                else:
                    # entferne die Überschrift indem wir die zuvor hinzugefügte Zeile entfernen
                    new_lines.pop()
                continue
            else:
                new_lines.append(line)
                i += 1

        if not removed:
            await ctx.send(f"❌ {member.display_name} wurde unter '{role_name}' nicht gefunden.")
            return

        new_content = '\n'.join(new_lines).strip()
        if new_content == "":
            new_content = " "  # Discord erlaubt keine komplett leere Nachricht beim Editieren

        await target_message.edit(content=new_content)

        # Versuche, die Discord-Rolle zu finden und vom Member zu entfernen
        role_obj = discord.utils.get(ctx.guild.roles, name=role_name)
        role_msg = ""
        if role_obj:
            try:
                await member.remove_roles(role_obj, reason="Rolle entfernt durch Bot via !remove")
                role_msg = f" Rolle '{role_name}' wurde entfernt."
            except discord.Forbidden:
                role_msg = f" ⚠️ Nachricht aktualisiert, konnte Rolle '{role_name}' nicht entfernen (fehlende Berechtigung)."
            except Exception as e:
                role_msg = f" ⚠️ Nachricht aktualisiert, Fehler beim Entfernen der Rolle: {e}"
        else:
            role_msg = f" ⚠️ Rolle '{role_name}' auf dem Server nicht gefunden."

        await ctx.send(f"✅ {member.display_name} wurde aus '{role_name}' entfernt!{role_msg}")

    except discord.Forbidden:
        await ctx.send("❌ Keine Berechtigung, die Nachricht zu bearbeiten!")
    except discord.NotFound:
        await ctx.send("❌ Nachricht oder Kanal nicht gefunden!")
    except Exception as e:
        await ctx.send(f"❌ Fehler: {str(e)}")
        print(f"Error in remove command: {e}")

@remove_member.error
async def remove_member_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Verwendung: `!remove <@User oder Name> <Rolle>`\nBeispiel: `!remove @Max ceo` oder `!remove Max Mustermann ceo`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Fehlerhafte Eingabe! Verwende: `!remove <@User oder Name> <Rolle>`")

# ...existing code...

if __name__ == "__main__":
    webserver.keep_alive()
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN environment variable not set")
    else:
        bot.run(TOKEN)

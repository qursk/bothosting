# weekly.py
import discord
from discord.ext import commands
import datetime
from config import WEEKLY_FILE, WEEKLY_CHANNEL_ID, WEEKLY_MESSAGE_ID
from utils import load_json, save_json, embed


class WeeklyCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.state = {"current_message": WEEKLY_MESSAGE_ID, "amounts": {}}

    async def load(self):
        default = {"current_message": WEEKLY_MESSAGE_ID, "amounts": {}}
        self.state = await load_json(WEEKLY_FILE, default)
        print("[WEEKLY] Loaded weekly_state")

    async def save(self):
        await save_json(WEEKLY_FILE, self.state)

    def current_week(self):
        return datetime.datetime.utcnow().isocalendar()[1]

    def build_embed(self):
        week = self.current_week()
        amounts = self.state.get("amounts", {})
        lines = [f"<@{mid}>: {amount} €" for mid, amount in amounts.items()]
        description = "\n".join(lines) if lines else "Keine Spieler."
        return embed(f"Liste der Wochenabgaben — KW {week}", description,
                     discord.Color.green())

    async def update_message(self, guild):
        channel = guild.get_channel(WEEKLY_CHANNEL_ID)
        msg_id = self.state.get("current_message")
        msg = None

        if msg_id:
            try:
                msg = await channel.fetch_message(msg_id)
            except:
                msg = None

        em = self.build_embed()

        if msg:
            await msg.edit(embed=em)
        else:
            new_msg = await channel.send(embed=em)
            self.state["current_message"] = new_msg.id
            await self.save()

    # -------------------------------------------------
    # Neue Liste erstellen + alle Beträge auf 0 setzen
    # -------------------------------------------------
    @commands.command()
    async def new_wa_msg(self, ctx):
        """Erstellt eine neue Wochenliste mit allen Beträgen = 0."""
        if ctx.channel.id != 1442649242714767380:
            return await ctx.send(
                f"Nur im Kanal <#{1442649242714767380}> erlaubt!"
            )

        channel = ctx.guild.get_channel(WEEKLY_CHANNEL_ID)

        # Spieler behalten, aber alle Beträge zurücksetzen
        old_amounts = self.state.get("amounts", {})
        new_amounts = {mid: 0 for mid in old_amounts.keys()}
        self.state["amounts"] = new_amounts

        # Neue Nachricht erzeugen
        em = self.build_embed()
        new_msg = await channel.send(embed=em)

        # Neue Message-ID setzen → ab jetzt die aktuelle Liste
        self.state["current_message"] = new_msg.id
        await self.save()

        await ctx.send(
            f"✔️ Neue Wochenliste wurde erstellt. "
            f"Alle Beträge wurden auf 0 gesetzt."
        )

    # -----------------------------
    # Standardbefehle
    # -----------------------------
    @commands.command()
    async def add_wa(self, ctx, member: discord.Member, amount: int):
        if ctx.channel.id != 1442649242714767380:
            return await ctx.send(
                f"Nur im Kanal <#{1442649242714767380}> erlaubt!")
        mid = str(member.id)
        self.state["amounts"][mid] = self.state["amounts"].get(mid, 0) + amount
        await self.update_message(ctx.guild)
        await self.save()
        await ctx.send(f"✔️ {amount} € zu {member.mention} hinzugefügt.")

    @commands.command()
    async def rm_wa(self, ctx, member: discord.Member, amount: int):
        if ctx.channel.id != 1442649242714767380:
            return await ctx.send(
                f"Nur im Kanal <#{1442649242714767380}> erlaubt!")
        mid = str(member.id)
        old = self.state["amounts"].get(mid, 0)
        self.state["amounts"][mid] = max(0, old - amount)
        await self.update_message(ctx.guild)
        await self.save()
        await ctx.send(f"✔️ {amount} € bei {member.mention} entfernt.")

# roles.py
import discord
from discord.ext import commands
from config import *
from utils import load_json, save_json, embed
import asyncio

role_lock = asyncio.Lock()
roles_data = {}  # Internal cache
weekly_cog = None  # Wird beim Setup gesetzt


def member_id_to_mention(mid: int):
    return f"<@{mid}>"


def build_role_embed():
    total = sum(len(members) for members in roles_data.values())
    em = embed("Secret Mitglieder Roaster", f"Aktive Mitglieder: **{total}**")
    for role_name, members in roles_data.items():
        value = "\n".join(member_id_to_mention(mid)
                          for mid in members) if members else "Frei"
        em.add_field(name=role_name, value=value, inline=False)
    return em


class RolesCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def load(self):
        global roles_data
        default = {role: [] for role in ROLE_MAPPING.values()}
        roles_data = await load_json(ROLES_FILE, default)
        print("[ROLES] Loaded roles_data")

        global weekly_cog
        weekly_cog = self.bot.get_cog("WeeklyCog")

    async def save(self):
        await save_json(ROLES_FILE, roles_data)

    @commands.command()
    async def show_roles(self, ctx):
        chunks = [
            f"**{role}:** " +
            ", ".join(member_id_to_mention(m) for m in members)
            for role, members in roles_data.items()
        ]
        await ctx.send("\n".join(chunks))

    @commands.command()
    async def add(self, ctx, member: discord.Member, role_key: str):
        if ctx.channel.id != TEXT_CHANNEL_ID:
            return await ctx.send(f"Nur im Kanal <#{TEXT_CHANNEL_ID}> erlaubt."
                                  )
        async with role_lock:
            role_key = role_key.lower()
            if role_key not in ROLE_MAPPING:
                return await ctx.send("Ungültige Rolle!")

            role_name = ROLE_MAPPING[role_key]
            role_id = ROLE_IDS[role_key]
            mid = member.id

            if mid in roles_data[role_name]:
                return await ctx.send("Member ist bereits eingetragen.")

            roles_data[role_name].append(mid)

            # Discord role
            r = ctx.guild.get_role(role_id)
            if r:
                try:
                    await member.add_roles(r)
                except Exception as e:
                    print(f"[Roles] Fehler add_roles: {e}")

            # Weekly-Liste updaten
            if weekly_cog:
                mid_str = str(member.id)
                weekly_cog.state["amounts"].setdefault(mid_str, 0)
                await weekly_cog.update_message(ctx.guild)
                await weekly_cog.save()

            # Embed updaten
            channel = ctx.guild.get_channel(ROLE_CHANNEL_ID)
            msg = await channel.fetch_message(ROLE_MESSAGE_ID)
            await msg.edit(embed=build_role_embed())
            await self.save()
            await ctx.send(
                f"✅ {member.mention} wurde zu **{role_name}** hinzugefügt!")

    @commands.command()
    async def remove(self, ctx, member: discord.Member, role_key: str):
        if ctx.channel.id != TEXT_CHANNEL_ID:
            return await ctx.send(f"Nur im Kanal <#{TEXT_CHANNEL_ID}> erlaubt."
                                  )
        async with role_lock:
            role_key = role_key.lower()
            if role_key not in ROLE_MAPPING:
                return await ctx.send("Ungültige Rolle!")

            role_name = ROLE_MAPPING[role_key]
            role_id = ROLE_IDS[role_key]
            mid = member.id

            if mid not in roles_data[role_name]:
                return await ctx.send("Member ist nicht eingetragen.")

            roles_data[role_name].remove(mid)

            # Discord role entfernen
            r = ctx.guild.get_role(role_id)
            if r:
                try:
                    await member.remove_roles(r)
                except Exception as e:
                    print(f"[Roles] Fehler remove_roles: {e}")

            # Weekly-Liste updaten: nur löschen, wenn Betrag 0
            if weekly_cog:
                mid_str = str(member.id)
                if weekly_cog.state["amounts"].get(mid_str, 0) == 0:
                    weekly_cog.state["amounts"].pop(mid_str, None)
                    await weekly_cog.update_message(ctx.guild)
                    await weekly_cog.save()

            # Embed updaten
            channel = ctx.guild.get_channel(ROLE_CHANNEL_ID)
            msg = await channel.fetch_message(ROLE_MESSAGE_ID)
            await msg.edit(embed=build_role_embed())
            await self.save()
            await ctx.send(
                f"🗑️ {member.mention} wurde aus **{role_name}** entfernt!")

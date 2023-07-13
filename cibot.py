import discord
from discord.ext import commands
from discord.ext.commands import Context, Greedy
from discord import app_commands
from typing import Optional, Literal
import uuid
import sqlite3
import random
import requests
import time
import random
from datetime import datetime
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="$", intents=intents)
tree = bot.tree

@tree.command(description="Lookup an eve character.")
@app_commands.describe(character_id="Lookup eve character.")
async def lookup(interaction: discord.Interaction, character_id: str = "character_id"):
    url = f"https://esi.evetech.net/latest/characters/{character_id}/"
    response = requests.get(url)
    zkill_url = f"https://zkillboard.com/api/stats/characterID/{character_id}/"
    zkill_response = requests.get(zkill_url)
    if zkill_response.status_code == 200:
        zkill_data = zkill_response.json()
        shipsLost = zkill_data["shipsLost"]
        shipsDestroyed = zkill_data["shipsDestroyed"]
        totalShips = shipsLost + shipsDestroyed
        if (totalShips > 30):
            flag = "\n**Recruitable**: ✅"
        else:
            flag = "\n**Recruitable**: ❌"
        shipsLoststr = str(shipsLost)
        shipsDestroyedstr = str(shipsDestroyed)
        zkill_ratio = "\n" + "**Kills**: " + shipsDestroyedstr + " **Losses**: " + shipsLoststr
    else:
        zkill_ratio = ""
    if response.status_code == 200:
        data = response.json()
        blacklist_array = ["Iedan","Dran Arcana"]
        if data["name"] in blacklist_array:
            is_blacklisted = "\n**Blacklisted**: ✅"
        if is_blacklisted == "\n**Blacklisted**: ✅":
            flag = "\n**Recruitable**: ❌"
        # Corp data
        corp_id = data["corporation_id"]
        url_corp = f"https://esi.evetech.net/latest/corporations/{corp_id}/"
        response_corp = requests.get(url_corp)
        if response_corp.status_code == 200:
            corp_data = response_corp.json()
            corp_name = corp_data["name"]
        else:
            corp_name = "Error!"
        # Alliance_data
        if "alliance_id" in corp_data:
            alliance_id = corp_data["alliance_id"]
            url_ally = f"https://esi.evetech.net/latest/alliances/{alliance_id}/"
            response_ally = requests.get(url_ally)
            if response_ally.status_code == 200:
                ally_data = response_ally.json()
                ally_name = ally_data["name"]
            else:
                ally_name = "Error!"
        else:
            ally_name = "No Alliance"
        # Convert the timestamp to the desired format
        birthday_timestamp = data["birthday"]
        birthday_datetime = datetime.strptime(birthday_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        formatted_birthday = birthday_datetime.strftime("%Y-%m-%d %H:%M:%S")
        if len(data) > 0:
            await interaction.response.send_message(
                "**" + data["name"] + "**: " + formatted_birthday + " (" + corp_name + " in " + ally_name + ")" + zkill_ratio + is_blacklisted + flag,
                ephemeral=True,
            )
        else:
            await interaction.response.send_message("No character found", ephemeral=True)
    else:
        await interaction.response.send_message("Error!", ephemeral=True)
    
        
@tree.command(description="Copies permissions from one channel to another.")
async def copy_permissions(interaction: discord.Interaction,
                           source_channel: discord.TextChannel,
                           target_channel: discord.TextChannel):

    await interaction.response.defer()

    source_overwrites = source_channel.overwrites

    for target, overwrite in source_overwrites.items():
        if isinstance(target, discord.Role):
            role = source_channel.guild.get_role(target.id)
            await target_channel.set_permissions(role, overwrite=overwrite)
        elif isinstance(target, discord.Member):
            member = source_channel.guild.get_member(target.id)
            await target_channel.set_permissions(member, overwrite=overwrite)

    await interaction.followup.send(f"Permissions copied from {source_channel.name} to {target_channel.name}.", ephemeral=True)
    
@tree.command(description="Checks for relay.")
@app_commands.describe(text="Burns hostile relay.")
async def burnrelay(interaction:discord.Interaction, text: str = "Burns Relays!"):
    log_channel_id = 1128446631067525130
    await interaction.response.send_message("Beginning cycles through...", ephemeral=True)
    role = discord.utils.get(interaction.guild.roles, name="Member")
    for member in role.members:
        random_number = random.randint(1000, 9999)
        random_number_str = str(random_number)
        await interaction.channel.set_permissions(member, view_channel=True)
        await interaction.channel.send(f"{member.display_name} ({member.id})." + random_number_str)
        await bot.get_channel(log_channel_id).send(f"**Log:** {member.display_name} ({member.id})." + random_number_str)
        await interaction.channel.set_permissions(member, overwrite=None)
        await interaction.channel.purge(limit=1)
    await interaction.followup.send("CI Bot task complete.", ephemeral=True)

@tree.command(description="Splits a role in half.")
async def split_role(interaction: discord.Interaction,
                     role_name_1: str,
                     role_name_2: str,
                     selected_role: discord.Role):

    await interaction.response.defer()
    new_role_1 = await interaction.guild.create_role(name=role_name_1)
    new_role_2 = await interaction.guild.create_role(name=role_name_2)

    members = selected_role.members
    num_members = len(members)

    num_members_1 = num_members // 2
    num_members_2 = num_members - num_members_1

    members_1 = members[:num_members_1]
    members_2 = members[num_members_1:]

    for member in members_1:
        await member.add_roles(new_role_1)

    for member in members_2:
        await member.add_roles(new_role_2)

    await interaction.followup.send(f"Created roles {role_name_1} and {role_name_2}, and split {num_members} members of {selected_role.name} between them.", ephemeral=True)

@tree.command(description="Lists users with a certain ticker in their nickname.")
async def search(interaction: discord.Interaction, ticker: str):
    await interaction.response.send_message("Query Complete! Results posted below.", ephemeral=True)
    members = interaction.guild.members
    matching_members = []
    for member in members:
        if ticker in member.display_name:
            matching_members.append(member)
    if not matching_members:
        response_text = f"No members found with '{ticker}' in their nickname."
    else:
        response_text = f"Members with '{ticker}' in their nickname:\n"
        for member in matching_members:
            roles = [role.name for role in member.roles]
            if "Corporation Leadership" in roles or "Alliance Execs" in roles:
                bold_name = f"**{member.display_name}**"
            else:
                bold_name = member.display_name

            if any(role in roles for role in ["CAP-Faxes", "CAP-Carriers", "CAP-Dreads"]):
                cap_suffix = "(cap)"
            else:
                cap_suffix = ""

            if any(role in roles for role in ["CAP-Titans", "CAP-Supers"]):
                scap_suffix = "**(scap)**"
            else:
                scap_suffix = ""

            if cap_suffix and scap_suffix:
                bold_name += " **(cap/scap)**"
            elif cap_suffix:
                bold_name += " **(cap)**"
            elif scap_suffix:
                bold_name += " **(scap)**"

            response_text += f"{bold_name}\n"

    channel = interaction.channel
    if len(response_text) <= 2000:
        await channel.send(response_text)
    else:
        response_list = response_text.split("\n")
        current_message = ""
        for response in response_list:
            if len(current_message) + len(response) + 1 <= 2000:
                current_message += response + "\n"
            else:
                await channel.send(current_message)
                current_message = response + "\n"
        if current_message != "":
            await channel.send(current_message)
    
@bot.command()
@commands.has_any_role("Admin")
async def sync(
  ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

target_user_id = 1073054731557150800 # Replace with your user ID
group_names = {"CAPS - Capitals": "capital group", "CAPS - Supers": "super group"}

@bot.event
async def on_member_remove(member):
    roles = [(role.mention, role.name) for role in member.roles if role.name in group_names.keys()]
    if roles:
        user = await bot.fetch_user(target_user_id)
        group_name = group_names[roles[0][1]]
        role_mentions = ", ".join([role[0] for role in roles])
        message = f"{member.display_name} (ID: <@{member.id}>) has left the server and was in the {group_name}."
        await user.send(message)
        
@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        target_user = await bot.fetch_user(target_user_id)
        
        # Relay text content
        await target_user.send(f"**{message.author}**: {message.content}")
        
        # Relay image attachments
        if message.attachments:
            for attachment in message.attachments:
                await target_user.send(attachment.url)
    
@bot.event
async def on_ready():
    await tree.sync() # Uncomment if you want global commands.
    print("Ready!")
bot.run('MTEyODEwNzIwMTI0NDk1NDY3NA.Ge7Ndp.s_asDVkFZuuwOZTl0N9PdD2wHfZR8Elxw3WdXA')
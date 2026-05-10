import discord
from discord.ext import commands
import random

import os
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------
# COIN STORAGE
# -----------------------
coins = {}

# -----------------------
# ROLE SHOP
# -----------------------
roles_shop = {
    "blox": {
        "role_id": 1502647506801000500,
        "cost": 200
    },

    "sailor": {
        "role_id": 1502647995798261800,
        "cost": 350
    },

    "wealthy": {
        "role_id": 1502648468664225792,
        "cost": 700
    }
}


# -----------------------
# BOT READY
# -----------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# -----------------------
# MESSAGE EVENT
# -----------------------
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    user_id = message.author.id

    # GIVE COINS
    coins[user_id] = coins.get(user_id, 0) + random.randint(3, 8)

    await bot.process_commands(message)


# -----------------------
# COINS COMMAND
# -----------------------
@bot.command()
async def coinscmd(ctx):

    amount = coins.get(ctx.author.id, 0)

    await ctx.send(f"💰 You have {amount} coins")


# -----------------------
# LOCKDOWN
# -----------------------
@bot.command()
async def lockdown(ctx):

    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Admin only.")
        return

    for channel in ctx.guild.text_channels:
        try:
            await channel.set_permissions(
                ctx.guild.default_role,
                send_messages=False
            )
        except:
            pass

    await ctx.send("🔒 Server locked down.")


# -----------------------
# REMOVE LOCKDOWN
# -----------------------
@bot.command()
async def lifted(ctx):

    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Admin only.")
        return

    for channel in ctx.guild.text_channels:
        try:
            await channel.set_permissions(
                ctx.guild.default_role,
                send_messages=True
            )
        except:
            pass

    await ctx.send("🔓 Lockdown removed.")


# -----------------------
# SHOP VIEW
# -----------------------
class ShopView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    # -------------------
    # BLOX FRUITS
    # -------------------
    @discord.ui.button(
        label="🥭 Blox Fruits Fan (200)",
        style=discord.ButtonStyle.success
    )
    async def blox_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        user_id = interaction.user.id
        cost = 200

        if coins.get(user_id, 0) < cost:

            await interaction.response.send_message(
                "❌ Not enough coins.",
                ephemeral=True
            )
            return

        role = interaction.guild.get_role(
            1502647506801000500
        )

        if role:
            await interaction.user.add_roles(role)

        coins[user_id] -= cost

        await interaction.response.send_message(
            "✅ Bought Blox Fruits Fan role.",
            ephemeral=True
        )

    # -------------------
    # SAILOR PIECE
    # -------------------
    @discord.ui.button(
        label="🚢 Sailor Piece Fan (350)",
        style=discord.ButtonStyle.primary
    )
    async def sailor_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        user_id = interaction.user.id
        cost = 350

        if coins.get(user_id, 0) < cost:

            await interaction.response.send_message(
                "❌ Not enough coins.",
                ephemeral=True
            )
            return

        role = interaction.guild.get_role(
            1502647995798261800
        )

        if role:
            await interaction.user.add_roles(role)

        coins[user_id] -= cost

        await interaction.response.send_message(
            "✅ Bought Sailor Piece Fan role.",
            ephemeral=True
        )

    # -------------------
    # WEALTHY
    # -------------------
    @discord.ui.button(
        label="💸 The Wealthy (700)",
        style=discord.ButtonStyle.secondary
    )
    async def wealthy_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        user_id = interaction.user.id
        cost = 700

        if coins.get(user_id, 0) < cost:

            await interaction.response.send_message(
                "❌ Not enough coins.",
                ephemeral=True
            )
            return

        role = interaction.guild.get_role(
            1502648468664225792
        )

        if role:
            await interaction.user.add_roles(role)

        coins[user_id] -= cost

        await interaction.response.send_message(
            "✅ Bought The Wealthy role.",
            ephemeral=True
        )


# -----------------------
# CREATE SHOP
# -----------------------
@bot.command()
async def shopcreate(ctx):

    embed = discord.Embed(
        title="🥭 Welcome to Blox Fruits / Sailor Piece Trading Shop!",
        description="Talk in chat to earn coins and buy exclusive roles.",
        color=discord.Color.green()
    )

    embed.add_field(
        name="🥭 Blox Fruits Fan",
        value="200 coins",
        inline=False
    )

    embed.add_field(
        name="🚢 Sailor Piece Fan",
        value="350 coins",
        inline=False
    )

    embed.add_field(
        name="💸 The Wealthy",
        value="700 coins",
        inline=False
    )

    await ctx.send(
        embed=embed,
        view=ShopView()
    )


# -----------------------
# RUN BOT
# -----------------------
bot.run(TOKEN)
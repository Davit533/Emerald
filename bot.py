import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import random
import os

# ==================================================
# KEEP ALIVE FOR RENDER
# ==================================================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is online"

def run_web():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    thread = Thread(target=run_web)
    thread.daemon = True
    thread.start()

# ==================================================
# TOKEN
# ==================================================
TOKEN = os.getenv("TOKEN")

# ==================================================
# INTENTS
# ==================================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# ==================================================
# BOT
# ==================================================
bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ==================================================
# DATA
# ==================================================
coins = {}

SHOP = {
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

# ==================================================
# LOCKDOWN TEXT
# ==================================================
LOCKDOWN_MSG = """
---------------------------------------
⚠️ THIS SERVER IS UNDER LOCKDOWN ⚠️
An admin has issued this lockdown
due to suspicious activity.
Please contact administrators.
---------------------------------------
"""

LIFTED_MSG = """
---------------------------------------
✅ LOCKDOWN HAS BEEN LIFTED ✅
Server restrictions were removed.
---------------------------------------
"""

# ==================================================
# READY EVENT
# ==================================================
@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()

        print(f"✅ Synced {len(synced)} slash commands")

    except Exception as e:
        print(f"❌ Sync Error: {e}")

    print(f"✅ Logged in as {bot.user}")

# ==================================================
# MESSAGE EVENT
# ==================================================
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    user_id = message.author.id

    current = coins.get(user_id, 0)

    coins[user_id] = current + random.randint(3, 8)

    await bot.process_commands(message)

# ==================================================
# /coins2
# IMPORTANT:
# renamed to force Discord refresh
# ==================================================
@bot.tree.command(
    name="coins2",
    description="Check your coins"
)
async def coins2(interaction: discord.Interaction):

    amount = coins.get(interaction.user.id, 0)

    await interaction.response.send_message(
        f"💰 You have {amount} coins"
    )

# ==================================================
# SHOP VIEW
# ==================================================
class ShopView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    async def buy_role(
        self,
        interaction,
        role_id,
        cost,
        role_name
    ):

        user_id = interaction.user.id

        balance = coins.get(user_id, 0)

        if balance < cost:

            await interaction.response.send_message(
                "❌ Not enough coins.",
                ephemeral=True
            )

            return

        role = interaction.guild.get_role(role_id)

        if role is None:

            await interaction.response.send_message(
                "❌ Role not found.",
                ephemeral=True
            )

            return

        await interaction.user.add_roles(role)

        coins[user_id] -= cost

        await interaction.response.send_message(
            f"✅ Bought {role_name}",
            ephemeral=True
        )

    @discord.ui.button(
        label="🥭 Blox (200)",
        style=discord.ButtonStyle.success
    )
    async def blox_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.buy_role(
            interaction,
            SHOP["blox"]["role_id"],
            SHOP["blox"]["cost"],
            "Blox Fruits Fan"
        )

    @discord.ui.button(
        label="🚢 Sailor (350)",
        style=discord.ButtonStyle.primary
    )
    async def sailor_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.buy_role(
            interaction,
            SHOP["sailor"]["role_id"],
            SHOP["sailor"]["cost"],
            "Sailor Piece Fan"
        )

    @discord.ui.button(
        label="💸 Wealthy (700)",
        style=discord.ButtonStyle.secondary
    )
    async def wealthy_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.buy_role(
            interaction,
            SHOP["wealthy"]["role_id"],
            SHOP["wealthy"]["cost"],
            "The Wealthy"
        )

# ==================================================
# /shop2
# renamed to refresh Discord cache
# ==================================================
@bot.tree.command(
    name="shop2",
    description="Open role shop"
)
async def shop2(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🥭 Trading Shop",
        description="Earn coins by chatting!",
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

    await interaction.response.send_message(
        embed=embed,
        view=ShopView()
    )

# ==================================================
# /lockdown2
# ==================================================
@bot.tree.command(
    name="lockdown2",
    description="Lock the server"
)
async def lockdown2(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "❌ Admin only.",
            ephemeral=True
        )

        return

    await interaction.response.defer()

    for channel in interaction.guild.text_channels:

        try:

            await channel.send(LOCKDOWN_MSG)

            await channel.set_permissions(
                interaction.guild.default_role,
                send_messages=False
            )

        except:
            pass

    await interaction.followup.send(
        "🔒 Server locked down."
    )

# ==================================================
# /lifted2
# ==================================================
@bot.tree.command(
    name="lifted2",
    description="Remove lockdown"
)
async def lifted2(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "❌ Admin only.",
            ephemeral=True
        )

        return

    await interaction.response.defer()

    for channel in interaction.guild.text_channels:

        try:

            await channel.set_permissions(
                interaction.guild.default_role,
                send_messages=True
            )

            await channel.send(LIFTED_MSG)

        except:
            pass

    await interaction.followup.send(
        "🔓 Lockdown removed."
    )

# ==================================================
# START BOT
# ==================================================
keep_alive()
bot.run(TOKEN)

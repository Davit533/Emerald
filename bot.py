import discord
from discord.ext import commands
import random
import os

# -----------------------
# KEEP ALIVE (Render)
# -----------------------
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# -----------------------
# TOKEN
# -----------------------
TOKEN = os.getenv("TOKEN")

# -----------------------
# INTENTS
# -----------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------
# DATA
# -----------------------
coins = {}

# -----------------------
# SHOP DATA
# -----------------------
SHOP = {
    "blox": {"role_id": 1502647506801000500, "cost": 200},
    "sailor": {"role_id": 1502647995798261800, "cost": 350},
    "wealthy": {"role_id": 1502648468664225792, "cost": 700},
}

# -----------------------
# MESSAGES
# -----------------------
LOCKDOWN_MSG = """
-----------------------------
⚠️ THIS SERVER IS UNDER LOCKDOWN ⚠️
An admin has issued a lockdown due to suspicious activity.
Please do not panic and contact administrators.
-----------------------------
"""

LIFTED_MSG = """
----------------------------
✅ LOCKDOWN LIFTED
The server is now back to normal.
----------------------------
"""

# -----------------------
# READY
# -----------------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# -----------------------
# COIN SYSTEM
# -----------------------
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    coins[message.author.id] = coins.get(message.author.id, 0) + random.randint(3, 8)

# -----------------------
# /COINS
# -----------------------
@bot.tree.command(name="coins", description="Check your coins")
async def coinscmd(interaction: discord.Interaction):

    amount = coins.get(interaction.user.id, 0)

    await interaction.response.send_message(f"💰 You have {amount} coins")

# -----------------------
# /SHOP
# -----------------------
class ShopView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    async def buy(self, interaction, role_id, cost):

        if coins.get(interaction.user.id, 0) < cost:
            return False

        role = interaction.guild.get_role(role_id)

        if role:
            await interaction.user.add_roles(role)

        coins[interaction.user.id] -= cost
        return True

    @discord.ui.button(label="🥭 Blox (200)", style=discord.ButtonStyle.green)
    async def blox(self, interaction, button):

        await interaction.response.defer(ephemeral=True)

        ok = await self.buy(interaction, SHOP["blox"]["role_id"], SHOP["blox"]["cost"])

        if not ok:
            await interaction.followup.send("❌ Not enough coins")
            return

        await interaction.followup.send("✅ Bought Blox role")

    @discord.ui.button(label="🚢 Sailor (350)", style=discord.ButtonStyle.blurple)
    async def sailor(self, interaction, button):

        await interaction.response.defer(ephemeral=True)

        ok = await self.buy(interaction, SHOP["sailor"]["role_id"], SHOP["sailor"]["cost"])

        if not ok:
            await interaction.followup.send("❌ Not enough coins")
            return

        await interaction.followup.send("✅ Bought Sailor role")

    @discord.ui.button(label="💸 Wealthy (700)", style=discord.ButtonStyle.grey)
    async def wealthy(self, interaction, button):

        await interaction.response.defer(ephemeral=True)

        ok = await self.buy(interaction, SHOP["wealthy"]["role_id"], SHOP["wealthy"]["cost"])

        if not ok:
            await interaction.followup.send("❌ Not enough coins")
            return

        await interaction.followup.send("✅ Bought Wealthy role")

@bot.tree.command(name="shop", description="Open shop")
async def shop(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🥭 Shop",
        description="Earn coins by chatting!",
        color=discord.Color.green()
    )

    embed.add_field(name="Blox", value="200 coins", inline=False)
    embed.add_field(name="Sailor", value="350 coins", inline=False)
    embed.add_field(name="Wealthy", value="700 coins", inline=False)

    await interaction.response.send_message(embed=embed, view=ShopView())

# -----------------------
# /LOCKDOWN
# -----------------------
@bot.tree.command(name="lockdown", description="Lock server")
async def lockdown(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only")
        return

    await interaction.response.defer()

    for channel in interaction.guild.text_channels:
        try:
            await channel.send(LOCKDOWN_MSG)
            await channel.set_permissions(interaction.guild.default_role, send_messages=False)
        except:
            pass

    await interaction.followup.send("🔒 Locked down")

# -----------------------
# /LIFTED
# -----------------------
@bot.tree.command(name="lifted", description="Unlock server")
async def lifted(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only")
        return

    await interaction.response.defer()

    for channel in interaction.guild.text_channels:
        try:
            await channel.send(LIFTED_MSG)
            await channel.set_permissions(interaction.guild.default_role, send_messages=True)
        except:
            pass

    await interaction.followup.send("🔓 Unlocked")

# -----------------------
# START BOT
# -----------------------
keep_alive()
bot.run(TOKEN)

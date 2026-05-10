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
# COINS SYSTEM
# -----------------------
coins = {}

# -----------------------
# SHOP ROLES
# -----------------------
roles_shop = {
    "blox": {"role_id": 1502647506801000500, "cost": 200},
    "sailor": {"role_id": 1502647995798261800, "cost": 350},
    "wealthy": {"role_id": 1502648468664225792, "cost": 700},
}

# -----------------------
# LOCKDOWN MESSAGES
# -----------------------
LOCKDOWN_MSG = """
---------------------------------------
⚠️ THIS SERVER IS UNDER LOCKDOWN ⚠️
An admin user has issued this lockdown
due to suspicious activity in the server
Please do not panic and for more info
contact your server's **Administrators!**
---------------------------------------
"""

LIFTED_MSG = """
---------------------------------------
✅ LOCKDOWN HAS BEEN LIFTED ✅
The server is now back to normal
You may continue chatting freely
Thank you for your patience
---------------------------------------
"""

# -----------------------
# READY
# -----------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# -----------------------
# COIN EARNING
# -----------------------
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    user_id = message.author.id
    coins[user_id] = coins.get(user_id, 0) + random.randint(3, 8)

    await bot.process_commands(message)

# -----------------------
# COINS COMMAND
# -----------------------
@bot.command()
async def coinscmd(ctx):
    await ctx.send(f"💰 You have {coins.get(ctx.author.id, 0)} coins")

# -----------------------
# LOCKDOWN (GLOBAL MESSAGE)
# -----------------------
@bot.command()
async def lockdown(ctx):

    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Admin only.")
        return

    # send message to ALL text channels
    for channel in ctx.guild.text_channels:
        try:
            await channel.send(LOCKDOWN_MSG)
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        except:
            pass

    await ctx.send("🔒 Server lockdown activated.")

# -----------------------
# LIFT LOCKDOWN
# -----------------------
@bot.command()
async def lifted(ctx):

    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Admin only.")
        return

    for channel in ctx.guild.text_channels:
        try:
            await channel.send(LIFTED_MSG)
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        except:
            pass

    await ctx.send("🔓 Lockdown removed.")

# -----------------------
# SHOP SYSTEM
# -----------------------
class ShopView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    def buy(self, interaction, role_id, cost, success_msg):

        user_id = interaction.user.id

        if coins.get(user_id, 0) < cost:
            return False

        role = interaction.guild.get_role(role_id)

        if role:
            interaction.user.add_roles(role)

        coins[user_id] -= cost
        return True

    @discord.ui.button(label="🥭 Blox Fruits (200)", style=discord.ButtonStyle.success)
    async def blox(self, interaction, button):
        if not self.buy(interaction, 1502647506801000500, 200, "Blox"):
            await interaction.response.send_message("❌ Not enough coins", ephemeral=True)
            return
        await interaction.response.send_message("✅ Bought Blox role", ephemeral=True)

    @discord.ui.button(label="🚢 Sailor Piece (350)", style=discord.ButtonStyle.primary)
    async def sailor(self, interaction, button):
        if not self.buy(interaction, 1502647995798261800, 350, "Sailor"):
            await interaction.response.send_message("❌ Not enough coins", ephemeral=True)
            return
        await interaction.response.send_message("✅ Bought Sailor role", ephemeral=True)

    @discord.ui.button(label="💸 Wealthy (700)", style=discord.ButtonStyle.secondary)
    async def wealthy(self, interaction, button):
        if not self.buy(interaction, 1502648468664225792, 700, "Wealthy"):
            await interaction.response.send_message("❌ Not enough coins", ephemeral=True)
            return
        await interaction.response.send_message("✅ Bought Wealthy role", ephemeral=True)

# -----------------------
# SHOP COMMAND
# -----------------------
@bot.command()
async def shopcreate(ctx):

    embed = discord.Embed(
        title="🥭 Trading Shop",
        description="Earn coins by chatting and buy roles below!",
        color=discord.Color.green()
    )

    embed.add_field(name="Blox Fruits", value="200 coins", inline=False)
    embed.add_field(name="Sailor Piece", value="350 coins", inline=False)
    embed.add_field(name="Wealthy", value="700 coins", inline=False)

    await ctx.send(embed=embed, view=ShopView())

# -----------------------
# RUN BOT
# -----------------------
bot.run(TOKEN)

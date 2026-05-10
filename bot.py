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
contact your server's Administrators!
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

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(e)

    print(f"Logged in as {bot.user}")

# -----------------------
# COIN EARNING
# -----------------------
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    user_id = message.author.id

    # GIVE COINS
    coins[user_id] = coins.get(user_id, 0) + random.randint(3, 8)

# -----------------------
# /COINS
# -----------------------
@bot.tree.command(name="coins", description="Check your coins")
async def coinscmd(interaction: discord.Interaction):

    amount = coins.get(interaction.user.id, 0)

    await interaction.response.send_message(
        f"💰 You have {amount} coins"
    )

# -----------------------
# /LOCKDOWN
# -----------------------
@bot.tree.command(name="lockdown", description="Lock the server")
async def lockdown(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "❌ Admin only.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        "🔒 Activating lockdown..."
    )

    for channel in interaction.guild.text_channels:

        try:
            await channel.send(LOCKDOWN_MSG)

            await channel.set_permissions(
                interaction.guild.default_role,
                send_messages=False
            )

        except:
            pass

# -----------------------
# /LIFTED
# -----------------------
@bot.tree.command(name="lifted", description="Remove lockdown")
async def lifted(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "❌ Admin only.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        "🔓 Removing lockdown..."
    )

    for channel in interaction.guild.text_channels:

        try:
            await channel.set_permissions(
                interaction.guild.default_role,
                send_messages=True
            )

            await channel.send(LIFTED_MSG)

        except:
            pass

# -----------------------
# SHOP VIEW
# -----------------------
class ShopView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    async def buy(self, interaction, role_id, cost):

        user_id = interaction.user.id

        if coins.get(user_id, 0) < cost:
            return False

        role = interaction.guild.get_role(role_id)

        if role:
            await interaction.user.add_roles(role)

        coins[user_id] -= cost

        return True

    # -------------------
    # BLOX
    # -------------------
    @discord.ui.button(
        label="🥭 Blox Fruits Fan (200)",
        style=discord.ButtonStyle.success
    )
    async def blox(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        success = await self.buy(
            interaction,
            1502647506801000500,
            200
        )

        if not success:

            await interaction.response.send_message(
                "❌ Not enough coins.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "✅ Bought Blox Fruits role.",
            ephemeral=True
        )

    # -------------------
    # SAILOR
    # -------------------
    @discord.ui.button(
        label="🚢 Sailor Piece Fan (350)",
        style=discord.ButtonStyle.primary
    )
    async def sailor(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        success = await self.buy(
            interaction,
            1502647995798261800,
            350
        )

        if not success:

            await interaction.response.send_message(
                "❌ Not enough coins.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "✅ Bought Sailor Piece role.",
            ephemeral=True
        )

    # -------------------
    # WEALTHY
    # -------------------
    @discord.ui.button(
        label="💸 The Wealthy (700)",
        style=discord.ButtonStyle.secondary
    )
    async def wealthy(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        success = await self.buy(
            interaction,
            1502648468664225792,
            700
        )

        if not success:

            await interaction.response.send_message(
                "❌ Not enough coins.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "✅ Bought Wealthy role.",
            ephemeral=True
        )

# -----------------------
# /SHOP
# -----------------------
@bot.tree.command(name="shop", description="Open the role shop")
async def shop(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🥭 Trading Shop",
        description="Earn coins by chatting and buy roles below!",
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

# -----------------------
# RUN BOT
# -----------------------
bot.run(TOKEN)

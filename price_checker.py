import os
import logging
import discord
from discord.ext import commands, tasks
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import aioconsole  # Til at checke efter input i terminal asycly

# Set up logging level to ERROR to suppress lower levels
logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)
# Makes it only print CRITICAL or ERROR lvl warnings to the terminal and ignores stuff like debug or info

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Use webdriver-manager to automatically manage ChromeDriver
service = Service(ChromeDriverManager().install(), log_path=os.devnull)

# Create intents
intents = discord.Intents.default()
intents.message_content = True

# Create a new Discord Bot instance with the specified intents
bot = commands.Bot(command_prefix='/', intents=intents)

# Discord bot token and channel ID
DISCORD_TOKEN = 'BOT-ID'  # Replace with your bot token
CHANNEL_ID = 1301340259564519536  # Replace with your channel ID
ROLE_ID = 1301608044475711488  # Replace with the actual role ID

# --- Price Checking Functionality ---
async def check_price():
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://www.bilkatogo.dk/produkt/heinz-baked-beans/44284/")
    try:
        price_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-price__integer"))
        )
        price = price_element.text
        now = datetime.now()
        date_time = now.strftime("%H:%M - %d/%m")
        channel = bot.get_channel(CHANNEL_ID)
        role = discord.utils.get(channel.guild.roles, id=ROLE_ID)
        if role:
            await channel.send(f"{role.mention} Heinz Baked Beans Costs: {price} DKK in Bilka at {date_time}")
        else:
            await channel.send("Role not found!")
    except Exception as e:
        print("Couldn't find the price on the page:", e)
    finally:
        driver.quit()

@tasks.loop(hours=1)
async def price_check_task():
    """Periodic task to check the price."""
    await check_price()

# --- Bot Events ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    price_check_task.start()

    # Start listening for terminal commands
    await listen_for_commands()

# --- Role Management Commands ---
# Adds the role
@bot.command(name='add')
async def add_role(ctx, *, arg=None):
    """Command to add a role to the user."""
    if arg == 'me':
        role = discord.utils.get(ctx.guild.roles, id=ROLE_ID)
        if role:
            print(f"Attempting to add role {role.name} to {ctx.author.name}")
            await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author.mention}, you have been given the {role.name} role!")
        else:
            await ctx.send("Role not found!")
    else:
        await ctx.send("Invalid argument. Use `/add me`.")

# Removes the role
@bot.command(name='remove')
async def remove_role(ctx, *, arg=None):
    """Command to remove a role to the user."""
    if arg == 'me':
        role = discord.utils.get(ctx.guild.roles, id=ROLE_ID)
        if role:
            print(f"Attempting to remove role {role.name} from {ctx.author.name}")
            await ctx.author.remove_roles(role)
            await ctx.send(f"{ctx.author.mention}, the {role.name} role has been removed from you!")
        else:
            await ctx.send("Role not found!")
    else:
        await ctx.send("Invalid argument. Use `/remove me`.")


# --- /Price Command ---
@bot.command(name='price')
async def price_command(ctx):
    await ctx.send("Checking the price...")
    await check_price()  # Call the check_price function and await its result
    

# # --- Listening for Terminal Commands ---
async def listen_for_commands():
    """Function to listen for commands from the terminal."""
    while True:
        command = await aioconsole.ainput("Enter command to send to Discord (or type 'exit' to quit): ")
        if command.lower() == 'exit':
            print("Exiting...")
            await bot.close()  # Gracefully close the bot if 'exit' is entered
            break
        elif command.startswith(""):
            channel = bot.get_channel(CHANNEL_ID)  # Replace with your channel ID
            if channel:
                await channel.send(command)  # Send the command as a message to the channel
            else:
                print("Channel not found.")



# --- Run the Bot ---
bot.run(DISCORD_TOKEN)








from enum import member
import os
import logging
import discord
import random
import re
import time
import json
import aiohttp
from discord import guild
from discord.ui import View, Button
import math
from collections import defaultdict
from discord.ext import commands
from dotenv import load_dotenv
import google.generativeai as genai
# =========================
# Load Environment
# =========================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
game_counter = 1
# =========================
# Logging
# =========================
handler = logging.FileHandler(
    filename="discord.log",
    encoding="utf-8",
    mode="w"
)

# =========================
# Intents (ONE TIME)
# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_member_join(member):
    WELCOME_CHANNEL_ID = 1461828500662128710
    intro_channel_id = 1462151264727990394
    RULES_CHANNEL_ID = 1461809896553971826
    GENERAL_CHANNEL_ID = 1461802394265321589
    
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    channel2 = bot.get_channel(GENERAL_CHANNEL_ID)
    if not channel2:
        return

    # Create the embed
    embed1 = discord.Embed(
        title=f"🎉 Welcome {member.name}!",
        description=(
            f"Welcome to **{member.guild.name} , {member.mention}!**\n\n"
            f"Take your time to introduce yourself and get familiar with the community: <#{intro_channel_id}>\n"
            f"Please check the rules here: <#{RULES_CHANNEL_ID}>\n"
            f"Say hi in {bot.get_channel(GENERAL_CHANNEL_ID).mention}!"
        ),
        color=discord.Color.random()
    )

    # Set GIF in the embed
    embed1.set_image(url="https://static.klipy.com/ii/71b2873e478b9d8d0482ea3ec777ba7f/dc/a3/G01Q5M7K.gif")

    # Set server logo as thumbnail (small, bottom-right style)
    embed1.set_thumbnail(url="https://media.discordapp.net/attachments/1462141976618078352/1475968615592235119/hamrokurapfp.png?ex=699f6a64&is=699e18e4&hm=9cb78a311b2a9dddee75412f9c17370519dda44170eab4e08ff67ac617db221a&=&format=webp&quality=lossless&width=352&height=352")

    # Footer with member count
    embed1.set_footer(text=f"You're member #{len(member.guild.members)}!")

    embed2 = discord.Embed(
        title=f"🎉 Welcome {member.name}!",
        description=(
            f"Welcome to **{member.guild.name} , {member.mention}!**\n\n"
            f"Take your time to introduce yourself and get familiar with the community: <#{intro_channel_id}>\n"
            f"Everyone please welcome {member.mention}!"
        ),
        color=discord.Color.random()
    )

    # Set server logo as thumbnail (small, bottom-right style)
    embed2.set_thumbnail(url="https://media.discordapp.net/attachments/1462141976618078352/1475968615592235119/hamrokurapfp.png?ex=699f6a64&is=699e18e4&hm=9cb78a311b2a9dddee75412f9c17370519dda44170eab4e08ff67ac617db221a&=&format=webp&quality=lossless&width=352&height=352")

    # Footer with member count
    embed2.set_footer(text=f"You're member #{len(member.guild.members)}!")

    await channel.send(f"{member.mention}", embed=embed1)
    await channel2.send(f"{member.mention}", embed=embed2)
# =========================
# Config
# =========================
CONFIG = {
    "DUO_CHANNEL_ID": 1462541076039471319,
    "TRIO_CHANNEL_ID": 1476919334600314962,  # <-- PUT YOUR TRIO CHANNEL ID HERE
    "SQUAD_CHANNEL_ID": 1462541289173028864,
    "TEAM_CHANNEL_ID": 1461889233399582813,
    "CATEGORY_ID": None
}


active_channels = set()
channel_owners = {}

# =========================
# Events
# =========================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and (not before.channel or before.channel.id != after.channel.id):
        await handle_join(member, after.channel)

    if before.channel and (not after.channel or before.channel.id != after.channel.id):
        await handle_leave(member, before.channel)
    user_id = str(member.id)

async def handle_join(member, channel):
    limit = 0
    prefix = ""

    if channel.id == CONFIG["DUO_CHANNEL_ID"]:
        limit, prefix = 2, "DUO"

    elif channel.id == CONFIG["TRIO_CHANNEL_ID"]:
        limit, prefix = 3, "TRIO"

    elif channel.id == CONFIG["SQUAD_CHANNEL_ID"]:
        limit, prefix = 4, "Game"   

    elif channel.id == CONFIG["TEAM_CHANNEL_ID"]:
        limit, prefix = 10, "TEAM"

    else:
        return

    guild = member.guild
    category = guild.get_channel(CONFIG["CATEGORY_ID"]) if CONFIG["CATEGORY_ID"] else channel.category
    allowed_role = guild.get_role(1492471388764639373)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(
            connect=False,
            speak=True,
            use_soundboard=True,
            use_embedded_activities=True,
            use_voice_activation=True,
            stream=True,
            use_external_apps=True
        ),
        allowed_role: discord.PermissionOverwrite(
            connect=True,
            speak=True,
            use_soundboard=True,
            use_embedded_activities=True,
            use_voice_activation=True,
            stream=True,
            use_external_apps=True
        ),
        member: discord.PermissionOverwrite(
            connect=True,
            speak=True,
            use_soundboard=True,
            use_embedded_activities=True,
            use_voice_activation=True,
            stream=True,
            use_external_apps=True
        ),
        guild.me: discord.PermissionOverwrite(
            connect=True,
            speak=True,
            use_soundboard=True,
            use_embedded_activities=True,
            use_voice_activation=True,
            stream=True,
            use_external_apps=True
        )
        }
    
     # Replace with your allowed role ID


    try:
        # Create the voice channel
        global game_counter

        new_channel = await guild.create_voice_channel(
            name=f"Game #{game_counter}",
            category=category,
            user_limit=limit,
            overwrites=overwrites,
            bitrate=96000
        )
        game_counter += 1
        await member.move_to(new_channel)
        active_channels.add(new_channel.id)
        channel_owners[new_channel.id] = member.id
        
        embed = discord.Embed(
            title="🔊 Temporary Voice Channel Created", 
            description=f"Welcome, {member.mention}! You are the owner of this channel.", 
            color=0x3498db
        )
        embed.add_field(name="Available Commands", value=(
            "`!vc-limit <n>` - Set user limit\n"
            "`!vc-transfer @user` - Transfer ownership\n"
            "`!vc-claim` - Claim ownership\n"
            "`!vc-owner` - Show current owner\n"
            "`!vc-kick @user` - Kick a user\n"
            "`!vc-ban @user` - Ban a user\n"
            "`!vc-unban @user` - Unban a user\n"
            "`!vc-lock` - Lock the channel\n"
            "`!vc-unlock` - Unlock the channel"
        ), inline=False)
        embed.set_footer(text="Commands only work in this channel's chat.")
        
        await new_channel.send(embed=embed)

    except Exception as e:
        print(f"❌ Error creating VC: {e}")

async def handle_leave(member, channel):
    if channel.id in active_channels and len(channel.members) == 0:
        try:
            game_counter -= 1
            await channel.delete()
            active_channels.discard(channel.id)
            channel_owners.pop(channel.id, None)
        except Exception as e:
            print(f"❌ Error deleting VC: {e}")

# =========================
# Helpers
# =========================
def get_user_vc(ctx):
    if not ctx.author.voice or not ctx.author.voice.channel:
        return None
    return ctx.author.voice.channel

def is_vc_owner():
    async def predicate(ctx):
        vc = get_user_vc(ctx)

        if not vc:
            await ctx.send("❌ You must be in your voice channel.")
            return False

        if vc.id not in active_channels:
            await ctx.send("❌ This is not a managed voice channel.")
            return False

        if channel_owners.get(vc.id) != ctx.author.id:
            await ctx.send("❌ Only the channel owner can use this.")
            return False

        return True
    return commands.check(predicate)


# =========================
# Commands
# =========================
@bot.command(name="vc-limit")
@is_vc_owner()
async def vc_limit(ctx, n: int):
    vc = get_user_vc(ctx)
    await vc.edit(user_limit=n)
    await ctx.send(f"✅ User limit set to **{n}**")


@bot.command(name="vc-transfer")
@is_vc_owner()
async def vc_transfer(ctx, member: discord.Member):
    vc = get_user_vc(ctx)

    if member not in vc.members:
        await ctx.send("❌ User must be in the voice channel.")
        return

    # Update owner
    channel_owners[vc.id] = member.id

    # Keep the prefix (DUO / TRIO / etc)
    prefix = vc.name.split(" - ")[-1] if " - " in vc.name else "VC"

    # Rename channel to new owner
    await vc.edit(name=f"{member.name} - {prefix}")

    await ctx.send(f"👑 Ownership transferred to {member.mention}")

@bot.command(name="vc-claim")
async def vc_claim(ctx):
    vc = get_user_vc(ctx)

    if not vc or vc.id not in active_channels:
        return

    owner_id = channel_owners.get(vc.id)
    owner = ctx.guild.get_member(owner_id) if owner_id else None

    if owner and owner in vc.members:
        await ctx.send("❌ Owner is still in the channel.")
        return

    # Update owner
    channel_owners[vc.id] = ctx.author.id

    # Keep prefix
    prefix = vc.name.split(" - ")[-1] if " - " in vc.name else "VC"

    # Rename channel
    await vc.edit(name=f"{ctx.author.name} - {prefix}")
    await ctx.send("👑 You have claimed ownership.")

@bot.command(name="vc-owner")
async def vc_owner(ctx):
    vc = get_user_vc(ctx)

    if not vc or vc.id not in active_channels:
        return

    owner_id = channel_owners.get(vc.id)
    owner = ctx.guild.get_member(owner_id) if owner_id else None

    await ctx.send(f"👑 Current owner: {owner.mention if owner else 'Unknown'}")


@bot.command(name="vc-kick")
@is_vc_owner()
async def vc_kick(ctx, member: discord.Member):
    vc = get_user_vc(ctx)

    if member not in vc.members:
        await ctx.send("❌ User is not in your voice channel.")
        return

    await member.move_to(None)
    await ctx.send(f"👞 Kicked {member.mention}")

@bot.command(name="vc-ban")
@is_vc_owner()
async def vc_ban(ctx, member: discord.Member):
    vc = get_user_vc(ctx)

    await vc.set_permissions(member, connect=False)

    if member in vc.members:
        await member.move_to(None)

    await ctx.send(f"🚫 Banned {member.mention} from the channel.")


@bot.command(name="vc-uban")
@is_vc_owner()
async def vc_unban(ctx, member: discord.Member):
    vc = get_user_vc(ctx)

    await vc.set_permissions(member, overwrite=None)
    await ctx.send(f"✅ Unbanned {member.mention}")

@bot.command(name="vc-lock")
@is_vc_owner()
async def vc_lock(ctx):
    channel = ctx.author.voice.channel if ctx.author.voice else None

    if not channel or channel.id not in active_channels:
        return await ctx.send("❌ You must be in your temporary voice channel.")

    await channel.set_permissions(
        ctx.guild.default_role,
        connect=False
    )

    await ctx.send("🔒 Voice channel locked. No one else can join.")

@bot.command(name="vc-unlock")
@is_vc_owner()
async def vc_unlock(ctx):
    channel = ctx.author.voice.channel if ctx.author.voice else None

    if not channel or channel.id not in active_channels:
        return await ctx.send("❌ You must be in your temporary voice channel.")

    await channel.set_permissions(
        ctx.guild.default_role,
        connect=True
    )

    await ctx.send("🔓 Voice channel unlocked. Anyone can join.")

@bot.command()
async def chup(ctx, member: discord.Member):
    await ctx.send(f"Chup muji {member.mention}")

@bot.command()
async def sut(ctx, member: discord.Member):
    await ctx.send(f"sut muji {member.mention}")

@bot.command()
async def sorry(ctx, member: discord.Member):
    embed = discord.Embed()
    embed.set_image(url="https://c.tenor.com/xcWphzVquJ8AAAAd/tenor.gif")
    await ctx.send(content=member.mention, embed=embed)


ROASTS = [
    "yo momma so old her birth certificate says expired",
    "yo momma so poor when i saw her kickin a can down the street i asked what she was doin she said movin",
    "yo momma so ugly she made u",
    "yo momma so stupid she put airbags on her computer in case it crashed",
    "yo momma so fat when she skips a meal the stock market drops",
    "yo momma so lazy she stuck her nose out the window and let the wind blow it",
    "yo momma so dumb she thought a quarterback was a refund",
    "yo momma so poor she can't even pay attention",
    "yo momma so fat when she goes to the beach the whales sing 'we are family'",
    "yo momma so ugly when she tried to join an ugly contest they said sorry not today",
    "You must have a Ph.D. in stupidology.",
    "You are like a software update. Every time I see you, I immediately think, 'Not now.'",
    "All mistakes are fixable—except for you.",
    "You’re the reason the divorce rate is so high.",
    "If I don’t answer you the first time, what makes you think the next 25 will work?",
    "I gave out all my trophies a while ago, but here’s a participation award.",
    "A glowstick has a brighter future than you.",
    "It’s sad what happened to your face. Oh, wait, that’s how it’s always looked?",
    "I’m listening. I just need a minute to process so much stupid information at once.",
    "When I look at you, I think, 'Where have you been my whole life? And can you go back there?'",
    "Beauty is only skin deep, but ugly goes clean to the bone.",
    "I would agree with you, but then we’d both be wrong.",
    "You look like something that came out of a slow cooker.",
    "It would be a great day if you accidentally used a glue stick instead of a Chapstick.",
    "I bet I could remove 90 percent of your good looks with a moist towelette.",
    "You’re so fake, even Barbie is jealous.",
    "I suggest you do a little soul-searching—you may actually find one.",
    "I know I make a lot of stupid choices, but hanging out with you was the worst of them all.",
    "Stupidity isn’t a crime, so you’re free to go.",
    "I was going to make a joke about your life, but I see life beat me to the punch.",
    "It must be fun to wake up each morning knowing that you are that much closer to achieving your dreams of complete and utter mediocrity.",
    "The truth will set you free: you’re the worst. Okay, you’re free to go.",
    "You remind me of the end pieces of a loaf of bread—nobody wants you.",
    "Calling you an idiot would be an insult to stupid people. You’re much worse than that.",
    "It’s a parent’s job to raise their children right. So, looking at you, it’s obvious that yours quit after just one day.",
    "You’re so fat, the photo I took of you last Christmas is still printing.",
    "Your birth certificate needs to be rewritten as a letter of apology.",
    "It must be nice to never use your brain.",
    "Hey, don’t stand too close to the fire. Plastic melts, you know.",
    "I’ll never forget the first time we met each other—but I promise I’ll keep trying.",
    "You’re just like a broken pencil—totally pointless.",
    "If idiots could fly, your house would be an airport.",
    "You bring everyone so much joy, especially when you leave a room.",
    "You have miles to go before you reach mediocre.",
    "You say I look ugly today? Good, I was trying to look like you.",
    "You’re dumber than a rock. At least a rock can hold a door open. What can you do?",
    "I used to believe in evolution until I met you. Now I’m not so sure.",
    "Don’t worry about me. Just worry about your eyebrows.",
    "I promise I’m not insulting you, I’m just describing you.",
    "I’d love to stay and chat, but I’d rather have open-heart surgery.",
    "Your face looks like something I’d draw with my left hand.",
    "You’re the reason that tubes of toothpaste have instructions on them.",
    "Uh oh! I smell smoke… are you thinking too hard again?",
    "Look on the bright side, if genius skips a generation, your kids will be absolutely brilliant.",
    "If I throw a stick for you, will you leave?",
    "I am unwilling to have a battle of wits with an unarmed opponent like yourself.",
    "The closest you’ll ever come to a brainstorm is a light drizzle.",
    "I don’t have the time (or enough crayons) to explain this to you.",
    "Congrats on getting your PhD in annoyance.",
    "If I had just one wish, it would be that you step on a LEGO while barefoot today."
    ]

@bot.command()
async def roast(ctx, member: discord.Member):
    if member.bot:
        await ctx.send("🤖 Roasting bots is unfair… they have feelings too.")
        return

    roast = random.choice(ROASTS)
    await ctx.send(f"🔥 {member.mention} {roast}")

RIZZ = [
    "Timro nickname ta blanket hola hai, herdai patyau patyau lagne raixau. https://c.tenor.com/lkXE8nvV6JsAAAAd/tenor.gif",
    "Are you Bhimsen Thapa ?? because you just erected my dharahara https://c.tenor.com/hlXzfw9TqK8AAAAd/tenor.gif",
    "hamlai pani maya le hera na parbatiiiii https://c.tenor.com/Rd8FQYPG2EwAAAAd/tenor.gif",
    "Are you Rajesh Hamal? Cuz, every time I see you I just want to say HEYY!!! https://c.tenor.com/vRs8EyzQvY4AAAAd/tenor.gif",
    "Bango bango thiye, sidha bhaye ma. Timilai dekhera fida bhaye ma. Bhannu ta dherai thiyo, tara aaile chai muji bhandai bida bhaye ma. https://c.tenor.com/SJbT1KH73loAAAAd/tenor.gif",
    "Andi Mandi Jhandi Jo Mero Girlfriend Hudaina Tyo ____. https://c.tenor.com/ZARBViZffU4AAAAd/tenor.gif",
    "Are you Mommy ko kuchho, cause you hit different? https://c.tenor.com/OfbnNJxQWLkAAAAd/tenor.gif",
    "Timi vayena vane ta chini haleko chiya pani mitho hunna https://c.tenor.com/e0X4v3Y16xYAAAAd/tenor.gif",
    "I am not an insurance agent, but will you beema girl? https://c.tenor.com/DGqcg27wcqEAAAAd/tenor.gif",
    "Timi sirak ta haina, tara herdai pattauna manlagyo https://c.tenor.com/14v-uu0p2zkAAAAd/tenor.gif",
    "Timro photo pathau na, ma taas kheldai thiye, mero Rani nei harayo k https://c.tenor.com/kCsgnAmVWSQAAAAd/tenor.gif",
    "Are you from Samakhusi? Cause you made my Ama Khusi! https://c.tenor.com/ysITqa52me8AAAAd/tenor.gif",
    "Are you dozer? I can stare you all day! https://c.tenor.com/E0V4tZA72HIAAAAd/tenor.gif",
    "If you have two kids in future and i also have two kids how many total kids we will have? (She will say 4) Nah just two https://c.tenor.com/SJlh3ytXmzMAAAAd/tenor.gif",
    "Are you Kathmandu? Cause you took my breath away! https://c.tenor.com/8VXRYGhuKFAAAAAd/tenor.gif",
    "I am gonna love you till the Melamchi ko pani arrived! (Sadly it’s here) https://c.tenor.com/Iga6pdXRmJgAAAAd/tenor.gif",
    "Is your dad biplov? Cause you are a bomb? https://c.tenor.com/4NYOBe8vcqYAAAAd/tenor.gif",
    "Your eyes are Patan ko galli, I keep getting lost in them. https://c.tenor.com/LHapB3z7oKEAAAAd/tenor.gif",
    "Timilai sugar lagxa vanera matra ho natra mitho mitho guff hanna malai ni auxa https://c.tenor.com/QqFAbHAdhckAAAAd/tenor.gif",
    "Are you Momo? Cause I wanna eat you Gwamma! https://c.tenor.com/4-HxN-cvB5sAAAAd/tenor.gif",
    "(She: Hawa timi) You called me Hawa, I don’t think you can live without it. https://c.tenor.com/rdkHWmsaP5sAAAAd/tenor.gif",
    "Ani khana Khayou ta? https://c.tenor.com/l8vCgpAK2H8AAAAd/tenor.gif",
    "Girl everytime I see you I feel like Aasok darji. Cuz timi vanda ramri koi chaina sansar mai. https://c.tenor.com/GQ66j05SZA8AAAAd/tenor.gif",
    "Raksi ta esai badnam xa, asli nasa ta timro ankha ma xa! https://c.tenor.com/iMZrys9vF5AAAAAd/tenor.gif",
    "We go together like daal and bhaat! https://c.tenor.com/Et5Mnh02jsIAAAAd/tenor.gif",
    "Did you call pathao? Cause I am here to pick you up! https://c.tenor.com/UGKQ56JfNLYAAAAd/tenor.gif",
    "I am gonna leave you like Bagmati; wet, dirty and constantly flowing. https://c.tenor.com/v6SFpiB8oNIAAAAd/tenor.gif"
]

TENOR_REGEX = r"(https?://\S+\.gif)"

def create_rizz_embed(author: discord.Member):
    rizz = random.choice(RIZZ)

    gif = None
    match = re.search(TENOR_REGEX, rizz)
    if match:
        gif = match.group(1)
        rizz = rizz.replace(gif, "").strip()

    embed = discord.Embed(
        description=rizz,
        color=0xff4d6d
    )
    embed.set_footer(text=f"Rizz dropped by {author.display_name}")

    if gif:
        embed.set_image(url=gif)

    return embed


@bot.command()
async def rizz(ctx, member: discord.Member = None):
    embed = create_rizz_embed(ctx.author)

    if member:
        await ctx.send(content=member.mention, embed=embed)
    else:
        await ctx.send(embed=embed)


ALLOWED_USER_IDS = [
    1441687923782062151,
    849537205725954058,
    1416509223399063582,
    1014412475908767785,
    804005263937241138
]

@bot.command()
async def move(ctx, *args):

    # 🔒 Check if user is in allowed list
    if ctx.author.id not in ALLOWED_USER_IDS:
        try:
            await ctx.message.delete()
        except:
            pass
        return

    # 🧹 Delete command message
    try:
        await ctx.message.delete()
    except:
        pass

    if len(args) < 2:
        return

    # 🎯 Last argument = channel ID
    try:
        channel_id = int(args[-1])
    except:
        return

    channel = ctx.guild.get_channel(channel_id)

    if not channel or not isinstance(channel, discord.VoiceChannel):
        return

    # 👥 Get mentioned users
    members = ctx.message.mentions

    if not members:
        return

    # 🚀 Move users
    for member in members:
        if member.voice and member.voice.channel:
            try:
                await member.move_to(channel)
            except:
                pass
# =========================
# Message Moderation
# =========================
BAD_WORDS = {"lado", "machikney", "randi", "rando", "bhalu","arjun", "turi"}
MUSIC_CHANNEL_ID = 1462153175912943637
BAD_WORDS_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(word) for word in BAD_WORDS) + r")\b",
    re.IGNORECASE
)
from collections import defaultdict

spam_tracker = defaultdict(list)

SPAM_WINDOW = 5      # seconds
SPAM_LIMIT = 10      # detect spam
KEEP_MESSAGES = 5    # messages to keep
F_RESPONSES = [
    "🎤 {user} approves this singing 👌",
    "👏 {user} says: that was clean!",
    "🔥 {user} enjoyed that performance!",
    "🎶 {user} is vibing with the singer!",
    "💯 {user} says nice vocals!"
]

FF_RESPONSES = [
    "🎤🔥 {user} says THAT WAS FIRE!",
    "👏👏 {user} is impressed with those vocals!",
    "🎶 {user} says the singer cooked!",
    "💯 {user} says that voice is elite!",
    "🔥 {user} is vibing HARD to that singing!"
]

W_RESPONSES = [
    "🚨 {user} says THAT WAS INSANE VOCALS!",
    "🎤💀 {user} just got blown away by that singing!",
    "🔥 {user} says the singer absolutely COOKED!",
    "🎶 {user} says this performance was legendary!",
    "💎 {user} says those vocals were god tier!"
]
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()
    # =========================
    # 2️⃣ Bad Word Detection
    # =========================

    if content == "sankar" and message.author.id == 1139607940232384524:
        await message.channel.send("<@696711346359894078>")
    
    if BAD_WORDS_PATTERN.search(message.content):
        try:
            await message.delete()
        except discord.Forbidden:
            pass

        embed = discord.Embed(color=0xff0000)
        embed.set_image(url="https://c.tenor.com/KZF6Cke4FH4AAAAd/tenor.gif")

        await message.channel.send(
            content=message.author.mention,
            embed=embed,
            delete_after=5
        )
        return


    # =========================
    # 3️⃣ Word Triggers (ONLY in specific channel)
    # =========================
    if message.channel.id == MUSIC_CHANNEL_ID:

        content = message.content.lower().strip()

        if content in ["f", "ff", "w", "uff"]:

            user_id = message.author.id
            now = time.time()

            # Store message timestamps
            spam_tracker[user_id].append(now)

            # Remove timestamps older than 5 sec
            spam_tracker[user_id] = [
                t for t in spam_tracker[user_id] if now - t < SPAM_WINDOW
            ]

            # If spam detected
            if len(spam_tracker[user_id]) > SPAM_LIMIT:

                messages = []

                async for msg in message.channel.history(limit=20):
                    if msg.author == message.author and msg.content.lower().strip() == content:
                        messages.append(msg)

                # delete extra messages (keep first 5)
                for msg in messages[KEEP_MESSAGES:]:
                    try:
                        await msg.delete()
                    except:
                        pass

            # F = nice
            if content == "f":
                response = random.choice(F_RESPONSES)
                await message.channel.send(response.format(user=message.author.mention))

            # FF = very nice
            elif content == "ff":
                response = random.choice(FF_RESPONSES)
                await message.channel.send(response.format(user=message.author.mention))

            # INSANELY GOOD
            elif content == "w":
                response = random.choice(W_RESPONSES)
                await message.channel.send(response.format(user=message.author.mention))
            
            # UFF reaction
            elif content == "uff":
                embed = discord.Embed(color=0xff0000)
                embed.set_image(url="https://static.klipy.com/ii/35ccce3d852f7995dd2da910f2abd795/25/03/7fBW7jWy.gif")

                await message.channel.send(
                    f"🎧 {message.author.mention} after hearing those vocals!",
                    embed=embed
                )
    await bot.process_commands(message)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

@bot.command()
async def ai(ctx, *, prompt):
    await ctx.typing()

    try:
        response = model.generate_content(prompt)
        text = response.text

        # Discord message limit
        if len(text) > 2000:
            text = text[:1990] + "..."

        await ctx.reply(text)

    except Exception as e:
        await ctx.reply(f"Error: {e}")

DATA_FILE = "participants.json" 
ALLOWED_CHANNEL_ID = 1488311639936598147
# ------------------ FILE HANDLING ------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"teams": []}

    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # File is empty or broken → reset it
        data = {"teams": []}
        save_data(data)
        return data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def is_allowed_channel(ctx):
    return ctx.channel.id == ALLOWED_CHANNEL_ID


# ------------------ EMBEDS ------------------
def format_error_embed():
    embed = discord.Embed(
        title="❌ Invalid Command Usage",
        description="You used the command incorrectly.",
        color=discord.Color.red()
    )

    embed.add_field(
        name="✅ Correct Format",
        value="```!register @user```",
        inline=False
    )

    embed.add_field(
        name="⚠️ Rules",
        value=(
            "- Mention only 1 user\n"
            "- User must not be already registered\n"
            "- Use this command in the correct channel"
        ),
        inline=False
    )

    return embed


def success_embed(team_name, members):
    embed = discord.Embed(
        title="✅ Team Registered Successfully!",
        color=discord.Color.green()
    )

    embed.add_field(name="Team Name", value=team_name, inline=False)
    embed.add_field(
        name="Members",
        value=" ".join([m.mention for m in members]),
        inline=False
    )

    return embed


# ------------------ COMMAND ------------------
# ------------------ COMMAND ------------------
@bot.command()
async def register(ctx, player: discord.Member):
    """
    Register a single participant in participants.json
    Usage: !register @player
    """

    # Channel check
    if not is_allowed_channel(ctx):
        await ctx.send("❌ You can only register in the designated channel.")
        return

    data = load_data()  # loads {"participants": [...]}

    # Check if player is already registered
    if player.id in data.get("participants", []):
        await ctx.send(f"❌ {player.mention} is already registered!")
        return

    # Add the player
    data.setdefault("participants", []).append(player.id)
    save_data(data)

    # Send confirmation embed
    embed = discord.Embed(
        title="✅ Registered Successfully!",
        description=f"{player.mention} has been added to the participants list.",
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)


# ------------------ ERROR HANDLER ------------------
@register.error
async def register_error(ctx, error):
    if not is_allowed_channel(ctx):
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=format_error_embed())
    elif isinstance(error, commands.BadArgument):
        await ctx.send(embed=format_error_embed())
    else:
        await ctx.send("⚠️ Something went wrong.")
        print(error)

    # ------------------ VIEW TEAMS ------------------
# ------------------ VIEW TEAMS ------------------
@bot.command()
async def participants(ctx):
    if not is_allowed_channel(ctx):
        return

    data = load_data()
    participant_ids = data.get("participants", [])

    if not participant_ids:
        await ctx.send("No participants registered yet.")
        return

    # Resolve IDs to member names
    members = []
    for uid in participant_ids:
        member = ctx.guild.get_member(uid)
        if member:
            members.append(member.name)
        else:
            members.append(f"Unknown User ({uid})")

    # Pagination settings
    page_size = 20
    total_pages = math.ceil(len(members) / page_size)
    current_page = 1

    def get_page_content(page):
        start = (page - 1) * page_size
        end = start + page_size
        page_members = members[start:end]
        return "\n".join([f"{i+1}. {name}" for i, name in enumerate(page_members, start=start)])

    # Create initial embed
    embed = discord.Embed(
        title=f"📋 Registered Participants (Page {current_page}/{total_pages})",
        description=get_page_content(current_page),
        color=discord.Color.blue()
    )

    # Buttons for pagination
    class Paginator(View):
        def __init__(self):
            super().__init__(timeout=120)  # 2 minutes timeout
            self.current_page = 1

        @discord.ui.button(label="⬅️ Previous", style=discord.ButtonStyle.gray)
        async def prev(self, interaction, button):
            if self.current_page > 1:
                self.current_page -= 1
                embed.description = get_page_content(self.current_page)
                embed.title = f"📋 Registered Participants (Page {self.current_page}/{total_pages})"
                await interaction.response.edit_message(embed=embed, view=self)

        @discord.ui.button(label="➡️ Next", style=discord.ButtonStyle.gray)
        async def next(self, interaction, button):
            if self.current_page < total_pages:
                self.current_page += 1
                embed.description = get_page_content(self.current_page)
                embed.title = f"📋 Registered Participants (Page {self.current_page}/{total_pages})"
                await interaction.response.edit_message(embed=embed, view=self)

    await ctx.send(embed=embed, view=Paginator())
    
Admins = [1139607940232384524, 1462248580793241623, 1257369692730036466]
# ------------------ LUDO MATCH ------------------
@bot.command()
async def ludomatch(ctx):
    if not is_allowed_channel(ctx):
        return
    if ctx.author.id not in Admins:
        await ctx.send("❌ You are not authorized to run this command.")
        return

    data = load_data()
    participant_ids = data.get("participants", [])

    if not participant_ids:
        await ctx.send("No participants registered yet.")
        return

    # Flatten all members
    participants_list = []
    for uid in participant_ids:
        member = ctx.guild.get_member(uid)
        if member:
            participants_list.append(member.name)
        else:
            participants_list.append(f"Unknown User ({uid})")

    random.shuffle(participants_list)

    matches = []
    waiting = []

    # Groups of 4 players
    for i in range(0, len(participants_list), 4):
        group = participants_list[i:i+4]
        if len(group) == 4:
            matches.append(group)
        else:
            waiting.extend(group)

    # Send matches in embeds (split if >25 fields)
    embed = discord.Embed(
        title="🎲 Ludo Matchmaking",
        description="4 players per match. Winner advances.",
        color=discord.Color.gold()
    )
    field_count = 0

    for idx, match in enumerate(matches, start=1):
        players = "\n".join([f"• {p}" for p in match])
        embed.add_field(name=f"🎮 Match {idx}", value=players, inline=False)
        field_count += 1

        if field_count == 25:  # max 25 fields per embed
            await ctx.send(embed=embed)
            embed = discord.Embed(color=discord.Color.gold())
            field_count = 0

    # Add remaining embed fields (if any) and waiting list
    if waiting or field_count > 0:
        if waiting:
            wait_list = ", ".join([f"{p}" for p in waiting])
            embed.add_field(name="🪑 Waiting List", value=wait_list, inline=False)
        await ctx.send(embed=embed)

@bot.command()
async def unregister(ctx, member: discord.Member = None):

    if not is_allowed_channel(ctx):
        return

    data = load_data()

    # If no member mentioned → unregister yourself
    if member is None:
        member = ctx.author

    if member != ctx.author and not ctx.author.id in Admins:
        await ctx.send("❌ You can only unregister yourself.")
        return
    # Check if user exists
    found = False
    if member.id in data.get("participants", []):
        data["participants"].remove(member.id)
        found = True

    if not found:
        await ctx.send(f"❌ {member.mention} is not registered.")
        return

    save_data(data)

    await ctx.send(f"🗑️ {member.mention} has been unregistered.")

Game_Admins = [1441514997938126930, 1419263240571191439]
import time

ROLE_ID = 1489373485896564946  # 🔁 replace with your role ID
COOLDOWN = 7200  # 2 hours in seconds

last_used = 0

PARTICIPANT_ROLE_ID = 1492471388764639373
@bot.command()
async def giveparticipantsrole(ctx):
    
    # 🔒 Admin check (reuse your Admins list)
    if ctx.author.id not in Admins:
        return await ctx.send("❌ You are not allowed to use this command.")

    # 📂 Load data
    if not os.path.exists("participants.json"):
        return await ctx.send("❌ participants.json not found.")

    with open("participants.json", "r") as f:
        data = json.load(f)

    participant_ids = data.get("participants", [])

    if not participant_ids:
        return await ctx.send("❌ No participants found.")

    role = ctx.guild.get_role(PARTICIPANT_ROLE_ID)

    if not role:
        return await ctx.send("❌ Role not found.")

    success = 0
    failed = 0

    for uid in participant_ids:
        member = ctx.guild.get_member(uid)

        if member:
            try:
                await member.add_roles(role)
                success += 1
            except:
                failed += 1
        else:
            failed += 1

    await ctx.send(f"✅ Role given to {success} users | ❌ Failed: {failed}")

@bot.command()
async def amongus(ctx):
    global last_used

    # ✅ Admin check
    if ctx.author.id not in Admins:
        return await ctx.send("❌ You are not allowed to use this command.")

    # ⏳ Cooldown check
    now = time.time()
    if now - last_used < COOLDOWN:
        remaining = int(COOLDOWN - (now - last_used))
        minutes = remaining // 60
        return await ctx.send(f"⏳ Wait {minutes} minutes before using this again.")

    # 🔔 Ping role
    role = ctx.guild.get_role(ROLE_ID)
    if not role:
        return await ctx.send("❌ Role not found.")

    await ctx.send(f"{role.mention} 🚨 Among Us event starting! Join up!")

    # Update cooldown
    last_used = now

bot.run(TOKEN)


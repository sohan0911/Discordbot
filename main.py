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
    await channel.send(embed=embed1)
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
    global game_counter  # 🔥 THIS IS THE FIX

    if channel.id in active_channels and len(channel.members) == 0:
        try:
            await channel.delete()
            active_channels.discard(channel.id)
            channel_owners.pop(channel.id, None)

            # Decrease counter safely
            game_counter = max(1, game_counter - 1)

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
    
    if BAD_WORDS_PATTERN.search(message.content) and message.author.id != 1139607940232384524:
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


DATA_FILE = "teams.json"


AUTHORIZED_USERS = [1139607940232384524,1462248580793241623,903299362912890891]

# 📍 Allowed channel ID
ALLOWED_CHANNEL_ID = 1500487123042701467


# 📂 Load data
def load_teams():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


# 💾 Save data
def save_teams(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


teams = load_teams()

def success_embed(title, description):
    return discord.Embed(
        title=f"✅ {title}",
        description=description,
        color=0x2ecc71
    )

def error_embed(title, description):
    return discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=0xe74c3c
    )

def info_embed(title, description):
    return discord.Embed(
        title=f"ℹ️ {title}",
        description=description,
        color=0x3498db
    )
# =========================
# ✅ CHECK DECORATORS
# =========================

def in_allowed_channel():
    async def predicate(ctx):
        return ctx.channel.id == ALLOWED_CHANNEL_ID
    return commands.check(predicate)


def is_admin():
    async def predicate(ctx):
        return ctx.author.id in AUTHORIZED_USERS
    return commands.check(predicate)


# =========================
# 🤖 COMMANDS
# =========================

# ✅ Register Team
@bot.command()
@in_allowed_channel()
@is_admin()
async def register(ctx, team_name: str = None, p1: str = None, p2: str = None, p3: str = None, p4: str = None, p5: str = None):
    global teams

    # ❗ Missing arguments handler (CUSTOM)
    if not all([team_name, p1, p2, p3, p4, p5]):
        embed = info_embed(
            "How to Register a Team",
            "**Correct Format:**\n"
            "`!register <team_name> <player1> <player2> <player3> <player4> <player5>`\n\n"
            "**Example:**\n"
            "`!register TeamAlpha John Mike Alex Sam Leo`\n\n"
            "⚠️ Make sure:\n"
            "- Exactly 5 players\n"
            "- No duplicate players\n"
            "- Team name is unique"
        )
        return await ctx.send(embed=embed)

    # ❌ Duplicate team
    if team_name in teams:
        return await ctx.send(embed=error_embed(
            "Team Already Exists",
            f"Team **{team_name}** is already registered."
        ))

    players = [p1, p2, p3, p4, p5]

    # ❌ Duplicate players check
    for existing_team, data in teams.items():
        for player in players:
            if player in data["players"]:
                return await ctx.send(embed=error_embed(
                    "Player Already Registered",
                    f"**{player}** is already in team **{existing_team}**"
                ))

    # ✅ Save team
    teams[team_name] = {
        "players": players,
        "captain": ctx.author.id
    }

    save_teams(teams)

    # 🎉 Success embed
    embed = success_embed(
        "Team Registered Successfully!",
        f"🏆 **Team:** {team_name}\n"
        f"👑 **Captain:** {ctx.author.mention}\n\n"
        f"👥 **Players:**\n"
        f"• {p1}\n• {p2}\n• {p3}\n• {p4}\n• {p5}"
    )

    await ctx.send(embed=embed)

# ❌ Remove Team (Admin Only)
@bot.command()
@in_allowed_channel()
@is_admin()
async def remove_team(ctx, team_name: str):
    global teams

    if team_name not in teams:
        return await ctx.send(embed=error_embed(
            "Team Not Found",
            f"No team named **{team_name}** exists."
        ))

    del teams[team_name]
    save_teams(teams)

    await ctx.send(embed=success_embed(
        "Team Removed",
        f"🗑️ Team **{team_name}** has been removed from the tournament."
    ))


# 🔍 Check Team 
@bot.command()
@in_allowed_channel()
@is_admin()
async def team(ctx, team_name: str):
    if team_name not in teams:
        return await ctx.send(embed=error_embed(
            "Team Not Found",
            f"No team named **{team_name}** exists."
        ))

    data = teams[team_name]
    players = data["players"]
    captain_id = data.get("captain")

    embed = discord.Embed(
        title=f"🏆 {team_name}",
        color=0x3498db
    )

    embed.add_field(
        name="👥 Players",
        value="\n".join(f"• {p}" for p in players),
        inline=False
    )

    if captain_id:
        embed.add_field(
            name="👑 Captain",
            value=f"<@{captain_id}>",
            inline=False
        )

    await ctx.send(embed=embed)


# 📋 List Teams 
@bot.command()
@in_allowed_channel()
async def teams_list(ctx):
    if not teams:
        return await ctx.send(embed=info_embed(
            "No Teams Registered",
            "📭 No teams have registered yet."
        ))

    embed = discord.Embed(
        title="🏆 Registered Teams",
        description=f"Total Teams: **{len(teams)}**",
        color=0x9b59b6
    )

    for team_name, data in teams.items():
        players = ", ".join(data["players"])
        embed.add_field(
            name=f"🏷️ {team_name}",
            value=f"👥 {players}",
            inline=False
        )

    await ctx.send(embed=embed)


# =========================
# ⚠️ ERROR HANDLER
# =========================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        if ctx.command and ctx.command.name in ["register", "remove_team", "team", "teams_list"]:
            if ctx.channel.id != ALLOWED_CHANNEL_ID:
                await ctx.send(embed=error_embed(
                    "Wrong Channel",
                    "Use this command in the tournament channel only."
                ))
            else:
                await ctx.send(embed=error_embed(
                    "Permission Denied",
                    "You are not allowed to use this command."
                ))

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=info_embed(
            "Command Usage",
            f"Incorrect usage of `{ctx.command}`.\n\nTry:\n"
            "`!register TeamName p1 p2 p3 p4 p5`"
        ))

    else:
        print(f"Unhandled error: {error}")

Game_Admins = [904018513444864081, 1419263240571191439, 1462248580793241623, 1139607940232384524, 861459299091742770, 889763889707884604]

ROLE_ID = 1489373485896564946 
COOLDOWN = 7200  

last_used = 0

@bot.command()
async def amongus(ctx):
    global last_used

    # ✅ Admin check
    if ctx.author.id not in Game_Admins:
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


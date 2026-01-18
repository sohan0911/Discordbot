from email.mime import message
import io
import aiohttp
import discord 
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'IM alive as {bot.user}')

@bot.event
async def on_member_join(member):
    await member.send(f'Welcome to the server, {member.mention}!')
    
@bot.event
async def on_member_remove(member):
    await member.send(f'Sorry to see you go, {member.mention}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith('hello'):
        await message.channel.send(f'Hello {message.author.mention}!')

    if "lado" in message.content.lower():
        await message.delete()

        embed = discord.Embed()
        embed.set_image(
            url="https://c.tenor.com/KZF6Cke4FH4AAAAd/tenor.gif"
        )

        await message.channel.send(
            content=message.author.mention,
            embed=embed
        )

    if "machikney" in message.content.lower():
        await message.delete()

        embed = discord.Embed()
        embed.set_image(
            url="https://c.tenor.com/KZF6Cke4FH4AAAAd/tenor.gif"
        )

        await message.channel.send(
            content=message.author.mention,
            embed=embed
        )

    if "randi" in message.content.lower():
        await message.delete()

        embed = discord.Embed()
        embed.set_image(
            url="https://c.tenor.com/KZF6Cke4FH4AAAAd/tenor.gif"
        )

        await message.channel.send(
            content=message.author.mention,
            embed=embed
        )

    if "rando" in message.content.lower():
        await message.delete()

        embed = discord.Embed()
        embed.set_image(
            url="https://c.tenor.com/KZF6Cke4FH4AAAAd/tenor.gif"
        )

        await message.channel.send(
            content=message.author.mention,
            embed=embed
        )

    if "turi" in message.content.lower():
        await message.delete()

        embed = discord.Embed()
        embed.set_image(
            url="https://c.tenor.com/KZF6Cke4FH4AAAAd/tenor.gif"
        )

        await message.channel.send(
            content=message.author.mention,
            embed=embed
        )

    await bot.process_commands(message)

@bot.command()
async def chup(ctx, member: discord.Member):
    if member == " ":
        await ctx.send(f'Chup muji {ctx.mention}')
    await ctx.send(f'Chup muji {member.mention}')

@bot.command()
async def sorry(ctx, member: discord.Member):
    embed = discord.Embed()
    embed.set_image(url="https://c.tenor.com/xcWphzVquJ8AAAAd/tenor.gif")

    await ctx.send(
        content=member.mention,
        embed=embed
    )

CONFIG = {
    'DUO_CHANNEL_ID': 1462541076039471319,   
    'SQUAD_CHANNEL_ID': 1462541289173028864, 
    'TEAM_CHANNEL_ID': 1461889233399582813,  
    'CATEGORY_ID': None       # Optional: ID of category to create channels in
}
# Setup Intents
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.messages = True     
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)
# Tracking Data
active_channels = set()        # Set of Voice Channel IDs
channel_owners = {}            # {channel_id: member_id}
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
@bot.event
async def on_voice_state_update(member, before, after):
    # Check if user joined a channel (or switched to one)
    if after.channel:
        if not before.channel or before.channel.id != after.channel.id:
            await handle_join(member, after.channel)
    # Check if user left a channel (or switched from one)
    if before.channel:
        if not after.channel or after.channel.id != before.channel.id:
            await handle_leave(member, before.channel)
async def handle_join(member, channel):
    limit = 0
    name_prefix = ""
    if channel.id == CONFIG['DUO_CHANNEL_ID']:
        limit = 2
        name_prefix = "DUO"
    elif channel.id == CONFIG['SQUAD_CHANNEL_ID']:
        limit = 4
        name_prefix = "SQUAD"
    elif channel.id == CONFIG['TEAM_CHANNEL_ID']:
        limit = 10
        name_prefix = "TEAM"
    else:
        return
    guild = member.guild
    category = guild.get_channel(CONFIG['CATEGORY_ID']) if CONFIG['CATEGORY_ID'] else channel.category
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(connect=True),
        member: discord.PermissionOverwrite(manage_channels=True, move_members=True, connect=True),
        guild.me: discord.PermissionOverwrite(manage_channels=True, move_members=True, connect=True, send_messages=True, embed_links=True)
    }
    try:
        channel_name = f"{member.name} - {name_prefix}"
        new_channel = await guild.create_voice_channel(
            name=channel_name,
            category=category,
            user_limit=limit,
            overwrites=overwrites
        )
        
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
            "`!vc-uban @user` - Unban a user"
        ), inline=False)
        embed.set_footer(text="Commands only work in this channel's chat.")
        
        await new_channel.send(embed=embed)
        
    except Exception as e:
        print(f"Error creating channel: {e}")
async def handle_leave(member, channel):
    if channel.id in active_channels:
        if len(channel.members) == 0:
            try:
                await channel.delete()
                active_channels.discard(channel.id)
                channel_owners.pop(channel.id, None)
            except Exception as e:
                print(f"Error deleting channel: {e}")
# --- Command Helpers ---
def is_owner():
    async def predicate(ctx):
        if ctx.channel.id not in active_channels:
            return False
        owner_id = channel_owners.get(ctx.channel.id)
        if owner_id != ctx.author.id:
            await ctx.send("❌ Only the owner can use this command.", delete_after=5)
            return False
        return True
    return commands.check(predicate)
# --- Commands ---
@bot.command(name="vc-limit")
@is_owner()
async def vc_limit(ctx, n: int):
    await ctx.channel.edit(user_limit=n)
    await ctx.send(f"✅ User limit set to **{n}**.")
@bot.command(name="vc-transfer")
@is_owner()
async def vc_transfer(ctx, new_owner: discord.Member):
    channel_owners[ctx.channel.id] = new_owner.id
    await ctx.channel.set_permissions(new_owner, manage_channels=True, move_members=True, connect=True)
    await ctx.channel.set_permissions(ctx.author, manage_channels=False, move_members=False)
    await ctx.send(f"👑 Ownership transferred to {new_owner.mention}")
@bot.command(name="vc-claim")
async def vc_claim(ctx):
    if ctx.channel.id not in active_channels:
        return
    current_owner_id = channel_owners.get(ctx.channel.id)
    if current_owner_id:
        owner = ctx.guild.get_member(current_owner_id)
        if owner and owner in ctx.channel.members:
            return await ctx.send("❌ The current owner is still in the channel!", delete_after=5)
    channel_owners[ctx.channel.id] = ctx.author.id
    await ctx.channel.set_permissions(ctx.author, manage_channels=True, move_members=True, connect=True)
    await ctx.send(f"👑 You have claimed ownership of this channel!")
@bot.command(name="vc-owner")
async def vc_owner(ctx):
    if ctx.channel.id not in active_channels:
        return
    owner_id = channel_owners.get(ctx.channel.id)
    owner = ctx.guild.get_member(owner_id) if owner_id else None
    await ctx.send(f"👑 The current owner is {owner.mention if owner else 'Unknown'}")
@bot.command(name="vc-kick")
@is_owner()
async def vc_kick(ctx, member: discord.Member):
    if member not in ctx.channel.members:
        return await ctx.send("❌ That user is not in this channel.")
    await member.move_to(None)
    await ctx.send(f"👞 Kicked {member.mention} from the channel.")
@bot.command(name="vc-ban")
@is_owner()
async def vc_ban(ctx, member: discord.Member):
    await ctx.channel.set_permissions(member, connect=False)
    if member in ctx.channel.members:
        await member.move_to(None)
    await ctx.send(f"🚫 Banned {member.mention} from joining this channel.")
@bot.command(name="vc-uban")
@is_owner()
async def vc_unban(ctx, member: discord.Member):
    await ctx.channel.set_permissions(member, overwrite=None)
    await ctx.send(f"✅ Unbanned {member.mention}. They can now join again.")
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(os.getenv("DISCORD_TOKEN"))
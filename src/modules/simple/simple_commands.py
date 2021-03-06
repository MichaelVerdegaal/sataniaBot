from asyncio import TimeoutError

import validators
from discord import Game, Embed
from discord.ext import commands

import src.constants as const
from src.modules.misc.misc_util import *


class Simple:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """|Used to test if bot is responsive and online"""
        await ctx.send("pong")

    @commands.command(hidden=True, name='dbping')
    @commands.is_owner()
    async def db_ping(self, ctx):
        """|Ping database."""
        if connected_to_db():
            await ctx.send('Connection is responsive.')
        else:
            await ctx.send('Unknown error appeared when pinging database.')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def status(self, ctx, *, activity):
        """|Change the status that the bot is displaying"""
        change_status(activity)
        await self.bot.change_presence(activity=Game(activity))

    @commands.command()
    async def advice(self, ctx):
        """|McDowell will give you her well thought out advice"""
        await ctx.send(f"Hear my all-knowing advice: *{get_advice()}*")

    @commands.command()
    async def toc(self, ctx, temperature):
        """|Converts a temperature in Fahrenheit to Celsius. Use <prefix>tof for reverse"""
        try:
            temp = float(temperature)
            fahrenheit = round(temp, 1)
            celsius = round(((fahrenheit - 32) * 5.0) / 9.0, 1)
            await ctx.send(f'{fahrenheit}° Fahrenheit is {celsius}° Celsius')
        except ValueError:
            await ctx.send(f'"{temperature}" is not a valid digit.')

    @commands.command()
    async def tof(self, ctx, temperature):
        """|Converts a temperature in Celsius to Fahrenheit. Use <prefix>toc for reverse"""
        try:
            temp = float(temperature)
            celsius = round(temp, 1)
            fahrenheit = round(((9.0 / 5.0) * celsius) + 32, 1)
            await ctx.send(f'{celsius}° Celsius is {fahrenheit}° Fahrenheit')
        except ValueError:
            await ctx.send(f'"{temperature}" is not a valid digit.')

    @commands.command()
    async def embed(self, ctx, color=None):
        """|Create an embed. For colors use the 'colors' command"""
        try:
            author = ctx.author
            new_check = simple_check(author, ctx.channel)
            discord_colors = get_discord_colors()
            title_message = await ctx.send(f'{author.name}, please type the title of the embed.')
            title = await self.bot.wait_for('message', timeout=30.0, check=new_check)
            await title.delete()
            await title_message.delete()

            description_message = await ctx.send(
                f'{author.name}, please type the description of the embed (useful if you have this '
                f'written in advance for large pieces of text).')
            description = await self.bot.wait_for('message', timeout=60.0, check=new_check)
            await description.delete()
            await description_message.delete()
            embed = Embed(title=title.content, description=description.content)

            if color:
                if color in discord_colors:
                    embed.colour = discord_colors[color]
                elif is_hex_color(color):
                    embed.colour = hex_to_rgb(color)

            url_prompt_message = await ctx.send(f'{author}, do you want to enter an url for the '
                                                f'embed? Type "Y" or "N" to answer')
            url_prompt = await self.bot.wait_for('message', timeout=30.0, check=new_check)
            await url_prompt.delete()
            await url_prompt_message.delete()
            url_prompt = url_prompt.content

            if url_prompt.lower() == 'y':
                url_message = await ctx.send(f'{author}, please enter the url')
                url = await self.bot.wait_for('message', timeout=30.0, check=new_check)
                await url.delete()
                await url_message.delete()
                url = url.content
                if validators.url(url):
                    embed.url = url
                else:
                    await ctx.send(f'"{url}" is not a valid url.')
                    return
            await ctx.send(embed=embed)
            await ctx.message.delete()
        except TimeoutError:
            await ctx.send('No response received, aborting command.')

    @commands.command()
    async def colors(self, ctx):
        """|List all colors that you can use in the embed command"""
        embed = Embed(title='Colors', description='Preset colors you can use in the embed command, '
                                                  'if these do not suit you, you can also enter a '
                                                  'hex color code.')
        for color in get_discord_colors():
            embed.add_field(name=color, value=const.INVISIBLE_CHAR)
        await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx):
        """|Display some info about the bot"""
        embed = Embed(color=const.EMBED_COLOR)
        embed.add_field(name='About',
                        value="McDowell is a bot which adds custom reactions to your server in "
                              "an elegant way. Unlike other bots however, McDowell doesn't instantly"
                              " respond whenever a keyword is mentioned, instead, this is all"
                              " based on chance. This makes sure you don't get tired of a reaction"
                              " easily, and makes it more fun by turning it into a game.")
        embed.add_field(name='Author', value='This bot is developed by All#9999')
        embed.add_field(name='Repository', value='https://bit.ly/2FYVIph')
        embed.set_footer(text=f'McDowell is running on version {const.VERSION}')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Simple(bot))

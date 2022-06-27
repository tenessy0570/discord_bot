import datetime

import wikipedia.exceptions

from img_urls import good_face_url
import discord.errors
from discord.errors import HTTPException
from utils import (
    in_bot_channel,
    receive_message_then_send,
    get_commands_list_to_send,
    get_embed,
    get_video_url_by_name,
    get_on_delete_content,
    message_is_song_name,
    connect_to_voice_chat_and_play_source,
    stop_source_playing,
    message_is_wiki_request,
    get_wiki_info_from_message_request
)
from decorators import (
    author_is_not_bot,
    notify_if_wrong_command
)


class Messages:
    @author_is_not_bot
    @notify_if_wrong_command
    async def on_message(self, message):
        if not in_bot_channel(message=message):
            return

        if await receive_message_then_send(message, "ping"):
            before_answer = message.created_at
            embed = discord.Embed()
            right_now = datetime.datetime.now()
            ping = (right_now - before_answer).microseconds // 1000
            embed.add_field(name="Pong! :ping_pong:", value=f"{ping} ms")
            await message.channel.send(embed=embed)
            return

        if await receive_message_then_send(message, "avatar"):
            image_to_send = get_embed(self.user.avatar_url)
            await message.channel.send(embed=image_to_send)
            return

        if await receive_message_then_send(message, "!help"):
            await message.channel.send(get_commands_list_to_send(self))
            return

        if message.attachments:
            await message.delete()
            await message.channel.send('No attachments! :)')
            return

        if await receive_message_then_send(message, "face"):
            image_to_send = get_embed(url=good_face_url)
            await message.channel.send(embed=image_to_send)
            return

        if message_is_wiki_request(message):

            try:
                wiki_info = get_wiki_info_from_message_request(message)
            except (
                    wikipedia.exceptions.DisambiguationError,
                    wikipedia.exceptions.PageError
            ):
                await message.channel.send("Please clarify what you meant (uppercase/lowercase makes sense)")
                return

            try:
                await message.channel.send(wiki_info)
            except HTTPException:
                await message.channel.send("Please clarify what you meant (uppercase/lowercase makes sense)")

            return

        if message_is_song_name(message):

            try:
                url = get_video_url_by_name(message)
            except (
                    NameError,
                    HTTPException
            ):
                await message.channel.send('Bad song name!')
                return

            await message.channel.send(url)

            await connect_to_voice_chat_and_play_source(self, message, url)
            return

        if await receive_message_then_send(message, "!stop"):

            try:
                stop_source_playing(self, message)
            except AttributeError:
                pass

            return

        return 1

    async def on_typing(self, channel, user, when):
        if not in_bot_channel(channel=channel):
            return

        await channel.send(f"{user.mention} started typing something on {when}. I saw it!")

    async def on_message_delete(self, message):
        if not in_bot_channel(message=message):
            return

        message_content = get_on_delete_content(message)

        await message.channel.send(
            f"{message.author.mention}'s message has just been deleted which was {message_content}"
        )


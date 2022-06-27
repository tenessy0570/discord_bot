import asyncio
import threading

import pafy
from asyncio import sleep

import discord
import wikipedia
from youtubesearchpython import VideosSearch

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


def on_ready_print(self):
    print("---------")
    print("Logged as")
    print(self.user.name)
    print(self.user.id)
    print("---------")


async def receive_message_then_send(message, received: str, to_send=""):
    if message.content == received:
        if to_send:
            await message.channel.send(to_send)
        return True


def get_commands_from_file(filename: str) -> tuple:
    with open(filename, 'r') as file:
        _help_commands = tuple((command.split('\n')[0] for command in file))
    return _help_commands


def message_is_video_name(message):
    return message.content.split(' ')[0] == '!video'


def _get_video_name_from_message(message):
    parsed_msg_list = message.content.split(' ')
    song_name = ' '.join(parsed_msg_list[1:])

    if not song_name:
        raise NameError("Song name can't be empty!")

    return song_name


def _get_movie_id(video_name):
    videos_search = VideosSearch(video_name, limit=1)
    return videos_search.result()['result'][0]['id']


def get_video_url_by_name(message):
    url = 'https://www.youtube.com/watch?v='
    video_name = _get_video_name_from_message(message)

    if not video_name:
        raise NameError

    try:
        video_id = _get_movie_id(video_name)
    except IndexError:
        raise NameError

    return url + video_id


def get_embed(url):
    return discord.Embed().set_image(url=url)


def get_commands_list_to_send(self):
    return "Available commands: \n" + self._help_commands_for_output


def is_embed(message):
    return message.content == ""


def in_bot_channel(channel=None, message=None):
    if message:
        channel = message.channel
    return channel.name == 'bot'


async def get_message_by_id(channel, message_id):
    return await discord.GroupChannel.fetch_message(self=channel, id=message_id)


def _get_reaction_info(self, payload):
    guild = self.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    return payload.emoji, member, payload.message_id


async def create_message_and_add_reactions(self, _channel, _roles_for_send):
    message = await _channel.send(_roles_for_send)
    for key in self._emojis:
        await message.add_reaction(emoji=self._emojis[key])


def create_and_get_roles_dict(_emojis):
    _roles = {}

    for key, i in zip(_emojis, range(1, len(_emojis) + 1)):
        _roles[_emojis[key]] = f"Role {i}"

    return _roles


def get_roles_for_send(self):
    roles = ""
    for key, value in self._roles.items():
        role_name = value
        role = _get_role_by_name(self, role_name)
        roles += f"{key} ~ <@&{role.id}>\n"
    return roles


def _get_role_by_name(self, name):
    return discord.utils.get(self.guilds[0].roles, name=name)


def get_role_from_payload(self, payload, channel):
    emoji, reacted_user, message_id = _get_reaction_info(self, payload)
    guild = channel.guild
    emoji = emoji.name.lower()
    role = discord.utils.get(guild.roles, name=self._roles[emoji])
    return role


def reacted_user_is_bot(self, payload):
    return payload.member == self.user


def get_on_delete_content(message):
    return f'"{message.content}"' \
            if not is_embed(message) \
            else 'just an embed or an image.'


def get_reacted_user(self, payload):
    guild = self.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)
    return user


def message_is_song_name(message):
    return message.content.split(' ')[0] == '!song'


async def connect_to_voice_chat_and_play_source(self, message, url):
    try:
        voice_channel = message.author.voice.channel
    except Exception:
        await message.channel.send("You must be in voice chat")
        return

    client = _get_voice_client(self, voice_channel)
    source = _get_source_by_url(url)

    await _disconnect_if_connected(client)

    voice_player = await voice_channel.connect()
    voice_player.play(source)

    await _disconnect_after_playing(voice_player, client)


def _get_source_by_url(url):
    video = pafy.new(url)
    audio = video.getbestaudio()
    source = discord.FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS, executable="ffmpeg/ffmpeg.exe")
    return source


async def _disconnect_if_connected(client):
    try:
        await client.move_to(None)
    except discord.errors.ClientException:
        pass
    else:
        await sleep(2.0)


def _get_voice_client(client, voice_channel):
    client = discord.VoiceClient(client=client, channel=voice_channel)
    return client


async def _disconnect_after_playing(voice_player, client):
    while voice_player.is_playing():
        await sleep(1.0)
    await client.move_to(None)


def stop_source_playing(self, message):
    client = discord.utils.get(self.voice_clients, guild__name=message.guild.name)
    client.stop()


def message_is_wiki_request(message):
    splitted = message.content.split(" ")
    try:
        return splitted[0] == "!about" and splitted[1]
    except IndexError:
        return False


def get_wiki_info_from_message_request(message):
    request = _get_request_from_message(message)
    return wikipedia.summary(request)


def _get_request_from_message(message):
    return " ".join(message.content.split(" ")[1:])

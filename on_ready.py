from utils import (
    get_commands_from_file,
    create_and_get_roles_dict,
    on_ready_print,
    create_message_and_add_reactions
)


class Ready:
    _help_commands = get_commands_from_file("commands_list_divided_with_newline")
    _help_commands_for_output = ('~ ' + command for command in _help_commands)
    _help_commands_for_output = '\n'.join(_help_commands_for_output)

    _emojis = {
        ":smiling_face_with_3_hearts:": u"\U0001F970",
        ":train:": u"\U0001F68B",
        ":kimono:": u"\U0001F458"
    }

    _pong = u"U+1F3D3"

    _roles = create_and_get_roles_dict(_emojis)

    async def on_ready(self):
        on_ready_print(self)
        # _channel = None
        #
        # for channel in self.get_all_channels():
        #     if channel.name != 'bot':
        #         _channel = channel
        #
        # _roles_for_send = await get_roles_for_send(self)
        # await create_message_and_add_reactions(self, _channel, _roles_for_send)

import re
from typing import Any
from datetime import datetime, timedelta
from contextlib import suppress

from aiogram import Router, Bot, F
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command, CommandObject, and_f
from aiogram.utils.markdown import hblockquote
from aiogram.exceptions import TelegramBadRequest 

from config import OWNER_ID

from pymorphy2 import MorphAnalyzer


def parse_time(time_string: str | None) -> datetime | None:
    if not time_string:
        return None
    
    match_ = re.match(r'(\d+)([a-z])', time_string.lower().strip())
    current_datetime = datetime.now()

    if match_:
        value, unit = int(match_.group(1)), match_.group(2)

        match unit:
            case 'm': time_delta = timedelta(minutes=value)
            case 'h': time_delta = timedelta(hours=value)
            case 'd': time_delta = timedelta(days=value)
            case 'w': time_delta = timedelta(weeks=value)
            case _: return None
    else:
        return None
    
    new_datetime = current_datetime + time_delta

    return new_datetime


router = Router()
router.message.filter(F.chat.type == 'supergroup')

morph = MorphAnalyzer(lang='ru')
triggers = ['бля', 'хуй', 'нах', 'ахуеть', 'ахуел', 'охуеть', 'охуел', 'блять', 'блядь', 'сука', 'пидор', 'пидр', 'ебать', 'ебан', 'еблан', 'ублюдок', 'сегэ', 'кутак', 'секмим', 'секте', 'секмэем', 'сегелгэн', 'сегелде']


@router.message(Command('rules', prefix='/!'))
async def rules_group_cmd(message: Message) -> None:
    await message.answer(f'Правила чата {message.chat.title} для её членов колхозников:\nhttps://telegra.ph/Pravila-kolhoznikov-02-03\n\n{hblockquote("Незнание правил не освобождает от ответственности!")}')


@router.message(and_f(Command('mute', prefix='/!'), F.from_user.id == OWNER_ID))
async def mute_group_cmd(message: Message, bot: Bot, command: CommandObject | None=None) -> Any:
    await message.delete()

    reply = message.reply_to_message

    if not reply:
        return await message.answer('👀 Член колхозников не найден!')
    
    until_date = parse_time(command.args)
    mention = reply.from_user.mention_html(reply.from_user.first_name)

    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,
            until_date=until_date,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_audios=False,
                can_send_documents=False,
                can_send_photos=False,
                can_send_videos=False,
                can_send_video_notes=False,
                can_send_voice_notes=False,
                can_send_polls=False,
                can_send_other_messages=False,
            ),
        )
        await message.answer(f'🤯 Члена колхозников <b>{mention}</b> лишили <b>Свободы Слова</b> на {command.args}!')


@router.message(and_f(Command('ban', prefix='/!'), F.from_user.id == OWNER_ID))
async def ban_group_cmd(message: Message, bot: Bot, command: CommandObject | None=None) -> Any:
    await message.delete()

    reply = message.reply_to_message

    if not reply:
        return await message.answer('👀 Член колхозников не найден!')
    
    until_date = parse_time(command.args)
    mention = reply.from_user.mention_html(reply.from_user.first_name)

    with suppress(TelegramBadRequest):
        await bot.ban_chat_member(
            chat_id=message.chat.id, user_id=reply.from_user.id, until_date=until_date
        )
        await message.answer(f'😱 Члена колхозников <b>{mention}</b> за<b>бан</b>или!')


@router.message(and_f(Command('mute', prefix='/!'), F.from_user.id != OWNER_ID))
async def mute_group_not_cmd(message: Message, bot: Bot, command: CommandObject | None=None) -> Any:
    await message.delete()

    await message.answer(f'{message.from_user.mention_html(message.chat.first_name)}, Обычный смертный член колхозников не имеет прав на использование этой команды!')


@router.message(and_f(Command('ban', prefix='/!'), F.from_user.id != OWNER_ID))
async def ban_group_not_cmd(message: Message, bot: Bot, command: CommandObject | None=None) -> Any:
    await message.delete()

    await message.answer(f'{message.from_user.mention_html(message.chat.first_name)}, Обычный смертный член колхозников не имеет прав на использование этой команды!')


@router.message(F.text)
async def profinity_filter(message: Message) -> None:
    for word in message.text.lower().strip().split():
        parsed_word = morph.parse(word)[0]
        normal_form = parsed_word.normal_form

        for trigger in triggers:
            if trigger in normal_form:
                await message.delete()
                return await message.answer(f'{message.from_user.mention_html(message.from_user.first_name)}, не ругайся!')
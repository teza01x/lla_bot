import asyncio
import time
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup
from telebot import types
from datetime import datetime
from async_markdownv2 import *
from async_sqlite import *
from text_scripts import *
from config import *


bot = AsyncTeleBot(telegram_token)


@bot.message_handler(commands=['start'])
async def start(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username

        try:
            referral_id = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None

            if referral_id:
                await add_ref_count(referral_id, user_id)
        except:
            pass


        chat_type = message.chat.type
        if chat_type == 'private':
            channel_member = await bot.get_chat_member(channel_id, user_id)
            if channel_member.status in ["creator", "administrator", "member"]:
                await change_sub_status(user_id, 1)
                main_menu_text = text_dict['main_menu_sub']
                main_menu_text = await escape(main_menu_text, flag=0)

                button_list0 = [
                    types.InlineKeyboardButton(buttons['check_referals'], callback_data="referal_check"),
                    types.InlineKeyboardButton(buttons['stat'], callback_data="ref_stat"),
                ]
                button_list1 = [
                    types.InlineKeyboardButton(buttons['receive_gift'], callback_data="gift"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1])


                with open("welcome_image.jpg", "rb") as welcome_photo:
                    await bot.send_photo(chat_id=message.chat.id, photo=welcome_photo)

                await bot.send_message(message.chat.id, text=main_menu_text, reply_markup=reply_markup, parse_mode="MarkdownV2", disable_web_page_preview=True)
            else:
                await change_sub_status(user_id, 0)
                main_menu_text = text_dict['main_menu_no_sub']
                main_menu_text = await escape(main_menu_text, flag=0)

                button_list1 = [
                    types.InlineKeyboardButton(buttons['sub_channel'], url="https://t.me/Liabarvideos"),
                ]
                button_list2 = [
                    types.InlineKeyboardButton(buttons['confirm_sub'], callback_data="confirm_channel_sub"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2])

                with open("welcome_image.jpg", "rb") as welcome_photo:
                    await bot.send_photo(chat_id=message.chat.id, photo=welcome_photo)

                await bot.send_message(message.chat.id, text=main_menu_text, reply_markup=reply_markup, parse_mode="MarkdownV2", disable_web_page_preview=True)

            if not await check_user_exists(user_id):
                try:
                    await add_user_to_db(user_id, username)
                except Exception as error:
                    print(f"Error adding user to db error:\n{error}")
            else:
                await update_username(user_id, username)
    except Exception as e:
        print(f"Error in start message: {e}")


@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    user_id = call.message.chat.id

    if call.data == "confirm_channel_sub":
        await bot.answer_callback_query(call.id)
        channel_member = await bot.get_chat_member(channel_id, user_id)
        if channel_member.status in ["creator", "administrator", "member"]:
            await change_sub_status(user_id, 1)
            text = text_dict['main_menu_sub']
            text = await escape(text, flag=0)

            button_list0 = [
                types.InlineKeyboardButton(buttons['check_referals'], callback_data="referal_check"),
                types.InlineKeyboardButton(buttons['stat'], callback_data="ref_stat"),
            ]
            button_list1 = [
                types.InlineKeyboardButton(buttons['receive_gift'], callback_data="gift"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1])

            try:
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2", disable_web_page_preview=True)
            except:
                pass
        else:
            await change_sub_status(user_id, 0)
            text = text_dict['main_menu_no_sub']
            text = await escape(text, flag=0)

            button_list1 = [
                types.InlineKeyboardButton(buttons['sub_channel'], url="https://t.me/Liabarvideos"),
            ]
            button_list2 = [
                types.InlineKeyboardButton(buttons['confirm_sub'], callback_data="confirm_channel_sub"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2])

            try:
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2", disable_web_page_preview=True)
            except:
                pass

    elif call.data == "referal_check":
        await bot.answer_callback_query(call.id)
        get_referal_count = len(await referals(user_id))

        if get_referal_count >= 4:
            text = text_dict['yes_4_refers'].format(get_referal_count)
            text = await escape(text, flag=0)

            button_list0 = [
                types.InlineKeyboardButton(buttons['check_referals'], callback_data="referal_check"),
                types.InlineKeyboardButton(buttons['stat'], callback_data="ref_stat"),
            ]
            button_list1 = [
                types.InlineKeyboardButton(buttons['receive_gift'], callback_data="gift"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1])

            try:
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2", disable_web_page_preview=True)
            except:
                pass
        else:
            text = text_dict['no_4_refers'].format(get_referal_count, user_id)
            text = await escape(text, flag=0)

            try:
                button_list0 = [
                    types.InlineKeyboardButton(buttons['check_referals'], callback_data="referal_check"),
                    types.InlineKeyboardButton(buttons['stat'], callback_data="ref_stat"),
                ]
                button_list1 = [
                    types.InlineKeyboardButton(buttons['receive_gift'], callback_data="gift"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1])
                try:
                    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2", disable_web_page_preview=True)
                except:
                    pass
            except:
                pass
    elif call.data == "ref_stat":
        await bot.answer_callback_query(call.id)
        text = await escape(text_dict['ref_page'].format(user_id), flag=0)

        try:
            button_list0 = [
                types.InlineKeyboardButton(buttons['check_referals'], callback_data="referal_check"),
                types.InlineKeyboardButton(buttons['stat'], callback_data="ref_stat"),
            ]
            button_list1 = [
                types.InlineKeyboardButton(buttons['receive_gift'], callback_data="gift"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1])

            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2", disable_web_page_preview=True)
        except:
            pass

    elif call.data == "gift":
        await bot.answer_callback_query(call.id)
        get_referal_count = len(await referals(user_id))
        if get_referal_count >= 4:
            with open("video_gift.mp4", "rb") as video_file:
                await bot.send_video(chat_id=call.message.chat.id, video=video_file, caption=text_dict['text_gift'], supports_streaming=True)
        else:
            try:
                text = await escape(text_dict['error_get_gift'], flag=0)
                button_list0 = [
                    types.InlineKeyboardButton(buttons['check_referals'], callback_data="referal_check"),
                    types.InlineKeyboardButton(buttons['stat'], callback_data="ref_stat"),
                ]
                button_list1 = [
                    types.InlineKeyboardButton(buttons['receive_gift'], callback_data="gift"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1])
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2", disable_web_page_preview=True)
            except:
                pass

# async def notif_send():
#     while True:
#         get_first_noti_users = await first_noti()
#         for user_id in get_first_noti_users:
#             with open('first_noti.jpg', 'rb') as first_photo:
#                 await bot.send_photo(chat_id=user_id, photo=first_photo, caption=text_dict['first_noti'])
#             await change_notif_status(user_id, 1)
#             current_time = int(time.time())
#             # time_to_add = 60 * 60 * 3 # + 3 hours
#             time_to_add = 5
#             unix_time = current_time + time_to_add
#             await update_unix(user_id, unix_time)
#
#         await asyncio.sleep(1)
#
#         get_second_noti_users = await second_noti()
#         for user_id in get_second_noti_users:
#             user_unix_time = await get_user_unix_time(user_id)
#             current_time = int(time.time())
#             if current_time >= user_unix_time:
#                 with open('second_video.mp4', 'rb') as second_video:
#                     await bot.send_video(chat_id=user_id, video=second_video, caption=text_dict['second_noti'])
#                 await change_notif_status(user_id, 2)
#                 current_time = int(time.time())
#                 # time_to_add = 60 * 60 * 3 # + 3 hours
#                 time_to_add = 5
#                 unix_time = current_time + time_to_add
#                 await update_unix(user_id, unix_time)
#
#         await asyncio.sleep(1)
#
#         get_third_noti_users = await third_noti()
#         for user_id in get_third_noti_users:
#             user_unix_time = await get_user_unix_time(user_id)коза
#             current_time = int(time.time())
#             if current_time >= user_unix_time:
#                 await bot.send_message(chat_id=user_id, text=text_dict['third_noti'], disable_web_page_preview=True)
#                 await change_notif_status(user_id, 3)
#
#         await asyncio.sleep(1)



async def main():
    try:
        bot_task = asyncio.create_task(bot.polling(non_stop=True, request_timeout=500))
        # notif = asyncio.create_task(notif_send())
        # await asyncio.gather(bot_task, notif)
        await asyncio.gather(bot_task)
    except Exception as error:
        print(error)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()

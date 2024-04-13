import aiosqlite
import asyncio
from config import *


async def check_user_exists(user_id):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT user_id FROM user WHERE user_id = ?", (user_id,))
            user = await result.fetchall()
        return bool(len(user))


async def add_user_to_db(user_id, username):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO user (user_id, username, menu_status, notif, sub_status, refers, unix) VALUES(?, ?, ?, ?, ?, ?, ?)", (user_id, username, 0, 0, 0, '', 0))
            await conn.commit()


async def update_username(user_id, username):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET username = ? WHERE user_id = ?", (username, user_id,))
            await conn.commit()


async def change_menu_status(user_id, status):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET menu_status = ? WHERE user_id = ?", (status, user_id,))
            await conn.commit()


async def get_user_status(user_id):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT menu_status FROM user WHERE user_id = ?", (user_id,))
            user_status = await result.fetchone()
            return user_status[0]


async def referals(user_id):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT refers FROM user WHERE user_id = ?", (user_id,))
            result = await result.fetchone()
            return [i for i in result[0].split(":") if len(i) > 0]


async def add_ref_count(user_id, ref_user_id):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            if int(ref_user_id) != int(user_id):
                get_prev_list = await cursor.execute("SELECT refers FROM user WHERE user_id = ?", (user_id,))
                result = await get_prev_list.fetchone()
                prev_list = [i for i in result[0].split(":") if len(i) > 0]

                get_list_of_all_refers = await cursor.execute("SELECT refers FROM user")
                result_list_of_all_refers = await get_list_of_all_refers.fetchall()
                all_refers_list = [i[0].split(":") for i in result_list_of_all_refers]
                all_refers = []
                for i in all_refers_list:
                    all_refers += i
                all_refers = [i for i in all_refers]


                if str(ref_user_id) not in prev_list and str(ref_user_id) not in all_refers:
                    prev_list.append(f"{ref_user_id}:")
                    result_str = ":".join(prev_list)
                    await cursor.execute("UPDATE user SET refers = ? WHERE user_id = ?", (result_str, user_id,))
                    await conn.commit()


async def change_sub_status(user_id, status):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET sub_status = ? WHERE user_id = ?", (status, user_id,))
            await conn.commit()


async def first_noti():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT user_id FROM user WHERE sub_status = ? AND notif = ?", (1, 0))
            result = await result.fetchall()
            return [i[0] for i in result]


async def second_noti():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT user_id FROM user WHERE sub_status = ? AND notif = ?", (1, 1))
            result = await result.fetchall()
            return [i[0] for i in result]


async def third_noti():
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT user_id FROM user WHERE sub_status = ? AND notif = ?", (1, 2))
            result = await result.fetchall()
            return [i[0] for i in result]


async def change_notif_status(user_id, status):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET notif = ? WHERE user_id = ?", (status, user_id,))
            await conn.commit()


async def update_unix(user_id, unix_time):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET unix = ? WHERE user_id = ?", (unix_time, user_id,))
            await conn.commit()


async def get_user_unix_time(user_id):
    async with aiosqlite.connect(data_base) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT unix FROM user WHERE user_id = ?", (user_id,))
            result = await result.fetchone()
            return result[0]

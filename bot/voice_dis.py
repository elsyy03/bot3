import discord
from discord.ext import commands
import asyncio
import logging

# --- Настройки ---
VOICE_TRIGGER_CHANNEL_ID = 1432954905022304256  # ID канала #создать-войс
MODERATOR_ROLE_ID = 1432778608631615589        # ID роли модератора
CATEGORY_PARENT_ID = 1432957058592014386        # ID категории для приватных каналов
# --- /Настройки ---

# Включаем необходимые нам intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Словарь для отслеживания владельцев каналов
channel_owners = {}

# Словарь для отслеживания, кто уже имеет канал
user_channels = {}

# Вспомогательная функция для проверки владельца канала или модератора
def is_channel_owner_or_moderator(voice_channel_id, user):
    owner_id = channel_owners.get(voice_channel_id)
    is_owner = owner_id == user.id
    is_moderator = any(role.id == MODERATOR_ROLE_ID for role in user.roles) if MODERATOR_ROLE_ID else False
    return is_owner or is_moderator

# --- События ---
@bot.event
async def on_ready():
    print(f'Бот {bot.user} подключился!')

@bot.event
async def on_voice_state_update(member, before, after):
    # 1. Обработка входа в триггерный канал
    if after.channel and after.channel.id == VOICE_TRIGGER_CHANNEL_ID:
        # Проверяем, есть ли у пользователя уже канал
        if member.id in user_channels:
            existing_channel_id = user_channels[member.id]
            existing_channel = bot.get_channel(existing_channel_id)
            if existing_channel and len(existing_channel.members) > 0:
                # Если канал существует и не пуст — переносим туда
                await member.move_to(existing_channel)
                await member.send(f"Вы уже имеете канал: {existing_channel.mention}. Перемещены туда.")
                return
            else:
                # Канал пуст — удаляем его и создаём новый
                if existing_channel:
                    await existing_channel.delete(reason="Пользователь создал новый канал")
                    del channel_owners[existing_channel_id]
                    del user_channels[member.id]

        guild = member.guild
        category = None
        if CATEGORY_PARENT_ID:
            category = discord.utils.get(guild.categories, id=CATEGORY_PARENT_ID)
        else:
            # Создаём новую приватную категорию
            category_overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(view_channel=True, manage_channels=True, manage_permissions=True)
            }
            category = await guild.create_category(
                f"Приват {member.display_name}",
                overwrites=category_overwrites
            )

        if not category:
            logging.error("Категория не найдена и не создана.")
            return

        # Создаём голосовой канал в категории
        voice_channel_overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=False),
            member: discord.PermissionOverwrite(connect=True, manage_channels=True, manage_permissions=True)
        }
        voice_channel = await guild.create_voice_channel(
            f"Канал {member.display_name}",
            category=category,
            overwrites=voice_channel_overwrites
        )

        # Перемещаем пользователя в новый канал
        await member.move_to(voice_channel)

        # Запоминаем владельца и связь пользователь <-> канал
        channel_owners[voice_channel.id] = member.id
        user_channels[member.id] = voice_channel.id

        # Отправляем панель управления в текстовый канал #настройка-канала
        control_text_channel = bot.get_channel(CONTROL_TEXT_CHANNEL_ID)
        if control_text_channel:
            try:
                view = ChannelControlView(voice_channel.id, bot)
                panel_msg = await control_text_channel.send(
                    f"⚙️ Управление каналом `{voice_channel.name}`\n"
                    f"Владелец: {member.mention}\n"
                    f"Голосовой канал: {voice_channel.mention}",
                    view=view
                )
            except Exception as e:
                logging.error(f"Ошибка при отправке панели в канал: {e}")
        else:
            logging.error("Канал для управления не найден.")

    # 2. Обработка выхода из канала
    if before.channel:
        channel_id = before.channel.id
        if channel_id in channel_owners:
            # Проверяем, остались ли участники
            if len(before.channel.members) == 0:
                category = before.channel.category
                # Удаляем канал
                await before.channel.delete(reason="Пустой приватный канал")
                # Удаляем запись о владельце
                del channel_owners[channel_id]
                # Удаляем запись о пользователе
                owner_id = next((uid for uid, cid in user_channels.items() if cid == channel_id), None)
                if owner_id:
                    del user_channels[owner_id]
                # Удаляем категорию, если она пуста и была создана ботом (опционально)
                # if category and len(category.channels) == 0 and category.name.startswith("Приват"):
                #     await category.delete(reason="Пустая приватная категория")

# --- Запуск бота ---
bot.run(os.getenv("DISCORD_TOKEN"))
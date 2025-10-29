import discord
from discord.ext import commands, tasks
from discord import ui
from datetime import datetime, timedelta
import asyncio
import json
import os

# --- НАСТРОЙКИ ---
# Файлы для хранения данных
WARNS_FILE = "warns.json"
TEMPORARY_PUNISHMENTS_FILE = "temporary_punishments.json"
TICKETS_FILE = "tickets.json"
USER_ROLES_BACKUP_FILE = "user_roles_backup.json"
MODERATION_STATS_FILE = "moderation_stats.json" # Новый файл для статистики
# --- ФУНКЦИИ ЗАГРУЗКИ И СОХРАНЕНИЯ ДАННЫХ ---
def load_warns():
    if os.path.exists(WARNS_FILE):
        with open(WARNS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_warns(warns):
    with open(WARNS_FILE, 'w', encoding='utf-8') as f:
        json.dump(warns, f, ensure_ascii=False, indent=2)

def load_temporary_punishments():
    if os.path.exists(TEMPORARY_PUNISHMENTS_FILE):
        with open(TEMPORARY_PUNISHMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_temporary_punishments(punishments):
    with open(TEMPORARY_PUNISHMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(punishments, f, ensure_ascii=False, indent=2)

def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_tickets(tickets):
    with open(TICKETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tickets, f, ensure_ascii=False, indent=2)

def load_user_roles():
    if os.path.exists(USER_ROLES_FILE):
        with open(USER_ROLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_user_roles(user_roles):
    with open(USER_ROLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_roles, f, ensure_ascii=False, indent=2)

# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ (БУДУТ ИНИЦИАЛИЗИРОВАНЫ В on_ready) ---
moderator_role_name = "Модератор"
helper_role_name = "Хелпер"
mute_role_name = "МУТ"
ban_role_name = "БАН"
log_channel_name = "логи"
tickets_category_name = "ТИКЕТЫ"
help_channel_name = "помощь"
log_tickets_channel_name = "логи-тикетов"
# --- ФУНКЦИИ ЗАГРУЗКИ И СОХРАНЕНИЯ ДАННЫХ ---
def load_warns():
    if os.path.exists(WARNS_FILE):
        with open(WARNS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_warns(warns):
    with open(WARNS_FILE, 'w', encoding='utf-8') as f:
        json.dump(warns, f, ensure_ascii=False, indent=2)

def load_temporary_punishments():
    if os.path.exists(TEMPORARY_PUNISHMENTS_FILE):
        with open(TEMPORARY_PUNISHMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_temporary_punishments(punishments):
    with open(TEMPORARY_PUNISHMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(punishments, f, ensure_ascii=False, indent=2)

def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_tickets(tickets):
    with open(TICKETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tickets, f, ensure_ascii=False, indent=2)

def load_user_roles():
    if os.path.exists(USER_ROLES_FILE):
        with open(USER_ROLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_user_roles(user_roles):
    with open(USER_ROLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_roles, f, ensure_ascii=False, indent=2)
# --- ФУНКЦИИ ЗАГРУЗКИ И СОХРАНЕНИЯ ДАННЫХ ---
def load_json_file(filename, default_value=None):
    if default_value is None:
        default_value = {}
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"Ошибка загрузки {filename}, создаем пустой файл.")
            return default_value
    return default_value

def save_json_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- НОВАЯ ФУНКЦИЯ: СТАТИСТИКА МОДЕРАТОРОВ ---
def load_mod_stats():
    return load_json_file(MODERATION_STATS_FILE)

def save_mod_stats(stats):
    save_json_file(MODERATION_STATS_FILE, stats)

def update_mod_stats(guild_id: int, moderator_id: int, action_type: str):
    """Обновляет статистику модератора"""
    stats = load_mod_stats()
    guild_str = str(guild_id)
    mod_str = str(moderator_id)
    
    if guild_str not in stats:
        stats[guild_str] = {}
    if mod_str not in stats[guild_str]:
        stats[guild_str][mod_str] = {'bans': 0, 'mutes': 0, 'warns': 0, 'tickets_closed': 0}
    
    if action_type in stats[guild_str][mod_str]:
        stats[guild_str][mod_str][action_type] += 1
    
    save_mod_stats(stats)

# --- КЛАССЫ ВЬЮ (ДЛЯ КНОПОК И МОДАЛОВ) ---

class TicketCreateView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CreateTicketButton())

class CreateTicketButton(ui.Button):
    def __init__(self):
        super().__init__(label='Создать тикет', style=discord.ButtonStyle.primary, emoji='📩', custom_id='persistent_create_ticket')

    async def callback(self, interaction: discord.Interaction):
        modal = TicketModal()
        await interaction.response.send_modal(modal)

class TicketCloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton())

class CloseTicketButton(ui.Button):
    def __init__(self):
        super().__init__(label='Закрыть тикет', style=discord.ButtonStyle.danger, emoji='🔒', custom_id='persistent_close_ticket')

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ У вас нет прав для закрытия тикетов!", ephemeral=True)
            return

        tickets = load_json_file(TICKETS_FILE)
        ticket_key = f"{interaction.guild.id}_{interaction.channel.id}"
        if ticket_key not in tickets:
            await interaction.response.send_message("❌ Этот канал не является тикетом!", ephemeral=True)
            return

        ticket_info = tickets[ticket_key]

        embed = discord.Embed(
            title="📋 История тикета",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(name="👤 Создатель", value=f"<@{ticket_info['user_id']}>", inline=True)
        embed.add_field(name="📅 Создан", value=f"<t:{int(ticket_info['created_at'])}:R>", inline=True)
        embed.add_field(name="📝 Тема", value=ticket_info['topic'], inline=False)

        messages = []
        async for message in interaction.channel.history(limit=100):
            if not message.author.bot:
                messages.append(f"**{message.author.display_name}:** {message.content}")
        if messages:
            history_text = "\n".join(reversed(messages[-20:]))
            if len(history_text) > 1000:
                history_text = history_text[:1000] + "..."
            embed.add_field(name="💬 История сообщений", value=history_text, inline=False)

        log_channel = discord.utils.get(interaction.guild.channels, name=log_tickets_channel_name)
        if not log_channel:
            try:
                log_channel = await interaction.guild.create_text_channel(
                    log_tickets_channel_name,
                    reason="Канал для логирования закрытых тикетов"
                )
            except discord.Forbidden:
                print(f"Не удалось создать канал {log_tickets_channel_name}")

        if log_channel:
            await log_channel.send(embed=embed)

        del tickets[ticket_key]
        save_json_file(TICKETS_FILE, tickets)

        # --- ОБНОВЛЕНИЕ СТАТИСТИКИ ЗАКРЫТИЯ ТИКЕТА ---
        update_mod_stats(interaction.guild.id, interaction.user.id, 'tickets_closed')
        # --- /ОБНОВЛЕНИЕ ---

        # --- ЛОГИРОВАНИЕ ЗАКРЫТИЯ ТИКЕТА ---
        log_channel_general = discord.utils.get(interaction.guild.channels, name=log_channel_name)
        if not log_channel_general:
            try:
                log_channel_general = await interaction.guild.create_text_channel(
                    log_channel_name,
                    reason="Канал для логирования действий модерации"
                )
            except discord.Forbidden:
                print(f"Не удалось создать канал {log_channel_name}")

        if log_channel_general:
            embed_log = discord.Embed(
                title="🎫 Тикет закрыт",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            embed_log.add_field(name="👤 Создатель тикета", value=f"<@{ticket_info['user_id']}>", inline=True)
            embed_log.add_field(name="👮 Закрыл", value=interaction.user.mention, inline=True)
            embed_log.add_field(name="📝 Тема", value=ticket_info['topic'], inline=False)
            embed_log.add_field(name="💬 Канал", value=interaction.channel.mention, inline=False)
            await log_channel_general.send(embed=embed_log)
        # --- /ЛОГИРОВАНИЕ ---

        await interaction.response.send_message("🔒 Тикет закрывается...")
        await asyncio.sleep(3)
        await interaction.channel.delete()

class TicketModal(ui.Modal, title='Создание тикета'):
    topic = ui.TextInput(label='Тема тикета', placeholder='Опишите кратко вашу проблему...', required=True, max_length=50)
    description = ui.TextInput(label='Подробное описание', placeholder='Опишите вашу проблему подробно...', style=discord.TextStyle.paragraph, required=True, max_length=500)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket(interaction, self.topic.value, self.description.value)

class WarnModal(ui.Modal, title='Выдать варн'):
    def __init__(self, target_user):
        super().__init__()
        self.target_user = target_user

    reason = ui.TextInput(label='Причина варна', placeholder='Введите причину...', required=True, max_length=100)

    async def on_submit(self, interaction: discord.Interaction):
        await add_warn(interaction, self.target_user, self.reason.value)
        try:
            await send_punishment_dm(self.target_user, "варн", self.reason.value, None, interaction.guild.name)
        except discord.HTTPException:
            pass
        # --- ОБНОВЛЕНИЕ СТАТИСТИКИ ВАРНОВ ---
        update_mod_stats(interaction.guild.id, interaction.user.id, 'warns')
        # --- /ОБНОВЛЕНИЕ ---
        await interaction.response.send_message(f"✅ {self.target_user.mention} получил варн по причине: {self.reason.value}", ephemeral=True)

class MuteModal(ui.Modal, title='Мут пользователя'):
    def __init__(self, target_user):
        super().__init__()
        self.target_user = target_user

    reason = ui.TextInput(label='Причина мута', placeholder='Введите причину...', required=True, max_length=100)
    duration = ui.TextInput(label='Длительность', placeholder='Пример: 30m, 2h, 1d, 7d (макс 28 дней)', default='30m', required=True, max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            duration_seconds = await parse_duration(self.duration.value)
            if not duration_seconds:
                await interaction.response.send_message("❌ Неверный формат времени! Используйте: 30m, 2h, 1d", ephemeral=True)
                return
            duration_minutes = duration_seconds // 60
            if duration_minutes > 40320: # 28 дней в минутах
                await interaction.response.send_message("❌ Максимальная длительность мута - 28 дней!", ephemeral=True)
                return

            mute_role = await get_or_create_mute_role(interaction.guild)
            await self.target_user.add_roles(mute_role, reason=f"Мут: {self.reason.value}")
            await add_temporary_punishment(interaction.guild.id, self.target_user.id, 'mute', duration_seconds, self.reason.value, interaction.user.id)
            
            # --- ОБНОВЛЕНИЕ СТАТИСТИКИ МУТОВ ---
            update_mod_stats(interaction.guild.id, interaction.user.id, 'mutes')
            # --- /ОБНОВЛЕНИЕ ---

            # --- ЛОГИРОВАНИЕ МУТА ---
            await log_action(interaction, self.target_user, f"Мут ({self.duration.value})", self.reason.value)
            # --- /ЛОГИРОВАНИЕ ---

            await send_punishment_dm(self.target_user, "мут", self.reason.value, self.duration.value, interaction.guild.name)
            await interaction.response.send_message(f"✅ {self.target_user.mention} получил мут на {self.duration.value} по причине: {self.reason.value}", ephemeral=True)
        except Exception as e:
            print(f"Ошибка при выдаче мута: {e}")
            await interaction.response.send_message(f"❌ Произошла ошибка при выдаче мута: {str(e)}", ephemeral=True)

class BanModal(ui.Modal, title='Бан пользователя'):
    def __init__(self, target_user):
        super().__init__()
        self.target_user = target_user

    reason = ui.TextInput(label='Причина бана', placeholder='Введите причину бана...', required=True, max_length=100)
    duration = ui.TextInput(label='Длительность бана', placeholder='Пример: 1h, 2d, 30m (оставьте пустым для перманентного)', required=False, max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            duration_text = self.duration.value.strip() if self.duration.value else "перманентный"
            duration_seconds = await parse_duration(self.duration.value) if self.duration.value else None

            ban_role = await get_or_create_ban_role(interaction.guild)
            await save_user_roles_backup(interaction.guild.id, self.target_user.id, self.target_user.roles)
            await self.target_user.add_roles(ban_role, reason=f"Временный бан: {self.reason.value}")

            for role in self.target_user.roles:
                if role != interaction.guild.default_role and role != ban_role:
                    try:
                        await self.target_user.remove_roles(role, reason="Снятие ролей при временном бане")
                    except:
                        pass

            # --- ОБНОВЛЕНИЕ СТАТИСТИКИ БАНОВ ---
            update_mod_stats(interaction.guild.id, interaction.user.id, 'bans')
            # --- /ОБНОВЛЕНИЕ ---

            # --- ЛОГИРОВАНИЕ БАНА ---
            await log_action(interaction, self.target_user, f"Временный бан ({duration_text})", self.reason.value)
            # --- /ЛОГИРОВАНИЕ ---

            if duration_seconds:
                await add_temporary_punishment(interaction.guild.id, self.target_user.id, 'temp_ban', duration_seconds, self.reason.value, interaction.user.id)

            await send_punishment_dm(self.target_user, "временный бан", self.reason.value, duration_text, interaction.guild.name)
            await interaction.response.send_message(f"✅ {self.target_user.mention} получил временный бан по причине: {self.reason.value}\nДлительность: {duration_text}", ephemeral=True)
        except Exception as e:
            print(f"Ошибка при выдаче бана: {e}")
            await interaction.response.send_message(f"❌ Произошла ошибка при выдаче бана: {str(e)}", ephemeral=True)

class ModerationView(ui.View):
    def __init__(self, target_user: discord.Member):
        super().__init__(timeout=30)
        self.target_user = target_user

    @ui.button(label='Кикнуть', style=discord.ButtonStyle.danger, emoji='👢')
    async def kick_button(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("❌ У вас нет прав для кика!", ephemeral=True)
            return
        try:
            reason = f"Кикнут через меню {interaction.user}"
            await self.target_user.kick(reason=reason)
            
            # --- ЛОГИРОВАНИЕ КИКА ---
            await log_action(interaction, self.target_user, "Кик", reason)
            # --- /ЛОГИРОВАНИЕ ---

            try:
                await send_punishment_dm(self.target_user, "кик", reason, None, interaction.guild.name)
            except discord.HTTPException:
                pass
            await interaction.response.send_message(f"✅ {self.target_user.mention} был кикнут!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ У бота нет прав для кика!", ephemeral=True)

    @ui.button(label='Забанить', style=discord.ButtonStyle.danger, emoji='🔨')
    async def ban_button(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ У вас нет прав для бана!", ephemeral=True)
            return
        modal = BanModal(self.target_user)
        await interaction.response.send_modal(modal)

    @ui.button(label='Мут', style=discord.ButtonStyle.primary, emoji='🔇')
    async def mute_button(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ У вас нет прав для мута!", ephemeral=True)
            return
        modal = MuteModal(self.target_user)
        await interaction.response.send_modal(modal)

    @ui.button(label='Снять наказания', style=discord.ButtonStyle.success, emoji='🔓')
    async def unpunish_button(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ У вас нет прав для снятия наказаний!", ephemeral=True)
            return
        try:
            mute_role = discord.utils.get(interaction.guild.roles, name=mute_role_name)
            if mute_role and mute_role in self.target_user.roles:
                await self.target_user.remove_roles(mute_role, reason="Снятие мута через меню")
                
                # --- ЛОГИРОВАНИЕ СНЯТИЯ МУТА ---
                await log_action(interaction, self.target_user, "Снятие мута", "Через меню модерации")
                # --- /ЛОГИРОВАНИЕ ---

            ban_role = discord.utils.get(interaction.guild.roles, name=ban_role_name)
            if ban_role and ban_role in self.target_user.roles:
                await self.target_user.remove_roles(ban_role, reason="Снятие бана через меню")
                
                # --- ЛОГИРОВАНИЕ СНЯТИЯ БАНА ---
                await log_action(interaction, self.target_user, "Снятие бана", "Через меню модерации")
                # --- /ЛОГИРОВАНИЕ ---

                await restore_user_roles_backup(interaction.guild, self.target_user)

            await interaction.response.send_message(f"✅ Наказания сняты с {self.target_user.mention}!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Ошибка при снятии наказаний: {str(e)}", ephemeral=True)

    @ui.button(label='Варн', style=discord.ButtonStyle.secondary, emoji='⚠️')
    async def warn_button(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ У вас нет прав для выдачи варнов!", ephemeral=True)
            return
        modal = WarnModal(self.target_user)
        await interaction.response.send_modal(modal)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except:
            pass

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

async def parse_duration(duration_str: str) -> int:
    if not duration_str:
        return None
    duration_str = duration_str.lower().strip()
    multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800}
    total_seconds = 0
    current_number = ''
    for char in duration_str:
        if char.isdigit():
            current_number += char
        elif char in multipliers:
            if current_number:
                total_seconds += int(current_number) * multipliers[char]
                current_number = ''
        else:
            return None
    return total_seconds if total_seconds > 0 else None

async def send_punishment_dm(user: discord.Member, punishment_type: str, reason: str, duration: str, guild_name: str):
    try:
        embed = discord.Embed(title="🚨 Уведомление о наказании", color=discord.Color.red(), timestamp=datetime.now())
        punishment_types = {"бан": "🔨 Бан", "временный бан": "🔨 Временный бан", "мут": "🔇 Мут", "кик": "👢 Кик", "варн": "⚠️ Варн"}
        embed.add_field(name="🔧 Тип наказания", value=punishment_types.get(punishment_type, punishment_type), inline=True)
        if duration: embed.add_field(name="⏱️ Длительность", value=duration, inline=True)
        embed.add_field(name="📋 Причина", value=reason or "Не указана", inline=False)
        if punishment_type in ["бан", "временный бан", "мут"] and duration:
            embed.add_field(name="ℹ️ Информация", value="Наказание будет автоматически снято по истечении времени", inline=False)
        await user.send(embed=embed)
        return True
    except discord.Forbidden:
        return False
    except Exception:
        return False

async def log_action(interaction: discord.Interaction, target_user: discord.Member, action: str, reason: str = ""):
    """Логирование действий в канал #логи"""
    log_channel = discord.utils.get(interaction.guild.channels, name=log_channel_name)
    if log_channel is None:
        try:
            log_channel = await interaction.guild.create_text_channel(
                log_channel_name,
                reason="Канал для логирования действий модерации"
            )
        except discord.Forbidden:
            print(f"Бот не может создать канал {log_channel_name}.")
            return False
    embed = discord.Embed(title="📝 Лог модерации", color=discord.Color.blue(), timestamp=datetime.now())
    embed.add_field(name="👮 Модератор", value=interaction.user.mention, inline=True)
    embed.add_field(name="👤 Пользователь", value=target_user.mention, inline=True)
    embed.add_field(name="🔧 Действие", value=action, inline=True)
    if reason: embed.add_field(name="📋 Причина", value=reason, inline=False)
    embed.set_footer(text=f"ID: {target_user.id}")
    try:
        await log_channel.send(embed=embed)
        return True
    except Exception as e:
        print(f"Ошибка при отправке в логи: {e}")
        return False

async def add_temporary_punishment(guild_id: int, user_id: int, punishment_type: str, duration: int, reason: str, moderator_id: int):
    punishments = load_json_file(TEMPORARY_PUNISHMENTS_FILE)
    key = f"{guild_id}_{user_id}"
    end_time = datetime.now() + timedelta(seconds=duration)
    punishments[key] = {'type': punishment_type, 'end_time': end_time.isoformat(), 'reason': reason, 'moderator_id': moderator_id, 'guild_id': guild_id, 'user_id': user_id}
    save_json_file(TEMPORARY_PUNISHMENTS_FILE, punishments)

async def save_user_roles_backup(guild_id: int, user_id: int, roles):
    """Сохраняет роли пользователя перед выдачей бана"""
    user_roles_backup_data = load_json_file(USER_ROLES_BACKUP_FILE)
    key = f"{guild_id}_{user_id}"
    role_ids = [role.id for role in roles if role != role.guild.default_role]
    user_roles_backup_data[key] = {'role_ids': role_ids, 'saved_at': datetime.now().isoformat()}
    save_json_file(USER_ROLES_BACKUP_FILE, user_roles_backup_data)

async def restore_user_roles_backup(guild: discord.Guild, user: discord.Member):
    """Восстанавливает роли пользователя после снятия бана"""
    user_roles_backup_data = load_json_file(USER_ROLES_BACKUP_FILE)
    key = f"{guild.id}_{user.id}"
    if key in user_roles_backup_data:
        role_ids = user_roles_backup_data[key]['role_ids']
        for role_id in role_ids:
            role = guild.get_role(role_id)
            if role and role not in user.roles:
                try:
                    await user.add_roles(role, reason="Восстановление ролей после бана")
                except:
                    pass
        del user_roles_backup_data[key]
        save_json_file(USER_ROLES_BACKUP_FILE, user_roles_backup_data)

async def get_or_create_ban_role(guild: discord.Guild):
    ban_role = discord.utils.get(guild.roles, name=ban_role_name)
    if ban_role is None:
        ban_role = await guild.create_role(name=ban_role_name, color=discord.Color.dark_red(), reason="Роль для временного бана")
        for channel in guild.channels:
            try:
                if isinstance(channel, discord.TextChannel):
                    if channel.name == help_channel_name:
                        await channel.set_permissions(ban_role, view_channel=True, send_messages=False, read_message_history=True)
                    else:
                        await channel.set_permissions(ban_role, view_channel=False, send_messages=False)
                elif isinstance(channel, discord.VoiceChannel):
                    await channel.set_permissions(ban_role, view_channel=False, connect=False)
            except discord.Forbidden:
                continue
    return ban_role

async def get_or_create_mute_role(guild: discord.Guild):
    mute_role = discord.utils.get(guild.roles, name=mute_role_name)
    if mute_role is None:
        mute_role = await guild.create_role(name=mute_role_name, color=discord.Color.dark_gray(), reason="Роль для мута")
        for channel in guild.channels:
            try:
                if isinstance(channel, discord.TextChannel):
                    await channel.set_permissions(mute_role, send_messages=False, add_reactions=False)
            except discord.Forbidden:
                continue
    return mute_role

async def setup_help_channel(guild: discord.Guild):
    help_channel = discord.utils.get(guild.text_channels, name=help_channel_name)
    if not help_channel:
        try:
            help_channel = await guild.create_text_channel(help_channel_name, topic="Канал для получения помощи. Создайте тикет для обращения к администрации")
        except discord.Forbidden:
            return None
    embed = discord.Embed(title="🆘 Центр помощи", description="Если вам нужна помощь администрации, создайте тикет нажав на кнопку ниже", color=discord.Color.blue())
    embed.add_field(name="📋 Как это работает?", value="1. Нажмите кнопку 'Создать тикет'\n2. Заполните форму\n3. Опишите вашу проблему в созданном канале", inline=False)
    embed.add_field(name="⏱ Время ответа", value="Администрация ответит в течение 24 часов", inline=True)
    embed.add_field(name="🔒 Конфиденциальность", value="Ваш тикет виден только вам и администрации", inline=True)
    view = TicketCreateView()
    try:
        await help_channel.purge(limit=10)
        await help_channel.send(embed=embed, view=view)
    except discord.Forbidden:
        pass
    return help_channel

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С ВАРНАМИ ---

async def add_warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    warns = load_json_file(WARNS_FILE)
    guild_id = str(interaction.guild.id)
    user_id = str(user.id)
    if guild_id not in warns: warns[guild_id] = {}
    if user_id not in warns[guild_id]: warns[guild_id][user_id] = []
    warn_data = {'reason': reason, 'moderator': f"{interaction.user.name} ({interaction.user.id})", 'timestamp': datetime.now().isoformat()}
    warns[guild_id][user_id].append(warn_data)
    save_json_file(WARNS_FILE, warns)
    
    # --- ОБНОВЛЕНИЕ СТАТИСТИКИ ВАРНОВ ---
    update_mod_stats(interaction.guild.id, interaction.user.id, 'warns')
    # --- /ОБНОВЛЕНИЕ ---

    # --- ЛОГИРОВАНИЕ ВАРНА ---
    await log_action(interaction, user, "Варн", reason)
    # --- /ЛОГИРОВАНИЕ ---

    warn_count = len(warns[guild_id][user_id])
    if warn_count >= 3:
        moderator_role = discord.utils.get(interaction.guild.roles, name=moderator_role_name)
        helper_role = discord.utils.get(interaction.guild.roles, name=helper_role_name)
        roles_to_remove = []
        if moderator_role and moderator_role in user.roles: roles_to_remove.append(moderator_role)
        if helper_role and helper_role in user.roles: roles_to_remove.append(helper_role)
        if roles_to_remove:
            await user.remove_roles(*roles_to_remove, reason="Автоматическое снятие ролей за 3+ варна")
            role_names = ", ".join([role.name for role in roles_to_remove])
            
            # --- ЛОГИРОВАНИЕ АВТО-СНЯТИЯ РОЛЕЙ ---
            await log_action(interaction, user, "Авто-снятие ролей", f"Сняты роли: {role_names} за 3+ варна")
            # --- /ЛОГИРОВАНИЕ ---

    embed = discord.Embed(title="⚠️ Выдан варн", color=discord.Color.orange(), timestamp=datetime.now())
    embed.add_field(name="👤 Пользователь", value=user.mention, inline=True)
    embed.add_field(name="👮 Модератор", value=interaction.user.mention, inline=True)
    embed.add_field(name="📊 Всего варнов", value=warn_count, inline=True)
    embed.add_field(name="📋 Причина", value=reason, inline=False)
    await interaction.followup.send(embed=embed, ephemeral=True)

async def remove_warn(interaction: discord.Interaction, user: discord.Member, warn_index: int = None):
    warns = load_json_file(WARNS_FILE)
    guild_id = str(interaction.guild.id)
    user_id = str(user.id)
    if guild_id not in warns or user_id not in warns[guild_id] or not warns[guild_id][user_id]:
        await interaction.response.send_message("❌ У пользователя нет варнов!", ephemeral=True)
        return
    if warn_index is None:
        removed_warn = warns[guild_id][user_id].pop()
    else:
        if warn_index < 1 or warn_index > len(warns[guild_id][user_id]):
            await interaction.response.send_message("❌ Неверный номер варна!", ephemeral=True)
            return
        removed_warn = warns[guild_id][user_id].pop(warn_index - 1)
    save_json_file(WARNS_FILE, warns)
    
    # --- ЛОГИРОВАНИЕ СНЯТИЯ ВАРНА ---
    await log_action(interaction, user, "Снятие варна", f"Снят варн: {removed_warn['reason']}")
    # --- /ЛОГИРОВАНИЕ ---

    await interaction.response.send_message(f"✅ Снят варн с {user.mention}\nПричина: {removed_warn['reason']}", ephemeral=True)

# --- ФУНКЦИЯ СОЗДАНИЯ ТИКЕТА ---

async def create_ticket(interaction: discord.Interaction, topic: str, description: str):
    guild = interaction.guild
    category = discord.utils.get(guild.categories, name=tickets_category_name)
    if not category:
        try:
            category = await guild.create_category_channel(tickets_category_name)
        except discord.Forbidden:
            await interaction.response.send_message("❌ У бота нет прав для создания каналов!", ephemeral=True)
            return
    ticket_number = len(load_json_file(TICKETS_FILE)) + 1
    try:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True, manage_channels=True)
        }
        moderator_role = discord.utils.get(guild.roles, name=moderator_role_name)
        if moderator_role:
            overwrites[moderator_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)
        ticket_channel = await category.create_text_channel(
            name=f"тикет-{ticket_number}-{interaction.user.display_name}",
            overwrites=overwrites,
            topic=f"Тикет от {interaction.user.display_name}: {topic}"
        )
        tickets = load_json_file(TICKETS_FILE)
        tickets[f"{guild.id}_{ticket_channel.id}"] = {'user_id': interaction.user.id, 'topic': topic, 'created_at': datetime.now().timestamp(), 'description': description}
        save_json_file(TICKETS_FILE, tickets)
        embed = discord.Embed(title=f"📩 Тикет #{ticket_number}", color=discord.Color.green(), timestamp=datetime.now())
        embed.add_field(name="👤 Создатель", value=interaction.user.mention, inline=True)
        embed.add_field(name="📝 Тема", value=topic, inline=True)
        embed.add_field(name="📋 Описание", value=description, inline=False)
        embed.set_footer(text="Тикет будет закрыт через 24 часа неактивности")
        view = TicketCloseView()
        message = await ticket_channel.send(embed=embed, view=view)
        await ticket_channel.send(f"🔔 {interaction.user.mention} ваш тикет создан! Опишите вашу проблему подробнее.")
        if moderator_role: await ticket_channel.send(f"📢 {moderator_role.mention} новый тикет требует внимания!")
        await interaction.response.send_message(f"✅ Тикет создан: {ticket_channel.mention}", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ У бота нет прав для создания каналов!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка при создании тикета: {str(e)}", ephemeral=True)

# --- ТАСК ДЛЯ ПРОВЕРКИ ВРЕМЕННЫХ НАКАЗАНИЙ ---

@tasks.loop(minutes=1)
async def check_temporary_punishments():
    punishments = load_json_file(TEMPORARY_PUNISHMENTS_FILE)
    current_time = datetime.now()
    to_remove = []
    for key, punishment in punishments.items():
        end_time = datetime.fromisoformat(punishment['end_time'])
        if current_time >= end_time:
            guild = bot.get_guild(punishment['guild_id'])
            if guild:
                try:
                    user = guild.get_member(punishment['user_id'])
                    if user:
                        if punishment['type'] == 'temp_ban':
                            ban_role = discord.utils.get(guild.roles, name=ban_role_name)
                            if ban_role and ban_role in user.roles:
                                await user.remove_roles(ban_role, reason="Автоматическое снятие временного бана")
                                await restore_user_roles_backup(guild, user)
                                
                                # --- ЛОГИРОВАНИЕ АВТО-СНЯТИЯ БАНА ---
                                await log_auto_punishment_remove(guild, user, "бан", punishment['reason'])
                                # --- /ЛОГИРОВАНИЕ ---

                        elif punishment['type'] == 'mute':
                            mute_role = discord.utils.get(guild.roles, name=mute_role_name)
                            if mute_role and mute_role in user.roles:
                                await user.remove_roles(mute_role, reason="Автоматическое снятие мута")
                                
                                # --- ЛОГИРОВАНИЕ АВТО-СНЯТИЯ МУТА ---
                                await log_auto_punishment_remove(guild, user, "мут", punishment['reason'])
                                # --- /ЛОГИРОВАНИЕ ---

                except Exception as e:
                    print(f"Ошибка при снятии наказания: {e}")
            to_remove.append(key)
    for key in to_remove:
        del punishments[key]
    if to_remove:
        save_json_file(TEMPORARY_PUNISHMENTS_FILE, punishments)

# --- НОВАЯ ФУНКЦИЯ ДЛЯ ЛОГИРОВАНИЯ АВТОМАТИЧЕСКОГО СНЯТИЯ НАКАЗАНИЙ ---
async def log_auto_punishment_remove(guild: discord.Guild, user: discord.Member, punishment_type: str, reason: str):
    log_channel = discord.utils.get(guild.channels, name=log_channel_name)
    if not log_channel:
        try:
            log_channel = await guild.create_text_channel(log_channel_name, reason="Канал для логирования действий модерации")
        except discord.Forbidden:
            print(f"Бот не может создать канал {log_channel_name} для логирования авто-снятия.")
            return
    embed = discord.Embed(title="🔓 Автоматическое снятие наказания", color=discord.Color.green(), timestamp=datetime.now())
    embed.add_field(name="👤 Пользователь", value=user.mention, inline=True)
    embed.add_field(name="🔧 Тип наказания", value=punishment_type, inline=True)
    embed.add_field(name="📋 Причина", value=reason or "Истекло время наказания", inline=True)
    try:
        await log_channel.send(embed=embed)
    except Exception as e:
        print(f"Ошибка при отправке лога авто-снятия: {e}")

# --- БОТ ---

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- КОМАНДЫ ---

@bot.tree.command(name="action", description="Меню модерации для пользователя")
async def action(interaction: discord.Interaction, пользователь: discord.Member):
    """Открывает меню модерации для указанного пользователя"""
    if пользователь == bot.user:
        await interaction.response.send_message("❌ Нельзя применить действия к боту!", ephemeral=True)
        return
    if пользователь == interaction.user:
        await interaction.response.send_message("❌ Нельзя применить действия к себе!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🚨 Меню модерации",
        description=f"Выберите действие для пользователя {пользователь.mention}",
        color=discord.Color.orange()
    )
    embed.add_field(name="👤 Пользователь", value=f"{пользователь.display_name} ({пользователь.id})", inline=True)
    embed.add_field(name="📅 Присоединился", value=f"<t:{int(пользователь.joined_at.timestamp())}:R>", inline=True)
    embed.set_thumbnail(url=пользователь.display_avatar.url)
    view = ModerationView(пользователь)
    # Отправляем сообщение сразу, так как это просто меню
    await interaction.response.send_message(embed=embed, view=view)
    view.message = await interaction.original_response()

@bot.tree.command(name="moderator", description="Выдать роль модератора пользователю")
async def moderator(interaction: discord.Interaction, пользователь: discord.Member):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ У вас нет прав для выдачи ролей!", ephemeral=True)
        return
    role = discord.utils.get(interaction.guild.roles, name=moderator_role_name)
    if role is None:
        try:
            role = await interaction.guild.create_role(
                name=moderator_role_name,
                color=discord.Color.blue(),
                permissions=discord.Permissions(kick_members=True, ban_members=True, manage_messages=True, moderate_members=True),
                reason="Создано ботом для команды /moderator"
            )
        except discord.Forbidden:
            await interaction.response.send_message("❌ У бота нет прав для создания ролей!", ephemeral=True)
            return
    try:
        await пользователь.add_roles(role, reason=f"Роль выдана через команду {interaction.user}")
        
        # --- ЛОГИРОВАНИЕ ВЫДАЧИ РОЛИ МОДЕРАТОРА ---
        await log_action(interaction, пользователь, "Выдача роли", moderator_role_name)
        # --- /ЛОГИРОВАНИЕ ---

        embed = discord.Embed(title="✅ Роль выдана", description=f"Пользователю {пользователь.mention} выдана роль {role.mention}", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ У бота нет прав для выдачи ролей!", ephemeral=True)

@bot.tree.command(name="helper", description="Выдать роль хелпера пользователю")
async def helper(interaction: discord.Interaction, пользователь: discord.Member):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ У вас нет прав для выдачи ролей!", ephemeral=True)
        return
    role = discord.utils.get(interaction.guild.roles, name=helper_role_name)
    if role is None:
        try:
            role = await interaction.guild.create_role(
                name=helper_role_name,
                color=discord.Color.green(),
                permissions=discord.Permissions(manage_messages=True, read_message_history=True, use_application_commands=True),
                reason="Создано ботом для команды /helper"
            )
        except discord.Forbidden:
            await interaction.response.send_message("❌ У бота нет прав для создания ролей!", ephemeral=True)
            return
    try:
        await пользователь.add_roles(role, reason=f"Роль выдана через команду {interaction.user}")
        
        # --- ЛОГИРОВАНИЕ ВЫДАЧИ РОЛИ ХЕЛПЕРА ---
        await log_action(interaction, пользователь, "Выдача роли", helper_role_name)
        # --- /ЛОГИРОВАНИЕ ---

        embed = discord.Embed(title="✅ Роль выдана", description=f"Пользователю {пользователь.mention} выдана роль {role.mention}", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ У бота нет прав для выдачи ролей!", ephemeral=True)

@bot.tree.command(name="бан", description="Забанить пользователя с причиной и временем")
async def ban_cmd(interaction: discord.Interaction, пользователь: discord.Member, причина: str, длительность: str = None):
    """Временный бан пользователя через роль БАН"""
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ У вас нет прав для бана!", ephemeral=True)
        return

    # Откладываем ответ
    await interaction.response.defer(ephemeral=True)

    try:
        duration_text = длительность if длительность else "перманентный"
        duration_seconds = await parse_duration(длительность) if длительность else None
        # Создаем или получаем роль БАН
        ban_role = await get_or_create_ban_role(interaction.guild)
        # Сохраняем текущие роли пользователя
        await save_user_roles(interaction.guild.id, пользователь.id, пользователь.roles)
        # Выдаем роль БАН
        await пользователь.add_roles(ban_role, reason=f"Временный бан: {причина}")
        # Снимаем все остальные роли
        for role in пользователь.roles:
            if role != interaction.guild.default_role and role != ban_role:
                try:
                    await пользователь.remove_roles(role, reason="Снятие ролей при временном бане")
                except:
                    pass
        if duration_seconds:
            await add_temporary_punishment(
                interaction.guild.id,
                пользователь.id,
                'temp_ban',
                duration_seconds,
                причина,
                interaction.user.id
            )
        await log_action(interaction, пользователь, f"Временный бан ({duration_text})", причина)
        await send_punishment_dm(
            пользователь,
            "временный бан",
            причина,
            duration_text,
            interaction.guild.name
        )
        # Отправляем финальное сообщение
        await interaction.followup.send(
            f"✅ {пользователь.mention} получил временный бан по причине: {причина}\nДлительность: {duration_text}"
        )

    except Exception as e:
        await interaction.followup.send(f"❌ Ошибка при выдаче бана: {str(e)}", ephemeral=True)

@bot.tree.command(name="мут", description="Выдать мут пользователю через роль")
async def mute_cmd(interaction: discord.Interaction, пользователь: discord.Member, длительность: str, причина: str):
    """Мут пользователя через роль МУТ"""
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ У вас нет прав для мута!", ephemeral=True)
        return

    # Откладываем ответ, чтобы избежать таймаута
    await interaction.response.defer(ephemeral=True)

    try:
        duration_seconds = await parse_duration(длительность)
        if not duration_seconds:
            await interaction.followup.send("❌ Неверный формат времени! Используйте: 30m, 2h, 1d", ephemeral=True)
            return
        duration_minutes = duration_seconds // 60
        if duration_minutes > 40320:
            await interaction.followup.send("❌ Максимальная длительность мута - 28 дней!", ephemeral=True)
            return

        # Создаем или получаем роль МУТ
        mute_role = await get_or_create_mute_role(interaction.guild)
        # Выдаем роль МУТ
        await пользователь.add_roles(mute_role, reason=f"Мут: {причина}")
        # Сохраняем временный мут
        await add_temporary_punishment(
            interaction.guild.id,
            пользователь.id,
            'mute',
            duration_seconds,
            причина,
            interaction.user.id
        )
        await log_action(interaction, пользователь, f"Мут ({длительность})", причина)
        await send_punishment_dm(
            пользователь,
            "мут",
            причина,
            длительность,
            interaction.guild.name
        )
        # Отправляем финальное сообщение
        await interaction.followup.send(
            f"✅ {пользователь.mention} получил мут на {длительность} по причине: {причина}"
        )

    except Exception as e:
        print(f"Ошибка при выдаче мута: {e}")
        await interaction.followup.send(f"❌ Ошибка при выдаче мута: {str(e)}", ephemeral=True)

@bot.tree.command(name="размут", description="Снять мут с пользователя")
async def unmute_cmd(interaction: discord.Interaction, пользователь: discord.Member):
    """Снять мут"""
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ У вас нет прав для снятия мута!", ephemeral=True)
        return

    # Откладываем ответ
    await interaction.response.defer(ephemeral=True)

    try:
        mute_role = discord.utils.get(interaction.guild.roles, name="МУТ")
        if mute_role and mute_role in пользователь.roles:
            await пользователь.remove_roles(mute_role, reason=f"Снятие мута {interaction.user}")
            await log_action(interaction, пользователь, "Снятие мута", "Через команду")
            await interaction.followup.send(f"✅ Мут снят с {пользователь.mention}!")
        else:
            await interaction.followup.send("❌ У пользователя нет мута!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Ошибка при снятии мута: {str(e)}", ephemeral=True)

@bot.tree.command(name="варн", description="Выдать варн пользователю")
async def warn_cmd(interaction: discord.Interaction, пользователь: discord.Member, причина: str):
    """Выдать варн"""
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ У вас нет прав для выдачи варнов!", ephemeral=True)
        return

    # Откладываем ответ
    await interaction.response.defer(ephemeral=True)

    try:
        await add_warn(interaction, пользователь, причина)
        # В `add_warn` уже используется `interaction.followup.send`, так что здесь ничего не нужно
    except Exception as e:
        await interaction.followup.send(f"❌ Ошибка при выдаче варна: {str(e)}", ephemeral=True)

@bot.tree.command(name="анварн", description="Снять варн с пользователя")
async def unwarn_cmd(interaction: discord.Interaction, пользователь: discord.Member, номер_варна: int = None):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ У вас нет прав для снятия варнов!", ephemeral=True)
        return
    await remove_warn(interaction, пользователь, номер_варна)

@bot.tree.command(name="варны", description="Посмотреть варны пользователя")
async def warns_cmd(interaction: discord.Interaction, пользователь: discord.Member):
    warns = load_json_file(WARNS_FILE)
    guild_id = str(interaction.guild.id)
    user_id = str(пользователь.id)
    if guild_id not in warns or user_id not in warns[guild_id] or not warns[guild_id][user_id]:
        await interaction.response.send_message(f"❌ У {пользователь.mention} нет варнов!", ephemeral=True)
        return
    user_warns = warns[guild_id][user_id]
    embed = discord.Embed(title=f"⚠️ Варны {пользователь.display_name}", color=discord.Color.orange(), timestamp=datetime.now())
    for i, warn in enumerate(user_warns, 1):
        timestamp = datetime.fromisoformat(warn['timestamp']).strftime("%d.%m.%Y %H:%M")
        embed.add_field(name=f"Варн #{i}", value=f"**Причина:** {warn['reason']}\n**Модератор:** {warn['moderator']}\n**Время:** {timestamp}", inline=False)
    embed.set_footer(text=f"Всего варнов: {len(user_warns)}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="настройкатикетов", description="Настроить систему тикетов")
async def setup_tickets_cmd(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ У вас нет прав для настройки тикетов!", ephemeral=True)
        return
    help_channel = await setup_help_channel(interaction.guild)
    if help_channel:
        await interaction.response.send_message(f"✅ Система тикетов настроена в канале {help_channel.mention}!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Не удалось настроить систему тикетов!", ephemeral=True)

@bot.tree.command(name="staff_profile", description="Посмотреть статистику модератора/хелпера")
async def staff_profile(interaction: discord.Interaction, пользователь: discord.Member):
    stats = load_mod_stats()
    guild_str = str(interaction.guild.id)
    mod_str = str(пользователь.id)
    
    if guild_str not in stats or mod_str not in stats[guild_str]:
        await interaction.response.send_message(f"❌ У {пользователь.mention} нет статистики модерации.", ephemeral=True)
        return
    
    user_stats = stats[guild_str][mod_str]
    
    embed = discord.Embed(
        title=f"📊 Профиль персонала: {пользователь.display_name}",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )
    embed.add_field(name="🔨 Банов", value=user_stats.get('bans', 0), inline=True)
    embed.add_field(name="🔇 Мутов", value=user_stats.get('mutes', 0), inline=True)
    embed.add_field(name="⚠️ Варнов", value=user_stats.get('warns', 0), inline=True)
    embed.add_field(name="🎫 Закрыто тикетов", value=user_stats.get('tickets_closed', 0), inline=True)
    embed.set_thumbnail(url=пользователь.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mod_history", description="Посмотреть историю наказаний пользователя")
async def mod_history(interaction: discord.Interaction, пользователь: discord.Member):
    """Показывает историю всех наказаний пользователя (варны, муты, баны)"""
    # Откладываем ответ, чтобы избежать таймаута
    await interaction.response.defer(ephemeral=True)

    try:
        # Собираем историю из варнов
        warns = load_warns()
        guild_id = str(interaction.guild.id)
        user_id = str(пользователь.id)
        user_warns = warns.get(guild_id, {}).get(user_id, [])

        # Собираем историю из временных наказаний (баны, муты)
        temp_punishments = load_temporary_punishments()
        user_temp_punishments = []
        for key, punishment in temp_punishments.items():
            if punishment.get('guild_id') == interaction.guild.id and punishment.get('user_id') == пользователь.id:
                user_temp_punishments.append(punishment)

        # Проверяем, есть ли вообще какие-либо записи
        if not user_warns and not user_temp_punishments:
            await interaction.followup.send(f"❌ У {пользователь.mention} нет истории наказаний.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📜 История модерации: {пользователь.display_name}",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=пользователь.display_avatar.url)

        # Добавляем варны, если они есть
        if user_warns:
            warn_list = []
            for i, warn in enumerate(user_warns, 1):
                timestamp = datetime.fromisoformat(warn['timestamp']).strftime("%d.%m.%Y %H:%M")
                warn_list.append(f"`#{i}` **{warn['reason']}** - {warn['moderator']} ({timestamp})")
            # Обрезаем список если слишком длинный
            if len(warn_list) > 10:
                 warn_list = warn_list[:10] + [f"... и ещё {len(user_warns) - 10}"]
            embed.add_field(name="⚠️ Варны", value="\n".join(warn_list), inline=False)

        # Добавляем временные наказания, если они есть
        if user_temp_punishments:
            punishment_list = []
            for punishment in user_temp_punishments:
                # Определяем тип наказания
                punishment_type = punishment['type']
                if punishment_type == 'temp_ban':
                    type_str = "Бан"
                elif punishment_type == 'mute':
                    type_str = "Мут"
                else:
                    type_str = punishment_type

                # Получаем имя модератора
                mod = interaction.guild.get_member(punishment['moderator_id'])
                mod_name = mod.display_name if mod else "Неизвестен"

                # Форматируем время окончания
                end_time = datetime.fromisoformat(punishment['end_time'])
                time_str = end_time.strftime("%d.%m.%Y %H:%M")

                punishment_list.append(f"**{type_str}** - {punishment['reason']} - {mod_name} (до {time_str})")

            # Обрезаем список если слишком длинный
            if len(punishment_list) > 10:
                 punishment_list = punishment_list[:10] + [f"... и ещё {len(user_temp_punishments) - 10}"]

            embed.add_field(name="🔨 История наказаний", value="\n".join(punishment_list), inline=False)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        print(f"Ошибка в команде /mod_history: {e}")
        await interaction.followup.send(f"❌ Произошла ошибка при показе истории: {str(e)}", ephemeral=True)

@bot.tree.command(name="test", description="Тестовая команда")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("Бот работает! ✅")

# --- СОБЫТИЯ БОТА ---

@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен!')
    check_temporary_punishments.start()
    for guild in bot.guilds:
        await setup_help_channel(guild)
        await get_or_create_ban_role(guild)
        await get_or_create_mute_role(guild)
    bot.add_view(TicketCreateView())
    bot.add_view(TicketCloseView())
    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(f"Ошибка синхронизации: {e}")

# --- ЗАПУСК БОТА ---
# ПОМНИТЕ: ЗАМЕНИТЕ 'YOUR_BOT_TOKEN_HERE' НА ВАШ НОВЫЙ ТОКЕН!
import os
bot.run(os.getenv('DISCORD_TOKEN'))
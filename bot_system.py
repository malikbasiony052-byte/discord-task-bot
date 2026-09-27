import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
from datetime import datetime
import zoneinfo
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=['!', '?'], intents=intents, help_command=None)

# أيدي قناة اللوج ورتب العصابة والإدارة
TASK_LOG_CHANNEL_ID = 1535001426302861403
GANG_ROLE_NAME = "𓆩ɢᴛᴀ𓆪・𝐆𝐀𝐍𝐆"
ALLOWED_ADMIN_ROLES = ["丶𝐋𝐞𝐚𝐝𝐞𝐫", "admin structure"]


def is_admin_authorized(user: discord.Member) -> bool:
    if user.guild_permissions.administrator:
        return True
    user_role_names = [role.name for role in user.roles]
    return any(role in user_role_names for role in ALLOWED_ADMIN_ROLES)


# 1️⃣ نموذج المودال (الأسئلة التي تظهر عند الضغط على زر "تم")
class TaskDeliveryModal(Modal, title="تسليم التاسك"):
    name_field = TextInput(
        label="الاسم :",
        style=discord.TextStyle.short,
        placeholder="اكتب اسمك...",
        required=True
    )
    resources_field = TextInput(
        label="الموارد :",
        style=discord.TextStyle.short,
        placeholder="اكتب الموارد المسلمة...",
        required=False
    )
    money_field = TextInput(
        label="الفلوس :",
        style=discord.TextStyle.short,
        placeholder="اكتب المبلغ المسلم...",
        required=False
    )
    delivered_to_field = TextInput(
        label="سلمت لمين :",
        style=discord.TextStyle.short,
        placeholder="اكتب اسم الشخص الذي سلمته...",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user
        
        tz = zoneinfo.ZoneInfo("Africa/Cairo")
        now = datetime.now(tz)
        formatted_date = now.strftime("%Y/%m/%d")
        formatted_time = now.strftime("%I:%M %p")

        res_val = self.resources_field.value if self.resources_field.value else "لا يوجد"
        money_val = self.money_field.value if self.money_field.value else "لا يوجد"
        name_val = self.name_field.value
        del_to_val = self.delivered_to_field.value

        embed = discord.Embed(
            title="📥 إثبات تسليم جديد تحت المراجعة",
            description=(
                f"👤 **معلومات العضو:**\n"
                f"الاسم: {user.mention}\n"
                f"🆔 **الـ ID:** `{user.id}`\n\n"
                f"─── ･ ｡ﾟ☆: *.☽ .* :☆ﾟ. ───\n\n"
                f"👤 **الاسم:** {name_val}\n"
                f"🎒 **الموارد:** `{res_val}`\n"
                f"💰 **الفلوس:** `{money_val}`\n"
                f"🤝 **سلمت لمين:** `{del_to_val}`\n\n"
                f"─── ･ ｡ﾟ☆: *.☽ .* :☆ﾟ. ───\n\n"
                f"⏰ **سلم التاسك الساعة:** {formatted_time} (بتاريخ {formatted_date})"
            ),
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        await interaction.response.send_message("✅ تم إرسال إثبات تسليم التاسك للإدارة بنجاح!", ephemeral=True)
        
        log_channel = bot.get_channel(TASK_LOG_CHANNEL_ID) or interaction.channel
        await log_channel.send(
            content=f"📢 **إثبات تسليم من {user.mention} يتطلب مراجعة الإدارة:**",
            embed=embed,
            view=AdminTaskReviewView(applicant=user, modal_data={
                "name": name_val,
                "resources": res_val,
                "money": money_val,
                "delivered_to": del_to_val,
                "time_str": f"{formatted_time} (بتاريخ {formatted_date})"
            })
        )


# 2️⃣ أزرار الإدارة (نعم سلم التاسك / لا لم يسلم التاسك)
class AdminTaskReviewView(View):
    def __init__(self, applicant: discord.Member, modal_data: dict):
        super().__init__(timeout=None)
        self.applicant = applicant
        self.modal_data = modal_data

    @discord.ui.button(label="نعم سلم التاسك", style=discord.ButtonStyle.success, custom_id="approve_task_btn")
    async def approve_button(self, interaction: discord.Interaction, button: Button):
        if not is_admin_authorized(interaction.user):
            await interaction.response.send_message("❌ عفواً، هذا الإجراء مخصص للإدارة فقط.", ephemeral=True)
            return

        embed = discord.Embed(
            title="TASK APPROVED ✅",
            description=(
                f"سلم التاسك {self.applicant.mention}\n\n"
                f"👤 **معلومات العضو**\n"
                f"الاسم : {self.applicant.mention}\n"
                f"🆔 `{self.applicant.id}`\n\n"
                f"👤 **الاسم:** {self.modal_data['name']}\n"
                f"🎒 **الموارد:**\n`{self.modal_data['resources']}`\n\n"
                f"💰 **الفلوس:** `{self.modal_data['money']}`\n"
                f"🤝 **سلمت لمين:** `{self.modal_data['delivered_to']}`\n\n"
                f"─── ･ ｡ﾟ☆: *.☽ .* :☆ﾟ. ───\n\n"
                f"⏰ **سلم التاسك الساعة:**\n{self.modal_data['time_str']}\n\n"
                f"تمت الموافقة بواسطة الإداري: **{interaction.user.display_name}**"
            ),
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=self.applicant.display_avatar.url)

        await interaction.response.edit_message(
            content=f"تم تسليم التاسك بنجاح {self.applicant.mention}",
            embed=embed,
            view=None
        )

    @discord.ui.button(label="لا لم يسلم التاسك", style=discord.ButtonStyle.danger, custom_id="reject_task_btn")
    async def reject_button(self, interaction: discord.Interaction, button: Button):
        if not is_admin_authorized(interaction.user):
            await interaction.response.send_message("❌ عفواً، هذا الإجراء مخصص للإدارة فقط.", ephemeral=True)
            return

        embed = discord.Embed(
            title="TASK REJECTED ❌",
            description=(
                f"لم يسلم التاسك {self.applicant.mention}\n\n"
                f"👤 **معلومات العضو**\n"
                f"الاسم : {self.applicant.mention}\n"
                f"🆔 `{self.applicant.id}`\n\n"
                f"👤 **الاسم:** {self.modal_data['name']}\n"
                f"🎒 **الموارد:**\n`{self.modal_data['resources']}`\n\n"
                f"💰 **الفلوس:** `{self.modal_data['money']}`\n"
                f"🤝 **سلمت لمين:** `{self.modal_data['delivered_to']}`\n\n"
                f"─── ･ ｡ﾟ☆: *.☽ .* :☆ﾟ. ───\n\n"
                f"⏰ **وقت التقديم:**\n{self.modal_data['time_str']}\n\n"
                f"تم الرفض بواسطة الإداري: **{interaction.user.display_name}**"
            ),
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=self.applicant.display_avatar.url)

        await interaction.response.edit_message(
            content=f"لم يتم تسليم التاسك بنجاح {self.applicant.mention}",
            embed=embed,
            view=None
        )


# 3️⃣ الرسالة والزر الرئيسي للبوت (تم)
class TaskSystemLaunchView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="تم", style=discord.ButtonStyle.success, custom_id="submit_task_main_btn")
    async def open_modal(self, interaction: discord.Interaction, button: Button):
        user = interaction.user
        gang_role = discord.utils.get(user.guild.roles, name=GANG_ROLE_NAME)
        
        if gang_role and gang_role not in user.roles:
            await interaction.response.send_message(f"❌ عفواً، هذا النظام مخصص فقط لأعضاء رتبة `{GANG_ROLE_NAME}`.", ephemeral=True)
            return

        await interaction.response.send_modal(TaskDeliveryModal())


@bot.event
async def on_ready():
    bot.add_view(TaskSystemLaunchView())
    await bot.tree.sync()
    print(f'✅ تم تشغيل بوت التاسكات ومزامنة أودام السلاش بنجاح: {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="📋 /create_task | TASK SYSTEM"))


# -------------------------------------------------------------
# أوامر السلاش (Slash Commands /)
# -------------------------------------------------------------

# 1. إنشاء رسالة التاسك الرئيسية بسلاش كوماندر
@bot.tree.command(name="create_task", description="إنشاء لوحة تسليم التاسك مع زر (تم)")
async def create_task_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="نظام التاسكات الجديد",
        description="سلمت التاسك اضغط على الزر أدناه و املا الاجابات الآتية",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, view=TaskSystemLaunchView())

# 2. إرسال رسالة في الخاص لشخص محدد (مكون من جزأين: نص الرسالة والمستلم)
@bot.tree.command(name="send_dm", description="إنشاء رسالة ترسل في خاص شخص")
@app_commands.describe(
    message="كتابة الرسالة التي تريد إرسالها",
    user="اختيار الشخص الذي سترسل له الرسالة في الخاص"
)
async def send_dm(interaction: discord.Interaction, message: str, user: discord.User):
    try:
        await user.send(f"📩 **رسالة خاصة من إدارة المهام:**\n\n{message}")
        await interaction.response.send_message(f"✅ تم إرسال الرسالة بنجاح إلى {user.mention} في الخاص.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ لم يتم إرسال الرسالة، خاص المستخدم المغلق.", ephemeral=True)

# 3. إسناد مهمة لعضو
@bot.tree.command(name="assign_task", description="إسناد مهمة محددة لعضو")
@app_commands.describe(user="العضو", task="اسم المهمة")
async def assign_task(interaction: discord.Interaction, user: discord.User, task: str):
    await interaction.response.send_message(f"📌 تم إسناد المهمة **({task})** إلى {user.mention}")

# 4. تحديث حالة المهمة
@bot.tree.command(name="set_status", description="تحديث حالة مهمة (قيد التنفيذ / مكتملة / معلقة)")
@app_commands.describe(task_id="رقم المهمة", status="الحالة الجديدة")
async def set_status(interaction: discord.Interaction, task_id: int, status: str):
    await interaction.response.send_message(f"🔄 تم تحديث حالة المهمة #{task_id} إلى: **{status}**")

# 5. إنهاء المهمة
@bot.tree.command(name="complete_task", description="علامة إنجاز للمهمة")
@app_commands.describe(task_id="رقم المهمة")
async def complete_task(interaction: discord.Interaction, task_id: int):
    await interaction.response.send_message(f"🎉 تم إكمال المهمة #{task_id} بنجاح!")

# 6. إغلاق المهمة
@bot.tree.command(name="close_task", description="إغلاق أو أرشفة المهمة")
@app_commands.describe(task_id="رقم المهمة")
async def close_task(interaction: discord.Interaction, task_id: int):
    await interaction.response.send_message(f"🔒 تم إغلاق المهمة #{task_id}.")

# 7. حذف مهمة
@bot.tree.command(name="delete_task", description="حذف مهمة من النظام")
@app_commands.describe(task_id="رقم المهمة")
async def delete_task(interaction: discord.Interaction, task_id: int):
    await interaction.response.send_message(f"🗑️ تم حذف المهمة #{task_id} من القائمة.")

# 8. تحديد الموعد النهائي (Deadline)
@bot.tree.command(name="set_deadline", description="تحديد الموعد النهائي لتسليم المهمة")
@app_commands.describe(task_id="رقم المهمة", date="التاريخ والوقت")
async def set_deadline(interaction: discord.Interaction, task_id: int, date: str):
    await interaction.response.send_message(f"⏰ تم تحديد موعد التسليم للمهمة #{task_id} في: **{date}**")

# 9. تذكير بالمهمة
@bot.tree.command(name="remind_task", description="إرسال تذكير للعضو بالمهمة المطلوبة")
@app_commands.describe(user="العضو", task="المهمة")
async def remind_task(interaction: discord.Interaction, user: discord.User, task: str):
    await interaction.response.send_message(f"🔔 تذكير موجه لـ {user.mention}: لا تنس إنجاز مهمة **({task})**!")

# 10. عرض قائمة المهام
@bot.tree.command(name="list_tasks", description="عرض كافة المهام الحالية")
async def list_tasks(interaction: discord.Interaction):
    await interaction.response.send_message("📄 جاري جلب قائمة كافة المهام...")

# 11. عرض المهام الخاصة بي
@bot.tree.command(name="my_tasks", description="عرض المهام المسندة إليك فقط")
async def my_tasks(interaction: discord.Interaction):
    await interaction.response.send_message(f"📊 قائمة المهام الخاصة بك يا {interaction.user.mention}:")

# 12. تحديد أولوية المهمة
@bot.tree.command(name="set_priority", description="تحديد أولوية المهمة (منخفضة / متوسطة / عالية)")
@app_commands.describe(task_id="رقم المهمة", level="الأولوية")
async def set_priority(interaction: discord.Interaction, task_id: int, level: str):
    await interaction.response.send_message(f"🚨 تم تغيير أولوية المهمة #{task_id} إلى **{level}**")

# 13. إضافة ملاحظة
@bot.tree.command(name="add_note", description="إضافة ملاحظة على مهمة")
@app_commands.describe(task_id="رقم المهمة", note="الملاحظة")
async def add_note(interaction: discord.Interaction, task_id: int, note: str):
    await interaction.response.send_message(f"📝 تم إضافة الملاحظة على المهمة #{task_id}: {note}")

# 14. نقل المهمة لروم آخر
@bot.tree.command(name="move_task", description="نقل المهمة إلى روم محدد")
@app_commands.describe(task_id="رقم المهمة", channel="الروم المستهدف")
async def move_task(interaction: discord.Interaction, task_id: int, channel: discord.TextChannel):
    await interaction.response.send_message(f"🚚 تم نقل بيانات المهمة #{task_id} إلى {channel.mention}")

# 15. إعادة إسناد المهمة
@bot.tree.command(name="reassign_task", description="تحويل المهمة لشخص آخر")
@app_commands.describe(task_id="رقم المهمة", new_user="العضو الجديد")
async def reassign_task(interaction: discord.Interaction, task_id: int, new_user: discord.User):
    await interaction.response.send_message(f"🔄 تم تحويل المهمة #{task_id} إلى {new_user.mention}")

# 16. إحصائيات المهام
@bot.tree.command(name="task_stats", description="عرض إحصائيات ونسب إنجاز المهام")
async def task_stats(interaction: discord.Interaction):
    await interaction.response.send_message("📈 **إحصائيات المهام:**\n- مكتملة: 0\n- قيد التنفيذ: 0")

# 17. طلب تمديد المهلة
@bot.tree.command(name="request_extension", description="طلب تمديد الوقت لمهمة معينة")
@app_commands.describe(task_id="رقم المهمة", reason="السبب")
async def request_extension(interaction: discord.Interaction, task_id: int, reason: str):
    await interaction.response.send_message(f"⏳ تم تقديم طلب تمديد للمهمة #{task_id}. السبب: {reason}")

# 18. إرسال تقرير إنجاز
@bot.tree.command(name="submit_proof", description="إرسال إثبات إنجاز المهمة")
@app_commands.describe(task_id="رقم المهمة", proof="الرابط أو التوضيح")
async def submit_proof(interaction: discord.Interaction, task_id: int, proof: str):
    await interaction.response.send_message(f"✅ تم تقديم إثبات إنجاز المهمة #{task_id}: {proof}")

# 19. تقييم الأداء
@bot.tree.command(name="rate_task", description="تقييم إنجاز المهمة من 1 إلى 5")
@app_commands.describe(task_id="رقم المهمة", rating="التقييم")
async def rate_task(interaction: discord.Interaction, task_id: int, rating: int):
    await interaction.response.send_message(f"⭐ تم تقييم المهمة #{task_id} بـ {rating}/5")

# 20. إضافة مكافأة
@bot.tree.command(name="add_reward", description="تحديد مكافأة أو نقاط عند إنهاء المهمة")
@app_commands.describe(task_id="رقم المهمة", points="عدد النقاط")
async def add_reward(interaction: discord.Interaction, task_id: int, points: int):
    await interaction.response.send_message(f"🎁 تم إضافة مكافأة قدرها {points} نقطة للمهمة #{task_id}")

# 21. تثبيت مهمة عاجلة
@bot.tree.command(name="pin_task", description="تثبيت مهمة هامة جداً في الأعلى")
@app_commands.describe(task_id="رقم المهمة")
async def pin_task(interaction: discord.Interaction, task_id: int):
    await interaction.response.send_message(f"📌 تم تثبيت المهمة #{task_id} كمهمة عاجلة.")

# 22. إيقاف استقبال المهام مؤقتاً
@bot.tree.command(name="pause_tasks", description="توقف مؤقت لاستقبال أي مهام جديدة")
async def pause_tasks(interaction: discord.Interaction):
    await interaction.response.send_message("⏸️ تم إيقاف استقبال المهام الجديدة مؤقتاً.")


# أمر التشغيل بالعلامة العادية (!task)
@bot.command(name='task', aliases=['تاسك', 'تاسكات'])
async def task_cmd(ctx):
    embed = discord.Embed(
        title="نظام التاسكات الجديد",
        description="سلمت التاسك اضغط على الزر أدناه و املا الاجابات الآتية",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=TaskSystemLaunchView())


bot.run("MTU1MjYyMzAwMDEwMzE1Nzg2MQ.GOrHEj.tVMQCGxjFENl3kZ51pv7rpUfNcadANmA9IOGmg")
      

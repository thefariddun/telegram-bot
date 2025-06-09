from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta
import telegram

class ToxicWordFilter:
    def __init__(self):
        self.bad_words = set([
            "ahmoq", "jinnisan", "tentak", "yo'qol", "kallang ishlamaydi", "nima keraging bor", 
            "mankurt", "ahmoqona", "kondan", "kallak", "o‘ziy", "beshbarmoq", "tizimni buzish", "tushunarsiz",
            "lazzatli", "kuntog‘ri", "o‘zini bilmas", "belgili", "yuzini qoplash", "xo‘sh", "oshqozon", "ochkolar",
        ])
        self.scam_words = set([
            "soxta", "aldov", "qoplama", "firibgarlik", "kredit", "aloqa", "jamiyat", "makr", "internetda", 
            "qarz", "foyda", "katta", "qarz olish", "to‘lov tizimlari", "eng yaxshisi", "yolg‘on", "spamming", 
            "kredit kartalari", "so‘nggi imkoniyat", "dizayn", "investitsiya", "foydali takliflar", "qo‘llab-quvvatlash", 
            "taklif etish", "bizning hisobot", "to‘g‘ri yo‘l", "yangiliklar", "investitsiya so‘nggi", "foydali rasmiy"
        ])

    def is_toxic(self, message: str) -> bool:
        message = message.lower()
        return any(word in message for word in self.bad_words)

    def is_scam(self, message: str) -> bool:
        message = message.lower()
        return any(word in message for word in self.scam_words)

class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.application = Application.builder().token(self.token).build()
        self.filter = ToxicWordFilter()
        self.user_warnings = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('👋 Salom! Men guruhingizdagi salbiy va firibgarlik so‘zlarini aniqlab, kerak bo‘lsa foydalanuvchini vaqtincha cheklayman.')

    async def check_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_text = update.message.text
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name

        if user_id not in self.user_warnings:
            self.user_warnings[user_id] = 0

        try:
            if self.filter.is_toxic(message_text):
                await update.message.delete()
                self.user_warnings[user_id] += 1
                await context.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"⚠️ @{username}, salbiy fikr bildirmang! Ogohlantirish: {self.user_warnings[user_id]}/3."
                )
            elif self.filter.is_scam(message_text):
                await update.message.delete()
                self.user_warnings[user_id] += 1
                await context.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"⚠️ @{username}, firibgarlikka oid xabar yubormang! Ogohlantirish: {self.user_warnings[user_id]}/3."
                )
            if self.user_warnings[user_id] >= 3:
                until_time = datetime.now() + timedelta(hours=1)
                await context.bot.restrict_chat_member(
                    chat_id=self.chat_id,
                    user_id=user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=until_time
                )
                await context.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"🚫 @{username} 3 marta ogohlantirildi. Endi 1 soat davomida xabar yoza olmaydi."
                )
                self.user_warnings[user_id] = 0
        except Exception as e:
            print(f"Xatolik yuz berdi: {e}")
            await update.message.reply_text("⚠️ Xabarni o‘chirishda yoki cheklashda xatolik yuz berdi.")

    def run(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.check_message))
        self.application.run_polling()
def main():
    TOKEN = '8011059457:AAFMYNOdfvdUKyI7jKMdxIL2Zo_DNc_qIYo'
    CHAT_ID = '@filtersafebottestgroup' 
    bot = TelegramBot(TOKEN, CHAT_ID)
    bot.run()

if __name__ == "__main__":
    main()

# RixStudio 1.0.0

کتابخانه پایتون برای کار با Rubika Bot API v3.

## نصب
فایل‌های ZIP را در یک پوشه استخراج کنید. همه فایل‌های پایتون باید کنار هم باشند.
در همان پوشه اجرا کنید: `pip install .`

## شروع سریع
```python
from rixstudio import RixStudio

bot = RixStudio("YOUR_BOT_TOKEN")

@bot.on_message()
async def handler(message):
    if message.text == "/start":
        await message.reply("سلام! 🎵")

bot.run()
```
در محیط asyncio فعال: `await bot.run_polling()`.

## نمونه ارسال موسیقی
```python
await bot.send_file(chat_id, "song.mp3", text="آهنگ")
```
نوع فایل mp3 به صورت خودکار Music انتخاب می‌شود.

## متدهای پوشش داده شده
getMe, getChat, sendMessage, sendPoll, sendLocation, sendContact, getUpdates,
forwardMessage, editMessageText, editInlineKeypad, deleteMessage, setCommands,
updateBotEndpoints, editChatKeypad, getFile, requestSendFile, sendFile,
banChatMember, unbanChatMember.

همراه با Long Polling، هندلر پیام، آپلود/دانلود فایل و MusicQueue.

## محدودیت‌ها
- ورود فقط با Bot Token است. Bot API ورود به حساب شخصی روبیکا با شماره/رمز یا session را ارائه نمی‌کند.
- مستندات Bot API ارسالی متد ویس‌چت/پخش زنده ندارد.
- نام متد ویرایش کیبورد در جدول و نمونه cURL متفاوت است؛ این نسخه `editInlineKeypad` را طبق نمونه cURL استفاده می‌کند.
- ساختار دقیق پاسخ آپلود ممکن است وابسته به پاسخ سرور باشد؛ قبل از استفاده عملی با یک فایل آزمایشی بررسی شود.
- این بسته از نظر syntax و import بررسی شده، اما با توکن زنده روبیکا آزمایش نشده است.
- توکن را در GitHub عمومی قرار ندهید.

from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler


TOKEN = ""


def bot_start(update, context):
    """/start - Introduce the bot"""
    update.message.reply_text("Hi! This is a RemindMe bot that helps you to create your notes in "
                              "Telegram. \n"
                              "If you want to use this service, you should register or log in.\n"
                              "/register - go to website and register your account.\n"
                              "/login - log in.\n"
                              "Hope you'll enjoy it!")


def main():
    REQUEST_KWARGS = {
        'proxy_url': 'socks5://79.110.164.22:8080'
    }

    updater = Updater(TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", bot_start))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
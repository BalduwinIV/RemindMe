from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from data import db_session
from data.users import *


TOKEN = ""

notes_keyboard = [['Show', 'Edit', 'Delete']]
notes_id_keyboard = [[], ['stop']]
notes_keyboard_markup = ReplyKeyboardMarkup(notes_keyboard, one_time_keyboard=True)
notes_id_keyboard_markup = ReplyKeyboardMarkup(notes_id_keyboard, one_time_keyboard=True)


def bot_start(update, context):
    """/start - Introduce the bot"""
    update.message.reply_text("Hi! This is a RemindMe bot that helps you to create your notes in "
                              "Telegram. \n"
                              "If you want to use this service, you should register or log in"
                              "(just to identify you).\n"
                              "/register <your username> <your password> - register your account.\n"
                              "/login <your username> <your password> - log in your account.\n")
    update.message.reply_text(update.message.chat_id)


def bot_help(update, context):
    """/help"""
    session = db_session.create_session()
    chat = session.query(Chat).filter(Chat.chat_id == update.message.chat_id).first()
    if chat:
        if chat.username:
            update.message.reply_text("/notes - show your notes.\n"
                                      "/create_note - create new note.")
        else:
            update.message.reply_text("/login - log in account.\n"
                                      "/register - register new account.")
    else:
        update.message.reply_text("/login - log in account.\n"
                                  "/register - register new account.")


def bot_login(update, context):
    if len(context.args) < 2:
        update.message.reply_text('You need to enter username and password.')
    else:
        username = context.args[0]
        password = context.args[1]
        session = db_session.create_session()
        user = session.query(User).filter(User.username == username).first()
        if user:
            if user.check_password(password):
                chat_id = update.message.chat_id
                chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
                if chat:
                    chat.user_id = user.id
                    chat.username = user.username
                else:
                    chat = Chat()
                    chat.chat_id = chat_id
                    chat.user_id = user.id
                    chat.username = user.username
                    session.add(chat)
                session.commit()
                update.message.reply_text(f'Hello, {username}!')
            else:
                update.message.reply_text('Wrong password.')
        else:
            update.message.reply_text('User does not exist.')


def bot_register(update, context):
    if len(context.args) < 2:
        update.message.reply_text('You need to enter username and password.')
    else:
        username = context.args[0]
        password = context.args[1]
        session = db_session.create_session()
        user = session.query(User).filter(User.username == username).first()
        if user:
            update.message.reply_text('Someone has already used this username. Try another.')
        else:
            chat_id = update.message.chat_id
            chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
            if chat:
                new_user = User()
                new_user.username = username
                new_user.set_password(password)
                session.add(new_user)
                chat.user_id = new_user.id
                chat.username = new_user.username
            else:
                new_user = User()
                new_user.username = username
                new_user.set_password(password)
                session.add(new_user)
                chat = Chat()
                chat.chat_id = chat_id
                chat.user_id = new_user.id
                chat.username = new_user.username
                session.add(chat)
            session.commit()
            update.message.reply_text(f'Hello, {username}!')


def bot_notes(update, context):
    update.message.reply_text("What do you want to do?", reply_markup=notes_keyboard_markup)
    return 1


def notes_options(update, context):
    user_answer = update.message.text
    if user_answer == notes_keyboard[0][0]:
        session = db_session.create_session()
        notes = session.query(Notes).all()
        update.message.reply_text("What note would you want to read:\n"
                                  "{}".format(''.join(['{}. {};\n'.format(item.id, item.title)
                                                       for item in notes])),
                                  reply_markup=notes_id_keyboard_markup)
        return 2
    elif user_answer == notes_keyboard[0][1]:
        return 1


def show_note(update, context):
    session = db_session.create_session()
    if update.message.text == notes_id_keyboard[1][0]:
        update.message.reply_text("What do you want to do?", reply_markup=notes_keyboard_markup)
        return 1
    try:
        note_id = int(update.message.text)
    except Exception:
        update.message.reply_text("Wrong id.")
        return ConversationHandler.END
    note = session.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        update.message.reply_text(text="Wrong id.", parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    update.message.reply_text(text="<b>{}</b>\n{}".format(note.title, note.content),
                              parse_mode=ParseMode.HTML)


def stop(update, context):
    update.message.reply_text("OK", reply_markup=ReplyKeyboardRemove())


def main():
    db_session.global_init('db/data.sqlite')
    print('Bot is running')

    REQUEST_KWARGS = {
        'proxy_url': 'http://80.187.140.26:8080'
    }

    updater = Updater(TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)

    dp = updater.dispatcher

    login = CommandHandler("login", bot_login, pass_args=True)
    register = CommandHandler("register", bot_register, pass_args=True)
    notes_handler = ConversationHandler(
        entry_points=[CommandHandler("notes", bot_notes)],
        states={
            1: [MessageHandler(Filters.text, notes_options)],
            2: [MessageHandler(Filters.text, show_note)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(CommandHandler("start", bot_start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(login)
    dp.add_handler(register)
    dp.add_handler(notes_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
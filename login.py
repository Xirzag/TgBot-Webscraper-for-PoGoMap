from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

from persistence import user_data

import logging

login_password = "yoursecretpass"


# Enable logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

NO_LOG, WRONG = range(2)


def check_pass(password):
    return password == login_password


def is_logged(user):
    return user_data(user.id)['logged'] == 'LOGGED'


def should_be_logged(f):
    def helper(bot, update, *args, **kwargs):
        user_data(update)['chat'] = update.message.chat_id
        if is_logged(update.message.from_user):
            return f(bot, update, *args, **kwargs)
        else:
            return ConversationHandler.END

    return helper


def start(bot, update):
    user_data(update)['chat'] = update.message.chat_id
    user_data(update).init('logged', 'NOT LOGGED')
    if is_logged(update.message.from_user):
        update.message.reply_text('You are alredy logged')
        return ConversationHandler.END

    update.message.reply_text('Log-in send pass')

    return NO_LOG


def login(bot, update):
    if check_pass(update.message.text):
        user = update.message.from_user

        logger.info("User logged %s", user.first_name)
        update.message.reply_text('Logged in the system.')

        user_data(user.id)['logged'] = 'LOGGED'

        return ConversationHandler.END
    else:
        user = update.message.from_user

        logger.info("Wrong Pass %s", user.first_name)
        update.message.reply_text('Wrong Pass.')

        return NO_LOG


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Cancel.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


@should_be_logged
def logout(bot, update):
    user_data(update)['logged'] = 'NOT LOGGED'
    update.message.reply_text('Logout',
                              reply_markup=ReplyKeyboardRemove())

    logger.info("User logged out %s", update.message.from_user.first_name)
    return ConversationHandler.END


def i_am_logged(bot, update):
    user = update.message.from_user
    update.message.reply_text("Yes" if is_logged(user) else "No",
                              reply_markup=ReplyKeyboardRemove())


def init(updater):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            NO_LOG: [MessageHandler(Filters.text, login)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp = updater.dispatcher

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('logout', logout))
    dp.add_handler(CommandHandler('logged', i_am_logged))

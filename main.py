import config
import dbworker
import parserHH


bot = config.telebot.TeleBot(config.token)
title = None
city = None


@bot.message_handler(commands=['start'])
def cmd_start(message):
    print('0')
    bot.send_message(message.chat.id, 'Title')
    dbworker.set_state(message.chat.id, config.States.S_GET_TITLE.value)


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_GET_TITLE.value)
def get_city(message):
    print('1')
    global title
    title = message.text
    bot.send_message(message.chat.id, 'City')
    dbworker.set_state(message.chat.id, config.States.S_GET_CITY.value)


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_GET_CITY.value)
def get_city(message):
    print('2')
    global city
    city = message.text
    bot.send_message(message.chat.id, 'Start parsing')
    parserHH.doParse(title, city)
    dbworker.set_state(message.chat.id, config.States.S_GET_CITY.value)


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_PARSE_DONE.value)
def parse_done(message):
    print('3')
    bot.send_message(message.chat.id, 'Parse done')
    dbworker.set_state(message.chat.id, config.States.S_START.value)


if __name__ == '__main__':
    bot.polling()

import config
import dbworker
import parserHH


bot = config.telebot.TeleBot(config.token)
title = None
city = None


@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.send_message(message.chat.id, 'Title')
    dbworker.set_state(message.chat.id, config.States.S_GET_TITLE.value)


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_GET_TITLE.value)
def get_title(message):
    global title
    title = '"' + message.text + '"'
    markup = config.telebot.types.InlineKeyboardMarkup()
    markup.add(config.telebot.types.InlineKeyboardButton(text='Россия', callback_data=113))
    markup.add(config.telebot.types.InlineKeyboardButton(text='Москва', callback_data=1))
    markup.add(config.telebot.types.InlineKeyboardButton(text='Санкт-Петербург', callback_data=2))
    bot.send_message(message.chat.id, 'Регион', reply_markup=markup)
    dbworker.set_state(message.chat.id, config.States.S_GET_CITY.value)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global city
    city = call.data
    bot.send_message(call.message.chat.id, 'Start parsing')
    stats = parserHH.doParse(title, city)
    bot.send_message(call.message.chat.id, 'Parse done')
    bot.send_message(call.message.chat.id, 'Найдено вакансий: ' + str(stats[-1]))
    img = open('dist_salary.png', 'rb')
    bot.send_photo(call.message.chat.id, img)
    img.close()
    bot.send_message(call.message.chat.id, 'Минимальная заработная плата: ' + str(stats[0]))
    bot.send_message(call.message.chat.id, 'Максимальная заработная плата: ' + str(stats[1]))
    bot.send_message(call.message.chat.id, 'Среднее по зарплатам: ' + str(stats[2]))
    bot.send_message(call.message.chat.id, 'Медиана по зарплатам: ' + str(stats[3]))
    bot.send_message(call.message.chat.id, 'Мода по  зарплатам: ' + str(stats[4]))
    doc = open('Vacancies.xlsx', 'rb')
    bot.send_document(call.message.chat.id, doc)
    doc.close()
    config.os.remove('Vacancies.xlsx')
    dbworker.set_state(call.message.chat.id, config.States.S_START.value)


if __name__ == '__main__':
    bot.polling()

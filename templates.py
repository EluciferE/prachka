import telebot

banner = "Все записи на таблицу будут от моего имени," \
         "поэтому доступ предоставляется не всем.\n\n" \
         "Боту нужно будет расписание, по которому он будет вас записывать:\n" \
         "1. День недели\n2. Время\n3. Машинка\n4. Запись (f.e. Иванов, 228г)\n\n" \
         "Если бот не сможет записать вас на вашу машинку, то попробудет записать на другие. " \
         "Вы всегда можете посмотреть ваши 'Текущие записи' в таблице и Удалить их"

TIMETABLE = "\n{}\n{}\nМашинка: {}\n{}"
NOTE = "{}\n{}\n{}\nМашинка: {}"

times = ["8:45 - 10:45", "12:00 - 14:00", "16:00 - 18:00", "20:00 - 22:00"]
days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

# KEYBOARDS

first_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
first_keyboard.row(telebot.types.KeyboardButton("Я хочу пользоваться ботом"))

admin_but = [telebot.types.KeyboardButton(x) for x in ['Запросы на доступ', 'Пользователи', 'Забанить', 'Разбанить',
                                                       'Основное меню']]
admin_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
admin_keyboard.row(admin_but[0], admin_but[1])
admin_keyboard.row(admin_but[2], admin_but[3])
admin_keyboard.row(admin_but[4])

days_buttons = [telebot.types.KeyboardButton(x) for x in days]
days_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
days_keyboard.row(days_buttons[0], days_buttons[1], days_buttons[2])
days_keyboard.row(days_buttons[3], days_buttons[4], days_buttons[5])
days_keyboard.row(days_buttons[6], telebot.types.KeyboardButton("⬅️ Назад"))
back = "⬅️ Назад"
times_buttons = [telebot.types.KeyboardButton(x) for x in times]
times_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
times_keyboard.row(times_buttons[0], times_buttons[1])
times_keyboard.row(times_buttons[2], times_buttons[3])
times_keyboard.row(telebot.types.KeyboardButton("⬅️ Назад"))

wedn_times_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
wedn_times_keyboard.row(times_buttons[2], times_buttons[3])
wedn_times_keyboard.row(telebot.types.KeyboardButton("⬅️ Назад"))

machines_buttons = [telebot.types.KeyboardButton(x) for x in ["1", "2", "3", "⬅️ Назад"]]
machines_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
machines_keyboard.row(machines_buttons[0], machines_buttons[1], machines_buttons[2])
machines_keyboard.row(telebot.types.KeyboardButton("⬅️ Назад"))

back_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
back_keyboard.row(telebot.types.KeyboardButton("⬅️ Назад"))

standard_buttons = [telebot.types.KeyboardButton(x) for x in ["Моё расписание", "Мои записи",
                                                              "Настроить расписание", "Удалить запись",
                                                              "Удалить расписание"]]
stand_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
stand_keyboard.row(standard_buttons[0], standard_buttons[1])
stand_keyboard.row(standard_buttons[2], standard_buttons[3])
stand_keyboard.row(standard_buttons[4])

accept_buttons = [telebot.types.KeyboardButton(x) for x in ["Подтвердить",
                                                            "Отмена"]]
accept_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
accept_keyboard.row(accept_buttons[0], accept_buttons[1])

accept_timetable_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
accept_timetable_keyboard.row(accept_buttons[0], accept_buttons[1])
accept_timetable_keyboard.row(telebot.types.KeyboardButton("⬅️ Назад"))

banned_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
banned_keyboard.row(telebot.types.KeyboardButton("Прости"))

import telebot

banner = "Все записи на таблицу будут от моего имени," \
         "поэтому доступ предоставляется не всем.\n\n" \
         "Боту нужно будет расписание, по которому он будет вас записывать:\n" \
         "1. День недели\n2. Время\n3. Машинка\n4. Запись (f.e. Иванов, 228г)\n\n" \
         "Если бот не сможет записать вас на вашу машинку, то попробудет записать на другие. " \
         "Вы всегда можете посмотреть ваши 'Текущие записи' в таблице и Удалить их\n\nЧтобы начать пользоваться ботом, нажмите на кнопку снизу"

TIMETABLE = "\n{}\n{}\nМашинка: {}\n{}"
NOTE = "{}\n{}\n{}\nМашинка: {}"

times1Machine = ["10:45 - 12:45", "15:00 - 17:00", "19:00 - 21:00", "22:45 - 0:30"]
times23Machine = ["8:45 - 10:45", "13:00 - 15:00", "17:00 - 19:00", "21:00 - 22:45"]
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


times1machine_buttons = [telebot.types.KeyboardButton(x) for x in times1Machine + [back]]
times23machine_buttons = [telebot.types.KeyboardButton(x) for x in times23Machine + [back]]

times1_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
times1_keyboard.row(times1machine_buttons[0], times1machine_buttons[1])
times1_keyboard.row(times1machine_buttons[2], times1machine_buttons[3])
times1_keyboard.row(times1machine_buttons[4])

times23_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
times23_keyboard.row(times23machine_buttons[0], times23machine_buttons[1])
times23_keyboard.row(times23machine_buttons[2], times23machine_buttons[3])
times23_keyboard.row(times23machine_buttons[4])

wedn_times_keyboard_1machine = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
wedn_times_keyboard_1machine.row(times1machine_buttons[2], times1machine_buttons[3])
wedn_times_keyboard_1machine.row(times1machine_buttons[4])

wedn_times_keyboard_23machine = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
wedn_times_keyboard_23machine.row(times23machine_buttons[2], times23machine_buttons[3])
wedn_times_keyboard_23machine.row(times23machine_buttons[4])

machines_buttons = [telebot.types.KeyboardButton(x) for x in ["1", "2", "3", "⬅️ Назад"]]
machines_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
machines_keyboard.row(machines_buttons[0], machines_buttons[1], machines_buttons[2])
machines_keyboard.row(telebot.types.KeyboardButton("⬅️ Назад"))

back_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
back_keyboard.row(telebot.types.KeyboardButton("⬅️ Назад"))

standard_buttons = [telebot.types.KeyboardButton(x) for x in ["Моё расписание", "Мои записи",
                                                              "Настроить расписание", "Удалить запись",
                                                              "Удалить расписание", "Авторизация"]]
stand_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
stand_keyboard.row(standard_buttons[0], standard_buttons[1])
stand_keyboard.row(standard_buttons[2], standard_buttons[3])
stand_keyboard.row(standard_buttons[4], standard_buttons[5])

accept_buttons = [telebot.types.KeyboardButton(x) for x in ["Подтвердить",
                                                            "Отмена"]]
accept_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
accept_keyboard.row(accept_buttons[0], accept_buttons[1])

accept_timetable_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
accept_timetable_keyboard.row(accept_buttons[0], accept_buttons[1])
accept_timetable_keyboard.row(telebot.types.KeyboardButton("⬅️ Назад"))

banned_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
banned_keyboard.row(telebot.types.KeyboardButton("Прости"))

#Keyboards for token menu

ask_token = [telebot.types.KeyboardButton(x) for x in ["Да", "Нет"]]
ask_token_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
ask_token_keyboard.row(ask_token[0], ask_token[1])

analyze_token = [telebot.types.KeyboardButton(x) for x in ["Поменять учетную запись", "Удалить авторизацию", back]]
analyze_token_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
analyze_token_keyboard.row(analyze_token[0], analyze_token[1])
analyze_token_keyboard.row(analyze_token[2])

mondayTimes = """
                            Понедельник
                            
10:45 - 12:45:    {}         08:45 - 10:45:    {}    {}
15:00 - 17:00:    {}         13:00 - 15:00:    {}    {}
19:00 - 21:00:    {}         17:00 - 19:00:    {}    {}
22:45 - 00:30:    {}         21:00 - 22:45:    {}    {}
"""

tuesdayTimes = """
                                Вторник
                            
10:45 - 12:45:    {}         08:45 - 10:45:    {}    {}
15:00 - 17:00:    {}         13:00 - 15:00:    {}    {}
19:00 - 21:00:    {}         17:00 - 19:00:    {}    {}
22:45 - 00:30:    {}         21:00 - 22:45:    {}    {}
"""

wednesdayTimes = """
                                Среда
                            
19:00 - 21:00:    {}         17:00 - 19:00:    {}    {}
22:45 - 00:30:    {}         21:00 - 22:45:    {}    {}
"""

thursdayTimes = """
                                Четверг
                        
10:45 - 12:45:    {}         08:45 - 10:45:    {}    {}
15:00 - 17:00:    {}         13:00 - 15:00:    {}    {}
19:00 - 21:00:    {}         17:00 - 19:00:    {}    {}
22:45 - 00:30:    {}         21:00 - 22:45:    {}    {}
"""

fridayTimes = """
                                Пятница
                            
10:45 - 12:45:    {}         08:45 - 10:45:    {}    {}
15:00 - 17:00:    {}         13:00 - 15:00:    {}    {}
19:00 - 21:00:    {}         17:00 - 19:00:    {}    {}
22:45 - 00:30:    {}         21:00 - 22:45:    {}    {}
"""

saturdayTimes = """
                                Суббота
                        
10:45 - 12:45:    {}         08:45 - 10:45:    {}    {}
15:00 - 17:00:    {}         13:00 - 15:00:    {}    {}
19:00 - 21:00:    {}         17:00 - 19:00:    {}    {}
22:45 - 00:30:    {}         21:00 - 22:45:    {}    {}
"""

sundayTimes = """
                            Воскресенье
                            
10:45 - 12:45:    {}         08:45 - 10:45:    {}    {}
15:00 - 17:00:    {}         13:00 - 15:00:    {}    {}
19:00 - 21:00:    {}         17:00 - 19:00:    {}    {}
22:45 - 00:30:    {}         21:00 - 22:45:    {}    {}
"""

msgTimes = {"понедельник": mondayTimes, "вторник": tuesdayTimes,
            "среда": wednesdayTimes, "четверг": thursdayTimes,
            "пятница": fridayTimes, "суббота": saturdayTimes,
            "воскресенье": sundayTimes}

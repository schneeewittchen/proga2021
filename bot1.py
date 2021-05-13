import telebot
import csv
from telebot import types
from collections import defaultdict

bot = telebot.TeleBot('1801207356:AAEVzvjlQ963q5ybpV_Yi6sZSo4EHKi8Uc4', parse_mode=None)
global_storage = defaultdict(list)
known_users = {}
user_state = {}
users_info = {}


@bot.message_handler(commands=['reg'])
def command_reg(message):
    us_id = message.chat.id
    markup_inline = types.InlineKeyboardMarkup()
    item_vegan = types.InlineKeyboardButton(text='веган', callback_data='vegan')
    item_vegetarian = types.InlineKeyboardButton(text='вегетарианец', callback_data='vegetarian')
    item_meat_eater = types.InlineKeyboardButton(text='ем всё', callback_data='no')
    markup_inline.add(item_vegan, item_vegetarian, item_meat_eater)
    bot.send_message(us_id, "Привет, я помогу подобрать оптимальный рецепт! Для начала укажи свой тип питания.",
                     reply_markup=markup_inline)
    user_state[us_id] = 'new'
    users_info[us_id] = {}
    

@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    us_id = call.message.chat.id
    if call.data == 'vegan':
        known_users[us_id] = 'вгн'
        bot.send_message(call.message.chat.id, 'Спасибо, я учту эту информацию при подборе рецепта!')
        welcome(call.message)
    elif call.data == 'vegetarian':
        known_users[us_id] = 'вгт'
        bot.send_message(call.message.chat.id, 'Спасибо, я учту эту информацию при подборе рецепта!')
        welcome(call.message)
    elif call.data == 'no':
        known_users[us_id] = 'нет'
        bot.send_message(call.message.chat.id, 'Спасибо, я учту эту информацию при подборе рецепта!')
        welcome(call.message)
    elif call.data == 'breakfast':
        (users_info[us_id])['meal'] = 'завтрак'
        bot.send_message(call.message.chat.id, 'Спасибо! Это поможет сделать твой запрос более точным!')
        ask_kkal(call.message)
    elif call.data == 'lunch':
        (users_info[us_id])['meal'] = 'обед'
        bot.send_message(call.message.chat.id, 'Спасибо! Это поможет сделать твой запрос более точным!')
        ask_kkal(call.message)
    elif call.data == 'dinner':
        (users_info[us_id])['meal'] = 'ужин'
        bot.send_message(call.message.chat.id, 'Спасибо! Это поможет сделать твой запрос более точным!')
        ask_kkal(call.message)
    elif call.data == 'dessert':
        (users_info[us_id])['meal'] = 'к чаю'
        bot.send_message(call.message.chat.id, 'Спасибо! Это поможет сделать твой запрос более точным!')
        ask_kkal(call.message)
    elif call.data == 'important':
        bot.send_message(call.message.chat.id, 'Чтобы указать калорийность блюда, напиши мне /kkal')
        bot.register_next_step_handler(call.message, answer)
    elif call.data == 'notimportant':
        (users_info[us_id])['kkal'] = 'все равно'
        bot.send_message(call.message.chat.id, alg(users_info[us_id], call.message.chat.id))


@bot.message_handler(commands=['recipe'])
def ask_products(message):
    us_id = message.chat.id
    bot.send_message(us_id, "Введи продукты через запятую.")
    bot.register_next_step_handler(message, ask_meal)


@bot.message_handler(content_types=['text'])
def welcome(message):
    us_id = message.chat.id
    if user_state[us_id] == 'old':
        bot.send_message(us_id, "Если хочешь, чтобы я еще раз подобрал рецепт, напиши мне /recipe .")
    elif user_state[us_id] == 'new':
        bot.send_message(us_id,
                         "Я очень рад с тобой познакомиться. Чтобы я подобрал рецепт по твоему запросу, напиши мне /recipe .")
        user_state[us_id] = 'old'
    bot.register_next_step_handler(message, ask_products)


def ask_meal(message):
    us_id = message.chat.id
    (users_info[us_id])['products'] = message.text
    markup_inline_2 = types.InlineKeyboardMarkup()
    item_breakfast = types.InlineKeyboardButton(text='завтрак', callback_data='breakfast')
    item_lunch = types.InlineKeyboardButton(text='обед', callback_data='lunch')
    item_dinner = types.InlineKeyboardButton(text='ужин', callback_data='dinner')
    item_dessert = types.InlineKeyboardButton(text='к чаю', callback_data='dessert')
    markup_inline_2.add(item_breakfast, item_lunch, item_dinner, item_dessert)
    bot.send_message(us_id, "Для какого приема пищи нужен рецепт?",
                     reply_markup=markup_inline_2)


def ask_kkal(message):
    markup_inline_3 = types.InlineKeyboardMarkup()
    item_kkal = types.InlineKeyboardButton(text='да', callback_data='important')
    item_nokkal = types.InlineKeyboardButton(text='нет', callback_data='notimportant')
    markup_inline_3.add(item_kkal, item_nokkal)
    bot.send_message(message.chat.id, "Важна ли калорийность блюда?",
                     reply_markup=markup_inline_3)


def alg(user_info, us_id):
    user_products = user_info['products'].lower().split(', ')
    user_meal = (users_info[us_id])['meal'].lower()
    user_kkal = user_info['kkal'].lower().split('-')
    user_type = known_users[us_id].lower()
    with open('recipes.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        best_match = 0
        for di in reader:
            product_match = 0
            for item in user_products:
                if item in di['ingredients']:
                    product_match += 1
            if product_match > best_match:
                if user_kkal[0] == 'все равно':
                    kkal_check = True
                elif int(user_kkal[0]) < int(di['kkal']) < int(user_kkal[1]):
                    kkal_check = True
                else:
                    kkal_check = False
                if (user_type in di['type'] and user_meal in di['meal'] and kkal_check == True):
                    best_match = product_match
                    best_id = di['id']
                    best_name = di['name']
                    best_recipe = di['recipe']
                    best_kkal = di['kkal']
    user_recipe = best_name + '\nРецепт: ' + best_recipe + '\nКалорийность на 100 г: ' + best_kkal
    return user_recipe


@bot.message_handler(commands=['kkal'])
def answer(message):
    us_id = message.chat.id
    bot.send_message(us_id, 'Введите диапазон калорийности через дефис по образцу: 100-200')
    bot.register_next_step_handler(message, get_kkal)


def get_kkal(message):
    us_id = message.chat.id
    (users_info[us_id])['kkal'] = message.text 
    bot.send_message(message.chat.id, alg((users_info[us_id]), message.chat.id))



bot.polling(none_stop=True, interval=0)

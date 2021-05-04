import telebot
import csv
from telebot import types
from collections import defaultdict

bot = telebot.TeleBot("1621672017:AAHP2qG9qRhnYgqDLaIoD_0lvcBeIc1QTGM", parse_mode=None)
global_storage = defaultdict(list)
known_users = {}
user_state = {}
user_info = {'products': '', 'meal': '', 'kkal': ''}


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


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    us_id = call.message.chat.id
    if call.data == 'vegan':
        known_users[us_id] = 'вгн'
    if call.data == 'vegetarian':
        known_users[us_id] = 'вгт'
    if call.data == 'no':
        known_users[us_id] = 'нет'
    bot.send_message(call.message.chat.id, 'Спасибо, мы учтём эту информацию при подборе рецепта!')
    print(known_users[us_id])
    welcome(call.message)


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
    if user_state[us_id] == 'new':
        bot.send_message(us_id,
                         "Я очень рад с тобой познакомиться. Чтобы я подобрал рецепт по твоему запросу, напиши мне /recipe .")
        user_state[us_id] = 'old'
    bot.register_next_step_handler(message, ask_products)


def ask_meal(message):
    user_info['products'] = message.text
    bot.send_message(message.from_user.id, 'Для какого приема пищи нужен рецепт?')
    bot.register_next_step_handler(message, ask_kkal)


def ask_kkal(message):
    user_info['meal'] = message.text
    bot.send_message(message.from_user.id, 'Какая калорийность блюда нужна?')
    bot.register_next_step_handler(message, answer)
    # print(user_info, user_state)


def alg(user_info, us_id):
    user_products = user_info['products'].lower().split(', ')
    user_meal = user_info['meal'].lower()
    user_kkal = user_info['kkal'].lower().split('-')
    user_type = known_users[us_id].lower()
    print(user_products, user_meal, user_kkal, user_type)
    with open('recipes.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        best_match = 0
        for di in reader:
            product_match = 0
            for item in user_products:
                if item in di['ingredients']:
                    product_match += 1
            if product_match > best_match:
                if user_kkal == 'все равно':
                    kkal_check = True
                elif int(user_kkal[0]) < int(di['kkal']) < int(user_kkal[1]):
                    kkal_check = True
                else:
                    kkal_check = False
                # print(kkal_check)
                if (user_type in di['type'] and user_meal in di['meal'] and kkal_check == True):
                    best_match = product_match
                    best_id = di['id']
                    best_name = di['name']
                    best_recipe = di['recipe']
                    best_kkal = di['kkal']
    user_recipe = best_name + '\nРецепт: ' + best_recipe + '\nКалорийность на 100 г: ' + best_kkal
    return user_recipe


@bot.message_handler(content_types=['text'])
def answer(message):
    us_id = message.chat.id
    user_info['kkal'] = message.text
    bot.send_message(us_id, alg(user_info, us_id))


bot.polling(none_stop=True, interval=0)

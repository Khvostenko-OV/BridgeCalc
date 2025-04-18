import os

import telebot
from telebot.types import InlineKeyboardButton as button
from dotenv import load_dotenv

load_dotenv(verbose=False, override=True)  # take environment variables from .env
bot = telebot.TeleBot(os.getenv("BOT_TOKEN",""))

POINTS = {'c': 20, 'd': 20, 'h': 30, 's': 30, 'n': 30}
SUITS = {'c': '♣️', 'd': '♦️', 'h': '♥️', 's': '♠️', 'n': 'БК'}
BONUS = {1: '', 2: 'на контре', 4: 'на реконтре'}
VULNERABLE = {False: 'до зоны', True: 'в зоне'}
GAME = [300, 500]
SLAM = [500, 750]
GSLAM = [1000, 1500]
OVER_TRICK = [50, 100]
UNDER_TRICK = [
    [0, -50, -150, -250, -400, -550, -700, -850, -1000],
    [0, -100, -250, -400, -550, -700, -850, -1000, -1150],
]

COMPENSA = [
    [1200,1200,1200,1200,1200,1100,1000,900,750,600,490,460,430,400,350,300,200,110,70,50,0,
     -50,-70,-110,-200,-300,-350,-400,-430,-460,-490,-600,-750,-900,-1000,-1100,-1200,-1200,-1200,-1200,-1200
    ],
    [1800,1800,1800,1800,1800,1650,1500,1350,1050,900,690,660,630,600,520,440,200,110,70,50,0,
    -50,-70,-110,-200,-440,-520,-600,-630,-660,-690,-900,-1050,-1350,-1500,-1650,-1800,-1800,-1800,-1800,-1800
    ],
]

IMP_TABLE = [0, 20, 50, 90, 130, 170, 220, 270, 320, 370, 430, 500, 600, 750, 900,
             1100, 1300, 1500, 1750, 2000, 2250, 2500, 3000, 3500, 4000
            ]

level = 1
suit = 'c'
factor = 1 # doubled, redoubled
tricks = 0 # over/under tricks
vul = False # vulnerable
counter = 70

# Make contract
def make(level, suit, factor, vul, tricks) -> int:
    res = POINTS[suit] * level
    if suit == 'n':
        res += 10
    res *= factor
    if res >= 100:
        res += GAME[vul]
    if level == 6:
        res += SLAM[vul]
    if level == 7:
        res += GSLAM[vul]
    if res < 100:
        res += 50
    if factor == 2:
        res += 50
    if factor == 4:
        res += 100
    if factor == 1:
        res += tricks * POINTS[suit]
    else:
        res += tricks * OVER_TRICK[vul] * factor
    return res


# Down contract
def down(factor, vul, tricks) -> int:
    if factor == 1:
        return tricks * OVER_TRICK[vul]
    else:
        return UNDER_TRICK[vul][-tricks] * factor


def imp_count(pt: int) -> int:
    sign = pt // abs(pt) if pt else 0
    imp = 24
    while abs(pt) < IMP_TABLE[imp]:
        imp -= 1
    return sign * imp


menu_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
menu_markup.add(telebot.types.KeyboardButton('/start'))


@bot.message_handler(commands=['start',])
def start(message):
    bot.send_message(message.chat.id, 'Старт', reply_markup=menu_markup)
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        button('1', callback_data='1level'), button('2', callback_data='2level'), button('3', callback_data='3level'),
        button('4', callback_data='4level'), button('5', callback_data='5level'), button('6', callback_data='6level'),
        button('7', callback_data='7level'),
    )
    bot.send_message(message.chat.id, 'Контракт:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def command_handler(call):
    global level, suit, factor, vul, tricks, counter
    try:
        if call.message:
            if 'level' in call.data:
                level = int(call.data[0])
                markup = telebot.types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    button('♣️', callback_data='c_suit'), button('♦️', callback_data='d_suit'),
                    button('♥️', callback_data='h_suit'), button('♠️', callback_data='s_suit'),
                    button('БК', callback_data='n_suit'),
                )
                bot.send_message(call.message.chat.id, f'{level} чего?', reply_markup=markup)
            elif 'suit' in call.data:
                suit = call.data[0]
                markup = telebot.types.InlineKeyboardMarkup(row_width=3)
                markup.add(
                    button('Просто', callback_data='1_factor'),
                    button('Контра', callback_data='2_factor'),
                    button('Реконтра', callback_data='4_factor'),
                )
                bot.send_message(call.message.chat.id, f'Контракт {level}{SUITS[suit]}:', reply_markup=markup)
            elif 'factor' in call.data:
                factor = int(call.data[0])
                markup = telebot.types.InlineKeyboardMarkup(row_width=3)
                markup.add(
                    button('До зоны', callback_data='0_vul'),
                    button('В зоне', callback_data='1_vul'),
                )
                bot.send_message(call.message.chat.id, f'Контракт {level}{SUITS[suit]} {BONUS[factor]}:', reply_markup=markup)
            elif 'vul' in call.data:
                vul = bool(int(call.data[0]))
                markup = telebot.types.InlineKeyboardMarkup(row_width=3)
                markup.add(
                    button('-1', callback_data='-1_trick'), button('-2', callback_data='-2_trick'), button('-3', callback_data='-3_trick'),
                    button('-4', callback_data='-4_trick'), button('-5', callback_data='-5_trick'), button('-6', callback_data='-6_trick'),
                    button('+1', callback_data='+1_trick'), button('+2', callback_data='+2_trick'), button('+3', callback_data='+3_trick'),
                    button('+4', callback_data='+4_trick'), button('+5', callback_data='+5_trick'), button('+6', callback_data='+6_trick'),
                    button('==', callback_data=' 0_trick'),
                )
                bot.send_message(call.message.chat.id, f'Контракт {level}{SUITS[suit]} {BONUS[factor]} {VULNERABLE[vul]}. Взяток:', reply_markup=markup)
            elif 'trick' in call.data:
                bot.send_message(call.message.chat.id, f'Контракт {level}{SUITS[suit]} {BONUS[factor]} {VULNERABLE[vul]}:')
                tricks = int(call.data[:2])
                tricks = 7 - level if level + tricks > 7 else tricks
                if tricks < 0:
                    bot.send_message(call.message.chat.id, f'Взяток {tricks}')
                elif tricks > 0:
                    bot.send_message(call.message.chat.id, f'Взяток +{tricks}')
                else:
                    bot.send_message(call.message.chat.id, 'Взяток - ровно')
                counter = make(level, suit, factor, vul, tricks) if tricks >= 0 else down(factor, vul, tricks)
                bot.send_message(call.message.chat.id, f'Очков: {counter}')
                bot.send_message(call.message.chat.id, 'Задайте баланс:')

    except Exception as e:
        print(repr(e))


@bot.message_handler(content_types=['text'])
def calculate(message):
    if message.text.isdigit() and int(message.text) <= 40:
        balance = int(message.text)
        final = counter + COMPENSA[vul][balance]
        imp = imp_count(final)
        if tricks < 0:
            tr = str(tricks)
        elif tricks > 0:
            tr = '+'+str(tricks)
        else:
            tr = '=='
        bot.send_message(message.chat.id, f'Контракт {level}{SUITS[suit]} {BONUS[factor]} {VULNERABLE[vul]} {tr}: {counter}')
        bot.send_message(message.chat.id, f'Баланс {balance}рс, компенсация: {COMPENSA[vul][balance]}')
        bot.send_message(message.chat.id, f'Сумма: {final}. Импов: {imp}', reply_markup=menu_markup)
    else:
        bot.send_message(message.chat.id, 'Задайте баланс:')


bot.infinity_polling()

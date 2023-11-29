import telebot
import time
import random
import psycopg2
from bd import host, user, password, db_name
import requests
import markovify
import Diplom

bot = telebot.TeleBot("6375113300:AAG9lAZMl9wmjgAbYBC1PgV36ni-L-S7nCY")
bot.send_message(-4023848883, "Я родился 🐣")

try:
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    connection.autocommit = True
    # bot.send_message(-4023848883, "Я в бд")
    # bot.send_message(-4023848883, "#" * 20)

except Exception as ex:
    bot.send_message(-4023848883, "Ошибка в работе БД")
    if connection:
        connection.close()
        bot.send_message(-4023848883, "#" * 20)
        bot.send_message(-4023848883, "Закрыл соеденение с БД")
cursor = connection.cursor()


@bot.message_handler(commands=["searchforafag"]) #Поиск пидора
def searchforafag(message):
    chat_id = message.chat.id
    cursor.execute(f"SELECT data_fag from data_fag where id_chat = {chat_id}")
    new_fag = cursor.fetchone()
    if new_fag is None:
        cursor.execute(
            f'insert into data_fag (id_user, id_chat, data_fag) values (1, {chat_id},{0})')

    fag_texts = ['<b>Пидр</b> сегодня', 'Карты сказали что <b>ПИДР</b> <b>ДНЯ</b>', 'Выбор сделан <b>Пидр</b> дня']
    cursor.execute(f"SELECT max(data_fag) from data_fag where id_chat = {chat_id}")
    time_hat_id = cursor.fetchone()
    time_fag_chat = int(time.time()) - time_hat_id[0]
    if time_fag_chat < 86400:  # количество секунд в день
        bot.send_message(message.chat.id, f"На сегодня пидоров хватит")
    else:
        cursor.execute(f"SELECT id_user, name_user from user_tg")
        users_all = cursor.fetchall()
        user_fag = random.choice(users_all)
        fag_text = random.choice(fag_texts)
        cursor.execute(f'UPDATE user_tg SET amount_fag = amount_fag+1 where id_user = {user_fag[0]};')
        cursor.execute(
            f'insert into data_fag (id_user, id_chat, data_fag) values ({user_fag[0]}, {message.chat.id},{time.time()})')
        bot.send_chat_action(chat_id=message.chat.id, action="typing", timeout=3)  # Имитация набора текста
        time.sleep(random.randint(1, 3))
        for _ in range(3):
            cursor.execute("SELECT text_music FROM text_music ORDER BY RANDOM() LIMIT 1")
            for text_music in cursor.fetchone():
                bot.send_message(message.chat.id, f"{text_music}")
                bot.send_chat_action(chat_id=message.chat.id, action="typing", timeout=3)  # Имитация набора текста
                time.sleep(random.randint(1, 3))


        bot.send_message(message.chat.id, f"{fag_text} @{user_fag[1]}", parse_mode='HTML')



@bot.message_handler(commands=["info"]) #Информация
def info(message):
    bot.send_chat_action(chat_id=message.chat.id, action="typing", timeout=3)  # Имитация набора текста
    time.sleep(random.randint(1, 3))
    bot.send_message(message.chat.id, """
    1. Для того что бы учавствовать в игре участник должен быть активным в чате \n 2. для того что бы быть пидором не обязательно быть активным пидором \n 3. И запомните ни слова о пидоре
    """)

@bot.message_handler(commands=["diplom"]) #Диплом пидора
def info(message):
    bot.send_chat_action(chat_id=message.chat.id, action="typing", timeout=3)  # Имитация набора текста
    time.sleep(random.randint(1, 3))
    bot.send_message(message.chat.id, "Сейчас оформлю все бумаги, одну секунду")
    cursor.execute(f'SELECT amount_fag FROM user_tg where id_user ={message.from_user.id} and chat_id = {message.chat.id}')
    amount_fag = cursor.fetchone()
    Diplom.pidor_1(f'{message.from_user.username}', amount_fag[0])
    img = open('image_tst.png', 'rb')
    bot.send_photo(message.chat.id, img)

@bot.message_handler(commands=["applicants"]) #Колл-во пидоров
def search_for_a_fag(message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id=message.chat.id, action="typing", timeout=3)  # Имитация набора текста
    time.sleep(random.randint(1, 3))
    cursor.execute(
        f"SELECT name_user, amount_fag FROM user_tg WHERE chat_id = {chat_id} ORDER BY amount_fag DESC LIMIT 10")  # сделать код с выводом 10 штук
    users_all = cursor.fetchall()
    info = ''
    rang = 1
    for el in users_all:
        info += f" <b>{rang}</b>  <b>{el[0]}</b> - {el[1]}\n"
        rang = rang + 1
        if rang == 11:
            break
    bot.send_message(message.chat.id, f"Топ 10 пидоров \n \n{info} Боритесь!", parse_mode='HTML')
@bot.message_handler(commands=["tellmewisdom"]) #скажи что-то мудрое
def tell_me_wisdom(message):
    resp = requests.get("https://api.forismatic.com/api/1.0/?method=getQuote&format=json")
    text = resp.json()
    bot.send_chat_action(chat_id=message.chat.id, action="typing", timeout=3)  # Имитация набора текста
    time.sleep(random.randint(1, 3))
    bot.send_message(message.chat.id, f"{text['quoteText']}")

"""
В  блоке ниже буду реализовывать общения и отвты на конкретные слова в чате
"""


@bot.message_handler(content_types="text")
def lalal(message):
    id_user = message.from_user.id
    name_user = message.from_user.username
    id_chat = message.chat.id
    cursor.execute(
        f"insert into text_message (text_user) values ('{message.text}') ") # Для сбора текста общения пользователей,для дальнейшего обучения бота диалогам.
    cursor.execute(f"SELECT id_user FROM user_tg where chat_id = {id_chat} and id_user={id_user}")

    if not cursor.fetchall():
        cursor.execute(
            f"insert into user_tg (id_user, name_user, amount_fag, chat_id) values ('{id_user}','{name_user}',0,{id_chat}) ")
        bot.send_message(message.chat.id, f"Добавил {name_user} в пидоры")

    if message.reply_to_message is not None:  # Если бота цитируют
        bot.send_chat_action(chat_id=message.chat.id, action="typing", timeout=3)  # Имитация набора текста
        time.sleep(random.randint(1, 3))  # Таймаут что бы прошла анимация текста
        bot.send_message(message.chat.id,
                         f"{message.from_user.username}, меня цитировать время терять")  # Отправляеть сообщения пользователю
    if "@bigeyedbotbot" in message.text:  # Если упоминули бота
        bot.send_chat_action(chat_id=message.chat.id, action="typing", timeout=3)  # Имитация набора текста
        time.sleep(random.randint(1, 3))  # Таймаут что бы прошла анимация текста
        bot.send_message(message.chat.id, "Зачем ты меня тыкаешь? У тебя же есть команды, вот и общайся ими.")
    if "бот" in message.text.lower():  # Если упоминули бота
        bot.send_chat_action(chat_id=message.chat.id, action="typing", timeout=3)  # Имитация набора текста
        time.sleep(random.randint(1, 3))  # Таймаут что бы прошла анимация текста
        with open('text_gen.txt', encoding='utf8') as text:
            text_model = markovify.Text(text)
            step = 0
            while step != 1:
                a = text_model.make_sentence()
                if a is None or len(a) == 45:
                    continue

                else:
                    step += 1
                    print(a)
        bot.send_message(message.chat.id, f"{a}", )
        bot.send_sticker(message.chat.id, sticker="CAACAgQAAxkBAAECHS1lX2r0_FkEZzb6ZlrF2B45QpiSxgAC-Q0AAse0kVMlfVlz7AesOjME")
    if "тупой" in message.text.lower():  # Если упоминули бота
        bot.send_chat_action(chat_id=message.chat.id, action="typing", timeout=3)  # Имитация набора текста
        time.sleep(random.randint(1, 3))  # Таймаут что бы прошла анимация текста
        bot.send_photo(message.chat.id, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT0V3dWFk4iQRtFto6BDQRJHEpNd33DwTuAt6pdjH2zatE_5wGtDY2WnLFFePAuH7qwaLw&usqp=CAU", caption="ну я же не специально!")
    if "голая" in message.text.lower():  # Если упоминули бота
        bot.send_chat_action(chat_id=message.chat.id, action="typing", timeout=3)  # Имитация набора текста
        time.sleep(random.randint(1, 3))  # Таймаут что бы прошла анимация текста
        bot.send_photo(message.chat.id, "https://i.pinimg.com/550x/e3/92/81/e39281d9aacc9757b3526baa55625a63.jpg")
    if "пидр" in message.text.lower():  # Если упоминули бота
        cursor.execute(f"SELECT max(data_fag) from data_fag where id_chat = {chat_id}")
        bot.send_chat_action(chat_id=message.chat.id, action="typing", timeout=3)  # Имитация набора текста
        time.sleep(random.randint(1, 3))  # Таймаут что бы прошла анимация текста
        # bot.send_message(message.chat.id, f"Все и так знаю кто пидр дня, да {}?")




bot.polling(none_stop=True)

text = 'sdgasgd'

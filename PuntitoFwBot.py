from dotenv import load_dotenv
load_dotenv()
import os
TOKEN = os.getenv("TOKEN")
import telebot
bot = telebot.TeleBot(TOKEN)
import sqlite3

canal_id=os.getenv("canal_id")
TABLE = "msg(msg_id INTEGER PRIMARY KEY, original_sender INTEGER, requested_by INTEGER)"

def create_table(table):
    con = sqlite3.connect('FwBot.db')
    cursorObj = con.cursor()
    cursorObj.execute("create table if not exists " + table)
    con.commit()
    con.close()

def already_in(new_msg):
    con = sqlite3.connect('FwBot.db')
    target = (new_msg,)
    
    cursorObj = con.cursor()
    cursorObj.execute("select msg_id from msg")
    msg_id_all = cursorObj.fetchall()
    con.close()

    return target in msg_id_all

def insert_new(new_msg_info):
    con = sqlite3.connect('FwBot.db')
    cursorObj = con.cursor()
    cursorObj.execute("insert into msg(msg_id, original_sender, requested_by) values(?,?,?)", new_msg_info)
    con.commit()
    con.close()

def user_info(user_id):
    con = sqlite3.connect('FwBot.db')
    cursorObj = con.cursor()
    cursorObj.execute("select * from msg where original_sender == "+ str(user_id))
    fw_org = cursorObj.fetchall()
    cursorObj.execute("select * from msg where requested_by == "+ str(user_id))
    fw_req = cursorObj.fetchall()
    con.close()
    return [len(fw_org),len(fw_req)]

def no_repetition(lista):
    return list(dict.fromkeys(lista))

def top(column, cant=5):
    con = sqlite3.connect('FwBot.db')
    cursorObj = con.cursor()
    cursorObj.execute("select %s from msg" %column)
    data = cursorObj.fetchall()
    data_norep = no_repetition(data)
    for i in range(len(data_norep)):
        rep = data.count(data_norep[i])
        data_norep[i] = list((data_norep[i],rep))
    data_norep.sort(reverse=True, key=lambda x: x[1])
    con.close()
    return data_norep[:cant]

def top_master(cant=5):
    return list((top("original_sender", cant),top("requested_by", cant)))
    
def get_user_tag(uid,cid):
    user_name = bot.get_chat_member(cid,uid).user.first_name
    return "[{}](tg://user?id={})".format(user_name,uid)

def get_user_name(uid,cid):
    user_name = bot.get_chat_member(cid,uid).user.first_name
    return user_name


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    global TABLE
    create_table(TABLE)
    bot.reply_to(message, "Hola! soy PuntitoForWardBot, simplemente utiliza /forward respondiendo a un mensaje para reenviarlo uwu")

@bot.message_handler(commands=["forward"])
def forwardeo(message):
    if "group" in message.chat.type:
        if message.reply_to_message is not None and not message.reply_to_message.from_user.is_bot:
            if not already_in(message.reply_to_message.message_id):
                msg_info = (message.reply_to_message.message_id, message.reply_to_message.from_user.id, message.from_user.id)
                insert_new(msg_info)
                bot.forward_message(message.chat.id, message.chat.id, message.reply_to_message.message_id)
                bot.forward_message(canal_id, message.chat.id, message.reply_to_message.message_id)
        else:
            bot.reply_to(message, "El comando se usa citando un mensaje de otro usuario po, owo")
    else:
        bot.reply_to(message, "Disculpa, solo funciono en grupos uwu")

@bot.message_handler(commands=["top"])
def mensaje_topn(message):
    bot_username = bot.get_me().username
    if message.text in ["/top","/top@"+bot_username]:
        m_text = "/top 5"
    else:
        m_text = message.text
    num = telebot.util.extract_arguments(m_text).strip()
    if num.isdigit():
        if int(num)==0:
            bot.reply_to(message, "El Top 0 está vacío! \nQue extraño, ¿no?")
        elif int(num)==69:
            bot.reply_to(message, "Jjjjajajkshs dijiste el número gracioso")
        elif int(num)>50:
            bot.reply_to(message, "Soy un bot chiquito y si me pides más de 50 usuarios en el top, me saturo y exploto. Por favor, no lo hagas uwu")
        else:
            chat_id = message.chat.id
            tops = top_master(int(num))
            top_org = tops[0]
            org = []
            top_req = tops[1]
            req = []
            for i in range(len(top_org)):
                org.append(get_user_name(top_org[i][0][0],chat_id)+" - "+str(top_org[i][1]))
            for i in range(len(top_req)):
                req.append(get_user_name(top_req[i][0][0],chat_id)+" - "+str(top_req[i][1]))
        
            response = "Top "+num+" forwardeados: \n"+"\n".join(org)+"\n\n"+"Top "+num+" forwarders: \n"+"\n".join(req)
            bot.reply_to(message, response)
    else:
        try:
            num = num.replace(",",".")
            fl = float(num)
        except ValueError:
            a = 0
        else:
            if not fl.is_integer():
                bot.reply_to(message, "¿Realmente quieres ver a %s usuarios en el Top?" %fl)
            else:
                bot.reply_to(message, "¿Por qué poner números así? ¿No ves que me confundes?")

@bot.message_handler(commands=["mis_forwards"])
def stats(message):
    chat_id=message.chat.id
    user_id=message.from_user.id
    user_name = message.from_user.first_name
    stats = user_info(user_id)
    response = "*{}*, te han forwardeado {} mensajes y has pedido {} forwards".format(user_name,stats[0],stats[1])
    bot.reply_to(message, response, parse_mode="MarkdownV2")

@bot.message_handler(commands=["tus_forwards"])
def stats(message):
    chat_id=message.chat.id
    if message.reply_to_message is not None and not message.reply_to_message.from_user.is_bot:
        user_id = message.reply_to_message.from_user.id
        user_name = get_user_name(user_id,chat_id)
        stats = user_info(user_id)
        response = "*{}*, te han forwardeado {} mensajes y has pedido {} forwards".format(user_name,stats[0],stats[1])
        bot.reply_to(message, response, parse_mode="MarkdownV2")
    else:
        bot.reply_to(message, "El comando se usa citando un mensaje de otro usuario po, owo")

@bot.message_handler(commands=["canal"])
def send_canal(message):
    bot.reply_to(message, "https://t.me/PuntitoForwarded")

bot.polling(none_stop=True)


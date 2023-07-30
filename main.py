import telebot
from telebot import types
import sqlite3
import datetime
from datetime import date

#Markups
MainMarkup = types.InlineKeyboardMarkup()

createButton = types.InlineKeyboardButton('Create ticket', callback_data='create')
listButton = types.InlineKeyboardButton('Ticket list', callback_data='list')

MainMarkup.row(createButton, listButton)

faqButton = types.InlineKeyboardButton('FAQ', callback_data='faq')
aboutButton = types.InlineKeyboardButton('About bot', callback_data='about')
MainMarkup.row(faqButton, aboutButton)
#----#
BackMarkup = types.InlineKeyboardMarkup()
backButton = types.InlineKeyboardButton('Back', callback_data='main')
BackMarkup.row(backButton)
#----#
BackToListMarkup = types.InlineKeyboardMarkup()
backToListButton = types.InlineKeyboardButton('Back', callback_data='list')
BackToListMarkup.row(backToListButton)
#Variables
StageParameter = 0
Tickets = 0
CurrentTicket = 0
AllTickets = 0
#Token
bot = telebot.TeleBot('TOKEN')

@bot.message_handler(commands=['start'])
def main(ctx):
    global MainMarkup, StageParameter
    StageParameter = 0
    conn = sqlite3.connect('data.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS tickets (id int auto_increment primary key, day varchar(50), time varchar(50), text varchar(400))')
    conn.commit()

    cur.close()
    conn.close()

    bot.send_message(ctx.chat.id, 'Hello! I am a Technical Support bot. How could i help you?', reply_markup=MainMarkup)
    if ctx.message_id - 1 > 0:
        bot.edit_message_reply_markup(ctx.chat.id, ctx.message_id - 1, reply_markup=None)

@bot.callback_query_handler(func=lambda ctx:True)
def handler(ctx):
    global MainMarkup, BackMarkup, StageParameter, Tickets, CurrentTicket
    match(ctx.data):
        #MainSection
        case 'create':
            bot.edit_message_text('Describe your problem here. The text must contain more than 40 characters. After creating a ticket, his status can be viewed in the "Ticket list"', ctx.message.chat.id, ctx.message.message_id)
            bot.edit_message_reply_markup(ctx.message.chat.id, ctx.message.message_id, reply_markup=BackMarkup)
            StageParameter = 1
            return
        case 'list':
            CurrentTicket = None
            ticketsList(ctx.message)
            return
        case 'faq':
            bot.edit_message_text('Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                                  'Lobortis elementum nibh tellus molestie nunc. Sit amet cursus sit amet. Sociis natoque penatibus et magnis dis parturient montes. '
                                  'Ut eu sem integer vitae justo eget magna. Interdum varius sit amet mattis vulputate enim. Odio facilisis mauris sit amet massa. '
                                  'Viverra nibh cras pulvinar mattis. Est ante in nibh mauris cursus mattis molestie a. Dictumst quisque sagittis purus sit. Tortor '
                                  'at auctor urna nunc. Congue nisi vitae suscipit tellus mauris a diam maecenas sed. Id volutpat lacus laoreet non curabitur gravida '
                                  'arcu. Ornare arcu dui vivamus arcu felis bibendum ut. Molestie nunc non blandit massa enim nec dui. Erat pellentesque adipiscing '
                                  'commodo elit at imperdiet.', ctx.message.chat.id, ctx.message.message_id)
            bot.edit_message_reply_markup(ctx.message.chat.id, ctx.message.message_id, reply_markup=BackMarkup)
            return
        case 'about':
            bot.edit_message_text('About bot: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.', ctx.message.chat.id, ctx.message.message_id)
            bot.edit_message_reply_markup(ctx.message.chat.id, ctx.message.message_id, reply_markup=BackMarkup)
            return
        case 'main':
            CurrentTicket = None
            bot.edit_message_text('Hello! I am a Technical Support bot. How could i help you?', ctx.message.chat.id, ctx.message.message_id)
            bot.edit_message_reply_markup(ctx.message.chat.id, ctx.message.message_id, reply_markup=MainMarkup)
            StageParameter = 0
            return
        case 'delete':
            deleteTicket(ctx.message, CurrentTicket)
            return

    #TicketSection
    for i in range(Tickets):
        msg_data = int(ctx.data)
        if i == msg_data:
            CurrentTicket = i

            TicketMarkup = types.InlineKeyboardMarkup()
            deleteButton = types.InlineKeyboardButton('Delete ticket', callback_data='delete')
            backButton = types.InlineKeyboardButton('back', callback_data='list')
            TicketMarkup.row(deleteButton)
            TicketMarkup.row(backButton)

            conn = sqlite3.connect('data.sql')
            cur = conn.cursor()

            cur.execute('SELECT * FROM tickets')
            data = cur.fetchall()

            bot.edit_message_text(f'{data[i][1]}, {data[i][2]} Ticket\nStatus: Not viewed\nTicket text:\n{data[i][3]}', ctx.message.chat.id, ctx.message.message_id)
            bot.edit_message_reply_markup(ctx.message.chat.id, ctx.message.message_id, reply_markup=TicketMarkup)
            
            cur.close()
            conn.close()

@bot.message_handler()
def createTicket(ctx):
    global StageParameter, BackMarkup, AllTickets
    if StageParameter != 1:
        return
    if len(ctx.text) < 40:
        bot.edit_message_reply_markup(ctx.chat.id, ctx.message_id - 1, reply_markup=None)
        bot.send_message(ctx.chat.id, 'Text must contain more than 40 characters', reply_markup=BackMarkup)
    else:
        text = ctx.text;
        day = date.today().strftime('%d.%m.%Y')
        time = datetime.datetime.today().strftime('%H:%M')

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()

        cur.execute('SELECT id FROM tickets')
        data = cur.fetchall()

        if len(data) != 0:
            id = max(data)
            max_id = data.index(id)
            AllTickets = max_id + 1

        cur.execute(f'INSERT INTO tickets (id, day, time, text) VALUES ("%s", "%s", "%s", "%s")' % (AllTickets, day, time, text))
        conn.commit()

        cur.close()
        conn.close()

        AllTickets += 1
        bot.edit_message_reply_markup(ctx.chat.id, ctx.message_id - 1, reply_markup=None)
        bot.send_message(ctx.chat.id, 'Ticket created!', reply_markup=BackMarkup)

def ticketsList(ctx):
    global backButton, Tickets, BackMarkup
    Tickets = 0
    ListMarkup = types.InlineKeyboardMarkup()

    conn = sqlite3.connect('data.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM tickets')
    data = cur.fetchall()

    if len(data) != 0:
        for el in data:
            locals()[f'button{Tickets}'] = types.InlineKeyboardButton(f'{el[1]}, {el[2]} Ticket', callback_data=f'{Tickets}')
            ListMarkup.row(locals()[f'button{Tickets}'])
            Tickets += 1
        ListMarkup.row(backButton)

        cur.close()
        conn.close()

        bot.edit_message_text('Ticket list', ctx.chat.id, ctx.message_id)
        bot.edit_message_reply_markup(ctx.chat.id, ctx.message_id, reply_markup=ListMarkup)
    else:
        cur.close()
        conn.close()

        bot.edit_message_text('You dont have tickets', ctx.chat.id, ctx.message_id)
        bot.edit_message_reply_markup(ctx.chat.id, ctx.message_id, reply_markup=BackMarkup)

def deleteTicket(ctx, id):
    global BackToListMarkup

    conn = sqlite3.connect('data.sql')
    cur = conn.cursor()

    cur.execute(f"DELETE FROM tickets WHERE id = '{int(id)}'")
    conn.commit()

    cur.execute('SELECT id FROM tickets')
    data = cur.fetchall()

    cur.close()
    conn.close()

    bot.edit_message_text('Ticket deleted succesfully!', ctx.chat.id, ctx.message_id)
    bot.edit_message_reply_markup(ctx.chat.id, ctx.message_id, reply_markup=BackToListMarkup)

bot.polling(none_stop=True)
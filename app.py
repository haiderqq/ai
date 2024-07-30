import telebot
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import google.generativeai as genai
import psycopg2
import PIL.Image
import io
'''
git add .
git commit -m "Update files"
git push heroku master
'''

'''
git remote add origin https://github.com/haiderqq/ai-bot.git
'''
bot = telebot.TeleBot(token="7164391412:AAGu3pMKXXfgQHDGQKwggacdvSQuASW54EA")
ADMIN_ID = 1214392661
channel_name = "@botifl_ai"
# إعداد الاتصال بقاعدة البيانات
DATABASE_URL = "postgres://koyeb-adm:hVa57pEYmJNI@ep-summer-thunder-a2u8j8ss.eu-central-1.pg.koyeb.app/koyebdb"
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def create_users_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            total_messages_sent INTEGER DEFAULT 0,
            preferred_language TEXT DEFAULT 'ar'  -- Default to Arabic
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

create_users_table()

def get_user_data(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT total_messages_sent, preferred_language FROM users WHERE user_id = %s', (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        return {'total_messages_sent': result[0], 'preferred_language': result[1]}
    return None

def save_user_data(user_id, data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO users (user_id, total_messages_sent, preferred_language) 
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET 
        total_messages_sent = EXCLUDED.total_messages_sent,
        preferred_language = EXCLUDED.preferred_language
    ''', (user_id, data['total_messages_sent'], data['preferred_language']))
    conn.commit()
    cur.close()
    conn.close()

# Function to handle changing language
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def change_language(call: CallbackQuery):
    user_id = str(call.from_user.id)
    new_language = call.data.split('_')[1]
    user_data = get_user_data(user_id)
    if user_data:
        user_data['preferred_language'] = new_language
        save_user_data(user_id, user_data)
        bot.send_message(call.message.chat.id, f"Language changed to {new_language}")
        
def get_text(key, language='ar'):
    texts = {
        'ar': {
            'welcome': "<b>مرحبًا انا بوت Chatgpt تم انشائي من قبل المبرمج @hd0rr , كيف يمكنني مساعدتك .؟</b>\n\nيمكنك استخدام هذا البوت لطرح الأسئلة على الذكاء الاصطناعي، فقط قم بارسال رسالة وسيقوم البوت بالرد عليك.",
            'help': "مساعدة",
            'contact_dev': "تواصل مع إدارة البوت",
            'choose_language': "اختر اللغة",
            'channel': f"يرجى الاشتراك في القناة {channel_name} لاستخدام البوت.",
            'help_txt': "يرجى استخدام هذا الأمر بالرد على رسالة ليتم الرد على الشخص الذي أرسلها.",
            'er_ai': "عذراً، لا يمكن الحصول على إجابة في الوقت الحالي."
        },
        'en': {
            'welcome': "<b>Welcome, I am the Chatgpt bot created by @hd0rr. How can I assist you?</b>\n\nYou can use this bot to ask AI questions, just send a message and the bot will respond.",
            'help': "Help",
            'contact_dev': "Contact Bot Admin",
            'choose_language': "Choose Language",
            'channel': f"Please subscribe to the channel {channel_name} to use the bot.",
            'help_txt': "Please use this command to reply to a message in order to respond to the person who sent it.",
            'er_ai': "Sorry, it is not possible to get an answer at the moment."
        },
        'fr': {
            'welcome': "<b>Bienvenue, je suis le bot Chatgpt créé par @hd0rr. Comment puis-je vous aider?</b>\n\nVous pouvez utiliser ce bot pour poser des questions à l'IA, envoyez simplement un message et le bot répondra.",
            'help': "Aide",
            'contact_dev': "Contacter l'administrateur du bot",
            'choose_language': "Choisir la langue",
            'channel': f"Veuillez vous abonner à la chaîne {channel_name} pour utiliser le bot.",
            'help_txt': "Veuillez utiliser cette commande pour répondre à un message afin de répondre à la personne qui l'a envoyé.",
            'er_ai':"Désolé, il n'est pas possible d'obtenir une réponse pour le moment."
        }
        # الفرنسية: Désolé, il n'est pas possible d'obtenir une réponse pour le moment.
        # الإنجليزية: Sorry, it is not possible to get an answer at the moment.
    }
    return texts.get(language, texts['ar']).get(key, '')

def get_user_language_from_db(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT preferred_language FROM users WHERE user_id = %s', (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        return result[0]
    return 'ar'  # إرجاع اللغة الافتراضية إذا لم يتم العثور على اللغة للمستخدم

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = "<b>مرحبًا انا بوت Chatgpt تم انشائي من قبل المبرمج @hd0rr , كيف يمكنني مساعدتك .؟</b>\n\nيمكنك استخدام هذا البوت لطرح الأسئلة على الذكاء الاصطناعي، فقط قم بارسال رسالة وسيقوم البوت بالرد عليك."
    chat_id = message.chat.id
    user_id = str(chat_id)
    user_data = get_user_data(user_id)
    if not user_data:
        save_user_data(user_id, {'total_messages_sent': 0, 'preferred_language': 'ar'})
        user_data = {'total_messages_sent': 0, 'preferred_language': 'ar'}
    user_language = user_data['preferred_language']
    welcome_message = get_text('welcome', user_language)
    # إرسال الرسالة المرحبة وتحديث اللغة بناءً على تفضيلات المستخدم

    keyboard = InlineKeyboardMarkup()
    help_button = InlineKeyboardButton(get_text('help', user_language), url="https://t.me/CGPTCommunity")
    contact_dev_button = InlineKeyboardButton(get_text('contact_dev', user_language), url="https://t.me/hd0rr")
    keyboard.add(help_button, contact_dev_button)

    language_button_ar = InlineKeyboardButton("العربية", callback_data='lang_ar')
    language_button_en = InlineKeyboardButton("English", callback_data='lang_en')
    language_button_fr = InlineKeyboardButton("Français", callback_data='lang_fr')
    keyboard.add(language_button_ar, language_button_en, language_button_fr)
    
    if message.from_user.id == ADMIN_ID:
        admin_button1 = InlineKeyboardButton("عدد المشتركين", callback_data='subscribers_count')
        admin_button2 = InlineKeyboardButton("إرسال رسالة جماعية", callback_data='broadcast')
        admin_button3 = InlineKeyboardButton("إرسال رسالة مباشرة", callback_data='send_message')
        keyboard.add(admin_button1)
        keyboard.add(admin_button2, admin_button3)
    
    bot.send_message(chat_id, welcome_message, parse_mode='HTML', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    if call.message.chat.type != 'private':
        return
    
    if call.data == 'subscribers_count':
        if call.from_user.id == ADMIN_ID:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM users')
            count = cur.fetchone()[0]
            cur.close()
            conn.close()
            bot.send_message(call.message.chat.id, f"عدد المشتركين في البوت: {count}")
    
    elif call.data == 'broadcast':
        if call.from_user.id == ADMIN_ID:
            msg = bot.send_message(call.message.chat.id, "يرجى إدخال الرسالة التي تريد إرسالها لجميع المشتركين:")
            bot.register_next_step_handler(msg, broadcast_message)

    elif call.data == 'send_message':
        if call.from_user.id == ADMIN_ID:
            msg = bot.send_message(call.message.chat.id, "يرجى إدخال هوية المستخدم والرسالة بالشكل التالي: user_id message")
            bot.register_next_step_handler(msg, send_direct_message)

def broadcast_message(message):
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        return
    text = message.text.strip()
    if not text:
        bot.send_message(message.chat.id, "عذراً، لا يمكن إرسال رسالة فارغة.")
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT user_id FROM users')
    user_ids = cur.fetchall()
    cur.close()
    conn.close()
    for user_chat_id in user_ids:
        try:
            bot.send_message(user_chat_id[0], text)
        except Exception as e:
            print(f"Error sending message to {user_chat_id}: {e}")

def send_direct_message(message):
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        return
    text = message.text.strip()
    if not text:
        bot.send_message(message.chat.id, "عذراً، لا يمكن إرسال رسالة فارغة.")
        return
    parts = text.split(' ', 1)
    if len(parts) != 2:
        bot.send_message(message.chat.id, "يرجى استخدام الأمر بالصيغة الصحيحة: user_id message")
        return
    target_user_id, text_message = parts
    try:
        bot.send_message(target_user_id, text_message)
        bot.send_message(message.chat.id, f"تم إرسال رسالتك إلى المستخدم ذو الهوية {target_user_id}")
    except Exception as e:
        bot.send_message(message.chat.id, f"حدث خطأ أثناء إرسال الرسالة: {e}")

def gpt(text) -> str:
    genai.configure(api_key='AIzaSyDuaXa8eeF_Mkoo_47tpGTrYdameWStWs0')
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    result = model.generate_content(text)
    try:
        return result.text
    except:
        return None
@bot.message_handler(commands=['reply'])
def reply_message(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = str(message.from_user.id)

        user_data = get_user_data(user_id)
        if not user_data:
            save_user_data(user_id, {'total_messages_sent': 0, 'preferred_language': 'ar'})
            user_data = {'total_messages_sent': 0, 'preferred_language': 'ar'}

        user_language = user_data['preferred_language']
        language = get_user_language_from_db(user_id)
        member = bot.get_chat_member(chat_id=channel_name, user_id=user_id)
        if member.status not in ["member", "administrator", "creator"]:
            bot.send_message(chat_id, get_text('channel', language))
            return

        replied_message = message.reply_to_message
        chat_id = replied_message.chat.id  # توجيه الرد في نفس المجموعة التي تم فيها الرد
        response = gpt(replied_message.text)

        if response:
            bot.send_message(chat_id, f"@{replied_message.from_user.username}\n{response}")  # إرسال الرد في المجموعة مع اسم المستخدم
            user_data['total_messages_sent'] += 1
            save_user_data(user_id, user_data)
        else:
            bot.send_message(chat_id, f"@{replied_message.from_user.username}\nعذراً، لا يمكن الحصول على إجابة في الوقت الحالي.")
    else:
        user_id = str(message.from_user.id)  # Define user_id here
        language = get_user_language_from_db(user_id)
        bot.send_message(message.chat.id, get_text('help_txt', language))
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    if message.chat.type == 'private' or message.text.startswith("/ask"):
        chat_id = message.chat.id
        user_id = str(message.from_user.id)

        user_data = get_user_data(user_id)
        if not user_data:
            save_user_data(user_id, {'total_messages_sent': 0, 'preferred_language': 'ar'})
            user_data = {'total_messages_sent': 0, 'preferred_language': 'ar'}

        user_language = user_data['preferred_language']
        language = get_user_language_from_db(user_id)
        member = bot.get_chat_member(chat_id=channel_name, user_id=user_id)
        if member.status not in ["member", "administrator", "creator"]:
            bot.send_message(chat_id, get_text('channel', language))
            return

        if message.text.startswith("/reply"):  # توجيه استخدام /reply إلى reply_message
            reply_message(message)
            return

        text = message.text.replace("/ask", "").strip()

        if not text:
            bot.send_message(chat_id, "يرجى كتابة نص بعد /ask لكي أستطيع مساعدتك.")
            return

        bot.send_chat_action(chat_id, 'typing')
        bot.reply_to(message, "📝")

        response = gpt(text)
        bot.send_chat_action(chat_id, 'cancel')
        bot.reply_to(message, response)

        user_data['total_messages_sent'] += 1
        save_user_data(user_id, user_data)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        if message.chat.type == 'private' or message.chat.type in ['group', 'supergroup']:
            chat_id = message.chat.id
            user_id = str(message.from_user.id)

            user_data = get_user_data(user_id)
            if not user_data:
                save_user_data(user_id, {'total_messages_sent': 0, 'preferred_language': 'ar'})
                user_data = {'total_messages_sent': 0, 'preferred_language': 'ar'}

            user_language = user_data['preferred_language']
            language = get_user_language_from_db(user_id)
            member = bot.get_chat_member(chat_id=channel_name, user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                bot.send_message(chat_id, get_text('channel', language))
                return
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            image = PIL.Image.open(io.BytesIO(downloaded_file))

            text = message.caption if message.caption else "وصف الصورة"

            bot.reply_to(message, "📝")
            genai.configure(api_key='AIzaSyDuaXa8eeF_Mkoo_47tpGTrYdameWStWs0')

            model = genai.GenerativeModel('models/gemini-1.5-flash')
            response = model.generate_content([text, image], stream=True)
            response.resolve()

            bot.reply_to(message, response.text)

            user_data['total_messages_sent'] += 1
            save_user_data(user_id, user_data)
    except Exception as e:
        print(e)
        bot.reply_to(message, "حدث خطأ أثناء معالجة الصورة.")

bot.infinity_polling()

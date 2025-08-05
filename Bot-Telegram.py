import telebot
from telebot import types

# Conexión con nuestro BOT
TOKEN = 'TOKEN_HERE'
bot = telebot.TeleBot(TOKEN)

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Menú principal
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_info = types.KeyboardButton('📖 Información')
    btn_cursos = types.KeyboardButton('🎓 Cursos')
    btn_contacto = types.KeyboardButton('📞 Contacto')
    markup.add(btn_info, btn_cursos, btn_contacto)
    
    bot.send_message(
        message.chat.id, 
        "¡Bienvenido! Soy tu asistente virtual. Elige una opción para continuar:",
        reply_markup=markup
    )

# Manejo de la opción Información
@bot.message_handler(func=lambda message: message.text == '📖 Información')
def send_information(message):
    # Creando botones con URLs
    markup = types.InlineKeyboardMarkup()
    btn_leer_mas = types.InlineKeyboardButton("Leer más", url="https://google.com/info")
    btn_ver_demo = types.InlineKeyboardButton("Ver demo", url="https://google.com")
    markup.add(btn_leer_mas, btn_ver_demo)
    
    # Enviando imagen, descripción y botones
    bot.send_photo(
        message.chat.id,
        photo="test.png",
        caption="Aquí tienes una descripción detallada sobre el contenido solicitado. "
                "Explora más detalles usando los botones a continuación.",
        reply_markup=markup
    )

# Manejo de la opción Cursos
@bot.message_handler(func=lambda message: message.text == '🎓 Cursos')
def send_courses(message):
    # Creando botones con URLs
    markup = types.InlineKeyboardMarkup()
    btn_curso_1 = types.InlineKeyboardButton("Curso 1", url="https://google.com")
    btn_curso_2 = types.InlineKeyboardButton("Curso 2", url="https://google.com/curso2")
    markup.add(btn_curso_1, btn_curso_2)
    
    # Enviando imagen, descripción y botones
    bot.send_photo(
        message.chat.id,
        photo="test2.png",
        caption="Aquí tienes los cursos recomendados. Selecciona uno para obtener más información.",
        reply_markup=markup
    )

# Manejo de la opción Contacto
@bot.message_handler(func=lambda message: message.text == '📞 Contacto')
def send_contact_info(message):
    # Creando botones con URLs
    markup = types.InlineKeyboardMarkup()
    btn_telegram = types.InlineKeyboardButton("Contáctanos por Telegram", url="https://t.me/soporte")
    btn_email = types.InlineKeyboardButton("Enviar un correo", url="mailto:soporte@google.com")
    markup.add(btn_telegram, btn_email)
    
    # Enviando imagen, descripción y botones
    bot.send_photo(
        message.chat.id,
        photo="test3.png",
        caption="¿Necesitas ayuda? Contáctanos a través de los siguientes medios:",
        reply_markup=markup
    )

# Respuesta genérica para mensajes no reconocidos
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    bot.send_message(
        message.chat.id,
        "No entendí tu solicitud. Por favor, selecciona una opción del menú."
    )

# Iniciar el bot
if __name__ == "__main__":
    print("Bot en ejecución...")
    bot.polling(none_stop=True)

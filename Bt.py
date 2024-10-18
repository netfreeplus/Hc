import telebot
from telebot import types
import requests

# Inicializa el bot con el token de Telegram
TOKEN = "TU_TOKEN_AQUÍ"
bot = telebot.TeleBot(TOKEN)

# Función que se ejecuta cuando el usuario usa /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Creando un menú con botones
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔍 Validar BIN")
    btn2 = types.KeyboardButton("💳 Generar tarjeta")
    btn3 = types.KeyboardButton("✔️ Validar tarjeta")
    markup.add(btn1, btn2, btn3)
    
    # Enviando mensaje con los botones
    bot.send_message(message.chat.id, "¡Bienvenido! Elige una opción:", reply_markup=markup)

# Función para validar el BIN (esto ya lo tienes implementado)
@bot.message_handler(func=lambda message: message.text == "🔍 Validar BIN")
def handle_bin(message):
    bot.send_message(message.chat.id, "Introduce el BIN que deseas validar (debe tener al menos 6 dígitos):")
    bot.register_next_step_handler(message, validate_bin)

def validate_bin(message):
    bin_input = message.text.strip()
    if not bin_input.isdigit() or len(bin_input) < 6:
        bot.send_message(message.chat.id, "Debes ingresar un BIN numérico de al menos 6 dígitos.")
    else:
        # Aquí va tu código para la validación del BIN con la API
        response = requests.get(f"https://data.handyapi.com/bin/{bin_input}")
        api = response.json()
        if api["Status"] == "SUCCESS":
            bot.send_message(message.chat.id, f"Información del BIN {bin_input}: {api}")
        else:
            bot.send_message(message.chat.id, "El BIN ingresado no es válido.")

# Función para generar tarjetas (usando el algoritmo de Luhn)
@bot.message_handler(func=lambda message: message.text == "💳 Generar tarjeta")
def generate_card(message):
    card_number = generate_luhn_card()
    bot.send_message(message.chat.id, f"Tarjeta generada: {card_number}")

def generate_luhn_card():
    import random
    def luhn_residue(digits):
        return sum(sum(divmod(int(d) * (1 + i % 2), 10)) for i, d in enumerate(digits[::-1])) % 10
    base = [str(random.randint(0, 9)) for _ in range(15)]
    check_digit = (10 - luhn_residue(base)) % 10
    return ''.join(base) + str(check_digit)

# Función para validar una tarjeta de crédito usando el algoritmo de Luhn
@bot.message_handler(func=lambda message: message.text == "✔️ Validar tarjeta")
def validate_card(message):
    bot.send_message(message.chat.id, "Introduce el número de tarjeta que deseas validar:")
    bot.register_next_step_handler(message, check_card)

def check_card(message):
    card_number = message.text.strip()
    if luhn_check(card_number):
        bot.send_message(message.chat.id, "La tarjeta es válida según el algoritmo de Luhn.")
    else:
        bot.send_message(message.chat.id, "La tarjeta no es válida.")

def luhn_check(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10 == 0

# Función para ejecutar el bot de forma continua
bot.polling(none_stop=True)

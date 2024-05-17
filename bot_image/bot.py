import paramiko
import os
from dotenv import load_dotenv
import logging
import re
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import logging
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
from pathlib import Path

#env_path = Path('../.env')
load_dotenv()

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

connection = None
def connectToDB():
    try:
        connection = psycopg2.connect(user=os.getenv('DB_USER'),password=os.getenv('DB_PASSWORD'),host=os.getenv('DB_HOST'),port=os.getenv('DB_PORT'), database=os.getenv('DB_DATABASE'))
    except (Exception, Error) as error:
        logging.debug("Ошибка при работе с PostgreSQL: %s", error)

logger = logging.getLogger(__name__)

TOKEN = os.getenv('TOKEN')
print(TOKEN)

# Функции paramiko для работы с удаленным сервером 
def monitoringFunc(query):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(str(query))
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data

def start(update: Update, context):
    logging.debug(f'start({update})')
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def helpCommand(update: Update, context):
    logging.debug(f'help({update})')
    update.message.reply_text('Список команд:\n/find_phone_number\n/find_email\n/verify_password\n/get_release\n/get_uname\
        \n/get_uptime\n/get_df\n/get_free\n/get_mpstat\n/get_w\n/get_auths\n/get_critical\n/get_ps\n/get_ss\n/get_apt_list\n/get_services\
        \n/get_repl_logs\n/get_emails\n/get_phone_numbers')

def findPhoneNumbersCommand(update: Update, context):
    logging.debug(f'findPhoneNumbers({update})')
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'

def findPhoneNumbers (update: Update, context):
    user_input = update.message.text 
    phoneNumRegex = re.compile(r'[8|\+7] ?\(?\d{3}\)? ?\d{3}[-| ]?\d{2}[-| ]?\d{2}') 
    phoneNumberList = phoneNumRegex.findall(user_input)
    
    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END 
    phoneNumbers = '' 
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n'
    update.message.reply_text(phoneNumbers) 
    update.message.reply_text('Записать найденные телефонные номера в базу данных?')
    context.user_data["data"] = phoneNumberList
    context.user_data["table"] = 'phone_numbers'
    context.user_data["column"] = 'phone'
    return 'insertData'

# -------------------- EMAIL -------------------

def findEmailCommand(update: Update, context):
    logging.debug(f'findEmailCommand({update})')
    update.message.reply_text('Введите текст для поиска Email адресов: ')
    return 'findEmail'

def findEmail (update: Update, context):
    user_input = update.message.text 
    emailRegex = re.compile(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)') 
    emailList = emailRegex.findall(user_input)
    if not emailList: 
        update.message.reply_text('Email адреса не найдены')
        return ConversationHandler.END 
    emails = ''
    for i in range(len(emailList)):
        emails += f'{i+1}. {emailList[i]}\n' 
    update.message.reply_text(emails) 
    update.message.reply_text('Записать найденные Email в базу данных?')
    context.user_data["data"] = emailList
    context.user_data["table"] = 'emails'
    context.user_data["column"] = 'email'
    return 'insertData'
    
# -------------- CHECK PASSWORD ----------------

def checkPasswordCommand(update: Update, context):
    logging.debug(f'checkPasswordCommand({update})')
    update.message.reply_text('Введите пароль для проверки сложности: ')
    return 'checkPassword'

def checkPassword (update: Update, context):
    user_input = update.message.text 
    passwordRegex = re.compile(r'(?=.*[0-9])(?=.*[!@#$%^&*()])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*()]{8,}') 
    passwordList = passwordRegex.findall(user_input)
    if not passwordList: 
        update.message.reply_text('Пароль простой')
        return ConversationHandler.END 
    else:
        update.message.reply_text('Пароль сложный') 
        return ConversationHandler.END
    
# ------------------------- MONITORING LINUX --------------------------------------

def getRelease(update: Update, context):
    logging.debug(f'getRelease({update})')
    return update.message.reply_text(monitoringFunc("cat /etc/*-release")) 

def getUname(update: Update, context):
    logging.debug(f'getUname({update})')
    return update.message.reply_text(monitoringFunc("uname -a")) 

def getUptime(update: Update, context):
    logging.debug(f'getUptime({update})')
    return update.message.reply_text(monitoringFunc("uptime -p")) 

def getDF(update: Update, context):
    logging.debug(f'getDF({update})')
    return update.message.reply_text(monitoringFunc("df -h")) 

def getFree(update: Update, context):
    logging.debug(f'getFree({update})')
    return update.message.reply_text(monitoringFunc("free -h -w")) 
    
def getMpstat(update: Update, context):
    logging.debug(f'getMpstat({update})')
    return update.message.reply_text(monitoringFunc("mpstat")) 

def getW(update: Update, context):
    logging.debug(f'getW({update})')
    return update.message.reply_text(monitoringFunc("w")) 

def getAuths(update: Update, context):
    logging.debug(f'getAuths({update})')
    return update.message.reply_text(monitoringFunc("last -n 10")) 

def getCritical(update: Update, context):
    logging.debug(f'getCritical({update})')
    return update.message.reply_text(monitoringFunc("journalctl -n 5 -p crit")) 

def getPS(update: Update, context):
    logging.debug(f'getPS({update})')
    return update.message.reply_text(monitoringFunc("ps")) 

def getSS(update: Update, context):
    logging.debug(f'getSS({update})')
    return update.message.reply_text(monitoringFunc("ss -lntu")) 

def getAptListCommand(update: Update, context):
    logging.debug(f'getAptListCommand({update})')
    update.message.reply_text('Введите all для вывода списка всех пакетов или название пакета для просмотра\
         подробной информации о нем: ')
    return 'getAptList'

def getAptList (update: Update, context):
    user_input = update.message.text 
    if user_input == "all": 
        update.message.reply_text(monitoringFunc("apt list --installed | head -n 50"))
        return ConversationHandler.END
    else:
        update.message.reply_text(monitoringFunc('apt show '+str(user_input)))
        return ConversationHandler.END 

def getServices(update: Update, context):
    logging.debug(f'getServices({update})')
    return update.message.reply_text(monitoringFunc("service --status-all")) 

def getReplLogs(update: Update, context):
    logging.debug(f'getReplLogs({update})')
    return update.message.reply_text(monitoringFunc("docker logs pt_start_db_1 -n 10 2>&1 | grep repl")) 
#-----------------------POSTGRESQL---------------------

def getEmails(update: Update, context):
    if connection == None:
        connectToDB()
    logging.debug(f'getEmails({update})')
    cursor = connection.cursor()
    cursor.execute("SELECT email FROM emails;")
    data = cursor.fetchall()
    entries = '' 
    for i in range(len(data)):
        entries += f'{i+1}. {data[i][0]}\n' 
    update.message.reply_text(entries) 
    return 

def getPhones(update: Update, context):
    if connection == None:
        connectToDB()
    logging.debug(f'getPhones({update})')
    cursor = connection.cursor()
    cursor.execute("SELECT phone FROM phone_numbers;")
    data = cursor.fetchall()
    entries = '' 
    for i in range(len(data)):
        entries += f'{i+1}. {data[i][0]}\n' 
    update.message.reply_text(entries) 
    return

def insertData(update: Update, context):
    if connection == None:
        connectToDB()
    user_input = update.message.text
    data = context.user_data["data"]
    table = context.user_data["table"]
    column = context.user_data["column"]
    print(user_input)
    if user_input == "да" or user_input == "yes" or user_input == "Да" or user_input == "Yes": 
        try:
            cursor = connection.cursor()
            for i in range(len(data)):
                cursor.execute(f"INSERT INTO {table} ({column}) VALUES ('{data[i]}');")
            update.message.reply_text('Данные записаны успешно')
            return ConversationHandler.END
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text('Произошла ошибка при записи данных')
            return ConversationHandler.END
    else:
        return ConversationHandler.END

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater(os.getenv('TOKEN'), use_context=True)
    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher
    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'insertData': [MessageHandler(Filters.text & ~Filters.command, insertData)],
        },
        fallbacks=[]
    )
    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
            'insertData': [MessageHandler(Filters.text & ~Filters.command, insertData)],
        },
        fallbacks=[]
    )
    convHandlerCheckPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', checkPasswordCommand)],
        states={
            'checkPassword': [MessageHandler(Filters.text & ~Filters.command, checkPassword)],
        },
        fallbacks=[]
    )
    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', getAptListCommand)],
        states={
            'getAptList': [MessageHandler(Filters.text & ~Filters.command, getAptList)],
        },
        fallbacks=[]
    )
    
  # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerCheckPassword)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("get_release",getRelease))
    dp.add_handler(CommandHandler("get_uname",getUname))
    dp.add_handler(CommandHandler("get_uptime",getUptime))
    dp.add_handler(CommandHandler("get_df",getDF))
    dp.add_handler(CommandHandler("get_free",getFree))
    dp.add_handler(CommandHandler("get_mpstat",getMpstat))
    dp.add_handler(CommandHandler("get_w",getW))
    dp.add_handler(CommandHandler("get_auths",getAuths))
    dp.add_handler(CommandHandler("get_critical",getCritical))
    dp.add_handler(CommandHandler("get_ps",getPS))
    dp.add_handler(CommandHandler("get_ss",getSS))
    dp.add_handler(convHandlerGetAptList)
    dp.add_handler(CommandHandler("get_services",getServices))
    dp.add_handler(CommandHandler("get_repl_logs",getReplLogs))
    dp.add_handler(CommandHandler("get_emails",getEmails))
    dp.add_handler(CommandHandler("get_phone_numbers",getPhones))
    
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

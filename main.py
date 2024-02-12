import logging,os,random, re
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from typing import List

TOKEN = ""
owner = []
# 檔案名稱
Bur_users = 'Bur_users.txt'
authorized_users = 'authorized_users.txt'
replies = 'replies.txt'
log_file_path = 'testbot.log'

if not os.path.isfile(log_file_path):
    with open(log_file_path, 'w') as f:
        print(f'日誌文件 {log_file_path} 已創建。')
else:
    print(f'日誌文件 {log_file_path} 已存在。')
if not os.path.isfile(replies):
    with open(replies, 'w', encoding='utf-8') as f:
        print(f'回覆文件 {replies} 已創建。')
else:
    print(f'回覆文件 {replies} 已存在。')
if not os.path.isfile(authorized_users):
    with open(authorized_users, 'w', encoding='utf-8') as f:
        print(f'人員文件 {authorized_users} 已創建。')
else:
    print(f'人員文件 {authorized_users} 已存在。')
if not os.path.isfile(Bur_users):
    with open(Bur_users, 'w', encoding='utf-8') as f:
        print(f'人員文件 {Bur_users} 已創建。')
else:
    print(f'人員文件 {Bur_users} 已存在。')

# 啟用日誌記錄
logging.basicConfig(
    filename='testbot.log',  # 日誌文件名稱
    filemode='a',  # 文件模式設為寫入模式
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日誌格式
    level=logging.INFO , # 日誌級別設為INFO
    encoding='utf-8'
)

def is_authorized(user_id: int) -> bool:
    """檢查用戶是否有權限"""
    return user_id in load_authorized_users() and user_id != owner
def is_bur(user_id: int) -> bool:
    """檢查用戶是否有權限"""
    return user_id in load_Bur_users() 

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('現在可以開始聊天拉')

def userid(update: Update, context: CallbackContext) -> None:
    # 檢查是否有回覆的訊息
    if update.message.reply_to_message:
        update.message.reply_text(f"userid : {update.message.reply_to_message.from_user.id}")
    else:
        update.message.reply_text(f"userid : {update.message.from_user.id}")

def delete(update: Update, context: CallbackContext) -> None:
    # 檢查是否有回覆的訊息
    if update.message.reply_to_message:
        # 檢查用戶是否在授權人員列表中
        if is_authorized(update.message.from_user.id):
            # 嘗試刪除訊息
            try:
                update.message.reply_to_message.delete()
                bot_mesg = update.message.reply_text('訊息已刪除。')
                update.message.delete()
                # 刪除訊息
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=bot_mesg.message_id)
                logging.info("successful delete message!")
            except:
                update.message.reply_text('無法刪除訊息。')
                logging.info("Error delete!")
        else:
            update.message.reply_text('你不是授權人員，Your action will be log。')
            logging.info(f"Not authorized member action."
                         f"Name:{update.message.from_user.name} ID:{update.message.from_user.id}")
    else:
        update.message.reply_text('請回覆一條訊息以刪除它。')

def ban(update: Update, context: CallbackContext) -> None:
    # 檢查是否有回覆的訊息
    if update.message.reply_to_message:
        # 檢查用戶是否在授權人員列表中
        if is_authorized(update.message.from_user.id):
            # 嘗試封鎖訊息
            try:
                update.message.chat.kick_member(update.message.reply_to_message.from_user.id)
                update.message.reply_text('用戶已封鎖。')
                logging.info("successful Ban user!")
            except:
                update.message.reply_text('封鎖失敗。')
                logging.info("Error Ban!")
        else:
            update.message.reply_text('你沒有權限封鎖用戶，Your action will be log。')
            logging.info(f"Not authorized member action."
                         f"Name:{update.message.from_user.name} ID:{update.message.from_user.id}")
    else:
        update.message.reply_text('請回覆一條訊息以刪除它。')

def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)

def anyone(update: Update, context: CallbackContext) -> None:
    update.message.reply_to_message.reply_text("沒有人你悲劇了！")
    update.message.delete()
    logging.info(f"not anyone! ")

def save_and_reply(update: Update, context: CallbackContext) -> None:
    if update.message and update.message.reply_to_message and update.message.reply_to_message.from_user.is_bot:
        message = update.message.text
        # 將 '@' 替換為 ' @ '
        message = message.replace('@', ' @ ')
        # 檢查訊息是否包含 "@"
        if "@" not in message:
            if not update.message.text.startswith('/'):
                # 使用正則表達式匹配中英文字符和標點符號
                words = re.findall(r"[（【《{]|\b\w+\b|[\u4e00-\u9FFF]|[，。！？、；：‘’“”）】》}]", message)
            # 隨機重排單詞
            random.shuffle(words)
            # 重新組合成句子
            new_message = ''.join(words)  # 不使用空格來連接單詞
             # 將新的句子寫入文件
            with open('replies.txt', 'a', encoding='utf-8') as f:
               f.write(new_message + '\n')
            # 讀取所有訊息
            with open('replies.txt', 'r', encoding='utf-8') as f:
                messages = f.readlines()
            # 隨機選擇一個訊息並發送
            response = random.choice(messages).strip()
            update.message.reply_text(response)
            logging.info("replies message send successful")
        else:
            update.message.reply_text("我不接受包含@的訊息喔！")

def load_messages() -> List[str]:
    # 檢查文件是否存在
    if os.path.isfile(replies):
        # 讀取文件
        with open(replies, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # 刪除換行符號並只保留文本部分
        messages = [line.strip() for line in lines]
        # 如果有訊息，則隨機選擇一個回覆
        if messages:
            return messages
    return []

def senrg(update: Update, context: CallbackContext) -> None:
    message = update.message.reply_to_message.text
    if "@" not in message:
        # 使用正則表達式匹配中英文字符和標點符號
        words = re.findall(r"[（【《{]|\b\w+\b|[\u4e00-\u9FFF]|[，。！？、；：‘’“”）】》}]", message)
        # 隨機重排單詞
        random.shuffle(words)
        # 重新組合成句子
        new_message = ' '.join(words)  # 不使用空格來連接單詞
        update.message.reply_text(new_message)
        logging.info("snerg successful")

def eras(update: Update, context: CallbackContext) -> None:
    if update.message and update.message.reply_to_message:
        if not update.message.reply_to_message.from_user.is_bot:
            # 獲取要刪除的訊息
            message_to_delete = update.message.reply_to_message.text
            # 讀取所有行
            with open(replies, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            # 找到要刪除的訊息並刪除
            lines = [line for line in lines if message_to_delete not in line]
            # 寫回文件
            with open(replies, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            update.message.reply_text('訊息已刪除。')
            logging.info(f"replies message successful delete")
        else:
            update.message.reply_text('請不要回覆bot的訊息。')
    else:
        update.message.reply_text('請提供要刪除的訊息。')

def load_authorized_users():
    authorized_users_list = []
    with open(authorized_users, 'r') as f:
            for line in f:
                try:
                    authorized_users_list.append(int(line.strip()))
                except ValueError:
                    print(f"無法將 {line.strip()} 轉換為整數，已跳過。")
    return authorized_users_list

def add_authorized_user(user_id):
    with open(authorized_users, 'a') as f:
        f.write(f"{user_id}\n")

def set_AU(update: Update, context: CallbackContext) -> None:
    if is_bur(update.message.from_user.id):
        if update.message.reply_to_message:
            new_user_id = update.message.reply_to_message.from_user.id
            add_authorized_user(new_user_id)
            update.message.reply_text(f"已添加用戶 {new_user_id} 到授權用戶列表。")
            logging.info(f"New user {new_user_id} add in {authorized_users}")
        else:
            update.message.reply_text('請回覆一條訊息以獲取用戶 ID。')
    else:
        update.message.reply_text('你沒有高級管理員權限，Your action will be log。')
        logging.info(f"Not authorized member action."
                    f"Name:{update.message.from_user.name} ID:{update.message.from_user.id}")

def load_Bur_users():
    Bur_users_list = []
    with open(Bur_users, 'r') as f:
            for line in f:
                try:
                    Bur_users_list.append(int(line.strip()))
                except ValueError:
                    print(f"無法將 {line.strip()} 轉換為整數，已跳過。")
    return Bur_users_list

def add_Bur_user(user_id):
    with open(Bur_users, 'a') as f:
        f.write(f"{user_id}\n")

def set_BU(update: Update, context: CallbackContext) -> None:
    if is_bur(update.message.from_user.id):
        if update.message.reply_to_message:
            new_user_id = update.message.reply_to_message.from_user.id
            add_Bur_user(new_user_id)
            update.message.reply_text(f"已添加用戶 {new_user_id} 到高級管理員用戶列表。")
            logging.info(f"New user {new_user_id} add in {Bur_users}")
        else:
            update.message.reply_text('請回覆一條訊息以獲取用戶 ID。')
    else:
        update.message.reply_text('你沒有高級管理員權限，Your action will be log。')
        logging.info(f"Not authorized member action."
                    f"Name:{update.message.from_user.name} ID:{update.message.from_user.id}")

def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("anyone", anyone))
    dp.add_handler(CommandHandler("delete", delete))
    dp.add_handler(CommandHandler("ban", ban))
    #dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, save_and_reply))
    #dp.add_handler(CommandHandler("eras", eras))
    dp.add_handler(CommandHandler("senrg", senrg))
    dp.add_handler(CommandHandler("userid", userid))
    dp.add_handler(CommandHandler("set_AU", set_AU))
    dp.add_handler(CommandHandler("set_BU", set_BU))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

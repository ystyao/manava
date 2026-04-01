import os
import time
import subprocess
import json
import board
import neopixel
from gpiozero import Button
from RPLCD.i2c import CharLCD
from dotenv import load_dotenv

# ==========================================
# 初始化与配置
# ==========================================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(PROJECT_DIR, "audio")

btn_scroll = Button(17) 
btn_select = Button(27) 

try:
    lcd = CharLCD('PCF8574', 0x27, port=1, charmap='A00', cols=16, rows=2)
except Exception as e:
    print("⚠️ LCD initialization failed.")
    exit(1)

NUM_PIXELS = 10
try:
    pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS, brightness=1.0, auto_write=False)
    pixels.fill((0, 0, 0))
    pixels.show()
except Exception as e:
    print(f"⚠️ NeoPixel init failed (run as sudo): {e}")
    pixels = None

# 🌟 全新定制：最高饱和度、极高对比度的纯粹色彩 (避开纯红)
CATEGORY_COLORS = {
    "intro": (0, 0, 255),        # 极致纯蓝 (纯粹的深海能量)
    "sleep": (150, 0, 255),      # 高亮霓虹紫 (蓝红混合，极具赛博感)
    "stress": (0, 255, 0),       # 极致纯绿 (最高亮度的通行信号)
    "activity": (120, 255, 0),   # 荧光黄绿 (充满动感与活力)
    "story": (0, 255, 255)       # 冰透青蓝 (最高亮度的发光水母色)
}

menu_items = [
    {"title": "1. Intro",    "play_line1": "Manava: Breath",    "play_line2": "Spirit of Ocean."},
    {"title": "2. Sleep",    "play_line1": "Deep Sea Echo...",  "play_line2": "Playing... "},
    {"title": "3. Stress",   "play_line1": "Calm the Tides..",  "play_line2": "Playing... "},
    {"title": "4. Activity", "play_line1": "Ocean Currents..",  "play_line2": "Playing... "},
    {"title": "5. Story",    "play_line1": "Whale's Song...",   "play_line2": "Playing... "}
]
current_idx = 0

# ==========================================
# 0 延迟音画同步核心 (权限降级黑科技)
# ==========================================
def play_audio_with_lights(category):
    filepath = os.path.join(AUDIO_DIR, f"{category}_advice.mp3")
    json_path = os.path.join(AUDIO_DIR, f"{category}_advice.json")
    base_color = CATEGORY_COLORS.get(category, (0, 255, 255))
    
    original_user = os.environ.get("SUDO_USER", "yaost")
    
    play_cmd = [
        "sudo", "-u", original_user, 
        "env", "XDG_RUNTIME_DIR=/run/user/1000", 
        "mpg123", "-q", filepath
    ]

    if not os.path.exists(filepath):
        print(f"⚠️ Audio missing: {filepath}")
        return

    if not pixels or not os.path.exists(json_path):
        subprocess.run(play_cmd)
        return

    try:
        with open(json_path, 'r') as f:
            brightness_array = json.load(f)
            
        process = subprocess.Popen(play_cmd)
        chunk_ms = 50 
        
        for brightness in brightness_array:
            if process.poll() is not None:
                break 
                
            r = int(base_color[0] * brightness)
            g = int(base_color[1] * brightness)
            b = int(base_color[2] * brightness)
            
            pixels.fill((r, g, b))
            pixels.show()
            
            time.sleep(chunk_ms / 1000.0)
            
        process.wait()
        
    except Exception as e:
        print(f"⚠️ Sync error: {e}")
        subprocess.run(play_cmd)
        
    finally:
        pixels.fill((0, 0, 0))
        pixels.show()

# ==========================================
# UI 轮询
# ==========================================
def draw_menu():
    lcd.clear()
    current_title = f">{menu_items[current_idx]['title']}"
    lcd.cursor_pos = (0, 0)
    lcd.write_string(current_title[:16]) 
    
    next_idx = (current_idx + 1) % len(menu_items)
    next_title = f" {menu_items[next_idx]['title']}"
    lcd.cursor_pos = (1, 0)
    lcd.write_string(next_title[:16])

print("Mānava Zero-Latency Interface running...")
draw_menu() 

try:
    while True:
        if btn_scroll.is_pressed:
            current_idx = (current_idx + 1) % len(menu_items)
            draw_menu()
            btn_scroll.wait_for_release()
            time.sleep(0.1)
            
        if btn_select.is_pressed:
            item = menu_items[current_idx]
            category = item["title"].lower().split(". ")[1]
            
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string(item["play_line1"])
            lcd.cursor_pos = (1, 0)
            lcd.write_string(item["play_line2"])
            
            play_audio_with_lights(category)
                
            draw_menu()
            btn_select.wait_for_release()
            time.sleep(0.1) 

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nExiting Mānava interface...")
    lcd.clear()
    if pixels:
        pixels.fill((0, 0, 0))
        pixels.show()
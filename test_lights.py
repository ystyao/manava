import time
import board
import neopixel

# 假设你的灯带上至少有 10 颗灯珠
NUM_PIXELS = 10 
pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS, brightness=0.5, auto_write=False)

print("🌊 正在测试深海光带... (按 Ctrl+C 停止)")

try:
    while True:
        # 点亮：深海蓝
        pixels.fill((0, 50, 150))
        pixels.show()
        print("💡 灯亮了！")
        time.sleep(1)
        
        # 熄灭
        pixels.fill((0, 0, 0))
        pixels.show()
        print("⬛ 熄灭！")
        time.sleep(1)

except KeyboardInterrupt:
    # 退出时确保灯带完全熄灭
    pixels.fill((0, 0, 0))
    pixels.show()
    print("\n✅ 测试结束。")
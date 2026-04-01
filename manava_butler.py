import os
import requests
import joblib
import subprocess
import json
import wave      # 纯原生音频库
import struct    # 纯原生数据解析库
import math      # 纯原生数学库
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv

# ==========================================
# 0. 初始化配置与环境变量
# ==========================================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(PROJECT_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

OURA_TOKEN = os.getenv("OURA_TOKEN")
DUKE_API_KEY = os.getenv("DUKE_API_KEY")

DUKE_BASE_URL = "https://litellm.oit.duke.edu/v1"
MODEL_NAME = "gpt-5-mini" 
client = OpenAI(api_key=DUKE_API_KEY, base_url=DUKE_BASE_URL)

# 尝试加载本地机器学习大脑
try:
    local_model = joblib.load(os.path.join(PROJECT_DIR, 'manava_health_model.pkl'))
    print("✅ Local classification model (manava_health_model.pkl) loaded successfully.")
except Exception as e:
    print(f"⚠️ Failed to load local model, will use default state: {e}")
    local_model = None

# ==========================================
# 1. 抓取真实生理数据
# ==========================================
def fetch_oura_data():
    headers = {"Authorization": f"Bearer {OURA_TOKEN}"}
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    
    data = {"readiness": 75, "sleep": 75, "steps": 4000, "calories": 200, "heart_rate": 60.0}
    
    if not OURA_TOKEN: return data

    try:
        readiness_res = requests.get(f"https://api.ouraring.com/v2/usercollection/daily_readiness?start_date={start_date}&end_date={end_date}", headers=headers).json()
        sleep_res = requests.get(f"https://api.ouraring.com/v2/usercollection/daily_sleep?start_date={start_date}&end_date={end_date}", headers=headers).json()
        activity_res = requests.get(f"https://api.ouraring.com/v2/usercollection/daily_activity?start_date={start_date}&end_date={end_date}", headers=headers).json()
        
        if readiness_res.get('data'): data["readiness"] = readiness_res['data'][-1]['score']
        if sleep_res.get('data'): data["sleep"] = sleep_res['data'][-1]['score']
        if activity_res.get('data'): 
            data["steps"] = activity_res['data'][-1]['steps']
            data["calories"] = activity_res['data'][-1]['active_calories']
        return data
    except Exception as e:
        print(f"⚠️ Oura data fetch failed, using default baseline data: {e}")
        return data

# ==========================================
# 2. 核心语音与硬核光效包络生成逻辑
# ==========================================
def generate_audio(category, today_data):
    filepath = os.path.join(AUDIO_DIR, f"{category}_advice.mp3")
    json_path = os.path.join(AUDIO_DIR, f"{category}_advice.json")
    text_to_speak = ""
    
    # ---------------------------------------------------------
    # 🌟 路由 A & B: 文本生成 (保持原样)
    # ---------------------------------------------------------
    if category in ["intro", "story"]:
        prompts = {
            "intro": "You are speaking to your old diving buddy. Warmly welcome her back to the ocean. In your very first sentence, smoothly combine your name, your identity as a humpback whale, and the meaning of your name (breath, spirit, and tidal rhythm). For example: 'Welcome back to the deep blue. It is I, Mānava, your humpback whale companion, your breath and spirit...' DO NOT introduce yourself a second time. Express quiet joy that she is here to rest. Keep it under 80 words, intimately warm, soft, and healing. No health data.",
            "story": "Tell a very short, poetic, and soothing story about a moment of pure tranquility you and your old diving friend once shared in the deep ocean. Focus on gentle bioluminescence or floating weightless in the soft blue light. [CRITICAL INSTRUCTION: Dive straight into the memory. DO NOT introduce yourself at the beginning, and DO NOT sign off or mention your name at the end. Just tell the story smoothly.] Make it a soft, warm, healing lullaby to calm her heart. Under 80 words. No health data."
        }
        try:
            response = client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "system", "content": prompts[category]}], temperature=0.8)
            text_to_speak = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ LLM request failed: {e}")
            text_to_speak = "Welcome back to the deep blue. It is I, Mānava, your humpback whale companion." if category == "intro" else "The ocean is quiet today, my friend. Let us drift and rest."
    else:
        features = [[today_data['heart_rate'], today_data['sleep'], 85.0, today_data['readiness']]]
        health_state = local_model.predict(features)[0] if local_model else 1
        if category == "sleep":
            if health_state == 0: text_to_speak = f"Yesterday, your sleep score was {today_data['sleep']}. This is quite low. You need to prioritize rest today and avoid strenuous tasks."
            elif health_state == 1: text_to_speak = f"Yesterday, your sleep score was {today_data['sleep']}. You are in a normal range. Keep maintaining a regular sleep schedule."
            else: text_to_speak = f"Yesterday, your sleep score was {today_data['sleep']}. Excellent recovery. You are fully rested and ready for a demanding day."
        elif category == "stress":
            if health_state == 0: text_to_speak = f"Your readiness score is {today_data['readiness']}. Your body is under stress right now. Focus on light activities and recovery today."
            elif health_state == 1: text_to_speak = f"Your readiness score is {today_data['readiness']}. You are in a balanced state. A normal daily routine is recommended."
            else: text_to_speak = f"Your readiness score is {today_data['readiness']}. Your stress levels are well managed and your body is fully recovered."
        elif category == "activity":
            if health_state == 0: text_to_speak = f"Yesterday you took {today_data['steps']} steps and burned {today_data['calories']} calories. Since your body needs recovery today, keep your activity very light."
            elif health_state == 1: text_to_speak = f"Yesterday you took {today_data['steps']} steps and burned {today_data['calories']} calories. Try to maintain this moderate level of movement today."
            else: text_to_speak = f"Yesterday you took {today_data['steps']} steps and burned {today_data['calories']} calories. Your body is handling the physical load very well. Keep up the great work."

    # ---------------------------------------------------------
    # 生成音频
    # ---------------------------------------------------------
    print(f"🎙️ [{category}] Synthesizing text...")
    if os.path.exists(filepath): os.remove(filepath)
    try:
        subprocess.run(["edge-tts", "--voice", "en-US-EmmaNeural", "--rate=-20%", "--text", text_to_speak, "--write-media", filepath], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Audio synthesis failed for {category}: {e}")
        return

    # ---------------------------------------------------------
    # 纯原生：手工解析音频包络并存为 JSON
    # ---------------------------------------------------------
    print(f"🎵 Parsing audio light envelope for {category} (Native Mode)...")
    wav_path = filepath.replace(".mp3", ".wav")
    try:
        # 1. 强行用 ffmpeg 将生成的 mp3 转为 Python 最容易读取的单声道 16-bit WAV
        subprocess.run(["ffmpeg", "-y", "-i", filepath, "-ac", "1", "-ar", "22050", wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        envelope = []
        with wave.open(wav_path, 'rb') as wf:
            framerate = wf.getframerate()
            sampwidth = wf.getsampwidth() # 16-bit = 2 bytes
            chunk_samples = int(framerate * 0.05) # 50ms 一帧
            chunk_bytes = chunk_samples * sampwidth
            
            # 读取所有原始二进制音频数据
            raw_data = wf.readframes(wf.getnframes())
            
            # 手工切片计算 RMS (音量均方根)
            for i in range(0, len(raw_data), chunk_bytes):
                chunk = raw_data[i:i+chunk_bytes]
                num_samples = len(chunk) // sampwidth
                if num_samples > 0:
                    # 将二进制数据解包为整数数组
                    samples = struct.unpack(f"<{num_samples}h", chunk)
                    # 计算这一小块的平均音量
                    rms = math.sqrt(sum(s*s for s in samples) / num_samples)
                    envelope.append(rms)
                    
        # 用完即删临时文件
        if os.path.exists(wav_path): os.remove(wav_path)
            
        max_rms = max(envelope) if envelope and max(envelope) > 0 else 1
        brightness_array = [min(1.0, max(0.1, (rms / max_rms) * 1.5)) for rms in envelope]
        
        with open(json_path, 'w') as f:
            json.dump(brightness_array, f)
            
        print(f"✅ Audio & Envelope ready: {category}\n")
    except Exception as e:
        print(f"❌ Native envelope parsing failed: {e}\n")
        if os.path.exists(wav_path): os.remove(wav_path)

# ==========================================
# 3. 主程序入口
# ==========================================
if __name__ == "__main__":
    print(f"\n🌊 Manava Hybrid Daily Generator started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    data = fetch_oura_data()
    print(f"📊 Today's fetched physiological data: {data}\n")
    
    for cat in ["intro", "sleep", "stress", "activity", "story"]:
        generate_audio(cat, data)
        
    print("🎉 All audio and light envelope files are ready! No pydub required!")
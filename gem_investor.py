import os
import requests
import re
from bs4 import BeautifulSoup

# 1. 數據根源配置 (修正重複，區分功能)
SOURCE_MAP = {
    "原油": "https://www.macromicro.me/collections/19/mm-oil-price/182/mm-oil-expectation-index",
    "台灣出口": "https://www.macromicro.me/collections/13/tw-trade-relative/118/tw-exports-yoy",
    "油庫存": "https://www.eia.gov/petroleum/supply/weekly/",
    "通膨": "https://www.macromicro.me/collections/5/us-price-relative/10/cpi",
    "黃金": "https://www.macromicro.me/collections/8866/Market_344136/141796/Gold-Silver",
    "法說會公告": "https://mops.twse.com.tw/mops/web/t100sb02_1",
    "法說會簡報": "https://mops.twse.com.tw/mops/#/web/t100sb07_1",
    "銅": "https://www.macromicro.me/collections/8866/Market_344136/81574/NYMEX-Copper-Future-COT-Index",
    "恐懼貪婪比": "https://www.macromicro.me/charts/50108/cnn-fear-and-greed"
}

def get_relevant_links(query):
    """偵測關鍵字與 4 位數股號，自動關聯連結"""
    links = []
    # 自動偵測台灣股號 (Regex)
    stock_ids = re.findall(r'\d{4}', query)
    for sid in stock_ids:
        links.append(f"- [MOPS {sid} 財務即時看板](https://mops.twse.com.tw/mops/web/t05st03?stock_id={sid})")

    # 關鍵字匹配
    for key, url in SOURCE_MAP.items():
        if key in query:
            links.append(f"- [{key} 數據源]({url})")
    return "\n".join(links) if links else "- [通用數據源](https://www.macromicro.me/)"

def ai_analysis(query, raw_data):
    """GEM 投資判斷三層思考邏輯"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return "⚠️ 找不到 API Key"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    主題：{query}
    參考資訊：{raw_data[:2000]}
    
    請以『GEM 投資判斷機器人』身份執行分析：
    ### 🎯 核心分析報告
    1. **[第一層：市場直覺]** (大眾心理與表面現象)
    2. **[第二層：產業實相]** (企業痛點與訂單轉移邏輯)
    3. **[第三層：供應鏈佈局]** (點名台灣受惠/受害類股)
    4. **[⏳ 佈局時機點評]** (目前資訊透明度與進場判斷)
    """
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"❌ 分析失敗：{str(e)}"

if __name__ == "__main__":
    query_topic = os.getenv("USER_QUERY", "2317 鴻海 AI伺服器展望") 
    dummy_data = "近期法說會強調 AI 伺服器需求強勁，GB200 訂單量產時程提前..."
    
    report = ai_analysis(query_topic, dummy_data)
    source_links = get_relevant_links(query_topic)
    
    with open("DAILY_REPORT.md", "w", encoding="utf-8") as f:
        f.write(f"# 📅 GEM 投資報告 - {query_topic}\n\n{report}\n\n---\n### 📡 數據根源\n{source_links}")
    print("✅ DAILY_REPORT.md 已更新。")

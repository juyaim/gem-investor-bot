import os
import requests
import re
from bs4 import BeautifulSoup

# 1. 數據根源配置 (修正重複鍵值，改用更精確的定義)
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
    """偵測關鍵字與股號，動態生成連結"""
    links = []
    
    # 自動偵測 4 位數台灣股號 (如 2317, 6669)
    stock_ids = re.findall(r'\d{4}', query)
    for sid in stock_ids:
        links.append(f"- [MOPS {sid} 財務即時看板](https://mops.twse.com.tw/mops/web/t05st03?stock_id={sid})")

    # 關鍵字匹配數據源
    for key, url in SOURCE_MAP.items():
        if key in query:
            links.append(f"- [{key} 數據源]({url})")
            
    return "\n".join(links) if links else "- [通用數據源](https://www.macromicro.me/)"

def ai_analysis(query, raw_data):
    """GEM 投資判斷核心邏輯"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ 錯誤：環境變數中找不到 GEMINI_API_KEY"

    # 使用 1.5 Flash 模型，反應速度更快且免費額度充足
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    主題：{query}
    參考數據：{raw_data[:2000]}
    
    請以『GEM 投資判斷機器人』身份執行分析：
    ### 🎯 核心分析報告
    1. **[第一層：市場直覺]** (描述表面現象與大眾心理)
    2. **[第二層：產業實相]** (分析企業痛點、成本轉嫁與補償機制)
    3. **[第三層：供應鏈佈局]** (精確點名台灣受惠/受害類股)
    4. **[⏳ 佈局時機點評]** (分析目前是過熱還是潛在機會)
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status() # 若 API 回傳錯誤碼則觸發 except
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"❌ AI 分析執行失敗，原因：{str(e)}"

if __name__ == "__main__":
    # 預設執行主題
    query_topic = os.getenv("USER_QUERY", "原油通膨與 2317 鴻海") 
    
    print(f"🚀 正在優化分析：{query_topic}...")
    
    # 模擬或接入真實數據 (此處可替換為爬蟲獲取的內容)
    sample_data = "近期原油價格波動劇烈，且電子權值股法說會釋出正向展望..."
    
    # 執行分析與連結獲取
    report = ai_analysis(query_topic, sample_data)
    source_links = get_relevant_links(query_topic)
    
    # 儲存報告
    report_content = f"# 📅 GEM 投資判斷報告\n\n**分析主題：** {query_topic}\n\n{report}\n\n"
    report_content += "---\n### 📡 數據根源與監控網址\n"
    report_content += source_links
    
    with open("DAILY_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("✅ 程式執行完畢，報告已更新至 DAILY_REPORT.md")

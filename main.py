
import logging
import requests
import pandas as pd
import ta
import asyncio
from telegram import Bot

# إعدادات البوت
TOKEN = "8197469444:AAEU671Af2O78MAq1Ickl7brf2M7iYn0mys"
USER_ID = 123456789  # سيتم التعديل لاحقاً بـ ID الحقيقي
bot = Bot(token=TOKEN)

# أزواج العملات الدقيقة
PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]

# احضار البيانات من Alpha Vantage (تحتاج مفتاح API حقيقي لاحقاً)
def fetch_data(pair):
    url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol={pair[:3]}&to_symbol={pair[3:]}&interval=5min&apikey=demo"
    response = requests.get(url)
    data = response.json()
    try:
        candles = pd.DataFrame.from_dict(data['Time Series FX (5min)'], orient='index', dtype=float)
        candles = candles.rename(columns={
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close"
        })
        candles = candles.sort_index()
        return candles
    except:
        return None

# تحليل فني بسيط باستخدام RSI و MACD
def analyze(df):
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()

    last = df.iloc[-1]
    if last['rsi'] < 30 and last['macd'] > last['macd_signal']:
        return "إشارة شراء قوية"
    elif last['rsi'] > 70 and last['macd'] < last['macd_signal']:
        return "إشارة بيع قوية"
    return None

# إرسال الإشارات كل 5 دقائق
async def run_bot():
    while True:
        for pair in PAIRS:
            df = fetch_data(pair)
            if df is not None:
                signal = analyze(df)
                if signal:
                    msg = f"{pair}: {signal} (فاصل 5 دقائق)"
                    await bot.send_message(chat_id=USER_ID, text=msg)
        await asyncio.sleep(300)  # كل 5 دقائق

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_bot())

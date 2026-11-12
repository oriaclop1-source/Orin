#!/usr/bin/env python3
"""Fetch stock statistics from Yahoo Finance and compute model price targets.

Writes stocks/data.json, which the stocks site loads. Runs in GitHub Actions
(.github/workflows/stocks-data.yml) several times a trading day.

Usage:  pip install yfinance && python3 stocks/fetch_data.py
"""
import json
import math
import os
import sys
import time
from datetime import datetime, timezone

import yfinance as yf

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# symbol -> Hebrew display name
STOCKS = {
    "AAPL": "אפל", "MSFT": "מיקרוסופט", "NVDA": "אנבידיה", "AMZN": "אמזון", "GOOGL": "אלפבית (גוגל)",
    "META": "מטא", "TSLA": "טסלה", "AVGO": "ברודקום", "BRK-B": "ברקשייר האת'וויי", "JPM": "ג'יי.פי מורגן",
    "V": "ויזה", "MA": "מאסטרקארד", "LLY": "אלי לילי", "UNH": "יונייטדהלת'", "XOM": "אקסון מוביל",
    "JNJ": "ג'ונסון אנד ג'ונסון", "PG": "פרוקטר אנד גמבל", "COST": "קוסטקו", "HD": "הום דיפו", "KO": "קוקה קולה",
    "PEP": "פפסיקו", "WMT": "וולמארט", "NFLX": "נטפליקס", "AMD": "AMD", "ORCL": "אורקל", "CRM": "סיילספורס",
    "ADBE": "אדובי", "PLTR": "פלנטיר", "INTC": "אינטל", "QCOM": "קוואלקום", "MU": "מיקרון", "ASML": "ASML",
    "TSM": "TSMC", "BAC": "בנק אוף אמריקה", "GS": "גולדמן זאקס", "DIS": "דיסני", "NKE": "נייקי",
    "MCD": "מקדונלד'ס", "SBUX": "סטארבקס", "PFE": "פייזר", "MRK": "מרק", "ABBV": "אבווי", "CVX": "שברון",
    "BA": "בואינג", "CAT": "קטרפילר", "UBER": "אובר", "SHOP": "שופיפיי", "PYPL": "פייפאל", "COIN": "קוינבייס",
    "PANW": "פאלו אלטו", "CRWD": "קראודסטרייק", "ANET": "אריסטה", "NOW": "סרביסנאו", "ISRG": "אינטואיטיב סרג'יקל",
    "TEVA": "טבע", "ESLT": "אלביט מערכות", "CHKP": "צ'ק פוינט", "NICE": "נייס", "MNDY": "מאנדיי",
    "WIX": "וויקס", "GLBE": "גלובל-אי", "CYBR": "סייברארק",
}
# ETFs get a simple scenario model instead of an earnings-based one.
ETFS = {
    "SPY": ("S&P 500", "stock"), "VOO": ("S&P 500", "stock"), "QQQ": ("נאסד״ק 100", "stock"),
    "VTI": ("שוק ארה״ב כולו", "stock"), "VXUS": ("מניות עולם", "stock"), "VT": ("כל העולם", "stock"),
    "SCHD": ("מניות דיבידנד", "stock"), "BND": ("אג״ח ארה״ב", "bond"), "SGOV": ("אג״ח קצר מאוד", "cash"),
}
SECTORS = {
    "Technology": "טכנולוגיה", "Communication Services": "תקשורת ומדיה", "Consumer Cyclical": "צריכה מחזורית",
    "Consumer Defensive": "צריכה בסיסית", "Healthcare": "בריאות", "Financial Services": "פיננסים",
    "Energy": "אנרגיה", "Industrials": "תעשייה", "Basic Materials": "חומרי גלם", "Real Estate": "נדל״ן",
    "Utilities": "תשתיות",
}
EXCH = {"NMS": "NASDAQ", "NGM": "NASDAQ", "NCM": "NASDAQ", "NAS": "NASDAQ", "NYQ": "NYSE", "NYS": "NYSE",
        "PCX": "AMEX", "ASE": "AMEX", "BTS": "AMEX"}


def num(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def avg(*vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def info_for(sym, tries=3):
    for i in range(tries):
        try:
            info = yf.Ticker(sym).info
            if info and num(info.get("currentPrice") or info.get("regularMarketPrice")):
                return info
        except Exception as e:  # network hiccups / rate limits
            print(f"  {sym}: {e}", file=sys.stderr)
        time.sleep(2 + 3 * i)
    return None


def tv_symbol(sym, info):
    ex = EXCH.get(info.get("exchange"), "NYSE")
    return f"{ex}:{sym.replace('-', '.')}"


def stock_model(price, i):
    """12-month model target: half valuation (forward EPS x fair P/E), half analyst consensus."""
    fe = num(i.get("forwardEps"))
    g_raw = num(i.get("earningsGrowth"))
    if g_raw is None or abs(g_raw) > 1.5:
        g_raw = num(i.get("revenueGrowth"))
    g = clamp(g_raw if g_raw is not None else 0.05, -0.10, 0.40)
    roe, margin, de = num(i.get("returnOnEquity")), num(i.get("profitMargins")), num(i.get("debtToEquity"))
    fair_pe = 12 + 60 * g
    if roe is not None and roe > 0.20:
        fair_pe += 2
    if margin is not None and margin > 0.20:
        fair_pe += 2
    if de is not None and de > 150:
        fair_pe -= 2
    fair_pe = clamp(fair_pe, 8, 40)

    val = val_bear = val_bull = None
    if fe and fe > 0:
        val = fe * (1 + g / 2) * fair_pe
        val_bear = fe * fair_pe * 0.75
        val_bull = fe * (1 + g) * fair_pe * 1.2

    n_an = num(i.get("numberOfAnalystOpinions")) or 0
    a_mean, a_low, a_high = (num(i.get(k)) for k in ("targetMeanPrice", "targetLowPrice", "targetHighPrice"))
    if n_an < 3:
        a_mean = a_low = a_high = None

    target = avg(val, a_mean)
    if target is None:
        target = price * 1.07
    target = clamp(target, price * 0.5, price * 1.8)

    beta = clamp(num(i.get("beta")) or 1.0, 0.6, 2.5)
    bear = avg(price * (1 - 0.30 * beta), a_low, val_bear)
    bull = avg(price * (1 + 0.35 * beta), a_high, val_bull)
    bear = min(bear, target * 0.92, price * 0.95)
    bull = max(bull, target * 1.08, price * 1.05)

    return {
        "target": round(target, 2), "bear": round(bear, 2), "bull": round(bull, 2),
        "valTarget": round(val, 2) if val else None, "fairPE": round(fair_pe, 1), "g": round(g, 3),
    }


def score(price, m, i):
    """0-100 model rating: upside, quality, analyst view, momentum."""
    up = m["target"] / price - 1
    s = 50 + clamp(up * 100, -30, 30)  # upside
    roe, margin = num(i.get("returnOnEquity")), num(i.get("profitMargins"))
    if roe is not None:
        s += clamp(roe * 20, -5, 6)
    if margin is not None:
        s += clamp(margin * 20, -5, 6)
    rec = num(i.get("recommendationMean"))
    if rec is not None:
        s += clamp((3 - rec) * 5, -8, 8)
    hi, lo = num(i.get("fiftyTwoWeekHigh")), num(i.get("fiftyTwoWeekLow"))
    if hi and lo and hi > lo:
        pos = (price - lo) / (hi - lo)
        s += (pos - 0.5) * 6
    return int(round(clamp(s, 0, 100)))


def main():
    out = {"updated": datetime.now(timezone.utc).isoformat(timespec="minutes"), "stocks": [], "etfs": []}
    fx = info_for("ILS=X")
    out["usdils"] = num((fx or {}).get("regularMarketPrice"))

    for sym, he in STOCKS.items():
        i = info_for(sym)
        if not i:
            print(f"skip {sym}", file=sys.stderr)
            continue
        price = num(i.get("currentPrice") or i.get("regularMarketPrice"))
        m = stock_model(price, i)
        div_rate = num(i.get("dividendRate"))
        out["stocks"].append({
            "s": sym, "tv": tv_symbol(sym, i), "he": he, "name": i.get("shortName") or sym,
            "sector": SECTORS.get(i.get("sector"), i.get("sector") or "אחר"),
            "price": round(price, 2), "chg": num(i.get("regularMarketChangePercent")),
            "mcap": num(i.get("marketCap")), "pe": num(i.get("trailingPE")), "fpe": num(i.get("forwardPE")),
            "eps": num(i.get("trailingEps")), "feps": num(i.get("forwardEps")),
            "revG": num(i.get("revenueGrowth")), "epsG": num(i.get("earningsGrowth")),
            "margin": num(i.get("profitMargins")), "roe": num(i.get("returnOnEquity")),
            "de": num(i.get("debtToEquity")), "beta": num(i.get("beta")),
            "div": round(div_rate / price, 4) if div_rate and price else 0,
            "hi52": num(i.get("fiftyTwoWeekHigh")), "lo52": num(i.get("fiftyTwoWeekLow")),
            "ch52": num(i.get("52WeekChange")),
            "aMean": num(i.get("targetMeanPrice")), "aLow": num(i.get("targetLowPrice")),
            "aHigh": num(i.get("targetHighPrice")), "aN": int(num(i.get("numberOfAnalystOpinions")) or 0),
            "rec": num(i.get("recommendationMean")),
            **m, "score": score(price, m, i),
        })
        time.sleep(0.4)

    for sym, (he, kind) in ETFS.items():
        i = info_for(sym)
        if not i:
            continue
        price = num(i.get("regularMarketPrice") or i.get("navPrice"))
        bear, base, bull = {"stock": (0.75, 1.07, 1.20), "bond": (0.92, 1.04, 1.08), "cash": (1.0, 1.035, 1.045)}[kind]
        out["etfs"].append({
            "s": sym, "tv": tv_symbol(sym, i), "he": he, "name": i.get("shortName") or sym, "kind": kind,
            "sector": "קרן סל", "price": round(price, 2), "chg": num(i.get("regularMarketChangePercent")),
            "target": round(price * base, 2), "bear": round(price * bear, 2), "bull": round(price * bull, 2),
        })

    if len(out["stocks"]) < 10:
        sys.exit(f"only {len(out['stocks'])} stocks fetched; keeping the previous data.json")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {len(out['stocks'])} stocks, {len(out['etfs'])} ETFs")


if __name__ == "__main__":
    main()

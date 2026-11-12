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
    "WIX": "וויקס", "GLBE": "גלובל-אי",
    # Israeli companies traded in the US
    "TSEM": "טאואר", "NVMI": "נובה", "CAMT": "קמטק", "FVRR": "פייבר", "LMND": "למונייד", "PAYO": "פיוניר",
    "ZIM": "צים", "INMD": "אינמוד", "SEDG": "סולאראדג'", "RDWR": "רדוור", "KRNT": "קורנית",
    "CEVA": "סיווה", "FROG": "ג'יפרוג", "CLBT": "סלברייט", "ORA": "אורמת", "ICL": "כיל",
    # chips & hardware
    "ADI": "אנלוג דיבייסס", "AMAT": "אפלייד מטריאלס", "LRCX": "לאם ריסרץ'", "KLAC": "KLA", "MRVL": "מארוול",
    "ARM": "ARM", "SMCI": "סופר מיקרו", "DELL": "דל", "HPQ": "HP", "IBM": "IBM", "CSCO": "סיסקו", "TXN": "טקסס אינסטרומנטס",
    "ON": "און סמיקונדקטור", "VRT": "ורטיב", "IONQ": "איון-קיו",
    # software & internet
    "SNOW": "סנופלייק", "DDOG": "דאטהדוג", "NET": "קלאודפלייר", "ZS": "זיסקיילר", "MDB": "מונגו-די-בי",
    "TEAM": "אטלסיאן", "WDAY": "וורקדיי", "INTU": "אינטואיט", "FTNT": "פורטינט", "OKTA": "אוקטה", "ACN": "אקסנצ'ר",
    "APP": "אפלוביין", "SPOT": "ספוטיפיי", "RBLX": "רובלוקס", "SNAP": "סנאפ", "PINS": "פינטרסט", "ABNB": "איירביאנבי",
    "BKNG": "בוקינג", "DASH": "דורדאש", "LYFT": "ליפט", "MELI": "מרקדו ליברה", "SE": "סי לימיטד",
    "BABA": "עליבאבא", "PDD": "PDD (טמו)", "JD": "JD.com", "MSTR": "מייקרוסטרטג'י",
    # fintech & finance
    "NU": "נובנק", "SOFI": "סופיי", "HOOD": "רובינהוד", "AFRM": "אפירם", "XYZ": "בלוק (סקוור)", "C": "סיטיגרופ",
    "WFC": "וולס פרגו", "MS": "מורגן סטנלי", "SCHW": "צ'רלס שוואב", "AXP": "אמריקן אקספרס", "BLK": "בלאקרוק",
    "SPGI": "S&P גלובל", "MCO": "מודי'ס", "PGR": "פרוגרסיב", "CB": "צ'אב",
    # cars & transport
    "F": "פורד", "GM": "ג'נרל מוטורס", "RIVN": "ריביאן", "LCID": "לוסיד", "NIO": "ניו", "TM": "טויוטה",
    "UPS": "UPS", "FDX": "פדקס", "UNP": "יוניון פסיפיק", "RKLB": "רוקט לאב",
    # health
    "NVO": "נובו נורדיסק", "AZN": "אסטרהזנקה", "AMGN": "אמג'ן", "GILD": "גיליאד", "REGN": "רג'נרון",
    "VRTX": "ורטקס", "BMY": "בריסטול מאיירס", "ABT": "אבוט", "TMO": "תרמו פישר", "DHR": "דנהר", "MDT": "מדטרוניק",
    "SYK": "סטרייקר", "BSX": "בוסטון סיינטיפיק", "ZTS": "זואטיס", "MRNA": "מודרנה", "CVS": "CVS", "CI": "סיגנה",
    "ELV": "אלבנס",
    # industry & defense
    "GE": "ג'נרל אלקטריק", "HON": "האניוול", "DE": "ג'ון דיר", "MMM": "3M", "LMT": "לוקהיד מרטין", "RTX": "RTX (רייתאון)",
    "NOC": "נורת'רופ גראמן", "GD": "ג'נרל דיינמיקס",
    # consumer
    "LOW": "לואו'ס", "TGT": "טארגט", "TJX": "TJX", "LULU": "לולולמון", "CMG": "צ'יפוטלה", "YUM": "יאם! (KFC, פיצה האט)",
    "MO": "אלטריה", "PM": "פיליפ מוריס", "CL": "קולגייט", "MDLZ": "מונדלז", "KHC": "קראפט היינץ", "EL": "אסתי לאודר",
    "SONY": "סוני", "GME": "גיימסטופ",
    # telecom, energy, utilities, real estate, materials
    "T": "AT&T", "VZ": "וריזון", "TMUS": "טי-מובייל", "CMCSA": "קומקאסט", "COP": "קונוקו פיליפס", "OXY": "אוקסידנטל",
    "SLB": "שלומברז'ה", "NEE": "נקסטרה אנרג'י", "DUK": "דיוק אנרג'י", "SO": "סאות'רן", "ENPH": "אנפייז", "FSLR": "פירסט סולאר",
    "AMT": "אמריקן טאואר", "PLD": "פרולוג'יס", "O": "ריאלטי אינקם", "LIN": "לינדה", "FCX": "פריפורט", "NEM": "ניומונט",
    "SAP": "SAP",
    # more mid-caps, biotech, AI, power, crypto miners, travel
    "CORT": "קורספט", "HIMS": "הימס אנד הרס", "TEM": "טמפוס AI", "RXRX": "רקורז'ן", "CRSP": "קריספר",
    "NTLA": "אינטליה", "DXCM": "דקסקום", "PODD": "אינסולט", "ALNY": "אלנילם",
    "BIIB": "ביוג'ן", "INCY": "אינסייט", "NBIX": "נורוקרין", "UTHR": "יונייטד ת'רפיוטיקס", "EXEL": "אקסליקסיס",
    "HALO": "הלוזיים", "ARGX": "ארג'נקס", "BNTX": "ביונטק", "VKTX": "וייקינג ת'רפיוטיקס",
    "SMMT": "סאמיט ת'רפיוטיקס", "OSCR": "אוסקר הלת'", "DOCS": "דוקסימיטי", "IDXX": "אידקס", "GEHC": "GE הלת'קר",
    "HCA": "HCA הלת'קר", "SNY": "סאנופי", "GSK": "GSK", "NVS": "נוברטיס", "MPWR": "מונוליתיק פאואר", "NXPI": "NXP",
    "MCHP": "מיקרוצ'יפ", "SWKS": "סקייוורקס", "QRVO": "קורבו", "LSCC": "לאטיס", "ALAB": "אסטרה לאבס",
    "CRDO": "קרדו", "COHR": "קוהרנט", "LITE": "לומנטום", "CIEN": "סיינה", "STX": "סיגייט", "WDC": "ווסטרן דיגיטל",
    "PSTG": "פיור סטורג'", "NTAP": "נטאפ", "HPE": "HPE", "ONTO": "אונטו", "ENTG": "אנטגריס", "TER": "טרדיין",
    "AMKR": "אמקור", "GFS": "גלובלפאונדריז", "SOUN": "סאונדהאונד", "BBAI": "ביגבר AI", "RGTI": "ריגטי",
    "QBTS": "D-Wave", "NBIS": "נביוס", "CRWV": "קורוויב", "S": "סנטינל וואן", "PATH": "יו-אייפאת'",
    "GTLB": "גיטלאב", "HUBS": "האבספוט", "TTD": "טרייד דסק", "ZM": "זום", "DOCU": "דוקוסיין", "TWLO": "טוויליו",
    "ESTC": "אלסטיק", "BILL": "ביל", "PCOR": "פרוקור", "IOT": "סמסרה", "U": "יוניטי",
    "DUOL": "דואולינגו", "ADSK": "אוטודסק", "CDNS": "קיידנס", "SNPS": "סינופסיס", "ETSY": "אטסי", "EBAY": "איביי",
    "CPNG": "קופנג", "GRAB": "גראב", "TOST": "טוסט", "CVNA": "קרבנה", "RDDT": "רדיט", "ROKU": "רוקו",
    "EA": "אלקטרוניק ארטס", "TTWO": "טייק-טו", "WBD": "וורנר ברוס דיסקברי", "UPST": "אפסטארט",
    "DKNG": "דראפטקינגס", "CHWY": "צ'ואי", "OKLO": "אוקלו", "SMR": "נוסקייל", "VST": "ויסטרה", "CEG": "קונסטליישן",
    "NRG": "NRG", "TLN": "טאלן", "GEV": "GE ורנובה", "CCJ": "קאמקו", "UEC": "אורניום אנרג'י", "EOG": "EOG",
    "PSX": "פיליפס 66", "MPC": "מרתון פטרוליום", "VLO": "ואלרו", "KMI": "קינדר מורגן", "WMB": "וויליאמס",
    "OKE": "ONEOK", "HAL": "הליברטון", "DVN": "דבון", "FANG": "דיימונדבק", "LNG": "שנייר", "BP": "BP",
    "SHEL": "של", "TTE": "טוטאל", "ASTS": "AST ספייסמובייל", "LUNR": "אינטואיטיב מאשינס", "JOBY": "ג'ובי",
    "ACHR": "ארצ'ר", "AXON": "אקסון", "LHX": "L3 האריס", "HII": "האנטינגטון אינגולס", "KTOS": "קרטוס",
    "AVAV": "איירוויירונמנט", "TDG": "טרנסדיים", "HWM": "האומט", "MARA": "מרה", "RIOT": "ריוט", "IREN": "איירן",
    "CLSK": "קלינספארק", "CELH": "סלסיוס", "ELF": "e.l.f.", "DECK": "דקרס (הוקה)", "ONON": "און (נעליים)",
    "CROX": "קרוקס", "WING": "וינגסטופ", "CAVA": "קאווה", "DPZ": "דומינוס", "RL": "ראלף לורן", "TPR": "טפסטרי",
    "MGM": "MGM", "LVS": "לאס וגאס סנדס", "RCL": "רויאל קריביאן", "CCL": "קרניבל", "NCLH": "נורוויג'יאן",
    "DAL": "דלתא", "UAL": "יונייטד", "AAL": "אמריקן איירליינס", "LUV": "סאות'ווסט", "MAR": "מריוט",
    "HLT": "הילטון", "EXPE": "אקספדיה", "UL": "יוניליוור", "DEO": "דיאג'יו", "BUD": "אנהייזר-בוש",
    "COF": "קפיטל וואן", "KKR": "KKR", "BX": "בלקסטון", "APO": "אפולו", "ARES": "אריס",
    "IBKR": "אינטראקטיב ברוקרס", "CME": "CME", "ICE": "ICE", "NDAQ": "נאסד״ק (החברה)", "MSCI": "MSCI",
    "FISV": "פייסרב", "FIS": "FIS", "GPN": "גלובל פיימנטס", "ETN": "איטון", "PH": "פארקר האניפין", "EMR": "אמרסון",
    "ITW": "אילינוי טול וורקס", "WM": "ווייסט מנג'מנט", "RSG": "ריפבליק סרביסס", "CTAS": "סינטס",
    "URI": "יונייטד רנטלס", "PWR": "קוואנטה", "FIX": "קומפורט סיסטמס", "EME": "אמקור גרופ", "TT": "טריין",
    "CARR": "קרייר", "OTIS": "אוטיס", "NUE": "נוקור", "STLD": "סטיל דיינמיקס", "ALB": "אלבמרל", "MP": "MP מטריאלס",
    "SCCO": "סאות'רן קופר", "AA": "אלקואה", "RIO": "ריו טינטו", "BHP": "BHP", "EQIX": "אקוויניקס",
    "DLR": "דיג'יטל ריאלטי", "SPG": "סיימון פרופרטי", "PSA": "פבליק סטורג'", "VICI": "VICI",
}
ISRAELI = {"TEVA", "ESLT", "CHKP", "NICE", "MNDY", "WIX", "GLBE", "TSEM", "NVMI", "CAMT", "FVRR", "LMND",
           "PAYO", "ZIM", "INMD", "SEDG", "RDWR", "KRNT", "CEVA", "FROG", "CLBT", "ORA", "ICL"}
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
    """12-month model target: 40% valuation (forward EPS x fair P/E), 60% analyst consensus."""
    fe, te = num(i.get("forwardEps")), num(i.get("trailingEps"))
    # expected growth: next-year EPS growth implied by the forward estimate, blended with revenue growth
    g_eps = fe / te - 1 if fe and te and fe > 0 and te > 0 else None
    g = avg(g_eps, num(i.get("revenueGrowth")))
    g = clamp(g if g is not None else 0.05, -0.10, 0.30)
    roe, margin, de = num(i.get("returnOnEquity")), num(i.get("profitMargins")), num(i.get("debtToEquity"))
    fair_pe = 10 + 50 * g
    if roe is not None and roe > 0.20:
        fair_pe += 1.5
    if margin is not None and margin > 0.20:
        fair_pe += 1.5
    if de is not None and de > 150:
        fair_pe -= 2
    fpe = num(i.get("forwardPE"))
    if fpe and fpe > 0:  # lean half on what the market pays today
        fair_pe = (fair_pe + clamp(fpe, 8, 45)) / 2
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

    if val and a_mean:
        # keep our valuation within 30% of the street so one noisy input can't dominate
        target = 0.4 * clamp(val, a_mean * 0.7, a_mean * 1.3) + 0.6 * a_mean
    else:
        target = val or a_mean or price * 1.07
    target = clamp(target, price * 0.6, price * 1.6)

    beta = clamp(num(i.get("beta")) or 1.0, 0.6, 2.5)
    bear = avg(price * (1 - 0.30 * beta), a_low, val_bear)
    bull = avg(price * (1 + 0.35 * beta), a_high, val_bull)
    bear = clamp(bear, price * 0.35, min(target * 0.92, price * 0.95))
    bull = clamp(bull, max(target * 1.08, price * 1.05), price * 2.2)

    return {
        "target": round(target, 2), "bear": round(bear, 2), "bull": round(bull, 2),
        "valTarget": round(val, 2) if val else None, "fairPE": round(fair_pe, 1), "g": round(g, 3),
    }


def score(price, m, i):
    """0-100 model rating: upside, quality, analyst view, momentum."""
    up = m["target"] / price - 1
    s = 50 + clamp(up * 60, -25, 25)  # upside
    roe, margin = num(i.get("returnOnEquity")), num(i.get("profitMargins"))
    if roe is not None:
        s += clamp(roe * 15, -5, 5)
    if margin is not None:
        s += clamp(margin * 15, -5, 5)
    rec = num(i.get("recommendationMean"))
    if rec is not None:
        s += clamp((2.5 - rec) * 6, -8, 8)
    hi, lo = num(i.get("fiftyTwoWeekHigh")), num(i.get("fiftyTwoWeekLow"))
    if hi and lo and hi > lo:
        s += ((price - lo) / (hi - lo) - 0.5) * 6
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
            "s": sym, "tv": tv_symbol(sym, i), "he": he, "name": i.get("shortName") or sym, "il": sym in ISRAELI,
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
        time.sleep(0.3)

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

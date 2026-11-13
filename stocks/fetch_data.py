#!/usr/bin/env python3
"""Fetch stock statistics from Yahoo Finance and compute fundamentals-only price targets.

Writes stocks/data.json, which the stocks site loads. Runs in GitHub Actions
(.github/workflows/stocks-data.yml) several times a trading day.

Usage:  pip install yfinance && python3 stocks/fetch_data.py
"""
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
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


HIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hist.json")
HIST_MAX_AGE_DAYS = 30
RISK_FREE, EQUITY_PREMIUM, TERMINAL_G = 0.045, 0.05, 0.025
GRAHAM_RATE_ADJ = 4.4 / 5.0  # Graham's bond-yield adjustment: 4.4% base / ~5% high-grade yield today


def history(sym, cache):
    """Annual revenue and net income (newest first) from the income statement, cached for a month."""
    today = datetime.now(timezone.utc).date()
    h = cache.get(sym)
    if h and (today - datetime.fromisoformat(h["t"]).date()).days < HIST_MAX_AGE_DAYS:
        return h
    try:
        df = yf.Ticker(sym).income_stmt
        rev = [num(v) for v in df.loc["Total Revenue"].tolist()]
        ni = [num(v) for v in df.loc["Net Income"].tolist()]
        pairs = [(r, n) for r, n in zip(rev, ni) if r and n is not None][:4]
        if pairs:
            h = {"t": today.isoformat(), "rev": [p[0] for p in pairs], "ni": [p[1] for p in pairs]}
            cache[sym] = h
    except Exception as e:
        print(f"  {sym} history: {e}", file=sys.stderr)
    return h


def stock_model(price, i, h):
    """Fair value from reported fundamentals only: no analyst targets, estimates or ratings.

    Up to three methods, averaged: Graham's earnings formula on cycle-normalised EPS,
    a 10-year discounted cash flow, and (banks/insurers) book value x ROE / cost of equity.
    """
    same_ccy = (i.get("financialCurrency") or "USD") == (i.get("currency") or "USD")
    shares = num(i.get("marketCap")) / price if num(i.get("marketCap")) else None
    financial = i.get("sector") == "Financial Services"
    margin, roe = num(i.get("profitMargins")), num(i.get("returnOnEquity"))
    beta = clamp(num(i.get("beta")) or 1.0, 0.7, 1.8)
    r = RISK_FREE + EQUITY_PREMIUM * beta

    # growth: the lower of multi-year revenue CAGR and the latest reported year-over-year growth
    cagr = None
    if h and len(h["rev"]) >= 3 and h["rev"][-1] > 0 and h["rev"][0] > 0:
        cagr = (h["rev"][0] / h["rev"][-1]) ** (1 / (len(h["rev"]) - 1)) - 1
    latest = num(i.get("revenueGrowth"))
    g = min(cagr, latest) if cagr is not None and latest is not None else avg(cagr, latest)  # the cautious one
    g = clamp(g if g is not None else 0.03, -0.05, 0.20)

    # cycle-normalised EPS: scale trailing EPS by (multi-year average margin / current margin)
    eps = num(i.get("trailingEps"))
    norm, cyc = 1.0, 0.3  # unknown history: assume some cyclicality
    if h and margin and margin > 0:
        margins = [n / rv for n, rv in zip(h["ni"], h["rev"])]
        norm = clamp(sum(margins) / len(margins) / margin, 0.5, 1.2)
        # cyclicality: the deepest fall in margin from an earlier peak (1 = fell into a loss).
        # Margins that only rose over time are improvement, not a cycle.
        peak, cyc = None, 0.0
        for mg in reversed(margins):  # history is newest first
            peak = mg if peak is None else max(peak, mg)
            if peak > 0:
                cyc = max(cyc, clamp((peak - mg) / peak, 0, 1))
        if margin < peak:
            cyc = max(cyc, clamp((peak - margin) / peak, 0, 1))
    haircut = 1 - 0.25 * cyc
    eps_n = eps * (0.5 + 0.5 * norm) if eps and eps > 0 else None
    fcf = num(i.get("freeCashflow"))
    ni_ttm = num(i.get("netIncomeToCommon"))
    # skip the DCF when cash flow is squeezed by a build-out (FCF under 40% of profit): it would value the
    # investment as if it were permanent
    squeezed = bool(fcf and ni_ttm and ni_ttm > 0 and fcf < 0.4 * ni_ttm)
    fcf_ps = fcf / shares if fcf and fcf > 0 and shares and same_ccy and not financial and not squeezed else None
    bv = num(i.get("bookValue")) if same_ccy and financial else None

    def value(dg, dr):
        gg, rr, vals = g + dg, r + dr, {}
        if eps_n:
            vals["graham"] = eps_n * max(8.5 + 2 * min(gg * 100, 10), 7) * GRAHAM_RATE_ADJ * haircut
        if fcf_ps:
            v, cf = 0.0, fcf_ps
            for t in range(1, 11):  # 5 years at g, then 5 years fading to the terminal rate
                cf *= 1 + (gg if t <= 5 else gg + (TERMINAL_G - gg) * (t - 5) / 5)
                v += cf / (1 + rr) ** t
            vals["dcf"] = (v + cf * (1 + TERMINAL_G) / (rr - TERMINAL_G) / (1 + rr) ** 10) * haircut
        if bv and bv > 0 and roe and roe > 0:
            vals["book"] = bv * clamp(roe / rr, 0.5, 4)
        if len(vals) > 1 and max(vals.values()) > 4 * min(vals.values()):
            vals = {k: v for k, v in vals.items() if v == min(vals.values())}  # methods disagree wildly: keep the low one
        return vals

    base = value(0, 0)
    spec = not base  # no positive earnings or cash flow to value
    if spec:
        fair = fair_lo = fair_hi = price
    else:
        fair = sum(base.values()) / len(base)
        lo, hi = value(-0.05, 0.015), value(0.05, -0.01)
        fair_lo, fair_hi = sum(lo.values()) / len(lo), sum(hi.values()) / len(hi)

    target = clamp(fair, price * 0.4, price * 2.0)
    bear = clamp(min(fair_lo, price * (1 - 0.25 * beta)), price * 0.3, min(target * 0.9, price * 0.95))
    bull = clamp(max(fair_hi, price * (1 + 0.25 * beta)), max(target * 1.1, price * 1.05), price * 2.5)
    return {
        "target": round(target, 2), "bear": round(bear, 2), "bull": round(bull, 2),
        "fair": round(fair, 2), "methods": {k: round(v, 2) for k, v in base.items()}, "spec": spec,
        "g": round(g, 3), "r": round(r, 3), "norm": round(norm, 2), "cyc": round(cyc, 2), "epsN": round(eps_n, 2) if eps_n else None,
        "cagr": round(cagr, 3) if cagr is not None else None,
    }


def score(price, m, i, h):
    """0-100 rating from reported numbers: value 40, quality 25, growth 15, balance sheet 10, momentum 10."""
    roe, margin = num(i.get("returnOnEquity")), num(i.get("profitMargins"))
    de, ch52 = num(i.get("debtToEquity")), num(i.get("52WeekChange"))
    val = 20.0 if m["spec"] else clamp(20 + (m["fair"] / price - 1) * 40, 0, 40)
    quality = clamp((roe or 0) * 40, 0, 10) + clamp((margin or 0) * 32, 0, 8)
    quality += 7 * sum(1 for n in h["ni"] if n > 0) / len(h["ni"]) if h else 3.5
    growth = clamp(m["g"] / 0.20, 0, 1) * 15
    if i.get("sector") == "Financial Services" or de is None:
        strength = 5.0  # leverage is the business model for banks; no data otherwise
    else:
        strength = clamp((250 - de) / 200, 0, 1) * 10
    momentum = clamp(((ch52 if ch52 is not None else 0) + 0.2) / 0.6, 0, 1) * 10
    parts = {"val": val, "q": quality, "gr": growth, "fin": strength, "mom": momentum}
    total = sum(parts.values())
    if m["spec"]:
        total = min(total, 50)
    return int(round(total)), {k: round(v, 1) for k, v in parts.items()}


def universe():
    """Extra symbols from universe.txt (shown with their English name)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "universe.txt")
    try:
        with open(path, encoding="utf-8") as f:
            syms = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    except OSError:
        return []
    return [x for x in syms if x not in STOCKS and x not in ETFS]


def stock_row(sym, he, curated, cache):
    i = info_for(sym, tries=3 if curated else 2)
    if not i or (not curated and i.get("quoteType") != "EQUITY"):
        print(f"skip {sym}", file=sys.stderr)
        return None
    price = num(i.get("currentPrice") or i.get("regularMarketPrice"))
    h = history(sym, cache)
    m = stock_model(price, i, h)
    sc, parts = score(price, m, i, h)
    div_rate = num(i.get("dividendRate"))
    name = i.get("shortName") or sym
    return {
        "s": sym, "tv": tv_symbol(sym, i), "he": he or name, "name": name, "il": sym in ISRAELI,
        "sector": SECTORS.get(i.get("sector"), i.get("sector") or "אחר"),
        "price": round(price, 2), "chg": num(i.get("regularMarketChangePercent")),
        "mcap": num(i.get("marketCap")), "pe": num(i.get("trailingPE")), "fpe": num(i.get("forwardPE")),
        "eps": num(i.get("trailingEps")), "feps": num(i.get("forwardEps")),
        "revG": num(i.get("revenueGrowth")), "epsG": num(i.get("earningsGrowth")),
        "margin": num(i.get("profitMargins")), "roe": num(i.get("returnOnEquity")),
        "de": num(i.get("debtToEquity")), "beta": num(i.get("beta")),
        "div": round(div_rate / price, 4) if div_rate and price else 0,
        "fcf": num(i.get("freeCashflow")), "ni": num(i.get("netIncomeToCommon")), "bv": num(i.get("bookValue")),
        "ccyOk": (i.get("financialCurrency") or "USD") == (i.get("currency") or "USD"),
        "hi52": num(i.get("fiftyTwoWeekHigh")), "lo52": num(i.get("fiftyTwoWeekLow")),
        "ch52": num(i.get("52WeekChange")),
        "aMean": num(i.get("targetMeanPrice")), "aLow": num(i.get("targetLowPrice")),
        "aHigh": num(i.get("targetHighPrice")), "aN": int(num(i.get("numberOfAnalystOpinions")) or 0),
        "rec": num(i.get("recommendationMean")),
        **m, "score": sc, "parts": parts,
    }


def main():
    out = {"updated": datetime.now(timezone.utc).isoformat(timespec="minutes"), "stocks": [], "etfs": []}
    fx = info_for("ILS=X")
    out["usdils"] = num((fx or {}).get("regularMarketPrice"))

    try:
        with open(HIST, encoding="utf-8") as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}
    jobs = [(sym, he, True) for sym, he in STOCKS.items()] + [(sym, None, False) for sym in universe()]
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = pool.map(lambda j: stock_row(*j, cache), jobs)
        out["stocks"] = [r for r in rows if r]
    curated = sum(1 for r in out["stocks"] if r["s"] in STOCKS)

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

    if curated < len(STOCKS) * 0.8:  # rate-limited or offline: don't overwrite good data with a partial pull
        sys.exit(f"only {curated} of {len(STOCKS)} main stocks fetched; keeping the previous data.json")
    with open(HIST, "w", encoding="utf-8") as f:
        json.dump(cache, f, separators=(",", ":"))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {len(out['stocks'])} stocks, {len(out['etfs'])} ETFs")


if __name__ == "__main__":
    main()

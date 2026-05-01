"""Industry stock universe for pair trading screening.

FULL_UNIVERSE: the 10-industry plan from the project spec.
SMOKE_UNIVERSE: 3 stocks/industry for smoke testing the pipeline end to end.
"""

FULL_UNIVERSE = {
    "Beverages":      ["KO", "PEP", "MNST", "KDP", "STZ", "TAP", "CELH", "FIZZ"],
    "Payments":       ["V", "MA", "AXP", "PYPL", "FIS", "FI", "GPN", "DFS"],
    "Energy":         ["XOM", "CVX", "COP", "EOG", "SLB", "OXY", "PSX", "MPC", "VLO", "HAL"],
    "Semiconductors": ["NVDA", "AMD", "INTC", "AVGO", "QCOM", "TXN", "MU", "AMAT", "LRCX", "KLAC"],
    "Airlines":       ["DAL", "UAL", "AAL", "LUV", "ALK", "JBLU", "CPA", "RYAAY", "SAVE", "HA"],
    "Banks":          ["JPM", "BAC", "C", "WFC", "GS", "MS", "USB", "PNC", "TFC", "BK"],
    "Retail":         ["WMT", "TGT", "COST", "DG", "DLTR", "KR", "HD", "LOW", "TJX", "ROST"],
    "Autos":          ["TSLA", "F", "GM", "RIVN", "LCID", "TM", "HMC", "STLA", "NIO", "XPEV"],
    "HealthCare":     ["JNJ", "PFE", "MRK", "ABBV", "LLY", "BMY", "GILD", "AMGN", "REGN", "BIIB"],
    "Communication":  ["GOOGL", "META", "NFLX", "DIS", "CMCSA", "T", "VZ", "TMUS", "SNAP", "PINS"],
}

SMOKE_UNIVERSE = {
    "Beverages":      ["KO", "PEP", "MNST"],
    "Payments":       ["V", "MA", "AXP"],
    "Energy":         ["XOM", "CVX", "COP"],
    "Semiconductors": ["NVDA", "AMD", "INTC"],
    "Airlines":       ["DAL", "UAL", "LUV"],
    "Banks":          ["JPM", "BAC", "WFC"],
    "Retail":         ["WMT", "TGT", "COST"],
    "Autos":          ["F", "GM", "TSLA"],
    "HealthCare":     ["JNJ", "PFE", "MRK"],
    "Communication":  ["GOOGL", "META", "NFLX"],
}


def all_tickers(universe):
    seen, ordered = set(), []
    for syms in universe.values():
        for s in syms:
            if s not in seen:
                seen.add(s)
                ordered.append(s)
    return ordered

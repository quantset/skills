#!/usr/bin/env python3
"""Deterministic arithmetic for the dcf-valuation skill. Standard library only.

    python dcf_math.py inputs.json            # prints the report tables as Markdown
    python dcf_math.py inputs.json --json     # prints every number as JSON

The skill gathers the inputs and makes the judgement calls (sector spread, terminal growth).
This script does what must come out the same every time: choosing and checking the base cash
flow, the reverse DCF (what today's price implies), three explicit scenarios (Bear / Base / Bull),
discounting, the equity bridge, the sanity checks, and the 3x3 sensitivity matrix.
Rates are in percent (8.75 means 8.75%). Money is in one currency unit.

inputs.json (null where a response had no value):
{
  "ticker": "us:MSFT", "currency": "USD", "price": 490.00, "price_date": "2026-11-25",
  "diluted_shares": 7430000000,
  "debt": 35481000000, "cash": 20281000000,
  "base": {"period_end": "2026-06-30", "form": "10-K", "free_cash_flow": 74000000000, "revenue": 281700000000},
  "fiscal_years": [                               # fiscal-year rows, any order; the six newest are used
    {"period_end": "2026-06-30", "revenue": 281700000000, "free_cash_flow": 74000000000}
  ],
  "sbc": 10700000000,                             # latest full-year stock-based compensation
  "consensus_growth_fy1_pct": 15.0, "consensus_growth_fy2_pct": 14.5,
  "analyst_count": 32,                            # from this fiscal year's estimate row
  "risk_free_pct": 4.25, "spread_pct": 4.50, "terminal_growth_pct": 2.5,
  "horizon_years": null,                          # optional: defaults to 10 when growth >= 12% else 5
  "peer_fcf_yields_pct": [3.1, 1.8, -42.8, 2.2]   # optional, from get_peers
}
"""
import json
import statistics
import sys
from datetime import date

GROWTH_CAP = 20.0          # base-case cap unless backed by broad analyst consensus
GROWTH_CAP_BACKED = 28.0   # allowed when both consensus years exceed 20% with >= 5 analysts
MIN_ANALYSTS = 5           # fewer estimates than this is not a consensus
FADE_10Y = 0.88            # single smooth 10-year fade across all growth rates (zero step-function cliff)
TV_SHARE_FLAG = 82.0       # above this share of value in the terminal year, the result is mostly an assumption
DISAGREE_FLAG = 45.0       # a model this far from the price says more about its assumptions than about the company
HISTORY_YEARS = 6
NORMALIZE_BAND = 15.0      # a base margin >15% away from the 3-year prior median (e.g. a CapEx surge) is normalized
STALE_DAYS = 200           # a base older than about two quarters no longer describes the business


def fiscal_history(data):
    rows = sorted((r for r in data.get("fiscal_years") or [] if r.get("period_end")), key=lambda r: r["period_end"])[-HISTORY_YEARS:]
    revenue = [r for r in rows if r.get("revenue")]
    cagr = None
    if len(revenue) >= 3 and revenue[0]["revenue"] > 0:
        cagr = ((revenue[-1]["revenue"] / revenue[0]["revenue"]) ** (1 / (len(revenue) - 1)) - 1) * 100
    # The normal year is judged against the three fiscal years before the base, never against itself.
    base_end = (data.get("base") or {}).get("period_end")
    margins = [r["free_cash_flow"] / r["revenue"] * 100 for r in rows
               if r.get("revenue") and r.get("free_cash_flow") is not None and r["period_end"] != base_end][-3:]
    return cagr, len(revenue), margins


def choose_base(data, margins):
    """The reported base, or a normalized one when the base is negative or >15% off its 3-year median margin."""
    base = data.get("base") or {}
    fcf, revenue = base.get("free_cash_flow"), base.get("revenue")
    if fcf is None:
        raise SystemExit("Missing input: base.free_cash_flow")
    label = "trailing twelve months" if base.get("form") == "10-Q" else "fiscal year"
    basis = f"{label} to {base.get('period_end')}"
    median = statistics.median(margins) if len(margins) == 3 else None
    margin = fcf / revenue * 100 if revenue else None
    off = median is not None and margin is not None and median != 0 and abs(margin - median) / abs(median) * 100 > NORMALIZE_BAND
    normal_candidate = (median / 100 * revenue) if median and median > 0 and revenue else None
    if fcf > 0 and not off:
        return fcf, basis, None, normal_candidate
    why = "is negative" if fcf <= 0 else f"margin {margin:.1f}% is more than {NORMALIZE_BAND:.0f}% away from the prior 3-year median {median:.1f}% (e.g. a capital-spending cycle)"
    if median is None or median <= 0 or not revenue:
        return None, basis, f"Base free cash flow ({fcf:,.0f}, {basis}) {why}, and there is no positive 3-year median margin to normalize on.", None
    return median / 100 * revenue, f"normalized: 3-year median FCF margin {median:.1f}% x revenue for the {basis}", \
        f"Reported base free cash flow ({fcf:,.0f}, {basis}) {why}. The model uses the normalized base ({median / 100 * revenue:,.0f}) and shows the reported-base figure alongside.", fcf


def year_one_growth(data, cagr):
    parts = [v for v in (data.get("consensus_growth_fy1_pct"), data.get("consensus_growth_fy2_pct"), cagr) if v is not None]
    if not parts:
        raise SystemExit("No growth evidence: give consensus revenue growth or fiscal-year revenue history.")
    raw = sum(parts) / len(parts)
    fy1, fy2 = data.get("consensus_growth_fy1_pct"), data.get("consensus_growth_fy2_pct")
    backed = (fy1 is not None and fy2 is not None and fy1 > GROWTH_CAP and fy2 > GROWTH_CAP
              and (data.get("analyst_count") or 0) >= MIN_ANALYSTS)
    cap = GROWTH_CAP_BACKED if backed else GROWTH_CAP
    return min(raw, cap), raw, cap


def value(fcf0, growth_pcts, wacc_pct, g_pct, net_debt, shares):
    wacc, g = wacc_pct / 100, g_pct / 100
    if wacc <= g:
        raise SystemExit(f"Discount rate {wacc_pct}% must exceed terminal growth {g_pct}%.")
    flows, fcf = [], fcf0
    for year, rate in enumerate(growth_pcts, 1):
        fcf *= 1 + rate / 100
        factor = 1 / (1 + wacc) ** year
        flows.append({"year": year, "growth_pct": rate, "fcf": fcf, "discount_factor": factor, "pv": fcf * factor})
    tv = fcf * (1 + g) / (wacc - g)
    pv_tv = tv * flows[-1]["discount_factor"]
    ev = sum(f["pv"] for f in flows) + pv_tv
    equity = ev - net_debt
    return {"flows": flows, "terminal_value": tv, "pv_terminal": pv_tv, "enterprise_value": ev,
            "equity_value": equity, "per_share": equity / shares, "tv_share_pct": pv_tv / ev * 100,
            "exit_multiple": tv / fcf}


def path(g1, g_inf, years=10):
    """Continuous 10-year geometric fade (`FADE_10Y`) toward `g_inf` — no threshold cliff at any growth rate."""
    rates = [g1]
    while len(rates) < years:
        rates.append(max(rates[-1] * FADE_10Y, g_inf))
    return rates


def reverse(fcf0, price, wacc_pct, g_pct, net_debt, shares, years=5):
    """Constant stage-1 FCF growth, then terminal growth, that makes value per share equal today's price."""
    low, high = -50.0, 300.0
    for _ in range(200):
        mid = (low + high) / 2
        if value(fcf0, [mid] * years, wacc_pct, g_pct, net_debt, shares)["per_share"] < price:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def run(data):
    for key in ("price", "diluted_shares", "debt", "cash", "risk_free_pct", "spread_pct", "terminal_growth_pct"):
        if data.get(key) is None:
            raise SystemExit(f"Missing input: {key}")
    cagr, years_used, margins = fiscal_history(data)
    fcf0, basis, base_note, alt_base = choose_base(data, margins)
    notes = [base_note] if base_note else []
    out = {"ticker": data.get("ticker"), "currency": data.get("currency"), "price": data["price"],
           "base_fcf": fcf0, "base_fcf_basis": basis, "normalized": bool(base_note), "notes": notes,
           "revenue_cagr_pct": cagr, "fiscal_years_with_revenue": years_used}
    if fcf0 is None:
        out["suitable"] = False
        notes.append("A cash-flow DCF does not fit this company now. Do not give a fair value.")
        return out
    out["suitable"] = True
    base_end, price_day = (data.get("base") or {}).get("period_end"), data.get("price_date")
    if base_end and price_day and (date.fromisoformat(price_day) - date.fromisoformat(base_end)).days > STALE_DAYS:
        notes.append(f"The base period ended {base_end}, more than two quarters before the price date {price_day}: say the base is stale.")
    g1, raw, cap = year_one_growth(data, cagr)
    if raw > cap:
        notes.append(f"Base-case Year-1 growth capped at {cap:.0f}% (evidence averaged {raw:.1f}%).")
    years = int(data["horizon_years"]) if data.get("horizon_years") else 10
    wacc, g = data["risk_free_pct"] + data["spread_pct"], data["terminal_growth_pct"]
    if g > data["risk_free_pct"]:
        notes.append(f"Terminal growth {g}% exceeds the risk-free rate {data['risk_free_pct']}%; lower it.")
    net_debt, shares = data["debt"] - data["cash"], data["diluted_shares"]
    rates = path(g1, g, years=years)
    base = value(fcf0, rates, wacc, g, net_debt, shares)
    sbc = data.get("sbc")
    owner = value(fcf0 - sbc, rates, wacc, g, net_debt, shares) if sbc is not None and fcf0 > sbc else None
    # Three explicit assumption scenarios so the reader sees how value moves with growth & WACC instead of one dogmatic point.
    bear_g1 = max(g, g1 * 0.65)
    bull_g1 = min(max(raw, g1 * 1.25), 35.0)
    bear_case = value(fcf0, path(bear_g1, max(1.5, g - 0.5), years=years), wacc + 0.75, max(1.5, g - 0.5), net_debt, shares)
    bull_case = value(fcf0, path(bull_g1, min(data["risk_free_pct"] - 0.25, g + 0.5), years=years), max(g + 1.5, wacc - 0.75), min(data["risk_free_pct"] - 0.25, g + 0.5), net_debt, shares)
    scenarios = {
        "bear": {"year_one_growth_pct": round(bear_g1, 2), "wacc_pct": round(wacc + 0.75, 2), "per_share": bear_case["per_share"]},
        "base": {"year_one_growth_pct": round(g1, 2), "wacc_pct": round(wacc, 2), "per_share": base["per_share"]},
        "bull": {"year_one_growth_pct": round(bull_g1, 2), "wacc_pct": round(max(g + 1.5, wacc - 0.75), 2), "per_share": bull_case["per_share"]},
    }
    matrix = [[value(fcf0, rates, wacc + dw, g + dg, net_debt, shares)["per_share"] for dg in (-0.5, 0.0, 0.5)]
              for dw in (-1.0, 0.0, 1.0)]
    assert abs(matrix[1][1] - base["per_share"]) < 1e-9, "centre cell must equal the base case"
    if base["tv_share_pct"] > TV_SHARE_FLAG:
        notes.append(f"Terminal value is {base['tv_share_pct']:.0f}% of enterprise value (flag above {TV_SHARE_FLAG:.0f}%).")
    yields = [y for y in data.get("peer_fcf_yields_pct") or [] if y is not None and 0 < y < 100]
    peer = 100 / statistics.median(yields) if len(yields) >= 3 else None
    notes.append(f"The terminal value assumes the company is worth {base['exit_multiple']:.1f}x its year-{years} free cash flow"
                 + (f"; peers trade at a median {peer:.1f}x today (n={len(yields)})." if peer else "; no peer median was available."))
    upside = (base["per_share"] / data["price"] - 1) * 100
    normal = None
    reported_unadjusted = None
    if base_note and alt_base and alt_base > 0:
        reported_unadjusted = value(alt_base, rates, wacc, g, net_debt, shares)["per_share"]
        notes.append(f"On the unadjusted reported base ({alt_base:,.0f}) the base-case value would be {reported_unadjusted:,.2f}.")
    elif not base_note and alt_base:
        normal = value(alt_base, rates, wacc, g, net_debt, shares)["per_share"]
        notes.append(f"On a 3-year median-margin base the model value would be {normal:,.2f}.")
    wide = abs(upside) > DISAGREE_FLAG
    if wide:
        notes.append(f"The base-case value is {abs(upside):.0f}% {'below' if upside < 0 else 'above'} the price. "
                     "Lead with what the price implies (the reverse DCF) and the three scenarios, and do not call the stock over- or undervalued off one set of assumptions.")
    rev_growth = reverse(fcf0, data["price"], wacc, g, net_debt, shares, years=years)
    out.update({
        "horizon_years": years,
        "sbc": sbc, "sbc_pct_of_fcf": sbc / fcf0 * 100 if sbc else None, "year_one_growth_pct": g1, "growth_path_pct": rates,
        "wacc_pct": wacc, "terminal_growth_pct": g, "net_debt": net_debt, "diluted_shares": shares, "base": base,
        "scenarios": scenarios,
        "owner_fcf_per_share": owner["per_share"] if owner else None,
        "upside_pct": upside, "normal_year_per_share": normal, "reported_base_per_share": reported_unadjusted,
        "sensitivity": {"wacc_pct": [wacc - 1, wacc, wacc + 1], "terminal_growth_pct": [g - 0.5, g, g + 0.5], "per_share": matrix},
        "reverse_dcf_growth_pct": rev_growth,
        "peer_median_price_to_fcf": peer,
        "confidence": ("low: the base was normalized, so lead with what the price implies" if base_note
                       else "low: the model and the price disagree widely, so lead with what the price implies" if wide else "normal"),
    })
    return out


def markdown(r):
    c = r["currency"] or ""
    if not r["suitable"]:
        return "\n".join(["**No point estimate.**", ""] + [f"- {n}" for n in r["notes"]])
    yrs = r["horizon_years"]
    sc = r["scenarios"]
    hist_str = f"{r['revenue_cagr_pct']:.1f}% historical revenue CAGR" if r["revenue_cagr_pct"] is not None else "n/a historical CAGR"
    rep_clause = (
        f" (on normalized FCF; on unadjusted reported FCF the Base value is **{r['reported_base_per_share']:,.2f}** {c})"
        if r.get("reported_base_per_share") is not None else ""
    )
    out = [
        f"**What {r['ticker']} at {r['price']:,.2f} {c} implies (Reverse DCF):** the market is pricing in **{r['reverse_dcf_growth_pct']:.1f}%** annual FCF growth over {yrs} years (at {r['wacc_pct']:.2f}% WACC, {r['terminal_growth_pct']:.2f}% terminal growth), vs. {hist_str}.",
        f"**Scenario range ({yrs}-year model):** Bear **{sc['bear']['per_share']:,.2f}** | Base **{sc['base']['per_share']:,.2f}** ({r['upside_pct']:+.1f}%){rep_clause} | Bull **{sc['bull']['per_share']:,.2f}** {c}.",
        "",
    ]
    if r["owner_fcf_per_share"] is not None:
        out += [f"SBC-adjusted (Owner FCF) base value: {r['owner_fcf_per_share']:,.2f} {c} (SBC is {r['sbc_pct_of_fcf']:.1f}% of base FCF).", ""]
    out += ["| Scenario | Year-1 Growth | WACC | Value / Share | vs. Price |", "|---|---|---|---|---|"]
    for label, key in (("Bear", "bear"), ("Base", "base"), ("Bull", "bull")):
        sv = sc[key]["per_share"]
        diff = (sv / r["price"] - 1) * 100
        out.append(f"| {label} | {sc[key]['year_one_growth_pct']:.1f}% | {sc[key]['wacc_pct']:.2f}% | {sv:,.2f} {c} | {diff:+.1f}% |")
    out += ["", "| Input | Value |", "|---|---|", f"| Base FCF | {r['base_fcf']:,.0f} ({r['base_fcf_basis']}) |",
            f"| Horizon | {yrs} years |", f"| Discount rate (Base) | {r['wacc_pct']:.2f}% |",
            f"| Terminal growth | {r['terminal_growth_pct']:.2f}% |",
            f"| Net debt | {r['net_debt']:,.0f} |", f"| Diluted shares | {r['diluted_shares']:,.0f} |", "",
            "| Year | Growth | FCF | Discount factor | Present value |", "|---|---|---|---|---|"]
    out += [f"| {f['year']} | {f['growth_pct']:.2f}% | {f['fcf']:,.0f} | {f['discount_factor']:.4f} | {f['pv']:,.0f} |" for f in r["base"]["flows"]]
    b, s = r["base"], r["sensitivity"]
    out += [f"| Terminal | {r['terminal_growth_pct']:.2f}% | {b['terminal_value']:,.0f} | | {b['pv_terminal']:,.0f} |", "",
            f"Enterprise value {b['enterprise_value']:,.0f}; equity value {b['equity_value']:,.0f}; "
            f"terminal share {b['tv_share_pct']:.1f}%; implied exit multiple {b['exit_multiple']:.1f}x.", "",
            "| Discount rate \\ Terminal growth | " + " | ".join(f"{g:.2f}%" for g in s["terminal_growth_pct"]) + " |", "|---|---|---|---|"]
    out += [f"| {w:.2f}% | " + " | ".join(f"{v:,.2f}" for v in row) + " |" for w, row in zip(s["wacc_pct"], s["per_share"])]
    out += [""] + [f"- {n}" for n in r["notes"]]
    return "\n".join(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    with open(sys.argv[1]) as handle:
        result = run(json.load(handle))
    print(json.dumps(result, indent=1) if "--json" in sys.argv else markdown(result))

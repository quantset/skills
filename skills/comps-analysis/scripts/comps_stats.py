#!/usr/bin/env python3
"""Deterministic arithmetic for the comps-analysis skill. Standard library only.

    python comps_stats.py comps.json            # peer table, benchmarks and implied range as Markdown
    python comps_stats.py comps.json --json

Every company is one object. Copy the fields from the calls named in the skill and leave a
field null when the response had no value. Money is in US dollars.

{
  "target": {
    "instrument_id": "us:AMD", "price": 406.03, "market_cap_b": 662.83,
    "latest_date": "2026-11-25",
    "enterprise_value_b": null, "total_debt": null, "cash": 7404000000,          # get_company_snapshot
    "revenue_ttm": 45436000000, "operating_income_ttm": 8050000000, "fundamentals_basis": "ttm",
    "pe_ttm": 210.4, "forward_eps": 16.37, "rev_growth_yoy_pct": 31.2, "roic_pct": null,
    "share_count_change_1y_pct": 1.0,
    "fy": {"period_end": "2025-12-27", "revenue": 34639000000, "ebitda": 4215000000, "free_cash_flow": 6735000000},
    "balance": {"long_term_debt": 7079000000, "current_portion_long_term_debt": 0,
                "notes_payable": null, "convertible_debt": null},
    "diluted_shares": 1661000000
  },
  "peers": [ {"instrument_id": "us:NVDA", "...": "same fields, without diluted_shares"} ]
}

Rules the script applies:
- EV / Revenue and EV / EBIT use the snapshot's trailing revenue and operating income when
  fundamentals_basis is "ttm"; otherwise the fiscal-year figures, and the row says so.
- EV / EBITDA and EV / FCF use the fiscal-year row ("fy"); trailing figures for them do not exist.
  A fiscal year that ended more than 270 days before the price date is flagged as stale.
- Debt is the snapshot total_debt, or the sum of the balance-sheet debt lines when that is empty.
- Enterprise value is the snapshot figure, or market cap + debt - cash when that is empty (marked "c").
- Forward P/E is price / forward_eps.
- A multiple that is zero, negative or missing is not meaningful (N/M) and stays out of the
  benchmarks. A benchmark needs at least three peers with a value.
- Percentiles use linear interpolation between the sorted values (the "inclusive" method).
"""
import json
import statistics
import sys

MIN_PEERS = 3    # two values do not make a range
STALE_DAYS = 270  # a fiscal year this old no longer describes a company that is growing or shrinking fast
MULTIPLES = ("ev_to_revenue", "ev_to_ebit", "ev_to_ebitda", "ev_to_fcf", "pe_ttm", "pe_forward")
OTHERS = ("rev_growth_yoy_pct", "fcf_margin_pct", "roic_pct", "share_count_change_1y_pct")
DEBT_LINES = ("long_term_debt", "current_portion_long_term_debt", "notes_payable", "convertible_debt")


def ratio(top, bottom):
    """A negative result is kept so the table can show it as not meaningful."""
    return top / bottom if top is not None and bottom else None


def prepare(company):
    row = dict(company)
    fy, balance = row.get("fy") or {}, row.get("balance") or {}
    debt, source = row.get("total_debt"), "snapshot"
    if debt is None and balance.get("long_term_debt") is not None:
        found = [line for line in DEBT_LINES if balance.get(line) is not None]
        debt = sum(balance[line] for line in found)
        source = "balance sheet (" + ", ".join(found) + (")" if len(found) > 1 else "; other debt lines empty, so likely understated)")
    row["debt"], row["debt_source"] = debt, source if debt is not None else None
    ev, row["ev_computed"] = None, False
    if row.get("enterprise_value_b") is not None:
        ev = row["enterprise_value_b"] * 1e9
    elif row.get("market_cap_b") is not None and debt is not None and row.get("cash") is not None:
        ev, row["ev_computed"] = row["market_cap_b"] * 1e9 + debt - row["cash"], True
    row["ev"] = ev
    trailing = row.get("fundamentals_basis") == "ttm"
    row["trailing"] = trailing
    row["ev_to_revenue"] = ratio(ev, row.get("revenue_ttm") if trailing and row.get("revenue_ttm") else fy.get("revenue"))
    row["ev_to_ebit"] = ratio(ev, row.get("operating_income_ttm")) if trailing else None
    row["ev_to_ebitda"] = ratio(ev, fy.get("ebitda"))
    row["ev_to_fcf"] = ratio(ev, fy.get("free_cash_flow"))
    row["pe_forward"] = ratio(row.get("price"), row.get("forward_eps"))
    row["fcf_margin_pct"] = fy["free_cash_flow"] / fy["revenue"] * 100 if fy.get("revenue") and fy.get("free_cash_flow") is not None else None
    row["fy_end"] = fy.get("period_end")
    return row


def benchmark(values, positive_only):
    usable = [v for v in values if v is not None and (v > 0 or not positive_only)]
    if len(usable) < MIN_PEERS:
        return {"n": len(usable), "p25": None, "median": None, "p75": None}
    low, _, high = statistics.quantiles(usable, n=4, method="inclusive")
    return {"n": len(usable), "p25": low, "median": statistics.median(usable), "p75": high}


def run(data):
    target = prepare(data["target"])
    peers = [prepare(p) for p in data.get("peers") or [] if p.get("instrument_id") != target.get("instrument_id")]
    stats = {key: benchmark([p.get(key) for p in peers], key in MULTIPLES) for key in MULTIPLES + OTHERS}
    shares, fy = target.get("diluted_shares"), target.get("fy") or {}
    net_debt = target["debt"] - target["cash"] if target["debt"] is not None and target.get("cash") is not None else None
    implied, notes = {}, []
    bases = (("ev_to_ebit", target.get("operating_income_ttm") if target["trailing"] else None),
             ("ev_to_ebitda", fy.get("ebitda")), ("ev_to_fcf", fy.get("free_cash_flow")))
    for key, base in bases:
        s = stats[key]
        usable = base is not None and base > 0 and shares and net_debt is not None and s["median"] is not None
        implied[key] = {q: (s[q] * base - net_debt) / shares for q in ("p25", "median", "p75")} if usable else None
    s, eps = stats["pe_forward"], target.get("forward_eps")
    implied["pe_forward"] = {q: s[q] * eps for q in ("p25", "median", "p75")} if eps and eps > 0 and s["median"] is not None else None
    if net_debt is None:
        notes.append("The target has no usable debt figure, so no enterprise-value multiple can be turned into a share price.")
    if target["ev_computed"]:
        notes.append(f"Target enterprise value is computed (market cap + debt - cash; debt from the {target['debt_source']}).")
    priced = target.get("latest_date")
    if priced:
        from datetime import date
        stale = [c["instrument_id"] for c in [target] + peers
                 if c.get("fy_end") and (date.fromisoformat(priced) - date.fromisoformat(c["fy_end"])).days > STALE_DAYS]
        if stale:
            notes.append(f"Fiscal year ended more than {STALE_DAYS} days before the price date for: " + ", ".join(stale)
                         + ". Their EV / EBITDA and EV / FCF are stale; prefer EV / Revenue and EV / EBIT, which are trailing.")
    untrailing = [c["instrument_id"] for c in [target] + peers if not c["trailing"]]
    if untrailing:
        notes.append("No trailing figures (EV / Revenue is on the fiscal year, EV / EBIT is n/a) for: " + ", ".join(untrailing) + ".")
    computed = [p["instrument_id"] for p in peers if p["ev_computed"]]
    if computed:
        notes.append("Enterprise value computed for: " + ", ".join(computed) + ".")
    missing = [p["instrument_id"] for p in peers if p["ev"] is None]
    if missing:
        notes.append("No enterprise value could be established for: " + ", ".join(missing) + ".")
    years = sorted({c["fy_end"][:7] for c in [target] + peers if c.get("fy_end")})
    if len(years) > 1:
        notes.append(f"Fiscal years end between {years[0]} and {years[-1]}; the multiples are not on one date.")
    return {"target": target, "peers": peers, "benchmarks": stats, "net_debt": net_debt, "implied_price": implied, "notes": notes}


def cell(value, suffix="", digits=1, meaningful=True):
    if value is None:
        return "n/a"
    return "N/M" if meaningful and value <= 0 else f"{value:,.{digits}f}{suffix}"


def markdown(r):
    out = ["| Company | Mkt Cap ($B) | EV ($B) | EV / Revenue | EV / EBIT | EV / EBITDA (FY) | EV / FCF (FY) | P/E (TTM) | Fwd P/E | Rev Growth YoY | FCF Margin (FY) | ROIC | 1Y Share Chg | Fiscal year end |",
           "|" + "---|" * 14]

    def line(label, c):
        ev = cell(c["ev"] / 1e9 if c["ev"] is not None else None) + (" c" if c["ev_computed"] else "")
        return (f"| {label} | {cell(c.get('market_cap_b'))} | {ev} | " + " | ".join(cell(c.get(k), "x") for k in MULTIPLES) + " | "
                + " | ".join(cell(c.get(k), "%", meaningful=False) for k in OTHERS) + f" | {c.get('fy_end') or 'n/a'} |")

    out.append(line(f"**{r['target'].get('instrument_id')}** (target)", r["target"]))
    out += [line(p.get("instrument_id"), p) for p in sorted(r["peers"], key=lambda p: -(p.get("market_cap_b") or 0))]
    b = r["benchmarks"]
    for label, q in (("25th percentile", "p25"), ("Median", "median"), ("75th percentile", "p75")):
        out.append(f"| *{label} (peers)* | | | " + " | ".join(cell(b[k][q], "x") for k in MULTIPLES) + " | "
                   + " | ".join(cell(b[k][q], "%", meaningful=False) for k in OTHERS) + " | |")
    out.append("| *Peers with a value* | | | " + " | ".join(str(b[k]["n"]) for k in MULTIPLES + OTHERS) + " | |")
    out += ["", "| Implied share price | 25th | Median | 75th |", "|---|---|---|---|"]
    for key, label in (("ev_to_ebit", "EV / EBIT (trailing)"), ("ev_to_ebitda", "EV / EBITDA (fiscal year)"),
                       ("ev_to_fcf", "EV / FCF (fiscal year)"), ("pe_forward", "Forward P/E")):
        v = r["implied_price"][key]
        out.append(f"| {label} | " + (" | ".join(f"{v[q]:,.2f}" for q in ("p25", "median", "p75")) if v else "n/a | n/a | n/a") + " |")
    out.append(f"\nCurrent price: {cell(r['target'].get('price'), digits=2)}. Net debt in the bridge: {cell(r['net_debt'], digits=0, meaningful=False)}.")
    out += [""] + [f"- {n}" for n in r["notes"]]
    return "\n".join(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    with open(sys.argv[1]) as handle:
        result = run(json.load(handle))
    print(json.dumps(result, indent=1) if "--json" in sys.argv else markdown(result))

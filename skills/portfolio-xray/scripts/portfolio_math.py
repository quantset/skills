#!/usr/bin/env python3
"""Deterministic arithmetic for the portfolio-xray skill. Standard library only.

    python portfolio_math.py portfolio.json            # Markdown: look-through exposure, correlations, drawdowns
    python portfolio_math.py portfolio.json --json

portfolio.json:
{
  "holdings": [{"id": "us:IVV", "weight_pct": 40}, {"id": "us:NVDA", "weight_pct": 25, "name": "NVIDIA Corp"}],
  "funds": {                                    # optional: rows from get_etf_data view="holdings", per fund held
    "us:IVV": [{"constituent_instrument_id": "us:NVDA", "ticker": "NVDA", "issuer": "NVIDIA CORP", "weight_pct": 7.4}]
  },
  "prices": {                                   # optional: rows from get_price_history, per holding
    "us:NVDA": [{"date": "2026-11-24", "close": 149.3}]
  },
  "analytics": {"instruments": [], "correlations": []},   # optional: the "data" object of the correlations call
  "benchmark": "index:SPX",                     # optional: the instrument in "analytics" to compare against
  "fundamentals": {                             # optional: from get_company_snapshot, per stock held
    "us:NVDA": {"pe_ttm": 18.9, "roic_pct": 63.2, "fcf_yield_pct": 2.7, "dividend_yield_pct": 0.35,
                "dividend_basis": null, "share_count_change_1y_pct": -1.2}
  }
}

A value under "funds", "prices", "analytics" or "fundamentals" may also be a path to a saved tool
response (a JSON file whose "data" key holds the rows).
Weights are percentages of the whole portfolio and are rescaled if they do not sum to 100.
"""
import json
import math
import sys

CONCENTRATION_FLAG = 15.0   # one issuer above this share of the portfolio is a single-name bet
CLUSTER_FLAG = 0.85         # holdings this correlated fall together
MIN_OVERLAP = 60            # fewer common trading days than this is too thin for a correlation
SHARE_CLASSES = (" class a", " class b", " class c", " cl a", " cl b", " cl c")
TRADING_DAYS = 252


def rows(value):
    if isinstance(value, str):
        with open(value) as handle:
            value = json.load(handle)
    return value.get("data", value) if isinstance(value, dict) else value


def issuer_key(name):
    """One key per company, so share classes and spelling variants of an issuer add up."""
    text = (name or "").lower().replace(",", " ").replace(".", " ")
    for suffix in SHARE_CLASSES:
        text = text.replace(suffix, "")
    return " ".join(text.split())


def look_through(holdings, funds):
    """Direct weight plus each fund's weight times the constituent's weight inside the fund, per issuer."""
    direct = {h["id"]: h["weight"] for h in holdings if h["id"] not in funds}
    by_symbol = {key.split(":", 1)[-1].upper(): key for key in direct}
    fund_rows = {fund: rows(value) for fund, value in funds.items()}
    # A direct holding joins its issuer when a fund row names it by instrument id or ticker.
    alias = {}
    for listing in fund_rows.values():
        for row in listing:
            held = row.get("constituent_instrument_id") if row.get("constituent_instrument_id") in direct else by_symbol.get((row.get("ticker") or "").upper())
            if held and row.get("issuer"):
                alias[held] = issuer_key(row["issuer"])
    names, exposure = {}, {}
    labels = {h["id"]: h.get("name") or h["id"] for h in holdings}
    for key, weight in direct.items():
        group = alias.get(key, key)
        names[group] = labels[key]
        exposure.setdefault(group, {"direct": 0.0, "through": {}})["direct"] += weight
    coverage = {}
    for fund_id, fund_weight in ((h["id"], h["weight"]) for h in holdings if h["id"] in funds):
        listed = 0.0
        for row in fund_rows[fund_id]:
            weight = row.get("weight_pct")
            if weight is None:
                continue
            listed += weight
            group = issuer_key(row.get("issuer")) or row.get("constituent_instrument_id") or row.get("ticker")
            if not group:
                continue
            names.setdefault(group, row.get("issuer") or row.get("ticker") or group)
            entry = exposure.setdefault(group, {"direct": 0.0, "through": {}})
            entry["through"][fund_id] = entry["through"].get(fund_id, 0.0) + fund_weight * weight / 100
        dates = sorted(row["as_of"] for row in fund_rows[fund_id] if row.get("as_of"))
        coverage[fund_id] = {"rows": len(fund_rows[fund_id]), "listed_pct": listed, "as_of": dates[-1] if dates else None,
                             "unattributed_pct": fund_weight * max(0.0, 100 - listed) / 100}
    table = [{"id": key, "name": names[key], "direct_pct": e["direct"], "through_pct": sum(e["through"].values()),
              "total_pct": e["direct"] + sum(e["through"].values()), "via": e["through"]} for key, e in exposure.items()]
    return sorted(table, key=lambda r: -r["total_pct"]), coverage


def series(value):
    points = {r["date"]: r["close"] for r in rows(value) if r.get("close") is not None and r.get("date")}
    return dict(sorted(points.items()))


def risk(prices):
    out = {}
    for key, value in prices.items():
        closes = list(series(value).values())
        if len(closes) < 2:
            continue
        peak, worst = closes[0], 0.0
        for close in closes:
            peak = max(peak, close)
            worst = min(worst, close / peak - 1)
        returns = [b / a - 1 for a, b in zip(closes, closes[1:]) if a]
        mean = sum(returns) / len(returns)
        spread = math.sqrt(sum((r - mean) ** 2 for r in returns) / max(len(returns) - 1, 1))
        dates = list(series(value))
        out[key] = {"from": dates[0], "to": dates[-1], "days": len(closes), "return_pct": (closes[-1] / closes[0] - 1) * 100,
                    "max_drawdown_pct": worst * 100, "volatility_pct": spread * math.sqrt(TRADING_DAYS) * 100}
    return out


def correlations(prices):
    """Pearson correlation of daily returns on the dates both holdings traded."""
    data = {key: series(value) for key, value in prices.items()}
    keys, out = sorted(data), {}
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            common = sorted(set(data[a]) & set(data[b]))
            ra = [data[a][y] / data[a][x] - 1 for x, y in zip(common, common[1:])]
            rb = [data[b][y] / data[b][x] - 1 for x, y in zip(common, common[1:])]
            if len(ra) < MIN_OVERLAP:
                out[(a, b)] = {"n": len(ra), "r": None}
                continue
            ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
            cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
            va, vb = sum((x - ma) ** 2 for x in ra), sum((y - mb) ** 2 for y in rb)
            out[(a, b)] = {"n": len(ra), "r": cov / math.sqrt(va * vb) if va and vb else None}
    return keys, out


def quality(holdings, fundamentals):
    """Weighted averages over the holdings that have a value; P/E is averaged as earnings yield."""
    out = {}
    for field in ("pe_ttm", "roic_pct", "fcf_yield_pct", "dividend_yield_pct", "share_count_change_1y_pct"):
        pairs = []
        for h in holdings:
            facts = fundamentals.get(h["id"]) or {}
            facts = (rows(facts) or [{}])[0] if isinstance(facts, (str, list)) else facts
            facts = facts.get("data", [facts])[0] if isinstance(facts.get("data"), list) else facts
            number = facts.get(field)
            if field == "dividend_yield_pct" and number is None and facts.get("dividend_basis") == "no_recorded_dividends":
                number = 0.0   # the company pays none; that is a yield of zero, not a missing value
            pairs.append((h["weight"], number))
        pairs = [(w, v) for w, v in pairs if v is not None and (field != "pe_ttm" or v > 0)]
        covered = sum(w for w, _ in pairs)
        if not covered:
            out[field] = {"value": None, "weight_covered_pct": 0.0}
        elif field == "pe_ttm":   # a weighted harmonic mean: one very high P/E cannot dominate
            out[field] = {"value": covered / sum(w / v for w, v in pairs), "weight_covered_pct": covered}
        else:
            out[field] = {"value": sum(w * v for w, v in pairs) / covered, "weight_covered_pct": covered}
    return out


def from_analytics(value, benchmark):
    """Return, volatility, drawdown and correlations as the correlations endpoint computed them, in US dollars."""
    body = rows(value)
    body = body[0] if isinstance(body, list) else body
    base = next((i.get("cumulative_return_pct") for i in body["instruments"] if i["instrument_id"] == benchmark), None)
    stats = {i["instrument_id"]: {"from": i.get("first_date"), "to": i.get("last_date"), "days": i.get("observations"),
                                  "return_pct": i.get("cumulative_return_pct"), "max_drawdown_pct": i.get("max_drawdown_pct"),
                                  "volatility_pct": i.get("annualized_volatility_pct"),
                                  "vs_benchmark_pct": None if base is None or i.get("cumulative_return_pct") is None else i["cumulative_return_pct"] - base}
             for i in body["instruments"]}
    pairs = {(c["instrument_a"], c["instrument_b"]): {"n": c.get("overlapping_sessions") or 0,
                                                       "r": c.get("correlation") if (c.get("overlapping_sessions") or 0) >= MIN_OVERLAP else None}
             for c in body["correlations"]}
    return stats, sorted(stats), pairs


def run(data):
    total = sum(h["weight_pct"] for h in data["holdings"])
    holdings = [{"id": h["id"], "name": h.get("name"), "weight": h["weight_pct"] * 100 / total} for h in data["holdings"]]
    benchmark = data.get("benchmark") or "index:SPX"
    funds, prices = data.get("funds") or {}, data.get("prices") or {}
    exposure, coverage = look_through(holdings, funds)
    keys, pairs = correlations(prices) if prices else ([], {})
    stats = risk(prices)
    if data.get("analytics"):
        stats, keys, pairs = from_analytics(data["analytics"], benchmark)
    return {"weights_rescaled": abs(total - 100) > 1e-9, "holdings": holdings, "look_through": exposure,
            "fund_coverage": coverage, "quality": quality(holdings, data.get("fundamentals") or {}),
            "risk": stats, "correlation_keys": keys,
            "correlations": [{"a": a, "b": b, **v} for (a, b), v in pairs.items()],
            "flags": [f"{r['name']} is {r['total_pct']:.1f}% of the portfolio once funds are looked through "
                      f"({r['direct_pct']:.1f}% direct + {r['through_pct']:.1f}% through funds)."
                      for r in exposure if r["total_pct"] > CONCENTRATION_FLAG]
                     + [f"{a} and {b} move together (correlation {v['r']:.3f} over {v['n']} common days)."
                        for (a, b), v in pairs.items() if v["r"] is not None and v["r"] >= CLUSTER_FLAG and benchmark not in (a, b)],
            "unattributed_pct": sum(c["unattributed_pct"] for c in coverage.values())}


def markdown(r):
    out = ["| Issuer | Direct | Through funds | True weight | Carried by |", "|---|---|---|---|---|"]
    out += [f"| {row['name']} | {row['direct_pct']:.2f}% | {row['through_pct']:.2f}% | {row['total_pct']:.2f}% | "
            + (", ".join(f"{fund} {w:.2f}%" for fund, w in row["via"].items()) or "direct only") + " |" for row in r["look_through"][:10]]
    out += [""] + [f"Fund {fund}: {c['rows']} constituent rows as of {c['as_of'] or 'n/a'}, covering {c['listed_pct']:.1f}% of the fund."
                   for fund, c in r["fund_coverage"].items()]
    if r["fund_coverage"]:
        out.append(f"{r['unattributed_pct']:.1f}% of the portfolio sits in fund holdings that were not returned, so every true weight is a floor.")
    labels = {"pe_ttm": "P/E (weighted harmonic)", "roic_pct": "ROIC %", "fcf_yield_pct": "FCF yield %",
              "dividend_yield_pct": "Dividend yield %", "share_count_change_1y_pct": "1Y share count change %"}
    if any(v["value"] is not None for v in r["quality"].values()):
        out += ["", "| Weighted average | Value | Portfolio weight covered |", "|---|---|---|"]
        out += [f"| {labels[k]} | " + ("n/a" if v["value"] is None else f"{v['value']:.2f}") + f" | {v['weight_covered_pct']:.1f}% |" for k, v in r["quality"].items()]
    if r["risk"]:
        def pct(value, signed=False):
            return "n/a" if value is None else f"{value:+.1f}%" if signed else f"{value:.1f}%"
        out += ["", "| Holding | Window | Days | Price return | Max drawdown | Annualized volatility | vs. benchmark |", "|---|---|---|---|---|---|---|"]
        out += [f"| {k} | {v['from']} to {v['to']} | {v['days']} | {pct(v['return_pct'], True)} | {pct(v['max_drawdown_pct'])} | "
                f"{pct(v['volatility_pct'])} | {pct(v.get('vs_benchmark_pct'), True)} |" for k, v in r["risk"].items()]
    if r["correlations"]:
        keys = r["correlation_keys"]
        table = {(c["a"], c["b"]): c for c in r["correlations"]}
        out += ["", "| Correlation | " + " | ".join(keys) + " |", "|---|" + "---|" * len(keys)]
        for a in keys:
            cells = []
            for b in keys:
                c = table.get((a, b)) or table.get((b, a))
                cells.append("1" if a == b else "n/a" if c is None or c["r"] is None else f"{c['r']:.3f}")
            out.append(f"| {a} | " + " | ".join(cells) + " |")
    out += [""] + [f"- {flag}" for flag in r["flags"]]
    if r["weights_rescaled"]:
        out.append("- Weights did not sum to 100% and were rescaled.")
    return "\n".join(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    with open(sys.argv[1]) as handle:
        result = run(json.load(handle))
    print(json.dumps(result, indent=1) if "--json" in sys.argv else markdown(result))

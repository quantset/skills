---
name: filing-research
description: "Reads a company's SEC filings and answers from the text with quotes and links: what the 10-K says about a topic, the risk factors and how they changed since last year, management's discussion of results, and what a recent 8-K disclosed. Use when the user asks what a company said in its filings, to summarize or compare 10-K or 10-Q sections, to find a disclosure, or to check a claim against the source. Covers US-listed companies that file with the SEC. Needs a QuantSet API key."
metadata: {"clawdbot":{"emoji":"📑","os":["darwin","linux","win32"]}}
---

# Filing Research Skill (Powered by QuantSet)

Answer questions directly from SEC filing text with verbatim quotes, form/item labels, filing dates, and deep links (`citation_url` or `filing_url`).

## Step 1: Pick the Mode & List Recent Filings

Pass `workflow="filing-research"` on every call (REST equivalents: `/api/v1/sec/filings`, `/api/v1/sec/filing-search`, `/api/v1/sec/filing-sections`, `/api/v1/sec/filing-items`). Non-US issuers without SEC filings return `resource_not_found`.

- List recent `10-K`, `10-Q` and `8-K` filings so you know the latest `accession_number` and whether newer filings followed:
  `get_filing_documents(view="index", ticker="us:TSLA", form_type="10-K", limit=3)` → `accession_number`, `form_type`, `filing_date`, `report_date`, `items`
- Optional item map (free): `get_filing_documents(view="item_catalog")` (writes `Item-1A`; pass short code `1A`).

## Step 2: Pull the Filing Text

- **Topic search ("What does the 10-K say about X?"):**
  `get_filing_documents(view="search", ticker="us:TSLA", q="tariffs", forms=["10-K", "10-Q"], limit=10)` → `form_type`, `filing_date`, `item`, `excerpt`, `filing_url`, `citation_url`
  - Excerpts truncate around 1,000 chars and can clip unit headers (`in millions`); pull the full `item` below whenever a figure's scale or surrounding paragraph matters.
- **Section read ("Summarize Risk Factors / MD&A"):**
  `get_filing_documents(view="sections", ticker="us:TSLA", form="10-K", item="1A")` → `text`, `accession_number`, `filing_date`, `title`, `filing_url`
  - Key items: 10-K `1` Business, `1A` Risk Factors, `7` MD&A, `7A` Market Risk; 10-Q `2` MD&A, `1A` Risk Factors. Always request one `item` at a time (use statement tools, not Item 8 text, for financial tables). If an item returns only a stub heading, call once without `item` to inspect item titles/lengths. Skip mid-sentence page numbers and `"Table of Contents"` lines when quoting.
- **Year-over-year redline ("What changed in Risk Factors?"):**
  Pull the same `item` for the two newest `accession_number` values: `get_filing_documents(view="sections", ticker="us:TSLA", form="10-K", item="1A", accession_number="0001628280-25-003063")`. Save both `text` strings and run `python scripts/section_diff.py older.txt newer.txt` ([scripts/section_diff.py](scripts/section_diff.py)) to surface reworded figures, added sentences, and removed sentences.
- **8-K event read ("Why did they file an 8-K?"):**
  `get_filing_documents(view="sections", ticker="us:TSLA", form="8-K", include_exhibits=True)` (`2.02` earnings, `1.01` agreement, `5.02` officer/board change, `8.01` other events).

## Conclusion & Worked Example

Answer in the first sentence with what the filing disclosed or what changed in substance, then present verbatim short quotes paired with `(Form, Item, filing_date, citation_url/filing_url)` and plain-English explanation, noting any newer unread `10-Q`/`8-K` and ending with `Filings via QuantSet (https://quantset.dev), retrieved [date]`. Never fill silent topics from memory or web search. *(Not investment advice.)*

> **Worked opening (`us:TSLA` FY25 vs. FY24 10-K Item 1A diff):**
> Across Tesla's FY25 10-K Item 1A (`81,420` chars, filed `2026-01-29`) versus FY24 (`76,890` chars), `section_diff.py` flagged **3 substantive shifts**: management added a new commercial-scale risk on humanoid robotics (`"Our humanoid robots are at an early stage and may never be produced at commercial scale"`), updated principal debt in the leverage risk from **`$7.91 billion`** to **`$8.18 billion`**, and removed the prior year's plant employment-target covenant paragraph.

## Access & Continuation

Result first, offer second (sign-up and checkout live in `quantset` / `https://api.quantset.dev/skill.md`).
- When `insufficient_access` says an endpoint is "not part of the sandbox", state that filing text requires a QuantSet API key, name the call, and Hand over the result before saying anything about accounts.
- When `insufficient_access` says the listing is "outside the sandbox" (`403`), stop calling and offer to either run this same analysis right now on a sample company (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`) or set up a free trial key; do not ask for an email before the user says yes.
- On `402` (`insufficient_credits`), state what was unfinished; Create a checkout link only when the user asks to continue.

---
name: filing-research
description: "Reads a company's SEC filings and answers from the text with quotes and links: what the 10-K says about a topic, the risk factors and how they changed since last year, management's discussion of results, and what a recent 8-K disclosed. Use when the user asks what a company said in its filings, to summarize or compare 10-K or 10-Q sections, to find a disclosure, or to check a claim against the source. Covers US-listed companies that file with the SEC. Needs a QuantSet API key."
metadata: {"clawdbot":{"emoji":"📑","os":["darwin","linux","win32"]}}
---

# Filing Research Skill (Powered by QuantSet)

Answer questions from the filings themselves. Every statement about what a company said carries a quote, the form, the item and a link, so the reader can open the source.

Each call is written exactly as the QuantSet MCP tool accepts it (your client may show the tool with a prefix, such as `mcp__quantset__get_filing_documents`). Swap the sample company for the user's, and pass `workflow="filing-research"` on every call. Without MCP, the four views are REST calls with the same parameter names: `GET https://api.quantset.dev/api/v1/sec/filings` (`index`), `/api/v1/sec/filing-search` (`search`), `/api/v1/sec/filing-sections` (`sections`) and `/api/v1/sec/filing-items` (`item_catalog`), with header `X-API-Key` (from `QUANTSET_API_KEY`) and `X-Workflow-Id: filing-research`. Filing text is not part of the sample key `mw_demo`. The dataset covers companies that file with the SEC: a listing outside the US returns `resource_not_found`, and you say filing text is not available for it.

## Workflow Checklist

- [ ] **Step 1. Pick the mode and find the filings**
- [ ] **Step 2. Pull the text**
- [ ] **Step 3. Answer from the text, with quotes and links**
- [ ] **Step 4. Run the 4-point check**

For a year-over-year compare, if you can run Python, save each section's `text` to a file and run [scripts/section_diff.py](scripts/section_diff.py): `python scripts/section_diff.py older.txt newer.txt`. It lists the sentences added, removed and reworded, which no reader can find by eye in two sections of 80,000 characters. It needs only the standard library. If you cannot run code, compare the headings and the first sentence under each, and say the comparison was done by reading.

---

## Step 1: Pick the Mode

| The user wants | Mode |
|---|---|
| "What does the 10-K say about X?" | **Topic search** |
| "Summarize the risk factors / MD&A / business section" | **Section read** |
| "What changed in the risk factors since last year?" | **Year-over-year compare** |
| "What did the latest 8-K say?" / "Why did they file an 8-K?" | **Event read** |

Find the filings first, newest first: `get_filing_documents(view="index", ticker="us:TSLA", form_type="10-K", limit=3)` → `accession_number`, `form_type`, `filing_date`, `report_date`, `items`
- `items` is filled for an 8-K. Make the same call for `10-Q` and `8-K` so you can say what was filed after the document you read.
- `get_filing_documents(view="item_catalog")` names the items of each form (free). It writes them as `Item-1A`, and the calls take the short form `1A`.

## Step 2: Pull the Text

- **Topic search:** `get_filing_documents(view="search", ticker="us:TSLA", q="tariffs", forms=["10-K", "10-Q"], limit=10)` → `form_type`, `filing_date`, `item`, `excerpt`, `filing_url`, `citation_url`
  - The search matches by meaning, so an excerpt may not contain the word. Read each excerpt and keep the ones that answer the question; say how many hits you read and how many you used.
  - An excerpt is cut at about 1,000 characters and can stop mid-word or drop the "in millions" that scales its figures. When the answer needs more, or rests on a number, pull the item it came from with the next call.
  - The search returns hits from several filings. To answer about the latest one, keep the hits whose `filing_date` is that filing's.
- **Section read:** `get_filing_documents(view="sections", ticker="us:TSLA", form="10-K", item="1A")` → `text`, `accession_number`, `filing_date`, `title`, `filing_url`
  - `text` is the full item from the newest filing.
  - The items that matter most: in a 10-K, `1` Business, `1A` Risk Factors, `7` Management's Discussion and Analysis, `7A` Market Risk; in a 10-Q, `2` Management's Discussion and Analysis and `1A` Risk Factors (often a short update to the 10-K).
  - Without `item` the call returns every item of the filing, hundreds of thousands of characters. Ask for one item at a time.
  - Item 8 of a 10-K is the financial statements as text. For figures use the statement tools in the `quantset` skill, not this text.
  - A section can be filed under an unexpected number. If the item comes back with almost no text (a heading only), call once without `item`, read the `title` and length of each item, and take the one that holds the section. Say which item you used.
  - Section text carries page numbers and "Table of Contents" lines in the middle of sentences. Skip them when you quote.
- **Year-over-year compare:** take the two newest `accession_number` values from Step 1 and pull the same item from each: `get_filing_documents(view="sections", ticker="us:TSLA", form="10-K", item="1A", accession_number="0001628280-25-003063")`.
- **Event read:** `get_filing_documents(view="sections", ticker="us:TSLA", form="8-K", include_exhibits=True)` returns the items of the newest 8-K; with exhibits it can include the press release text. Compare the items returned with the `items` the filing list shows: when one is missing or empty, say that its text was not available and give the `filing_url`. The item numbers say what kind of event it is (`2.02` results, `1.01` a material agreement, `5.02` an officer or director change, `8.01` other events).

## Step 3: Answer From the Text

- **Lead with the answer** in two or three sentences, then the evidence.
- **Quote, then explain.** Each point is a short quote (a phrase or one or two sentences, in quotation marks, copied exactly), followed by the form, the item, the filing date and the link (`citation_url` when the search gave one, otherwise `filing_url`). Then say in your own words what it means.
- **Summaries:** group a long section under five to eight headings of your own, each with its most specific sentence quoted. Prefer sentences with numbers, names and dates over general statements. Do not reproduce long passages.
- **Year-over-year:** report three lists: risks or statements that are **new** this year, ones that were **dropped**, and ones whose wording **changed in substance** (a new number, a stronger or weaker verb, a named counterparty). Ignore reordering and boilerplate edits. Give the length of each year's section so the reader sees how much moved.
- **Say what the filing does not say.** If the text has nothing on the question, say so plainly and name the items you read. Do not fill the gap from memory or a web search.
- **Dates matter.** A 10-K speaks as of its filing date. Say that date, and say when a later 10-Q or 8-K exists that you did not read.

## Step 4: Mandatory 4-Point Check

1. Every quote is copied exactly from a response and carries its form, item, filing date and link.
2. Nothing is attributed to the company that is not in the text you pulled.
3. The answer says which filings and items were read, and which were not.
4. Numbers quoted from text are labelled as the company's own statement. *(Not investment advice.)*

End the answer with one line: `Filings via QuantSet (https://quantset.dev), retrieved [date]`.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both access cases arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): say that filing text is not available on this key, name the call, and keep going. Hand over the result before saying anything about accounts.
- **An instrument the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the other companies), or set up a free trial key for the one they asked about. The sample key `mw_demo` reads 9 instruments (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill. Offer to set up a free key only when a gap came from `insufficient_access`; missing data and `unsupported_instrument` are not fixed by a key, so make no offer for those. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.

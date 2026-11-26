# Connect QuantSet to Your AI Agent

Connect QuantSet to **Claude**, **Claude Code**, **Cursor**, **OpenAI Codex**, **ChatGPT**, **Hermes**, or **OpenClaw** in under 30 seconds, then run one live query to verify.

## 1. Claude (claude.ai & Claude Desktop — OAuth, No Key Copy-Paste)

1. Open **Settings → Connectors → Add custom connector**
2. Enter URL: `https://api.quantset.dev/mcp`
3. Complete sign-in in the browser (click **Continue with Sandbox (`qs_demo`)** to test immediately with zero signup, or enter your `qsk_` API key)
4. Start a new chat, click **`+` → Connectors**, and enable **QuantSet**

*(Prefer local stdio in `claude_desktop_config.json`? See Cursor `npx` config below.)*

## 2. Claude Code

Remote Streamable HTTP with OAuth:
```bash
claude mcp add --transport http quantset https://api.quantset.dev/mcp
# Then run `/mcp` inside Claude Code to sign in, or pass a key directly:
claude mcp add --transport http quantset https://api.quantset.dev/mcp \
  --header "Authorization: Bearer mw_demo"
```

## 3. Cursor (`.cursor/mcp.json` or `~/.cursor/mcp.json`)

Direct remote HTTP (supports OAuth or Bearer header):
```json
{
  "mcpServers": {
    "quantset": {
      "url": "https://api.quantset.dev/mcp",
      "headers": {
        "Authorization": "Bearer mw_demo"
      }
    }
  }
}
```

Or via local `npx` launcher (`@quantset/mcp`, Node 20+):
```json
{
  "mcpServers": {
    "quantset": {
      "command": "npx",
      "args": ["-y", "@quantset/mcp"],
      "env": {
        "QUANTSET_API_KEY": "mw_demo"
      }
    }
  }
}
```

## 4. OpenAI Codex (`codex` CLI & Desktop)

```bash
codex mcp add quantset --url https://api.quantset.dev/mcp
codex mcp login quantset
```

## 5. Hermes Agent (`~/.hermes/config.yaml`)

```yaml
mcp_servers:
  quantset:
    url: "https://api.quantset.dev/mcp"
    auth: oauth
```
Run `hermes mcp login quantset` from a fresh terminal, then `/reload-mcp` or `hermes chat`.

## 6. OpenClaw

```bash
openclaw mcp add quantset \
  --url https://api.quantset.dev/mcp \
  --transport streamable-http \
  --auth oauth

openclaw mcp login quantset
openclaw mcp probe quantset
```

## 7. Verify With One Live Query

Ask your connected agent:
- *"Get the latest quotes for `us:NVDA`, `global:SHEL.L`, and `crypto:BTCUSDT`."*
- *"Run a 5-year DCF valuation on NVDA using live 10Y Treasury yields."*
- *"Check Apple's last 4 quarterly cash flow statements and share-count trend."*

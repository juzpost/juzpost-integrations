# LobeHub MCP Marketplace listing

LobeHub lists MCP servers at https://lobehub.com/mcp. Publishing goes through the `lhm` CLI (`npm i -g @lobehub/market-cli`, Node 22+) and needs a browser login (`lhm login`, OIDC) plus a GitHub OAuth connection (`lhm github connect`) by the repository owner. Machine credentials cannot publish, so this is an owner step.

`lhm.plugin.json` here is the draft manifest for the hosted JuzPost MCP server (`https://www.juzpost.com/mcp`, 19 tools, generated from `CF-JuzPostAPI/mcp.openapi.json`). The manifest must sit in the root of the repository that gets published; the natural home is `github.com/juzpost/juzpost-cli` (the public MCP implementation). Steps:

1. Copy `lhm.plugin.json` to the root of the juzpost-cli checkout, commit and push to main (the listing README is read from the default branch).
2. `lhm login`, then `lhm github connect`.
3. `lhm plugin publish https://github.com/juzpost/juzpost-cli`.
4. `lhm plugin list` to verify. Later updates: `lhm plugin update`.

Limits: 10 publish attempts per account per hour.

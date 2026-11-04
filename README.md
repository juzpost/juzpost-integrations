# juzpost-integrations

Third-party platform integrations for [JuzPost](https://www.juzpost.com), the social media scheduler. Each integration is a thin client over the public REST API at `https://www.juzpost.com/api/cli/v1` ([reference](https://api.juzpost.com/docs)). Nothing here runs inside JuzPost itself, and nothing here needs a change in the product to work.

| Folder | Platform | Status |
|---|---|---|
| [`make/`](make/) | [Make](https://www.make.com) custom app (14 modules, 3 RPCs) | built, needs first deploy + review |
| [`n8n/`](n8n/) | n8n community node `n8n-nodes-juzpost` (action node with 5 resources, polling trigger) | published: [n8n-nodes-juzpost@0.2.0](https://www.npmjs.com/package/n8n-nodes-juzpost) with provenance; verification pending at n8n |
| [`pipedream/`](pipedream/) | Pipedream components (7 actions, 2 polling sources) | written, PR waits on Pipedream creating the app (issue #22281) |
| [`lobehub/`](lobehub/) | LobeHub MCP Marketplace manifest for the hosted MCP server | draft, owner publishes with the lhm CLI |

## Why a separate repository

The JuzPost product repo is production code with its own release gates. These integrations are published to other companies' marketplaces, reviewed by their teams on their schedules, and versioned against their SDKs. Keeping them here means a marketplace review never blocks a product deploy, and a product change never has to wait for a marketplace to catch up. Each integration only talks to the versioned public API, so it keeps working as long as that API does.

## Authentication

Every integration uses a JuzPost API key. In the JuzPost dashboard open **Settings, General**, find the **API keys** card and choose **Generate API key**. The key starts with `jp_live_` and is shown once. It belongs to exactly one workspace, and every call acts on that workspace.

## Layout

```
make/            the Make app, in Make Apps SDK local-development layout
  makecomapp.json   manifest: components, code files, deployment origins
  general/          base (URL, auth header sanitising, error mapping)
  connections/      API-key connection
  modules/          one folder per module
  rpcs/             dynamic dropdowns (accounts, groups)
  test-scenarios/   blueprints used for the Make review run
n8n/             npm package n8n-nodes-juzpost (credentials/, nodes/JuzPost/)
pipedream/juzpost/  Pipedream app file, actions/, sources/ for a PR to PipedreamHQ/pipedream
lobehub/         lhm.plugin.json draft for the LobeHub MCP Marketplace
scripts/         generators and helpers
docs/            listing copy, test plan, review notes
```

## License

MIT. See [LICENSE](LICENSE).

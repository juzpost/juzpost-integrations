# n8n-nodes-juzpost

An [n8n](https://n8n.io) community node for [JuzPost](https://www.juzpost.com), the social media scheduler. Plan a month of content in one calendar and publish to YouTube, TikTok, Instagram, Facebook, X, LinkedIn, Pinterest, Threads, Bluesky, Tumblr and WordPress.

## Installation

In n8n open **Settings, Community Nodes**, choose **Install**, and enter `n8n-nodes-juzpost`. Or follow the [community nodes installation guide](https://docs.n8n.io/integrations/community-nodes/installation/).

## Credentials

Create a **JuzPost API** credential with an API key. In JuzPost open **Settings, General**, find the **API keys** card and choose **Generate API key**. The key starts with `jp_live_` and is shown once. One key belongs to one workspace.

## Nodes

**JuzPost** (action node, usable as an AI agent tool)

| Resource | Operations |
|---|---|
| Post | Create Draft, Update Draft, Delete Draft, Get, Get Many, Schedule, Smart Schedule |
| Media | Upload (binary in, media key out) |
| Account | Get Many (filter by platform or channel group) |
| Channel Group | Get, Get Many |
| Workspace | Get My Account, Get Workspace |

**JuzPost Trigger** (polling): emits a post each time it reaches a chosen status, for example posted or failed.

## Typical flow

1. **Media, Upload** with the binary from any node (HTTP Request, Google Drive, Dropbox). Returns a media key.
2. **Post, Create Draft** with the caption, type and media key. Returns the post ID.
3. **Post, Schedule** with the post ID, the accounts and a publish time. Leave the time empty to publish now.

Or create several drafts and let **Post, Smart Schedule** spread them over your preset posting times. Use **Dry Run** first to see the plan.

## Notes

- A post is a draft until it is scheduled. Scheduling needs at least 10 minutes of lead time and at most about 6 months.
- **Schedule** returns `success: false` with per-account `results` when some accounts failed. Inspect `results`.
- Uploads: videos up to 500 MB, images up to 15 MB. The binary's MIME type must match the file.
- The API creates at most 30 posts per hour per workspace through integrations.

## Resources

- [JuzPost REST API reference](https://api.juzpost.com/docs)
- [n8n community nodes documentation](https://docs.n8n.io/integrations/community-nodes/)

## License

MIT

# JuzPost for Make

Schedule and publish social media posts from your Make scenarios. One draft, up to ten accounts, across YouTube, TikTok, Instagram, Facebook, X, LinkedIn, Pinterest, Threads, Bluesky, Tumblr and WordPress.

## Connection

Create a connection with a JuzPost API key. In JuzPost open **Settings, General**, find the **API keys** card and choose **Generate API key**. The key starts with `jp_live_` and is shown once at creation. Revoke it from the same card.

## Typical flow

1. **Upload a Media File** with the file data from any Make module (HTTP, Google Drive, Dropbox, ...). It returns a **Media Key**.
2. **Create a Draft Post** with the caption, the post type and the media keys. It returns a **Post ID**.
3. **Schedule a Post** with the post ID, the accounts and a publish time. Leave the time empty to publish right away.

Or create several drafts and let **Smart Schedule Posts** spread them over your preset posting times. Run it with **Dry Run** on first to see the plan.

## Modules

**Posts:** Create a Draft Post, Upload a Media File, Schedule a Post, Smart Schedule Posts, Get a Post, Update a Draft Post, Delete a Draft Post, List Posts.

**Triggers:** Watch Posts (polls for posts that reached a status, such as posted or failed).

**Accounts:** List Connected Accounts, List Channel Groups, Get a Channel Group, Get My Account.

**Other:** Make an API Call, for anything in the [REST reference](https://api.juzpost.com/docs) that has no module yet.

## Notes

- A post is a draft until it is scheduled. Scheduling needs at least 5 minutes of lead time and at most about 6 months.
- **Schedule a Post** returns HTTP 200 even when some accounts failed. Check each entry in **Results**.
- Uploads: videos up to 500 MB, images up to 15 MB, 20 uploads per minute. The **Content Type** must match the file.
- The API creates at most 30 posts per hour per workspace through integrations.
- Plan limits apply. **Get My Account** lists the **Blocked Reasons** before you attempt a write.

Support: support@juzpost.com

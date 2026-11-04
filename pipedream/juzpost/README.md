# JuzPost components for Pipedream

[JuzPost](https://www.juzpost.com) is a social media scheduler: plan a month of content in one calendar and publish to YouTube, TikTok, Instagram, Facebook, X, LinkedIn, Pinterest, Threads, Bluesky, Tumblr and WordPress.

These components follow the [Pipedream component guidelines](https://pipedream.com/docs/components/contributing/guidelines) and are meant for a pull request to `PipedreamHQ/pipedream` under `components/juzpost/`, once the JuzPost app exists in Pipedream's registry (requested in [PipedreamHQ/pipedream#22281](https://github.com/PipedreamHQ/pipedream/issues/22281)). The app's auth field is assumed to be `api_key` (a JuzPost API key from Settings, General, API keys; sent as `Authorization: Bearer`).

Actions: Create Draft Post, Upload Media, Schedule Post, Smart Schedule Posts, Get Post, List Posts, List Connected Accounts.
Sources (polling): Post Published, Post Failed.

Typical flow: Upload Media → Create Draft Post → Schedule Post. Or several drafts → Smart Schedule Posts (dry run first).

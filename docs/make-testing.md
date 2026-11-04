# Make app: first deploy and test plan

The app was written from the Make Custom Apps documentation and the JuzPost OpenAPI spec without a Make developer account, so the first deploy is also the first run. Work through this list in order.

## 1. Create the app in Make

1. In Make open **Custom apps** and create a new app: name `juzpost` (internal, cannot change), label `JuzPost`, description `Schedule and publish social media posts to 11 platforms from one calendar.`, theme `#7C3AED`, language English.
2. Upload the logo: `assets/juzpost-make-logo.png` (512 x 512, icon on the brand violet). Make shows it inside a rounded square, so keep margins.
3. Note the app ID Make assigns (it may be `juzpost` or `juzpost-xxxxxx`).

## 2. Deploy from this repo

**Option A, one command (no VS Code needed).** In Make click your avatar, Profile, API, Add token, with the scopes `sdk-apps:read` and `sdk-apps:write`. Save the token as `.secrets/make-apikey` at the repo root (gitignored). Then:

```
MAKE_ZONE=eu2 python3 scripts/deploy_make.py --dry-run   # prints the plan
MAKE_ZONE=eu2 python3 scripts/deploy_make.py             # creates the app and every component
```

Use the zone from your Make URL (`eu1`, `eu2`, `us1`, `us2`). The script creates the app itself if it does not exist, so step 1 above is only needed when you prefer to create it by hand. Re-running updates everything in place. Make appends a random suffix to the app name (ours is `juzpost-k2gkrv`) and reuses it for the connection; both are recorded in `make/.deploy-state.json`, which is committed. Deployed to zone us2 on 2026-11-04.

**Option B, VS Code extension.**

1. Install the **Make Apps Editor** VS Code extension and open this repository.
2. Create `.secrets/make-apikey` at the repo root with a Make API token that has the custom-apps scopes (`apps:read`, `apps:write`). The folder is gitignored.
3. In `make/makecomapp.json` set `origins[0].appId` to the ID from step 1 and `baseUrl` to your zone's API (`https://eu1.make.com/api`, `https://eu2.make.com/api`, `https://us1.make.com/api`, ...).
4. Right-click `makecomapp.json` and choose **Deploy to Make**. For every unpaired component choose **Deploy as new remote** (use "apply for all").
5. The extension may rewrite `makecomapp.json` with an `idMapping` block. Commit that.

## 3. Things to verify on first run

These are the assumptions that could not be checked without a Make account. Each is isolated to one file.

| Assumption | Where | If wrong |
|---|---|---|
| Base `headers` is not needed for auth because every module sets `Authorization` itself. This keeps the bearer token off the presigned storage PUT. | every `*.communication.iml.json` | Nothing to do; this is the safe direction. |
| An unset optional parameter resolves to `undefined` and the key is dropped from the JSON body. | `createPost`, `updatePost`, `schedulePost`, `smartSchedule` | Wrap each optional with `{{if(parameters.x, parameters.x)}}` or the API will reject `""`. |
| `length(parameters.data)` returns the byte length of a buffer. | `uploadMedia` presign body | Make **File Size (bytes)** required instead of advanced. |
| `"type": "binary"` with `"body": "{{parameters.data}}"` sends raw bytes on the PUT. | `uploadMedia` second request | Documented by Make's own presign example; if storage returns 403, compare `Content-Type` and length. |
| `{{temp.signedUrl}}` as an absolute `url` is not prefixed with `baseUrl`. | `uploadMedia` second request | Documented: a full URL is used as is. |
| The `"{{...}}"` header spread in the universal module merges user headers with the auth header. | `makeApiCall` | Copy Make's own "Make an API call" template from any approved app. |
| `response.trigger` with `type: date` on `updatedAt` dedupes correctly for the polling trigger. | `watchPosts` | Switch to `type: id` with `order: desc`. |
| `formatDate(parameters.startDate, 'YYYY-MM-DD')` formats in the scenario's timezone. | `smartSchedule` | Add the workspace timezone as the third argument. |
| `makecomapp.json` code-file keys (`staticParams`, `mappableParams`, `interface`, `samples`, `scope`) match the extension's expected names. | `makecomapp.json` | The extension reports the key it expects on first deploy; rename in `scripts/gen_make_app.py` and regenerate. |

## 4. Scenario smoke test

Use a throwaway JuzPost workspace with one connected account.

1. **Get My Account** returns the workspace and an empty `blocked` list.
2. **List Connected Accounts** returns the account; the dropdown in **Schedule a Post** shows `platform · username`.
3. **HTTP, Get a file** on a small PNG, then **Upload a Media File** with content type `image/png`. Expect a media key under your workspace prefix.
4. **Create a Draft Post** type Image with that key. Expect a post ID.
5. **Schedule a Post** 10 minutes ahead. Expect `success: true` and one `scheduled` result.
6. **Get a Post**: `targets[0].status` is `scheduled`.
7. **Watch Posts** with status `scheduled`: the post appears once and not again on the next poll.
8. **Delete a Draft Post** on a second draft. Expect `deleted: true`.
9. **Smart Schedule Posts** with `dryRun` on and one draft. Expect a plan and no timers.

## 5. Submit for review

Make reviews custom apps before they are public. The listing copy is in `docs/make-listing.md`. Requirements that matter for approval: every module has a description, interface and sample; the connection validates the key; no secrets in `common`; the universal module is named "Make an API Call".

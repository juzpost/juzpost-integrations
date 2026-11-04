#!/usr/bin/env python3
"""Generate the JuzPost Make app under <repo>/make from one Python description.

Why a generator: Make's app format is ~60 small IMLJSON files that must agree on
names, parameters, interfaces and samples. One source keeps them consistent.
Run:  python3 -I gen_make_app.py /path/to/juzpost-integrations
"""
import json, os, sys

ROOT = sys.argv[1]
APP = os.path.join(ROOT, "make")
AUTH = {"Authorization": "Bearer {{connection.apiKey}}"}
PAGE = {"limit": 20, "nextCursor": None, "hasMore": False}

def w(path, data, raw=False):
    full = os.path.join(APP, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        if raw:
            f.write(data)
        else:
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.write("\n")

# ---------------------------------------------------------------- shared specs
ACCOUNT_IF = [
    {"name": "id", "type": "text", "label": "Account ID"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "platform", "type": "text", "label": "Platform"},
    {"name": "avatarUrl", "type": "url", "label": "Avatar URL"},
    {"name": "isActive", "type": "boolean", "label": "Is Active"},
    {"name": "createdAt", "type": "date", "label": "Connected At"},
]
ACCOUNT_SAMPLE = {
    "id": "0f1c2d3e-4a5b-4c6d-8e9f-0a1b2c3d4e5f", "username": "juzpost",
    "platform": "instagram", "avatarUrl": "https://cdn.juzpost.com/brand/icon.png",
    "isActive": True, "createdAt": "2026-09-01T10:00:00.000Z",
}
GROUP_IF = [
    {"name": "id", "type": "text", "label": "Group ID"},
    {"name": "name", "type": "text", "label": "Name"},
    {"name": "accountIds", "type": "array", "label": "Account IDs", "spec": {"type": "text", "label": "Account ID"}},
    {"name": "accountCount", "type": "uinteger", "label": "Account Count"},
    {"name": "createdAt", "type": "date", "label": "Created At"},
]
GROUP_SAMPLE = {
    "id": "6b7c8d9e-0f1a-4b2c-9d3e-4f5a6b7c8d9e", "name": "all-shorts",
    "accountIds": ["0f1c2d3e-4a5b-4c6d-8e9f-0a1b2c3d4e5f"], "accountCount": 1,
    "createdAt": "2026-09-01T10:05:00.000Z",
}
POST_LIST_IF = [
    {"name": "id", "type": "text", "label": "Post ID"},
    {"name": "status", "type": "text", "label": "Status"},
    {"name": "type", "type": "text", "label": "Type"},
    {"name": "title", "type": "text", "label": "Title"},
    {"name": "content", "type": "text", "label": "Content"},
    {"name": "mediaUrls", "type": "array", "label": "Media Keys", "spec": {"type": "text", "label": "Media Key"}},
    {"name": "scheduledFor", "type": "date", "label": "Scheduled For"},
    {"name": "coverR2Key", "type": "text", "label": "Cover Key"},
    {"name": "createdAt", "type": "date", "label": "Created At"},
    {"name": "updatedAt", "type": "date", "label": "Updated At"},
]
POST_LIST_SAMPLE = {
    "id": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d", "status": "scheduled", "type": "video",
    "title": "Three edits that stop the scroll", "content": "Three edits that stop the scroll in the first second.",
    "mediaUrls": ["ws_abc123/media/clip_03.mp4"], "scheduledFor": "2026-11-10T14:00:00.000Z",
    "coverR2Key": None, "createdAt": "2026-11-04T09:00:00.000Z", "updatedAt": "2026-11-04T09:30:00.000Z",
}
TARGET_IF = [
    {"name": "socialAccountId", "type": "text", "label": "Account ID"},
    {"name": "platform", "type": "text", "label": "Platform"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "status", "type": "text", "label": "Status"},
    {"name": "publishAt", "type": "date", "label": "Publish At"},
    {"name": "publishedAt", "type": "date", "label": "Published At"},
    {"name": "error", "type": "text", "label": "Error"},
    {"name": "link", "type": "url", "label": "Link"},
]
TARGET_SAMPLE = {
    "socialAccountId": "0f1c2d3e-4a5b-4c6d-8e9f-0a1b2c3d4e5f", "platform": "instagram",
    "username": "juzpost", "status": "scheduled", "publishAt": "2026-11-10T14:00:00.000Z",
    "publishedAt": None, "error": None, "link": None,
}
POST_IF = POST_LIST_IF[:5] + [
    {"name": "mediaUrls", "type": "array", "label": "Media Keys", "spec": {"type": "text", "label": "Media Key"}},
    {"name": "coverR2Key", "type": "text", "label": "Cover Key"},
    {"name": "scheduledFor", "type": "date", "label": "Scheduled For"},
    {"name": "metadata", "type": "collection", "label": "Metadata", "spec": [
        {"name": "title", "type": "text", "label": "Title"},
        {"name": "description", "type": "text", "label": "Description"},
        {"name": "hashtags", "type": "array", "label": "Hashtags", "spec": {"type": "text", "label": "Hashtag"}},
        {"name": "source", "type": "text", "label": "Source"},
        {"name": "client", "type": "text", "label": "Client"},
    ]},
    {"name": "socialAccountIds", "type": "array", "label": "Account IDs", "spec": {"type": "text", "label": "Account ID"}},
    {"name": "targets", "type": "array", "label": "Targets", "spec": TARGET_IF},
    {"name": "createdAt", "type": "date", "label": "Created At"},
    {"name": "updatedAt", "type": "date", "label": "Updated At"},
]
POST_SAMPLE = {
    **{k: POST_LIST_SAMPLE[k] for k in ["id", "status", "type", "title", "content", "mediaUrls", "coverR2Key", "scheduledFor"]},
    "metadata": {"title": "Three edits that stop the scroll", "description": "", "hashtags": ["editing", "shorts"], "source": "connector", "client": "make"},
    "socialAccountIds": ["0f1c2d3e-4a5b-4c6d-8e9f-0a1b2c3d4e5f"],
    "targets": [TARGET_SAMPLE],
    "createdAt": "2026-11-04T09:00:00.000Z", "updatedAt": "2026-11-04T09:30:00.000Z",
}
HASHTAGS_PARAM = {
    "name": "hashtags", "type": "array", "label": "Hashtags",
    "help": "Without the leading #. Stored in the post's metadata.",
    "spec": {"type": "text", "label": "Hashtag"}, "labels": {"add": "Add a hashtag"},
}
POST_TYPE_PARAM = {
    "name": "type", "type": "select", "label": "Post Type", "default": "text",
    "help": "Anything other than Text and Blog must have at least one media key before it can be scheduled. Blog is a WordPress post: Title is required and Description is the body.",
    "options": [
        {"label": "Text", "value": "text"}, {"label": "Image", "value": "image"},
        {"label": "Video", "value": "video"}, {"label": "Story", "value": "story"},
        {"label": "Blog (WordPress)", "value": "blog"},
    ],
}
LIMIT_PARAM = {
    "name": "limit", "type": "uinteger", "label": "Limit", "default": 20, "required": True,
    "help": "Maximum number of results to return and work with during one execution cycle.",
}
ACCOUNTS_SELECT = {
    "name": "socialAccountIds", "type": "select", "label": "Social Accounts", "required": True,
    "multiple": True, "options": "rpc://listAccounts", "validate": {"minItems": 1, "maxItems": 10},
    "help": "Between one and ten connected accounts. Pick from the list or map account IDs from List Connected Accounts.",
}

def paginated(url, qs, output="{{item}}"):
    return {
        "url": url, "method": "GET", "headers": AUTH, "qs": qs,
        "response": {"iterate": "{{body.data}}", "output": output, "limit": "{{parameters.limit}}"},
        "pagination": {"condition": "{{body.pagination.hasMore}}", "qs": {"cursor": "{{body.pagination.nextCursor}}"}},
    }

# ---------------------------------------------------------------- modules
MODULES = {}

def module(name, label, description, kind, crud, communication, mappable=None, static=None, interface=None, samples=None):
    MODULES[name] = dict(label=label, description=description, moduleType=kind, actionCrud=crud,
                        communication=communication, mappableParams=mappable or [],
                        staticParams=static or [], interface=interface or [], samples=samples or {})

module("getMyAccount", "Get My Account",
       "Returns the user, workspace, plan, entitlements, quotas and the reasons a write would be refused. Call it first in a new scenario.",
       "action", "read",
       {"url": "/me", "method": "GET", "headers": AUTH, "response": {"output": "{{body}}"}},
       interface=[
           {"name": "user", "type": "collection", "label": "User", "spec": [
               {"name": "id", "type": "text", "label": "User ID"}, {"name": "email", "type": "email", "label": "Email"}]},
           {"name": "credential", "type": "collection", "label": "Credential", "spec": [
               {"name": "type", "type": "text", "label": "Type"},
               {"name": "scopes", "type": "array", "label": "Scopes", "spec": {"type": "text", "label": "Scope"}},
               {"name": "expiresAt", "type": "date", "label": "Expires At"}]},
           {"name": "workspace", "type": "collection", "label": "Workspace", "spec": [
               {"name": "id", "type": "text", "label": "Workspace ID"}, {"name": "name", "type": "text", "label": "Name"},
               {"name": "slug", "type": "text", "label": "Slug"}, {"name": "role", "type": "text", "label": "Role"},
               {"name": "timezone", "type": "text", "label": "Timezone"},
               {"name": "defaultTimes", "type": "array", "label": "Default Posting Times", "spec": {"type": "text", "label": "HH:MM"}}]},
           {"name": "plan", "type": "collection", "label": "Plan", "spec": [
               {"name": "id", "type": "text", "label": "Plan ID"}, {"name": "name", "type": "text", "label": "Name"},
               {"name": "trialActive", "type": "boolean", "label": "Trial Active"}]},
           {"name": "billing", "type": "collection", "label": "Billing", "spec": []},
           {"name": "entitlements", "type": "collection", "label": "Entitlements", "spec": []},
           {"name": "quotas", "type": "collection", "label": "Quotas", "spec": []},
           {"name": "limits", "type": "collection", "label": "Limits", "spec": []},
           {"name": "blocked", "type": "array", "label": "Blocked Reasons", "spec": {"type": "text", "label": "Reason"}},
       ],
       samples={
           "user": {"id": "9c8b7a6d-5e4f-4a3b-8c2d-1e0f9a8b7c6d", "email": "maker@example.com"},
           "credential": {"type": "api_key", "scopes": ["read", "create", "edit", "admin"], "expiresAt": None},
           "workspace": {"id": "2d3e4f5a-6b7c-4d8e-9f0a-1b2c3d4e5f6a", "name": "JuzPost Studio", "slug": "juzpost-studio",
                         "role": "owner", "timezone": "Asia/Kolkata", "defaultTimes": ["09:00", "13:00", "18:00"]},
           "plan": {"id": "growth", "name": "Growth", "trialActive": False},
           "billing": {}, "entitlements": {}, "quotas": {}, "limits": {}, "blocked": [],
       })

module("listAccounts", "List Connected Accounts",
       "Returns the connected social accounts. Their IDs are what Schedule a Post takes.",
       "search", None,
       paginated("/accounts", {"platform": "{{parameters.platform}}", "groupId": "{{parameters.groupId}}",
                                "sort": "{{parameters.sort}}", "order": "{{parameters.order}}", "limit": 100}),
       mappable=[
           {"name": "platform", "type": "select", "label": "Platform", "help": "Only accounts on this network.",
            "options": [{"label": p.capitalize() if p != "x" else "X", "value": p} for p in
                        ["youtube", "tiktok", "instagram", "facebook", "x", "linkedin", "pinterest", "threads", "bluesky", "tumblr", "wordpress"]]},
           {"name": "groupId", "type": "select", "label": "Channel Group", "options": "rpc://listGroups",
            "help": "Only accounts that belong to this channel group."},
           {"name": "sort", "type": "select", "label": "Sort By", "default": "createdAt", "advanced": True,
            "options": [{"label": "Connected At", "value": "createdAt"}, {"label": "Username", "value": "username"}, {"label": "Platform", "value": "platform"}]},
           {"name": "order", "type": "select", "label": "Order", "default": "desc", "advanced": True,
            "options": [{"label": "Descending", "value": "desc"}, {"label": "Ascending", "value": "asc"}]},
           LIMIT_PARAM,
       ],
       interface=ACCOUNT_IF, samples=ACCOUNT_SAMPLE)

module("listGroups", "List Channel Groups",
       "Returns the named bundles of accounts. A group name is what Smart Schedule Posts takes.",
       "search", None,
       paginated("/groups", {"name": "{{parameters.name}}", "limit": 100}),
       mappable=[{"name": "name", "type": "text", "label": "Name Contains"}, LIMIT_PARAM],
       interface=GROUP_IF, samples=GROUP_SAMPLE)

module("getGroup", "Get a Channel Group",
       "Returns one channel group with the full list of its account IDs.",
       "action", "read",
       {"url": "/groups/{{parameters.groupId}}", "method": "GET", "headers": AUTH, "response": {"output": "{{body}}"}},
       mappable=[{"name": "groupId", "type": "select", "label": "Channel Group", "required": True, "options": "rpc://listGroups"}],
       interface=GROUP_IF, samples=GROUP_SAMPLE)

module("listPosts", "List Posts",
       "Returns posts newest first. From and To filter on creation time, not on the scheduled time.",
       "search", None,
       paginated("/posts", {"status": "{{parameters.status}}", "accountId": "{{parameters.accountId}}",
                             "from": "{{parameters.from}}", "to": "{{parameters.to}}",
                             "sort": "{{parameters.sort}}", "order": "{{parameters.order}}", "limit": 100}),
       mappable=[
           {"name": "status", "type": "select", "label": "Status",
            "options": [{"label": "Draft", "value": "draft"}, {"label": "Scheduled", "value": "scheduled"},
                        {"label": "Posted", "value": "posted"}, {"label": "Failed", "value": "failed"}]},
           {"name": "accountId", "type": "select", "label": "Social Account", "options": "rpc://listAccounts",
            "help": "Only posts that target this account."},
           {"name": "from", "type": "date", "label": "Created After"},
           {"name": "to", "type": "date", "label": "Created Before"},
           {"name": "sort", "type": "select", "label": "Sort By", "default": "createdAt", "advanced": True,
            "help": "Sorting by Scheduled For leaves out unscheduled drafts.",
            "options": [{"label": "Created At", "value": "createdAt"}, {"label": "Scheduled For", "value": "scheduledFor"}]},
           {"name": "order", "type": "select", "label": "Order", "default": "desc", "advanced": True,
            "options": [{"label": "Descending", "value": "desc"}, {"label": "Ascending", "value": "asc"}]},
           LIMIT_PARAM,
       ],
       interface=POST_LIST_IF, samples=POST_LIST_SAMPLE)

module("getPost", "Get a Post",
       "Returns one post with its metadata and the per-account delivery state in Targets.",
       "action", "read",
       {"url": "/posts/{{parameters.postId}}", "method": "GET", "headers": AUTH, "response": {"output": "{{body}}"}},
       mappable=[{"name": "postId", "type": "text", "label": "Post ID", "required": True}],
       interface=POST_IF, samples=POST_SAMPLE)

module("createPost", "Create a Draft Post",
       "Creates a post in draft status. Nothing is published until Schedule a Post or Smart Schedule Posts runs.",
       "action", "create",
       {"url": "/posts", "method": "POST", "headers": AUTH,
        "body": {"content": "{{parameters.content}}", "type": "{{parameters.type}}", "title": "{{parameters.title}}",
                 "description": "{{parameters.description}}", "hashtags": "{{parameters.hashtags}}",
                 "mediaUrls": "{{parameters.mediaKeys}}", "coverR2Key": "{{parameters.coverKey}}"},
        "response": {"output": {"id": "{{body.id}}"}}},
       mappable=[
           {"name": "content", "type": "text", "label": "Content", "multiline": True,
            "help": "The caption or body, up to 2200 characters. Per-platform limits are checked at schedule time."},
           POST_TYPE_PARAM,
           {"name": "mediaKeys", "type": "array", "label": "Media Keys",
            "help": "Media Key values from Upload a Media File, in the order they should be published.",
            "spec": {"type": "text", "label": "Media Key"}, "labels": {"add": "Add a media key"}},
           {"name": "title", "type": "text", "label": "Title", "help": "Keep it under 100 characters if the post will be scheduled."},
           {"name": "description", "type": "text", "label": "Description", "multiline": True,
            "help": "Long-form description for platforms that have one, and the body of a Blog post."},
           HASHTAGS_PARAM,
           {"name": "coverKey", "type": "text", "label": "Cover Image Key", "advanced": True,
            "help": "Media Key of an uploaded cover image."},
       ],
       interface=[{"name": "id", "type": "text", "label": "Post ID"}],
       samples={"id": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d"})

module("updatePost", "Update a Draft Post",
       "Edits a post that is still a draft. Omitted fields are left untouched. A scheduled or published post cannot be edited.",
       "action", "update",
       {"url": "/posts/{{parameters.postId}}", "method": "PATCH", "headers": AUTH,
        "body": {"content": "{{parameters.content}}", "type": "{{parameters.type}}", "title": "{{parameters.title}}",
                 "description": "{{parameters.description}}", "hashtags": "{{parameters.hashtags}}",
                 "mediaUrls": "{{parameters.mediaKeys}}", "coverR2Key": "{{parameters.coverKey}}"},
        "response": {"output": {"id": "{{body.id}}"}}},
       mappable=[
           {"name": "postId", "type": "text", "label": "Post ID", "required": True},
           {"name": "content", "type": "text", "label": "Content", "multiline": True},
           {k: v for k, v in POST_TYPE_PARAM.items() if k != "default"},
           {"name": "mediaKeys", "type": "array", "label": "Media Keys", "help": "Replaces the whole list.",
            "spec": {"type": "text", "label": "Media Key"}, "labels": {"add": "Add a media key"}},
           {"name": "title", "type": "text", "label": "Title"},
           {"name": "description", "type": "text", "label": "Description", "multiline": True},
           HASHTAGS_PARAM,
           {"name": "coverKey", "type": "text", "label": "Cover Image Key", "advanced": True},
       ],
       interface=[{"name": "id", "type": "text", "label": "Post ID"}],
       samples={"id": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d"})

module("deletePost", "Delete a Draft Post",
       "Permanently deletes a post that is still a draft. A scheduled or published post cannot be deleted.",
       "action", "delete",
       {"url": "/posts/{{parameters.postId}}", "method": "DELETE", "headers": AUTH, "response": {"output": "{{body}}"}},
       mappable=[{"name": "postId", "type": "text", "label": "Post ID", "required": True}],
       interface=[
           {"name": "deleted", "type": "boolean", "label": "Deleted"},
           {"name": "post", "type": "collection", "label": "Deleted Post", "spec": [
               {"name": "title", "type": "text", "label": "Title"}, {"name": "content", "type": "text", "label": "Content"},
               {"name": "type", "type": "text", "label": "Type"}, {"name": "mediaCount", "type": "uinteger", "label": "Media Count"}]},
       ],
       samples={"deleted": True, "post": {"title": "Three edits that stop the scroll", "content": "Three edits...", "type": "video", "mediaCount": 1}})

module("uploadMedia", "Upload a Media File",
       "Uploads an image or video to the JuzPost media library and returns the Media Key to use in Create a Draft Post.",
       "action", "create",
       [
           {"url": "/storage/presign", "method": "POST", "headers": AUTH,
            "body": {"relativeKey": "media/{{parameters.fileName}}", "contentType": "{{parameters.contentType}}",
                     "operation": "upload", "contentLength": "{{parseNumber(ifempty(parameters.contentLength, length(parameters.data)), '.')}}"},
            "response": {"temp": {"signedUrl": "{{body.signedUrl}}", "resolvedKey": "{{body.resolvedKey}}"}}},
           {"url": "{{temp.signedUrl}}", "method": "PUT", "headers": {"Content-Type": "{{parameters.contentType}}"},
            "type": "binary", "body": "{{parameters.data}}",
            "response": {"valid": "{{statusCode >= 200 && statusCode < 300}}",
                         "error": {"message": "Storage refused the upload (HTTP {{statusCode}}). The declared Content Type or size did not match the bytes sent."},
                         "output": {"mediaKey": "{{temp.resolvedKey}}", "fileName": "{{parameters.fileName}}",
                                    "contentType": "{{parameters.contentType}}"}}},
       ],
       mappable=[
           {"name": "fileName", "type": "filename", "label": "File Name", "required": True, "semantic": "file:name",
            "help": "Letters, digits, dot, underscore and dash only, for example clip_03.mp4."},
           {"name": "data", "type": "buffer", "label": "Data", "required": True, "semantic": "file:data"},
           {"name": "contentType", "type": "select", "label": "Content Type", "required": True,
            "help": "Must match the file. Videos up to 500 MB, images up to 15 MB.",
            "options": [{"label": "video/mp4", "value": "video/mp4"}, {"label": "video/quicktime (.mov)", "value": "video/quicktime"},
                        {"label": "video/webm", "value": "video/webm"}, {"label": "image/jpeg", "value": "image/jpeg"},
                        {"label": "image/png", "value": "image/png"}, {"label": "image/webp", "value": "image/webp"}]},
           {"name": "contentLength", "type": "uinteger", "label": "File Size (bytes)", "advanced": True,
            "help": "Leave empty to compute it from the data. Set it when the upstream module reports the size."},
       ],
       interface=[
           {"name": "mediaKey", "type": "text", "label": "Media Key"},
           {"name": "fileName", "type": "text", "label": "File Name"},
           {"name": "contentType", "type": "text", "label": "Content Type"},
       ],
       samples={"mediaKey": "ws_abc123/media/clip_03.mp4", "fileName": "clip_03.mp4", "contentType": "video/mp4"})

module("schedulePost", "Schedule a Post",
       "Sends one draft to up to ten accounts at a time, or publishes it right away when Publish At is empty.",
       "action", "create",
       {"url": "/posts/{{parameters.postId}}/schedule", "method": "POST", "headers": AUTH,
        "body": {"socialAccountIds": "{{parameters.socialAccountIds}}", "publishAt": "{{parameters.publishAt}}",
                 "title": "{{parameters.title}}", "description": "{{parameters.description}}", "hashtags": "{{parameters.hashtags}}"},
        "response": {"output": "{{body}}"}},
       mappable=[
           {"name": "postId", "type": "text", "label": "Post ID", "required": True, "help": "A draft from Create a Draft Post."},
           ACCOUNTS_SELECT,
           {"name": "publishAt", "type": "date", "label": "Publish At",
            "help": "At least 5 minutes and at most about 6 months ahead. Leave empty to publish now."},
           {"name": "title", "type": "text", "label": "Title Override", "advanced": True, "help": "Up to 100 characters."},
           {"name": "description", "type": "text", "label": "Description Override", "advanced": True, "multiline": True},
           {**HASHTAGS_PARAM, "label": "Hashtags Override", "advanced": True},
       ],
       interface=[
           {"name": "success", "type": "boolean", "label": "Success"},
           {"name": "results", "type": "array", "label": "Results", "spec": [
               {"name": "socialAccountId", "type": "text", "label": "Account ID"},
               {"name": "platform", "type": "text", "label": "Platform"},
               {"name": "username", "type": "text", "label": "Username"},
               {"name": "status", "type": "text", "label": "Status"},
               {"name": "error", "type": "text", "label": "Error"}]},
       ],
       samples={"success": True, "results": [{"socialAccountId": "0f1c2d3e-4a5b-4c6d-8e9f-0a1b2c3d4e5f", "platform": "instagram",
                                              "username": "juzpost", "status": "scheduled"}]})

module("smartSchedule", "Smart Schedule Posts",
       "Spreads drafts across your preset posting times, a minimum number per day. Run with Dry Run on first to see the plan.",
       "action", "create",
       {"url": "/schedule", "method": "POST", "headers": AUTH,
        "body": {"minPerDay": "{{parseNumber(parameters.minPerDay, '.')}}", "group": "{{parameters.group}}",
                 "socialAccountIds": "{{parameters.socialAccountIds}}", "postIds": "{{parameters.postIds}}",
                 "startDate": "{{if(parameters.startDate, formatDate(parameters.startDate, 'YYYY-MM-DD'))}}",
                 "times": "{{parameters.times}}", "dryRun": "{{parameters.dryRun}}"},
        "response": {"output": "{{body}}"}},
       mappable=[
           {"name": "minPerDay", "type": "uinteger", "label": "Posts Per Day", "required": True, "default": 1,
            "help": "1 to 20, and not more than the number of posting times."},
           {"name": "group", "type": "select", "label": "Channel Group", "options": "rpc://listGroupNames",
            "help": "Every post goes to every account in the group. Or map explicit accounts below."},
           {**ACCOUNTS_SELECT, "required": False, "validate": {"maxItems": 10}, "help": "Used instead of the group when set."},
           {"name": "postIds", "type": "array", "label": "Post IDs", "spec": {"type": "text", "label": "Post ID"},
            "help": "Specific drafts, in the order to place them. Leave empty to schedule every draft, oldest first."},
           {"name": "startDate", "type": "date", "label": "Start Date", "time": False, "help": "First day to place posts on. Defaults to tomorrow."},
           {"name": "times", "type": "array", "label": "Posting Times", "spec": {"type": "text", "label": "HH:MM"},
            "help": "Wall-clock times in the workspace timezone, overriding the workspace defaults for this run."},
           {"name": "dryRun", "type": "boolean", "label": "Dry Run", "default": False, "help": "Return the plan without creating any timers."},
       ],
       interface=[
           {"name": "scheduled", "type": "array", "label": "Scheduled", "spec": [
               {"name": "postId", "type": "text", "label": "Post ID"}, {"name": "publishAt", "type": "date", "label": "Publish At"},
               {"name": "accountIds", "type": "array", "label": "Account IDs", "spec": {"type": "text", "label": "Account ID"}},
               {"name": "status", "type": "text", "label": "Status"}, {"name": "error", "type": "text", "label": "Error"}]},
           {"name": "skipped", "type": "array", "label": "Skipped", "spec": [
               {"name": "postId", "type": "text", "label": "Post ID"}, {"name": "reason", "type": "text", "label": "Reason"}]},
           {"name": "plan", "type": "collection", "label": "Plan", "spec": [
               {"name": "timezone", "type": "text", "label": "Timezone"}, {"name": "perDay", "type": "uinteger", "label": "Per Day"},
               {"name": "days", "type": "uinteger", "label": "Days"},
               {"name": "slotsUsed", "type": "array", "label": "Slots Used", "spec": {"type": "text", "label": "HH:MM"}}]},
           {"name": "dryRun", "type": "boolean", "label": "Dry Run"},
       ],
       samples={"scheduled": [{"postId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d", "publishAt": "2026-11-05T03:30:00.000Z",
                               "accountIds": ["0f1c2d3e-4a5b-4c6d-8e9f-0a1b2c3d4e5f"], "status": "scheduled"}],
                "skipped": [], "plan": {"timezone": "Asia/Kolkata", "perDay": 1, "days": 1, "slotsUsed": ["09:00"]}, "dryRun": False})

module("watchPosts", "Watch Posts",
       "Triggers when a post reaches the chosen status, for example when one is published or fails.",
       "trigger", None,
       {"url": "/posts", "method": "GET", "headers": AUTH,
        "qs": {"status": "{{parameters.status}}", "sort": "createdAt", "order": "desc", "limit": 100},
        "response": {"iterate": "{{body.data}}", "output": "{{item}}", "limit": "{{parameters.limit}}",
                     "trigger": {"id": "{{item.id}}", "date": "{{item.updatedAt}}", "type": "date", "order": "desc"}},
        "pagination": {"condition": "{{body.pagination.hasMore}}", "qs": {"cursor": "{{body.pagination.nextCursor}}"}}},
       static=[
           {"name": "status", "type": "select", "label": "Status", "required": True, "default": "posted",
            "options": [{"label": "Posted", "value": "posted"}, {"label": "Failed", "value": "failed"},
                        {"label": "Scheduled", "value": "scheduled"}, {"label": "Draft", "value": "draft"}]},
           {**LIMIT_PARAM, "default": 10},
       ],
       interface=POST_LIST_IF, samples={**POST_LIST_SAMPLE, "status": "posted"})

module("makeApiCall", "Make an API Call",
       "Performs an arbitrary authorized call to the JuzPost REST API.",
       "universal", None,
       {"url": "{{parameters.url}}", "method": "{{parameters.method}}",
        "headers": {**AUTH, "{{...}}": "{{toCollection(parameters.headers, 'key', 'value')}}"},
        "qs": "{{toCollection(parameters.qs, 'key', 'value')}}", "body": "{{parameters.body}}",
        "response": {"output": {"body": "{{body}}", "headers": "{{headers}}", "statusCode": "{{statusCode}}"}}},
       mappable=[
           {"name": "url", "type": "text", "label": "URL", "required": True,
            "help": "Path relative to https://www.juzpost.com/api/cli/v1, for example /posts."},
           {"name": "method", "type": "select", "label": "Method", "required": True, "default": "GET",
            "options": [{"label": "GET", "value": "GET"}, {"label": "POST", "value": "POST"}, {"label": "PATCH", "value": "PATCH"},
                        {"label": "PUT", "value": "PUT"}, {"label": "DELETE", "value": "DELETE"}]},
           {"name": "headers", "type": "array", "label": "Headers", "default": [{"key": "Content-Type", "value": "application/json"}],
            "spec": [{"name": "key", "type": "text", "label": "Key"}, {"name": "value", "type": "text", "label": "Value"}]},
           {"name": "qs", "type": "array", "label": "Query String",
            "spec": [{"name": "key", "type": "text", "label": "Key"}, {"name": "value", "type": "text", "label": "Value"}]},
           {"name": "body", "type": "any", "label": "Body"},
       ],
       interface=[
           {"name": "body", "type": "any", "label": "Body"},
           {"name": "headers", "type": "collection", "label": "Headers", "spec": []},
           {"name": "statusCode", "type": "uinteger", "label": "Status Code"},
       ],
       samples={"body": {"data": [], "pagination": PAGE}, "headers": {"content-type": "application/json"}, "statusCode": 200})

# ---------------------------------------------------------------- RPCs
RPCS = {
    "listAccounts": {
        "label": "List accounts (options)",
        "communication": {
            "url": "/accounts", "method": "GET", "headers": AUTH, "qs": {"limit": 100, "sort": "platform", "order": "asc"},
            "response": {"limit": 500, "iterate": "{{body.data}}",
                         "output": {"label": "{{item.platform}} · {{item.username}}{{if(item.isActive, '', ' (needs reconnect)')}}", "value": "{{item.id}}"}},
            "pagination": {"condition": "{{body.pagination.hasMore}}", "qs": {"cursor": "{{body.pagination.nextCursor}}"}},
        },
    },
    "listGroups": {
        "label": "List channel groups (options, value = id)",
        "communication": {
            "url": "/groups", "method": "GET", "headers": AUTH, "qs": {"limit": 100, "sort": "name", "order": "asc"},
            "response": {"limit": 500, "iterate": "{{body.data}}",
                         "output": {"label": "{{item.name}} ({{item.accountCount}} accounts)", "value": "{{item.id}}"}},
            "pagination": {"condition": "{{body.pagination.hasMore}}", "qs": {"cursor": "{{body.pagination.nextCursor}}"}},
        },
    },
    "listGroupNames": {
        "label": "List channel groups (options, value = name)",
        "communication": {
            "url": "/groups", "method": "GET", "headers": AUTH, "qs": {"limit": 100, "sort": "name", "order": "asc"},
            "response": {"limit": 500, "iterate": "{{body.data}}",
                         "output": {"label": "{{item.name}} ({{item.accountCount}} accounts)", "value": "{{item.name}}"}},
            "pagination": {"condition": "{{body.pagination.hasMore}}", "qs": {"cursor": "{{body.pagination.nextCursor}}"}},
        },
    },
}

# ---------------------------------------------------------------- write files
w("general/base.iml.json", {
    "baseUrl": "https://www.juzpost.com/api/cli/v1",
    "headers": {"Accept": "application/json"},
    "response": {
        "error": {
            "message": "[{{statusCode}}] {{ifempty(body.error.message, body.error)}}",
            "400": {"type": "DataError", "message": "[400] {{body.error.message}}"},
            "401": {"type": "InvalidAccessTokenError", "message": "[401] The API key is missing, revoked or wrong. Create a new one under Settings, General, API keys."},
            "402": {"type": "InvalidConfigurationError", "message": "[402] {{body.error.message}}"},
            "404": {"type": "DataError", "message": "[404] {{body.error.message}}"},
            "409": {"type": "DataError", "message": "[409] {{body.error.message}}"},
            "422": {"type": "DataError", "message": "[422] {{body.error.message}}"},
            "429": {"type": "RateLimitError", "message": "[429] {{body.error.message}}"},
        }
    },
    "log": {"sanitize": ["request.headers.authorization"]},
})

w("connections/juzpost/juzpost.communication.iml.json", {
    "url": "https://www.juzpost.com/api/cli/v1/me", "method": "GET",
    "headers": {"Authorization": "Bearer {{parameters.apiKey}}", "Accept": "application/json"},
    "response": {
        "valid": "{{statusCode === 200}}",
        "error": {"message": "[{{statusCode}}] {{ifempty(body.error.message, 'The API key was not accepted.')}}"},
        "metadata": {"type": "text", "value": "{{ifempty(body.user.email, body.workspace.name)}}"},
    },
    "log": {"sanitize": ["request.headers.authorization"]},
})
w("connections/juzpost/juzpost.params.iml.json", [
    {"name": "apiKey", "type": "password", "label": "API Key", "required": True,
     "help": "In JuzPost open Settings, General, then the API keys card and choose Generate API key. The key starts with jp_live_ and is shown once."},
])

for name, m in MODULES.items():
    d = f"modules/{name}/{name}"
    w(f"{d}.communication.iml.json", m["communication"])
    w(f"{d}.mappableParams.iml.json", m["mappableParams"])
    w(f"{d}.staticParams.iml.json", m["staticParams"])
    w(f"{d}.interface.iml.json", m["interface"])
    w(f"{d}.samples.iml.json", m["samples"])

for name, r in RPCS.items():
    d = f"rpcs/{name}/{name}"
    w(f"{d}.communication.iml.json", r["communication"])
    w(f"{d}.params.iml.json", [])

w("modules/groups.json", [
    {"label": "Posts", "modules": ["createPost", "uploadMedia", "schedulePost", "smartSchedule", "getPost", "updatePost", "deletePost", "listPosts"]},
    {"label": "Triggers", "modules": ["watchPosts"]},
    {"label": "Accounts", "modules": ["listAccounts", "listGroups", "getGroup", "getMyAccount"]},
    {"label": "Other", "modules": ["makeApiCall"]},
])

manifest = {
    "fileVersion": 1,
    "generalCodeFiles": {"base": "general/base.iml.json", "common": None, "readme": "README.md", "groups": "modules/groups.json"},
    "components": {
        "connection": {"juzpost": {"label": "JuzPost API key", "connectionType": "basic",
                                   "codeFiles": {"communication": "connections/juzpost/juzpost.communication.iml.json",
                                                 "params": "connections/juzpost/juzpost.params.iml.json", "common": None}}},
        "module": {name: {"label": m["label"], "description": m["description"], "moduleType": m["moduleType"],
                          "actionCrud": m["actionCrud"], "connection": "juzpost", "altConnection": None,
                          **({"webhook": None} if m["moduleType"] == "instant_trigger" else {}),
                          "codeFiles": {"communication": f"modules/{name}/{name}.communication.iml.json",
                                        "staticParams": f"modules/{name}/{name}.staticParams.iml.json",
                                        "mappableParams": f"modules/{name}/{name}.mappableParams.iml.json",
                                        "interface": f"modules/{name}/{name}.interface.iml.json",
                                        "samples": f"modules/{name}/{name}.samples.iml.json",
                                        "scope": None}}
                   for name, m in MODULES.items()},
        "function": {},
        "rpc": {name: {"label": r["label"], "connection": "juzpost", "altConnection": None,
                       "codeFiles": {"communication": f"rpcs/{name}/{name}.communication.iml.json",
                                     "params": f"rpcs/{name}/{name}.params.iml.json"}}
                for name, r in RPCS.items()},
        "webhook": {},
    },
    "origins": [
        {"label": "JuzPost on Make (set appId after creating the app in Make)", "baseUrl": "https://eu2.make.com/api", "appId": "juzpost",
         "appVersion": 1, "apikeyFile": "../.secrets/make-apikey"},
    ],
}
w("makecomapp.json", manifest)
print("modules:", len(MODULES), "rpcs:", len(RPCS))

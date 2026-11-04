import { axios } from "@pipedream/platform";

export default {
  type: "app",
  app: "juzpost",
  propDefinitions: {
    postId: {
      type: "string",
      label: "Post ID",
      description: "ID of a post, as returned by Create Draft Post or List Posts",
    },
    socialAccountIds: {
      type: "string[]",
      label: "Social Accounts",
      description: "Between one and ten connected accounts",
      async options({ prevContext }) {
        const { data, pagination } = await this.listAccounts({
          params: {
            limit: 100,
            cursor: prevContext?.cursor,
            sort: "platform",
            order: "asc",
          },
        });
        return {
          options: data.map((a) => ({
            label: `${a.platform} · ${a.username}${a.isActive ? "" : " (needs reconnect)"}`,
            value: a.id,
          })),
          context: { cursor: pagination?.hasMore ? pagination.nextCursor : undefined },
        };
      },
    },
    groupName: {
      type: "string",
      label: "Channel Group",
      description: "A named bundle of accounts. Every post goes to every account in it.",
      optional: true,
      async options() {
        const { data } = await this.listGroups({ params: { limit: 100 } });
        return data.map((g) => ({
          label: `${g.name} (${g.accountCount} accounts)`,
          value: g.name,
        }));
      },
    },
    postType: {
      type: "string",
      label: "Post Type",
      description: "Anything other than `text` and `blog` needs at least one media key before it can be scheduled. `blog` is a WordPress post: title required, description is the body.",
      options: ["text", "image", "video", "story", "blog"],
      default: "text",
      optional: true,
    },
    content: {
      type: "string",
      label: "Content",
      description: "The caption or body, up to 2200 characters",
      optional: true,
    },
    title: {
      type: "string",
      label: "Title",
      description: "Keep it under 100 characters if the post will be scheduled",
      optional: true,
    },
    description: {
      type: "string",
      label: "Description",
      description: "Long-form description for platforms that have one, and the body of a blog post",
      optional: true,
    },
    hashtags: {
      type: "string[]",
      label: "Hashtags",
      description: "Without the leading `#`",
      optional: true,
    },
    mediaKeys: {
      type: "string[]",
      label: "Media Keys",
      description: "Keys returned by Upload Media, in publish order",
      optional: true,
    },
    status: {
      type: "string",
      label: "Status",
      description: "Post status to filter on",
      options: ["draft", "scheduled", "posted", "failed"],
      optional: true,
    },
    maxResults: {
      type: "integer",
      label: "Max Results",
      description: "Maximum number of posts to return",
      default: 50,
      optional: true,
    },
  },
  methods: {
    _baseUrl() {
      return "https://www.juzpost.com/api/cli/v1";
    },
    _headers() {
      return {
        Authorization: `Bearer ${this.$auth.api_key}`,
        "Content-Type": "application/json",
      };
    },
    _makeRequest({ $ = this, path, ...opts } = {}) {
      return axios($, {
        url: `${this._baseUrl()}${path}`,
        headers: this._headers(),
        ...opts,
      });
    },
    getMe(opts = {}) {
      return this._makeRequest({ path: "/me", ...opts });
    },
    getWorkspace(opts = {}) {
      return this._makeRequest({ path: "/workspace", ...opts });
    },
    listAccounts(opts = {}) {
      return this._makeRequest({ path: "/accounts", ...opts });
    },
    listGroups(opts = {}) {
      return this._makeRequest({ path: "/groups", ...opts });
    },
    listPosts(opts = {}) {
      return this._makeRequest({ path: "/posts", ...opts });
    },
    getPost({ postId, ...opts }) {
      return this._makeRequest({ path: `/posts/${encodeURIComponent(postId)}`, ...opts });
    },
    createPost(opts = {}) {
      return this._makeRequest({ method: "POST", path: "/posts", ...opts });
    },
    updatePost({ postId, ...opts }) {
      return this._makeRequest({ method: "PATCH", path: `/posts/${encodeURIComponent(postId)}`, ...opts });
    },
    deletePost({ postId, ...opts }) {
      return this._makeRequest({ method: "DELETE", path: `/posts/${encodeURIComponent(postId)}`, ...opts });
    },
    schedulePost({ postId, ...opts }) {
      return this._makeRequest({ method: "POST", path: `/posts/${encodeURIComponent(postId)}/schedule`, ...opts });
    },
    smartSchedule(opts = {}) {
      return this._makeRequest({ method: "POST", path: "/schedule", ...opts });
    },
    presign(opts = {}) {
      return this._makeRequest({ method: "POST", path: "/storage/presign", ...opts });
    },
    /** Follows cursor pagination until exhausted or `max` rows collected. */
    async paginate({ fn, params = {}, max = 0 }) {
      const out = [];
      let cursor;
      do {
        const page = await fn({ params: { ...params, limit: 100, cursor } });
        out.push(...(page.data ?? []));
        cursor = page.pagination?.hasMore ? page.pagination.nextCursor : undefined;
        if (max && out.length >= max) return out.slice(0, max);
      } while (cursor);
      return out;
    },
  },
};

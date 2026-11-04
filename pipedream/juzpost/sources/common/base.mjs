import juzpost from "../../juzpost.app.mjs";

/** Shared polling source: emits a post each time it reaches `status`. */
export default function makeSource({ key, name, description, status, summary }) {
  return {
    key,
    name,
    description: `${description} [See the documentation](https://api.juzpost.com/docs#tag/Posts/operation/listPosts)`,
    version: "0.0.1",
    type: "source",
    dedupe: "unique",
    props: {
      juzpost,
      db: "$.service.db",
      timer: {
        type: "$.interface.timer",
        default: { intervalSeconds: 15 * 60 },
      },
    },
    async run() {
      const { data } = await this.juzpost.listPosts({
        params: { status, sort: "createdAt", order: "desc", limit: 100 },
      });
      for (const post of data.reverse()) {
        this.$emit(post, {
          id: `${post.id}-${post.updatedAt}`,
          summary: summary(post),
          ts: Date.parse(post.updatedAt),
        });
      }
    },
  };
}

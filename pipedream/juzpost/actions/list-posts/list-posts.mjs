import juzpost from "../../juzpost.app.mjs";
import { clean } from "../../common/common.mjs";

export default {
  key: "juzpost-list-posts",
  name: "List Posts",
  description: "Returns posts newest first. [See the documentation](https://api.juzpost.com/docs#tag/Posts/operation/listPosts)",
  version: "0.0.1",
  type: "action",
  annotations: { destructiveHint: false, openWorldHint: true, readOnlyHint: true },
  props: {
    juzpost,
    status: { propDefinition: [juzpost, "status"] },
    maxResults: { propDefinition: [juzpost, "maxResults"] },
  },
  async run({ $ }) {
    const posts = await this.juzpost.paginate({
      fn: (opts) => this.juzpost.listPosts({ $, ...opts }),
      params: clean({ status: this.status, sort: "createdAt", order: "desc" }),
      max: this.maxResults,
    });
    $.export("$summary", `Fetched ${posts.length} posts`);
    return posts;
  },
};

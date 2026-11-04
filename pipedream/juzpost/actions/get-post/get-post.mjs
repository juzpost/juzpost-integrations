import juzpost from "../../juzpost.app.mjs";

export default {
  key: "juzpost-get-post",
  name: "Get Post",
  description: "Returns one post with its metadata and the per-account delivery state in `targets`. [See the documentation](https://api.juzpost.com/docs#tag/Posts/operation/getPost)",
  version: "0.0.1",
  type: "action",
  annotations: { destructiveHint: false, openWorldHint: true, readOnlyHint: true },
  props: {
    juzpost,
    postId: { propDefinition: [juzpost, "postId"] },
  },
  async run({ $ }) {
    const response = await this.juzpost.getPost({ $, postId: this.postId });
    $.export("$summary", `Fetched post ${this.postId} (${response.status})`);
    return response;
  },
};

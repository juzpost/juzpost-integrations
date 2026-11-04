import juzpost from "../../juzpost.app.mjs";
import { clean } from "../../common/common.mjs";

export default {
  key: "juzpost-create-draft-post",
  name: "Create Draft Post",
  description: "Creates a post in draft status. Nothing is published until Schedule Post or Smart Schedule Posts runs. [See the documentation](https://api.juzpost.com/docs#tag/Posts/operation/createPost)",
  version: "0.0.1",
  type: "action",
  annotations: { destructiveHint: false, openWorldHint: true, readOnlyHint: false },
  props: {
    juzpost,
    content: { propDefinition: [juzpost, "content"] },
    type: { propDefinition: [juzpost, "postType"] },
    mediaKeys: { propDefinition: [juzpost, "mediaKeys"] },
    title: { propDefinition: [juzpost, "title"] },
    description: { propDefinition: [juzpost, "description"] },
    hashtags: { propDefinition: [juzpost, "hashtags"] },
    coverKey: {
      type: "string",
      label: "Cover Image Key",
      description: "Media key of an uploaded cover image",
      optional: true,
    },
  },
  async run({ $ }) {
    const data = clean({
      content: this.content,
      type: this.type,
      mediaUrls: this.mediaKeys,
      title: this.title,
      description: this.description,
      hashtags: this.hashtags,
      coverR2Key: this.coverKey,
    });
    const response = await this.juzpost.createPost({ $, data });
    $.export("$summary", `Created draft post ${response.id}`);
    return response;
  },
};

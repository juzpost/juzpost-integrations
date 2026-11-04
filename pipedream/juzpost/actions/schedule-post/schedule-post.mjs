import juzpost from "../../juzpost.app.mjs";
import { clean } from "../../common/common.mjs";

export default {
  key: "juzpost-schedule-post",
  name: "Schedule Post",
  description: "Sends a draft to up to ten accounts at a time, or publishes it right away when Publish At is empty. [See the documentation](https://api.juzpost.com/docs#tag/Scheduling/operation/schedulePost)",
  version: "0.0.1",
  type: "action",
  annotations: { destructiveHint: false, openWorldHint: true, readOnlyHint: false },
  props: {
    juzpost,
    postId: { propDefinition: [juzpost, "postId"] },
    socialAccountIds: { propDefinition: [juzpost, "socialAccountIds"] },
    publishAt: {
      type: "string",
      label: "Publish At",
      description: "ISO 8601 UTC instant, at least 10 minutes and at most about 6 months ahead. Leave empty to publish now.",
      optional: true,
    },
    title: { propDefinition: [juzpost, "title"], label: "Title Override" },
    description: { propDefinition: [juzpost, "description"], label: "Description Override" },
    hashtags: { propDefinition: [juzpost, "hashtags"], label: "Hashtags Override" },
  },
  async run({ $ }) {
    const data = clean({
      socialAccountIds: this.socialAccountIds,
      publishAt: this.publishAt ? new Date(this.publishAt).toISOString() : undefined,
      title: this.title,
      description: this.description,
      hashtags: this.hashtags,
    });
    const response = await this.juzpost.schedulePost({ $, postId: this.postId, data });
    const ok = (response.results ?? []).filter((r) => r.status === "scheduled").length;
    $.export("$summary", `Scheduled post ${this.postId} to ${ok} of ${this.socialAccountIds.length} accounts`);
    return response;
  },
};

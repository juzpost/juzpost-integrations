import juzpost from "../../juzpost.app.mjs";
import { clean } from "../../common/common.mjs";

export default {
  key: "juzpost-smart-schedule-posts",
  name: "Smart Schedule Posts",
  description: "Spreads drafts across the workspace posting times, a minimum number per day. Use Dry Run first to see the plan. [See the documentation](https://api.juzpost.com/docs#tag/Scheduling/operation/smartSchedule)",
  version: "0.0.1",
  type: "action",
  annotations: { destructiveHint: false, openWorldHint: true, readOnlyHint: false },
  props: {
    juzpost,
    minPerDay: {
      type: "integer",
      label: "Posts Per Day",
      description: "1 to 20, and not more than the number of posting times",
      default: 1,
    },
    group: { propDefinition: [juzpost, "groupName"] },
    socialAccountIds: {
      propDefinition: [juzpost, "socialAccountIds"],
      description: "Used instead of the channel group when set",
      optional: true,
    },
    postIds: {
      type: "string[]",
      label: "Post IDs",
      description: "Specific drafts to place, in order. Leave empty to schedule every draft, oldest first.",
      optional: true,
    },
    startDate: {
      type: "string",
      label: "Start Date",
      description: "First day to place posts on as `YYYY-MM-DD` in the workspace timezone. Defaults to tomorrow.",
      optional: true,
    },
    times: {
      type: "string[]",
      label: "Posting Times",
      description: "`HH:MM` wall-clock times in the workspace timezone, overriding the defaults for this run",
      optional: true,
    },
    dryRun: {
      type: "boolean",
      label: "Dry Run",
      description: "Return the plan without creating any timers",
      default: false,
      optional: true,
    },
  },
  async run({ $ }) {
    const data = clean({
      minPerDay: this.minPerDay,
      group: this.group,
      socialAccountIds: this.socialAccountIds,
      postIds: this.postIds,
      startDate: this.startDate,
      times: this.times,
      dryRun: this.dryRun || undefined,
    });
    const response = await this.juzpost.smartSchedule({ $, data });
    $.export("$summary", `${this.dryRun ? "Planned" : "Scheduled"} ${response.scheduled?.length ?? 0} posts, skipped ${response.skipped?.length ?? 0}`);
    return response;
  },
};

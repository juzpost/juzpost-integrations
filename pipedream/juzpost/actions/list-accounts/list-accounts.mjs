import juzpost from "../../juzpost.app.mjs";
import { clean } from "../../common/common.mjs";

export default {
  key: "juzpost-list-accounts",
  name: "List Connected Accounts",
  description: "Returns the connected social accounts. Their IDs are what Schedule Post takes. [See the documentation](https://api.juzpost.com/docs#tag/Accounts/operation/listAccounts)",
  version: "0.0.1",
  type: "action",
  annotations: { destructiveHint: false, openWorldHint: true, readOnlyHint: true },
  props: {
    juzpost,
    platform: {
      type: "string",
      label: "Platform",
      description: "Only accounts on this network",
      options: ["youtube", "tiktok", "instagram", "facebook", "x", "linkedin", "pinterest", "threads", "bluesky", "tumblr", "wordpress"],
      optional: true,
    },
  },
  async run({ $ }) {
    const accounts = await this.juzpost.paginate({
      fn: (opts) => this.juzpost.listAccounts({ $, ...opts }),
      params: clean({ platform: this.platform }),
    });
    $.export("$summary", `Fetched ${accounts.length} accounts`);
    return accounts;
  },
};

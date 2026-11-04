import makeSource from "../common/base.mjs";

export default makeSource({
  key: "juzpost-post-failed",
  name: "Post Failed",
  description: "Emit new event when a JuzPost post failed to publish on at least one account.",
  status: "failed",
  summary: (p) => `Failed: ${p.title || p.content?.slice(0, 60) || p.id}`,
});

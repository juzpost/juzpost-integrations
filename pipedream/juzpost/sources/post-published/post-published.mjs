import makeSource from "../common/base.mjs";

export default makeSource({
  key: "juzpost-post-published",
  name: "Post Published",
  description: "Emit new event when a JuzPost post has been published.",
  status: "posted",
  summary: (p) => `Published: ${p.title || p.content?.slice(0, 60) || p.id}`,
});

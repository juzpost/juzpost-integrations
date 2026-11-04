import juzpost from "../../juzpost.app.mjs";
import { axios } from "@pipedream/platform";
import fs from "fs";

export default {
  key: "juzpost-upload-media",
  name: "Upload Media",
  description: "Uploads an image or video to the JuzPost media library and returns the media key to use in Create Draft Post. [See the documentation](https://api.juzpost.com/docs#tag/Storage/operation/presignStorage)",
  version: "0.0.1",
  type: "action",
  annotations: { destructiveHint: false, openWorldHint: true, readOnlyHint: false },
  props: {
    juzpost,
    filePath: {
      type: "string",
      label: "File Path or URL",
      description: "A file in `/tmp` (for example from a previous step) or a public https URL",
    },
    fileName: {
      type: "string",
      label: "File Name",
      description: "Letters, digits, dot, underscore and dash, for example `clip_03.mp4`. Defaults to the last path segment.",
      optional: true,
    },
    contentType: {
      type: "string",
      label: "Content Type",
      description: "Must match the file. Videos up to 500 MB, images up to 15 MB.",
      options: ["video/mp4", "video/quicktime", "video/webm", "image/jpeg", "image/png", "image/webp"],
    },
  },
  async run({ $ }) {
    const isUrl = /^https?:\/\//i.test(this.filePath);
    const bytes = isUrl
      ? Buffer.from(await axios($, { url: this.filePath, responseType: "arraybuffer" }))
      : fs.readFileSync(this.filePath);
    const fileName = (this.fileName || this.filePath.split("/").pop().split("?")[0]).replace(/[^A-Za-z0-9._-]/g, "_");

    const { signedUrl, resolvedKey } = await this.juzpost.presign({
      $,
      data: {
        relativeKey: `media/${fileName}`,
        contentType: this.contentType,
        operation: "upload",
        contentLength: bytes.length,
      },
    });
    await axios($, {
      method: "PUT",
      url: signedUrl,
      headers: { "Content-Type": this.contentType },
      data: bytes,
      maxBodyLength: Infinity,
    });
    $.export("$summary", `Uploaded ${fileName} (${bytes.length} bytes)`);
    return { mediaKey: resolvedKey, fileName, contentType: this.contentType, contentLength: bytes.length };
  },
};

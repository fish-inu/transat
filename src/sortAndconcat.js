const fs = require("fs");

(async () => {
  let files = await fs.readdirSync("./files");
  let sorted = files.sort((a, b) => {
    return (
      fs.statSync("./files/" + a).mtimeMs - fs.statSync("./files/" + b).mtimeMs
    );
  });
  let text = sorted.reduce((acc, cur, i) => {
    let content = fs.readFileSync("./files/" + cur, { encoding: "utf-8" });
    return acc + '\n' + content;
  }, "");
  fs.writeFileSync("./deno-manual.txt", text);
})();

import { readFile, readdir } from "node:fs/promises";
import { extname, join, relative } from "node:path";

const root = new URL("..", import.meta.url).pathname;
const extensions = new Set([".js", ".jsx", ".css", ".html"]);
const errors = [];
let checked = 0;

async function walk(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (["node_modules", "dist"].includes(entry.name)) continue;
    const path = join(directory, entry.name);
    if (entry.isDirectory()) await walk(path);
    else if (extensions.has(extname(path))) {
      checked += 1;
      const lines = (await readFile(path, "utf8")).split("\n");
      lines.forEach((line, index) => {
        if (line.trimEnd() !== line) errors.push(`${relative(root, path)}:${index + 1}: trailing whitespace`);
      });
    }
  }
}

await walk(root);
if (errors.length) {
  console.error(errors.join("\n"));
  process.exitCode = 1;
} else {
  console.log(`lint: checked ${checked} frontend files`);
}

import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

test("frontend manifest exposes reproducible quality commands", async () => {
  const packageJson = JSON.parse(await readFile(new URL("../package.json", import.meta.url)));
  for (const command of ["test", "lint", "build"]) assert.ok(packageJson.scripts[command]);
  await access(new URL("../src/main.jsx", import.meta.url));
  await access(new URL("../index.html", import.meta.url));
});

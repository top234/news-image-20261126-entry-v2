// news-image-20261126-entry-v2 — entrypoint (Node 22 stdlib only).
// Renders entry.png with generate.py (python3, fallback python) into
// OUTPUT_DIR ?? MAKEFUN_OUTPUT_DIR ?? "/output".
// If Python/PIL/generate.py is unavailable, copies the bundled entry.png.
// Verifies the PNG (signature, IHDR 1024x1024, <=1 MiB, IEND trailer),
// prints sha256 + drawn/bundled path. Never deletes the output dir.
import { spawnSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.OUTPUT_DIR ?? process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const outPath = join(outDir, "entry.png");

function sha256(buf) {
  return createHash("sha256").update(buf).digest("hex");
}

function verifyPng(buf, label) {
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  if (buf.length < 8 || !buf.subarray(0, 8).equals(sig)) {
    throw new Error(`${label}: bad PNG signature`);
  }
  if (buf.length < 33 || buf.toString("ascii", 12, 16) !== "IHDR") {
    throw new Error(`${label}: missing IHDR`);
  }
  const w = buf.readUInt32BE(16);
  const h = buf.readUInt32BE(20);
  if (w !== 1024 || h !== 1024) {
    throw new Error(`${label}: expected 1024x1024, got ${w}x${h}`);
  }
  if (buf.length > 1024 * 1024) {
    throw new Error(`${label}: ${buf.length} bytes exceeds 1 MiB`);
  }
  const iend = Buffer.from([0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82]);
  if (!buf.subarray(buf.length - 8).equals(iend)) {
    throw new Error(`${label}: missing IEND trailer`);
  }
  return { width: w, height: h, bytes: buf.length, sha256: sha256(buf) };
}

function tryPython(py) {
  const gen = join(here, "generate.py");
  if (!existsSync(gen)) return null;
  const tmp = join(outDir, ".entry-drawn.png");
  const r = spawnSync(py, [gen, tmp], { encoding: "utf8", timeout: 120000 });
  if (r.error || r.status !== 0) {
    console.error(`${py}: generate.py failed: ${r.error?.message ?? ""}${r.stderr ?? ""}`.trim());
    return null;
  }
  if (!existsSync(tmp)) return null;
  return readFileSync(tmp);
}

mkdirSync(outDir, { recursive: true });

let buf = null;
let mode = "bundled";
for (const py of ["python3", "python"]) {
  const drawn = tryPython(py);
  if (!drawn) continue;
  try {
    verifyPng(drawn, `drawn (${py})`);
    buf = drawn;
    mode = "drawn";
    break;
  } catch (e) {
    console.error(`drawn PNG failed verification, trying next source: ${e.message}`);
  }
}
if (!buf) {
  const bundled = join(here, "entry.png");
  if (!existsSync(bundled)) {
    throw new Error("no Python/PIL/generate.py and no bundled entry.png");
  }
  buf = readFileSync(bundled);
}
const info = verifyPng(buf, mode);
writeFileSync(outPath, buf);
// Re-read the written file and verify it byte-for-byte: a truncated or
// corrupted write must fail loudly instead of passing a stale hash.
const written = readFileSync(outPath);
const writtenInfo = verifyPng(written, "written output");
if (writtenInfo.sha256 !== info.sha256) {
  throw new Error("written output hash mismatch — output may be truncated");
}
console.log(JSON.stringify({ mode, output: outPath, ...writtenInfo }));

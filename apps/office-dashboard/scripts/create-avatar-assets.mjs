import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const appDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(appDir, "../..");
const sheetPath = path.join(repoRoot, "docs/dashboard/references/agent-avatars.png");
const outputDir = path.join(appDir, "public/assets/avatars");

const avatars = [
  {
    fileName: "input-parser.png",
    crop: { left: 28, top: 42, width: 330, height: 430 }
  },
  {
    fileName: "content-strategy.png",
    crop: { left: 398, top: 28, width: 354, height: 444 }
  },
  {
    fileName: "insight.png",
    crop: { left: 780, top: 28, width: 342, height: 444 }
  },
  {
    fileName: "blog-writer.png",
    crop: { left: 1152, top: 32, width: 350, height: 440 }
  },
  {
    fileName: "linkedin-writer.png",
    crop: { left: 26, top: 548, width: 334, height: 420 }
  },
  {
    fileName: "telegram-newsletter.png",
    crop: { left: 410, top: 548, width: 334, height: 420 }
  },
  {
    fileName: "self-reflection.png",
    crop: { left: 790, top: 548, width: 334, height: 420 }
  },
  {
    fileName: "revision.png",
    crop: { left: 1158, top: 548, width: 350, height: 420 }
  }
];

function isConnectedCardBackground(r, g, b) {
  const brightness = (r + g + b) / 3;
  const channelSpread = Math.max(r, g, b) - Math.min(r, g, b);

  return brightness > 204 && channelSpread < 52;
}

function removeConnectedBackground(buffer, width, height) {
  const visited = new Uint8Array(width * height);
  const stack = [];

  const pushIfBackground = (x, y) => {
    if (x < 0 || y < 0 || x >= width || y >= height) return;
    const index = y * width + x;
    if (visited[index]) return;

    const offset = index * 4;
    const r = buffer[offset];
    const g = buffer[offset + 1];
    const b = buffer[offset + 2];

    if (!isConnectedCardBackground(r, g, b)) return;
    visited[index] = 1;
    stack.push(index);
  };

  for (let x = 0; x < width; x += 1) {
    pushIfBackground(x, 0);
    pushIfBackground(x, height - 1);
  }

  for (let y = 0; y < height; y += 1) {
    pushIfBackground(0, y);
    pushIfBackground(width - 1, y);
  }

  while (stack.length > 0) {
    const index = stack.pop();
    const x = index % width;
    const y = Math.floor(index / width);
    const offset = index * 4;
    buffer[offset + 3] = 0;

    pushIfBackground(x + 1, y);
    pushIfBackground(x - 1, y);
    pushIfBackground(x, y + 1);
    pushIfBackground(x, y - 1);
  }

  return buffer;
}

async function createTransparentAvatar({ crop, fileName }) {
  const { data, info } = await sharp(sheetPath)
    .extract(crop)
    .ensureAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true });

  const cleaned = removeConnectedBackground(Buffer.from(data), info.width, info.height);

  const trimmed = await sharp(cleaned, {
    raw: {
      width: info.width,
      height: info.height,
      channels: 4
    }
  })
    .trim({ background: { r: 0, g: 0, b: 0, alpha: 0 }, threshold: 8 })
    .resize(232, 232, {
      fit: "contain",
      background: { r: 0, g: 0, b: 0, alpha: 0 }
    })
    .extend({
      top: 14,
      bottom: 14,
      left: 14,
      right: 14,
      background: { r: 0, g: 0, b: 0, alpha: 0 }
    })
    .png()
    .toBuffer();

  await sharp(trimmed).png().toFile(path.join(outputDir, fileName));
}

async function createPublishAvatarFromRevision() {
  const publishPath = path.join(outputDir, "publish.png");
  try {
    await fs.access(publishPath);
    return;
  } catch {
    // Keep the generated publish avatar when present. This fallback only prevents a missing asset.
  }

  await fs.copyFile(
    path.join(outputDir, "revision.png"),
    publishPath
  );
}

async function createVisualAgentAvatars() {
  const copies = [
    ["insight.png", "visual-strategy.png"],
    ["linkedin-writer.png", "image-prompt.png"],
    ["publish.png", "image-generator.png"],
    ["self-reflection.png", "visual-quality.png"]
  ];

  await Promise.all(
    copies.map(([source, target]) =>
      fs.copyFile(path.join(outputDir, source), path.join(outputDir, target))
    )
  );
}

await fs.mkdir(outputDir, { recursive: true });
await Promise.all(avatars.map(createTransparentAvatar));
await createPublishAvatarFromRevision();
await createVisualAgentAvatars();

console.log(`extracted ${avatars.length} original transparent avatar assets and visual agent aliases in ${outputDir}`);

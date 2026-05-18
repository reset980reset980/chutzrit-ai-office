import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(appDir, "../..");
const broadcastingRoot = path.join(repoRoot, "outputs/broadcasting");
const generatedDir = path.join(appDir, "src/data/generated");
const generatedPath = path.join(generatedDir, "officeStatus.json");
const publicGeneratedRoot = path.join(appDir, "public/generated/broadcasting");
const currentStatusPath = path.join(broadcastingRoot, "logs/current-status.json");

const today = new Intl.DateTimeFormat("en-CA", {
  timeZone: "Asia/Tokyo",
  year: "numeric",
  month: "2-digit",
  day: "2-digit"
}).format(new Date());

const agentIds = [
  "input-parser",
  "content-strategy",
  "insight",
  "blog-writer",
  "linkedin-writer",
  "telegram-newsletter",
  "self-reflection",
  "revision",
  "visual-strategy",
  "image-prompt",
  "image-generator",
  "visual-observation",
  "visual-quality",
  "publish"
];

async function readJson(filePath) {
  try {
    return JSON.parse(await fs.readFile(filePath, "utf8"));
  } catch {
    return null;
  }
}

async function readText(filePath) {
  return fs.readFile(filePath, "utf8").catch(() => "");
}

async function fileExists(filePath) {
  try {
    const stat = await fs.stat(filePath);
    return stat.isFile();
  } catch {
    return false;
  }
}

async function dirExists(dirPath) {
  try {
    const stat = await fs.stat(dirPath);
    return stat.isDirectory();
  } catch {
    return false;
  }
}

async function listPackageDirs(scope) {
  const scopeDir = path.join(broadcastingRoot, scope);
  if (!(await dirExists(scopeDir))) return [];

  const entries = await fs.readdir(scopeDir, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(scopeDir, entry.name));
}

function getRecordDate(record) {
  return String(record.generatedAt || record.executedAt || "").slice(0, 10);
}

function hasPublishedChannel(record) {
  const statuses = Object.values(record.channelPublishStatus || {});
  const urls = Object.values(record.publishedUrls || {});
  return statuses.includes("published") || urls.some(Boolean);
}

function normalizeNewsletterChannels(value) {
  const normalized = { ...(value || {}) };
  if (normalized.discord && !normalized.telegram) {
    normalized.telegram = normalized.discord;
  }
  delete normalized.discord;
  return normalized;
}

function sanitizeDisplayText(value) {
  return String(value || "")
    .replaceAll("Discord 뉴스레터", "Telegram 뉴스레터")
    .replaceAll("Discord", "Telegram")
    .replaceAll("discord", "telegram");
}

function toPublicUrl(relativePath) {
  return `/${relativePath.split(path.sep).map(encodeURIComponent).join("/")}`;
}

function getPackageStatus(record) {
  if (record.externalApiStatus === "failed") return "failed";
  if (Object.values(record.channelPublishStatus || {}).includes("failed")) return "failed";
  if (Object.values(record.channelPublishStatus || {}).includes("blocked_until_blog_url")) {
    return "blocked";
  }
  if (hasPublishedChannel(record)) return "published";
  if (record.qualityPassed) return "ready";
  return "review";
}

function getFirstContentLine(markdown) {
  if (!markdown) return "";
  return markdown
    .split("\n")
    .map((line) => line.trim())
    .find((line) => line && !line.startsWith("#")) || "";
}

async function copyVisualPreviews(scope, packageId, packageDir, visualAssets) {
  const assets = visualAssets?.assets || {};
  const previews = {};

  for (const [channel, asset] of Object.entries(assets)) {
    if (!asset || typeof asset !== "object") continue;

    const sourcePath = asset.path
      ? path.resolve(String(asset.path))
      : path.join(packageDir, String(asset.relative_path || ""));
    if (!(await fileExists(sourcePath))) continue;

    const extension = path.extname(sourcePath) || ".png";
    const publicRelativePath = path.join(
      "generated",
      "broadcasting",
      scope,
      packageId,
      "visuals",
      `${channel}${extension}`
    );
    const targetPath = path.join(appDir, "public", publicRelativePath);
    await fs.mkdir(path.dirname(targetPath), { recursive: true });
    await fs.copyFile(sourcePath, targetPath);

    previews[channel] = {
      url: toPublicUrl(publicRelativePath),
      status: asset.status || "",
      size: asset.size || "",
      quality: asset.quality || "",
      provider: asset.provider || "",
      model: asset.model || ""
    };
  }

  return previews;
}

async function readPackageDocuments(packageDir) {
  const documentSpecs = [
    ["blog", "Blog 원고", "blog.md"],
    ["linkedin", "LinkedIn 원고", "linkedin.md"],
    ["telegram", "Telegram 뉴스레터", "telegram.md"],
    ["strategy", "전략 문서", "strategy.md"],
    ["insight", "인사이트 문서", "insight.md"],
    ["reflection", "평가 문서", "reflection.md"],
    ["publish-plan", "배포 계획", "publish-plan.json"],
    ["visual-strategy", "이미지 전략", "visual-strategy.json"],
    ["image-prompts", "이미지 프롬프트", "image-prompts.json"],
    ["visual-assets", "이미지 산출물", "visual-assets.json"],
    ["visual-observations", "이미지 실제 검수", "visual-observations.json"],
    ["visual-quality", "이미지 평가", "visual-quality.json"],
    ["metadata", "메타데이터", "metadata.json"],
    ["approval-status", "승인 상태", "approval-status.json"]
  ];
  const documents = [];

  for (const [key, label, fileName] of documentSpecs) {
    const filePath = path.join(packageDir, fileName);
    const content = await readText(filePath);
    if (!content.trim()) continue;

    documents.push({
      key,
      label,
      fileName,
      path: path.relative(repoRoot, filePath),
      content: compactPreview(sanitizeDisplayText(content), 20000)
    });
  }

  return documents;
}

async function readPackage(scope, packageDir) {
  const metadata = await readJson(path.join(packageDir, "metadata.json"));
  if (!metadata) return null;

  const publishPlan = await readJson(path.join(packageDir, "publish-plan.json"));
  const visualAssets = await readJson(path.join(packageDir, "visual-assets.json"));
  const visualQuality = await readJson(path.join(packageDir, "visual-quality.json"));
  const sourceMarkdown = await readText(path.join(packageDir, "source.md"));
  const blogMarkdown = await readText(path.join(packageDir, "blog.md"));
  const linkedinMarkdown = await readText(path.join(packageDir, "linkedin.md"));
  const telegramMarkdown =
    (await readText(path.join(packageDir, "telegram.md"))) ||
    (await readText(path.join(packageDir, "discord.md")));

  const packageId = metadata.package_id || path.basename(packageDir);
  const visualPreviewUrls = await copyVisualPreviews(
    scope,
    packageId,
    packageDir,
    metadata.visual_assets ? { assets: metadata.visual_assets } : visualAssets
  );
  const documents = await readPackageDocuments(packageDir);
  const channelPublishStatus = normalizeNewsletterChannels(
    metadata.channel_publish_status ||
      Object.fromEntries(
        Object.entries(publishPlan?.channels || {}).map(([channel, value]) => [
          channel,
          value?.status || "unknown"
        ])
      )
  );

  const publishedUrls = normalizeNewsletterChannels(
    metadata.published_urls ||
      Object.fromEntries(
        Object.entries(publishPlan?.channels || {}).map(([channel, value]) => [
          channel,
          value?.url || ""
        ])
      )
  );
  const channelProcessingStatus = normalizeNewsletterChannels(
    metadata.channel_processing_status || {}
  );
  const publishChannels = publishPlan?.channels || {};
  const newsletterPublishChannel = publishChannels.telegram || publishChannels.discord || {};

  return {
    id: packageId,
    scope,
    title: metadata.title || packageId,
    generatedAt: metadata.generated_at || publishPlan?.executed_at || "",
    inputType: metadata.input_type || "unknown",
    sourceSummary: metadata.source_summary || getFirstContentLine(sourceMarkdown),
    targetPersona: metadata.target_persona || "",
    qualityScore: metadata.quality_score ?? null,
    qualityPassed: Boolean(metadata.quality_passed),
    revisionCount: metadata.revision_count ?? 0,
    channelProcessingStatus,
    channelPublishStatus,
    publishedUrls,
    visualAssetsStatus: metadata.visual_assets_status || visualAssets?.status || "",
    visualAssets: metadata.visual_assets || visualAssets?.assets || {},
    visualPreviewUrls,
    visualQuality: metadata.visual_quality || visualQuality || {},
    externalApiStatus: metadata.external_api_status || publishPlan?.external_api_status || "",
    path: path.relative(repoRoot, packageDir),
    statusReason:
      publishPlan?.channels?.blog?.reason ||
      publishPlan?.channels?.linkedin?.reason ||
      newsletterPublishChannel?.reason ||
      "",
    packageStatus: "unknown",
    previews: {
      blog: compactPreview(blogMarkdown),
      linkedin: compactPreview(linkedinMarkdown),
      telegram: compactPreview(telegramMarkdown)
    },
    documents
  };
}

function compactPreview(value, limit = 14000) {
  const text = String(value || "").trim();
  if (text.length <= limit) return text;
  return `${text.slice(0, limit).trim()}\n\n...`;
}

function dedupeById(records) {
  const byId = new Map();
  for (const record of records) {
    byId.set(record.id, record);
  }
  return [...byId.values()];
}

async function loadRecords(scope) {
  const records = [];
  for (const packageDir of await listPackageDirs(scope)) {
    const record = await readPackage(scope, packageDir);
    if (record) {
      record.packageStatus = getPackageStatus(record);
      records.push(record);
    }
  }

  return records.sort((a, b) => String(b.generatedAt).localeCompare(String(a.generatedAt)));
}

function buildMetricDetails({ todayDrafts, todayFinals, reviewQueue, publishedToday }) {
  return {
    inputs: {
      title: "오늘 입력",
      description: "outputs/broadcasting/drafts에서 오늘 생성된 입력 패키지",
      records: todayDrafts
    },
    completed: {
      title: "작성 완료",
      description: "outputs/broadcasting/final에 저장된 오늘 최종본",
      records: todayFinals
    },
    review: {
      title: "검토 대기",
      description: "최종본이 없거나 품질 통과 전 상태인 오늘 패키지",
      records: reviewQueue
    },
    published: {
      title: "배포 완료",
      description: "오늘 최종본 중 하나 이상의 채널에 published URL 또는 published 상태가 있는 패키지",
      records: publishedToday
    }
  };
}

function getLatest(records) {
  return [...records].sort((a, b) => String(b.generatedAt).localeCompare(String(a.generatedAt)))[0];
}

function normalizeAgentStatus(value) {
  const normalized = String(value || "").toUpperCase();
  return ["WORKING", "IDLE", "REVIEW", "ERROR"].includes(normalized) ? normalized : null;
}

function getRuntimeAgent(currentStatus, id) {
  const agents = currentStatus?.agents;
  if (!agents) return null;
  if (Array.isArray(agents)) return agents.find((agent) => agent?.id === id) || null;
  if (typeof agents === "object") return agents[id] || null;
  return null;
}

function getCodexUsage(currentStatus) {
  const usage =
    currentStatus?.codexUsage || currentStatus?.codex_usage || currentStatus?.codex || null;
  if (!usage || typeof usage !== "object") return null;

  const used = Number(usage.used ?? usage.tokensUsed ?? usage.tokens_used);
  const limit = Number(usage.limit ?? usage.tokenLimit ?? usage.token_limit);
  if (!Number.isFinite(used) || !Number.isFinite(limit) || limit <= 0) return null;

  return {
    status: "available",
    used,
    limit,
    percentage: Math.min(100, Math.round((used / limit) * 100)),
    label: usage.label || "Codex 사용량",
    reason: "outputs/broadcasting/logs/current-status.json에서 읽은 값"
  };
}

function getTextValue(source, keys, fallback) {
  for (const key of keys) {
    if (typeof source?.[key] === "string" && source[key].trim()) {
    return sanitizeDisplayText(source[key]);
    }
  }

  return sanitizeDisplayText(fallback);
}

function isPendingReview(record) {
  if (hasPublishedChannel(record)) return false;

  const statuses = Object.values(record.channelPublishStatus || {});
  return (
    !record.qualityPassed ||
    ["approval_required", "auto_dispatch_pending", "review", "pending"].some((status) =>
      statuses.includes(status)
    )
  );
}

function getSnapshotStatus(id, { todayDrafts, reviewQueue, publishedToday }) {
  if (todayDrafts.length === 0) return "IDLE";

  if (reviewQueue.length > 0) {
    return [
      "blog-writer",
      "linkedin-writer",
      "self-reflection",
      "revision",
      "visual-strategy",
      "image-prompt",
      "image-generator",
      "visual-quality"
    ].includes(id)
      ? "WORKING"
      : "IDLE";
  }

  if (publishedToday.length > 0) {
    return ["telegram-newsletter", "publish"].includes(id) ? "WORKING" : "IDLE";
  }

  return ["input-parser", "content-strategy", "insight"].includes(id) ? "WORKING" : "IDLE";
}

function getSnapshotTask(id, status) {
  if (status === "IDLE") {
    return "휴식 중이다. 다음 입력이 들어오면 자동으로 재개한다.";
  }

  const tasks = {
    "input-parser": "최근 입력 패키지를 분석 중이다.",
    "content-strategy": "최근 입력의 콘텐츠 방향을 정리 중이다.",
    insight: "후츠릿 관점의 실무 인사이트를 보강 중이다.",
    "blog-writer": "검토 대기 패키지의 블로그 원고 상태를 확인 중이다.",
    "linkedin-writer": "검토 대기 패키지의 LinkedIn 원고 상태를 확인 중이다.",
    "telegram-newsletter": "Telegram 뉴스레터 발송 상태를 확인 중이다.",
    "visual-strategy": "최근 패키지의 이미지 콘셉트를 확인 중이다.",
    "image-prompt": "최근 패키지의 이미지 프롬프트를 확인 중이다.",
    "image-generator": "최근 패키지의 이미지 생성 상태를 확인 중이다.",
    "visual-observation": "최근 패키지의 실제 이미지 관찰 결과를 확인 중이다.",
    "visual-quality": "최근 패키지의 이미지 적합성을 확인 중이다.",
    "self-reflection": "검토 대기 패키지의 품질 점수를 점검 중이다.",
    revision: "기준 미달 또는 승인 대기 패키지의 수정 포인트를 확인 중이다.",
    publish: "최근 배포 링크와 채널별 게시 상태를 확인 중이다."
  };

  return tasks[id] || "오늘 산출물 기준으로 상태를 정리 중이다.";
}

function deriveAgents({ latest, currentStatus, todayDrafts, reviewQueue, publishedToday }) {
  const hasCurrentStatus = Boolean(currentStatus);
  const idleTask = hasCurrentStatus
    ? "현재 운영 상태를 표시한다."
    : "오늘 산출물 기준으로 운영 화면을 표시한다.";

  const common = {
    status: "IDLE",
    statusSource: hasCurrentStatus ? "실시간 운영 상태" : "오늘 산출물 스냅샷",
    currentTask: idleTask,
    nextTask: "새 broadcasting 입력이 들어오면 파이프라인을 다시 실행한다.",
    updatedAt: latest?.generatedAt || ""
  };

  const publishHasIssue =
    latest?.externalApiStatus === "failed" ||
    Object.values(latest?.channelPublishStatus || {}).some((status) =>
      ["failed", "blocked_until_blog_url"].includes(status)
    );

  const agents = {
    "input-parser": {
      ...common,
      recentOutput: latest
        ? `최근 입력 타입 ${latest.inputType}: ${latest.sourceSummary || latest.title}`
        : "아직 outputs 기반 입력 기록이 없다."
    },
    "content-strategy": {
      ...common,
      recentOutput: latest?.targetPersona
        ? `최근 타깃 독자: ${latest.targetPersona}`
        : "최근 전략 기록이 없다."
    },
    insight: {
      ...common,
      recentOutput: latest?.sourceSummary
        ? `최근 핵심 맥락: ${latest.sourceSummary}`
        : "최근 인사이트 기록이 없다."
    },
    "blog-writer": {
      ...common,
      recentOutput: `블로그 채널 상태: ${latest?.channelProcessingStatus?.blog || "기록 없음"}`
    },
    "linkedin-writer": {
      ...common,
      recentOutput: `LinkedIn 채널 상태: ${
        latest?.channelProcessingStatus?.linkedin || "기록 없음"
      }`
    },
    "telegram-newsletter": {
      ...common,
      recentOutput: `Telegram 뉴스레터 상태: ${
        latest?.channelPublishStatus?.telegram || latest?.channelProcessingStatus?.telegram || "기록 없음"
      }`
    },
    "visual-strategy": {
      ...common,
      recentOutput: `이미지 콘셉트 상태: ${latest?.visualAssetsStatus || "기록 없음"}`
    },
    "image-prompt": {
      ...common,
      recentOutput: `이미지 프롬프트 상태: ${
        latest?.visualAssetsStatus === "pending_generation" ? "생성 대기" : latest?.visualAssetsStatus || "기록 없음"
      }`
    },
    "image-generator": {
      ...common,
      recentOutput: `이미지 생성 상태: ${latest?.visualAssetsStatus || "기록 없음"}`
    },
    "visual-observation": {
      ...common,
      recentOutput:
        latest?.visualQuality?.score == null
          ? "실제 이미지 관찰 기록 없음"
          : `실제 PNG 검수 후 이미지 품질 ${latest.visualQuality.score}점`
    },
    "visual-quality": {
      ...common,
      recentOutput:
        latest?.visualQuality?.score == null
          ? "이미지 품질 기록 없음"
          : `이미지 품질 점수 ${latest.visualQuality.score}점`
    },
    "self-reflection": {
      ...common,
      recentOutput:
        latest?.qualityScore == null
          ? "최근 품질 점수 기록이 없다."
          : `최근 품질 점수 ${latest.qualityScore}점, 통과 여부 ${
              latest.qualityPassed ? "통과" : "미통과"
            }`
    },
    revision: {
      ...common,
      recentOutput: `최근 수정 루프 ${latest?.revisionCount ?? 0}회`
    },
    publish: {
      ...common,
      status: publishHasIssue ? "ERROR" : latest && hasPublishedChannel(latest) ? "IDLE" : "IDLE",
      currentTask: publishHasIssue
        ? "마지막 배포 결과에 실패 또는 중단 채널이 있어 확인이 필요하다."
        : idleTask,
      recentOutput: latest
        ? `최근 배포 상태: ${JSON.stringify(latest.channelPublishStatus)}`
        : "아직 배포 기록이 없다.",
      nextTask: publishHasIssue
        ? "실패 원인을 확인하고 배포 어댑터 조건을 맞춘 뒤 재시도한다."
        : common.nextTask
    }
  };

  return agentIds.reduce((result, id) => {
    const runtimeAgent = getRuntimeAgent(currentStatus, id);
    const outputAgent = agents[id];

    if (runtimeAgent) {
      result[id] = {
        ...outputAgent,
        status: normalizeAgentStatus(runtimeAgent.status) || outputAgent.status,
        statusSource: "실시간 운영 상태",
        currentTask: getTextValue(
          runtimeAgent,
          ["currentTask", "current_task", "task", "activity"],
          outputAgent.currentTask
        ),
        recentOutput: getTextValue(
          runtimeAgent,
          ["recentOutput", "recent_output", "lastOutput", "last_output"],
          outputAgent.recentOutput
        ),
        nextTask: getTextValue(
          runtimeAgent,
          ["nextTask", "next_task", "next"],
          outputAgent.nextTask
        ),
        updatedAt: getTextValue(
          runtimeAgent,
          ["updatedAt", "updated_at", "timestamp", "lastUpdated"],
          outputAgent.updatedAt
        )
      };
      return result;
    }

    const snapshotStatus = getSnapshotStatus(id, {
      todayDrafts,
      reviewQueue,
      publishedToday
    });

    result[id] = {
      ...outputAgent,
      status: snapshotStatus,
      currentTask: getSnapshotTask(id, snapshotStatus)
    };
    return result;
  }, {});
}

await fs.rm(publicGeneratedRoot, { recursive: true, force: true });
await fs.mkdir(publicGeneratedRoot, { recursive: true });

const currentStatus = await readJson(currentStatusPath);
const draftRecords = await loadRecords("drafts");
const finalRecords = await loadRecords("final");
const todayDrafts = draftRecords.filter((record) => getRecordDate(record) === today);
const todayFinals = finalRecords.filter((record) => getRecordDate(record) === today);
const finalIds = new Set(finalRecords.map((record) => record.id));
const reviewQueue = todayDrafts.filter(
  (record) => !finalIds.has(record.id) || isPendingReview(record)
);
const publishedToday = todayFinals.filter(hasPublishedChannel);
const latest = getLatest(dedupeById([...finalRecords, ...draftRecords]));
const hasCurrentStatus = Boolean(currentStatus);
const codexUsage = getCodexUsage(currentStatus);
const demoCodexLimit = 200000;
const demoCodexUsed = Math.min(
  demoCodexLimit,
  42000 + todayDrafts.length * 3400 + reviewQueue.length * 1600 + publishedToday.length * 1200
);

const generated = {
  generatedAt: new Date().toISOString(),
  today,
  dataSource: {
    broadcastingRoot: path.relative(repoRoot, broadcastingRoot),
    liveStatusFile: path.relative(repoRoot, currentStatusPath),
    liveStatusAvailable: hasCurrentStatus,
    codexUsageAvailable: Boolean(codexUsage),
    codexUsageReason: codexUsage
      ? "current-status.json에 Codex 사용량이 기록되어 있다."
      : "오늘 산출물 기준 사용량 추정치를 표시한다."
  },
  tokenUsage:
    codexUsage || {
      status: "available",
      used: demoCodexUsed,
      limit: demoCodexLimit,
      percentage: Math.round((demoCodexUsed / demoCodexLimit) * 100),
      label: "Codex 사용량",
      reason: "오늘 산출물 기준 사용량 추정"
    },
  metrics: {
    todayInputs: todayDrafts.length,
    completedContents: todayFinals.length,
    reviewQueue: reviewQueue.length,
    published: publishedToday.length,
    overallProgress:
      todayDrafts.length === 0 ? 0 : Math.round((todayFinals.length / todayDrafts.length) * 100),
    systemStatus: hasCurrentStatus
      ? "실시간 운영 상태 동기화 중"
      : "오늘 산출물 기준 · 자동화 대기 중"
  },
  metricDetails: buildMetricDetails({
    todayDrafts,
    todayFinals,
    reviewQueue,
    publishedToday
  }),
  latestPackage: latest || null,
  derivedAgents: deriveAgents({
    latest,
    currentStatus,
    todayDrafts,
    reviewQueue,
    publishedToday
  })
};

await fs.mkdir(generatedDir, { recursive: true });
await fs.writeFile(generatedPath, `${JSON.stringify(generated, null, 2)}\n`);
console.log(`generated dashboard status from ${broadcastingRoot}`);

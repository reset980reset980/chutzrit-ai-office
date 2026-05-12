import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(appDir, "../..");
const broadcastingRoot = path.join(repoRoot, "outputs/broadcasting");
const generatedDir = path.join(appDir, "src/data/generated");
const generatedPath = path.join(generatedDir, "officeStatus.json");
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
  "discord-newsletter",
  "self-reflection",
  "revision",
  "publish"
];

async function readJson(filePath) {
  try {
    return JSON.parse(await fs.readFile(filePath, "utf8"));
  } catch {
    return null;
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

async function readPackage(scope, packageDir) {
  const metadata = await readJson(path.join(packageDir, "metadata.json"));
  if (!metadata) return null;

  const publishPlan = await readJson(path.join(packageDir, "publish-plan.json"));
  const sourceMarkdown = await fs
    .readFile(path.join(packageDir, "source.md"), "utf8")
    .catch(() => "");

  const packageId = metadata.package_id || path.basename(packageDir);
  const channelPublishStatus =
    metadata.channel_publish_status ||
    Object.fromEntries(
      Object.entries(publishPlan?.channels || {}).map(([channel, value]) => [
        channel,
        value?.status || "unknown"
      ])
    );

  const publishedUrls =
    metadata.published_urls ||
    Object.fromEntries(
      Object.entries(publishPlan?.channels || {}).map(([channel, value]) => [
        channel,
        value?.url || ""
      ])
    );

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
    channelProcessingStatus: metadata.channel_processing_status || {},
    channelPublishStatus,
    publishedUrls,
    externalApiStatus: metadata.external_api_status || publishPlan?.external_api_status || "",
    path: path.relative(repoRoot, packageDir),
    statusReason:
      publishPlan?.channels?.blog?.reason ||
      publishPlan?.channels?.linkedin?.reason ||
      publishPlan?.channels?.discord?.reason ||
      "",
    packageStatus: "unknown"
  };
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
      return source[key];
    }
  }

  return fallback;
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
    return ["blog-writer", "linkedin-writer", "self-reflection", "revision"].includes(id)
      ? "WORKING"
      : "IDLE";
  }

  if (publishedToday.length > 0) {
    return ["discord-newsletter", "publish"].includes(id) ? "WORKING" : "IDLE";
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
    "discord-newsletter": "Discord 뉴스레터 발송 상태를 확인 중이다.",
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
    "discord-newsletter": {
      ...common,
      recentOutput: `Discord 뉴스레터 상태: ${
        latest?.channelPublishStatus?.discord || latest?.channelProcessingStatus?.discord || "기록 없음"
      }`
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

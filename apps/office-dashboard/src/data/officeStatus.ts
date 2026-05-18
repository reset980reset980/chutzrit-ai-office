import generatedStatus from "./generated/officeStatus.json";
import { assetPaths } from "./assets";
import type {
  Agent,
  AgentMotion,
  AgentStatus,
  MetricDetail,
  MetricKey,
  OfficeDataSource,
  OfficeMetrics,
  OfficeStatus,
  TokenUsage
} from "../types";

type GeneratedAgentState = {
  status: AgentStatus;
  statusSource: string;
  currentTask: string;
  recentOutput: string;
  nextTask: string;
  updatedAt: string;
};

type GeneratedStatus = {
  dataSource: OfficeDataSource;
  tokenUsage: TokenUsage;
  metrics: OfficeMetrics;
  metricDetails: Record<MetricKey, MetricDetail>;
  derivedAgents: Record<string, GeneratedAgentState>;
};

const liveData = generatedStatus as GeneratedStatus;

const agentDefinitions = [
  {
    id: "input-parser",
    name: "입력 분석가",
    role: "Telegram 입력 분석",
    position: { x: 10, y: 50 }
  },
  {
    id: "content-strategy",
    name: "콘텐츠 전략가",
    role: "핵심 메시지와 플랫폼 방향 설계",
    position: { x: 29, y: 42 }
  },
  {
    id: "insight",
    name: "인사이트 설계자",
    role: "후츠릿 관점과 실무 포인트 보강",
    position: { x: 43, y: 42 }
  },
  {
    id: "blog-writer",
    name: "블로그 작가",
    role: "블로그 원고 작성",
    position: { x: 55, y: 42 }
  },
  {
    id: "linkedin-writer",
    name: "LinkedIn 작가",
    role: "LinkedIn 게시글 작성",
    position: { x: 69, y: 42 }
  },
  {
    id: "telegram-newsletter",
    name: "뉴스레터 작가",
    role: "Telegram 뉴스레터 작성",
    position: { x: 83, y: 42 }
  },
  {
    id: "self-reflection",
    name: "품질 검수자",
    role: "완성본 품질 평가",
    position: { x: 31, y: 72 }
  },
  {
    id: "revision",
    name: "수정 담당자",
    role: "기준 미달 원고 수정",
    position: { x: 43, y: 72 }
  },
  {
    id: "visual-strategy",
    name: "비주얼 전략가",
    role: "이미지 콘셉트 설계",
    position: { x: 55, y: 72 }
  },
  {
    id: "image-prompt",
    name: "이미지 프롬프트 작가",
    role: "생성 프롬프트 작성",
    position: { x: 67, y: 72 }
  },
  {
    id: "image-generator",
    name: "이미지 제작자",
    role: "대표 이미지 생성",
    position: { x: 79, y: 72 }
  },
  {
    id: "visual-quality",
    name: "이미지 검수자",
    role: "이미지 적합성 평가",
    position: { x: 91, y: 72 }
  },
  {
    id: "publish",
    name: "배포 담당자",
    role: "멀티플랫폼 배포 상태 확인",
    position: { x: 80, y: 88 }
  }
] as const;

function getMotion(id: string, status: AgentStatus): AgentMotion {
  if (status === "ERROR") return "error";
  if (status === "IDLE") return "resting";
  if (status === "REVIEW") return id === "revision" ? "revising" : "reviewing";

  if (id === "input-parser") return "reading";
  if (id === "content-strategy" || id === "insight" || id === "visual-strategy" || id === "image-prompt") {
    return "thinking";
  }
  if (id === "publish") return "publishing";
  return "typing";
}

function getEnergyLevel(id: string, status: AgentStatus) {
  if (status === "ERROR") return 31;
  if (status === "REVIEW") return 68;

  const baseByAgent: Record<string, number> = {
    "input-parser": 91,
    "content-strategy": 86,
    insight: 84,
    "blog-writer": 78,
    "linkedin-writer": 76,
    "telegram-newsletter": 82,
    "self-reflection": 73,
    revision: 71,
    "visual-strategy": 82,
    "image-prompt": 79,
    "image-generator": 88,
    "visual-quality": 76,
    publish: 88
  };

  const base = baseByAgent[id] ?? 80;
  return status === "WORKING" ? Math.max(58, base - 8) : base;
}

function buildAgent(definition: (typeof agentDefinitions)[number]): Agent {
  const derived = liveData.derivedAgents[definition.id];
  const status = derived?.status ?? "IDLE";

  return {
    ...definition,
    status,
    avatar: assetPaths.avatars[definition.id],
    motion: getMotion(definition.id, status),
    energyLevel: getEnergyLevel(definition.id, status),
    currentTask: derived?.currentTask ?? "상태 데이터 없음",
    recentOutput: derived?.recentOutput ?? "최근 산출물 기록 없음",
    nextTask: derived?.nextTask ?? "새 입력 대기",
    updatedAt: derived?.updatedAt ?? "",
    statusSource: derived?.statusSource
  };
}

const publishStatus = liveData.derivedAgents.publish?.status ?? "IDLE";
const hasWorkingWriters = [
  "blog-writer",
  "linkedin-writer",
  "telegram-newsletter"
].some((id) => liveData.derivedAgents[id]?.status === "WORKING");
const hasWorkingReview = ["self-reflection", "revision"].some(
  (id) => liveData.derivedAgents[id]?.status === "WORKING"
);
const hasWorkingVisuals = [
  "visual-strategy",
  "image-prompt",
  "image-generator",
  "visual-quality"
].some((id) => liveData.derivedAgents[id]?.status === "WORKING");

export const officeStatus: OfficeStatus = {
  teamName: "콘텐츠배포팀",
  title: "후츠릿 AI 오피스",
  subtitle: "24시간 무인 AI 콘텐츠 제작 파이프라인",
  tokenUsage: liveData.tokenUsage,
  metrics: liveData.metrics,
  metricDetails: liveData.metricDetails,
  dataSource: liveData.dataSource,
  pipelineStages: [
    {
      id: "telegram-input",
      label: "Telegram Input",
      detail: "outputs 입력 기록",
      status: "IDLE",
      position: { x: 10, y: 12 }
    },
    {
      id: "strategy",
      label: "Strategy",
      detail: "전략 산출물 기록",
      status: "IDLE",
      position: { x: 30, y: 12 }
    },
    {
      id: "writers",
      label: "Writers",
      detail: "채널별 원고 기록",
      status: hasWorkingWriters ? "WORKING" : "IDLE",
      position: { x: 52, y: 12 }
    },
    {
      id: "review",
      label: "Review",
      detail: "품질 점수 기록",
      status: hasWorkingReview ? "WORKING" : "IDLE",
      position: { x: 68, y: 12 }
    },
    {
      id: "visuals",
      label: "Visuals",
      detail: "대표 이미지 기록",
      status: hasWorkingVisuals ? "WORKING" : "IDLE",
      position: { x: 80, y: 12 }
    },
    {
      id: "publish",
      label: "Publish",
      detail: "배포 결과 기록",
      status: publishStatus,
      position: { x: 92, y: 12 }
    }
  ],
  agents: agentDefinitions.map(buildAgent)
};

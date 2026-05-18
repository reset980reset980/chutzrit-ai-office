export type AgentStatus = "WORKING" | "IDLE" | "REVIEW" | "ERROR";

export type AgentMotion =
  | "typing"
  | "thinking"
  | "reading"
  | "reviewing"
  | "revising"
  | "publishing"
  | "resting"
  | "error";

export type Agent = {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
  avatar: string;
  motion: AgentMotion;
  energyLevel: number;
  position: {
    x: number;
    y: number;
  };
  currentTask: string;
  recentOutput: string;
  nextTask: string;
  updatedAt: string;
  statusSource?: string;
};

export type PipelineStage = {
  id: string;
  label: string;
  detail: string;
  status: AgentStatus;
  position: {
    x: number;
    y: number;
  };
};

export type TokenUsage =
  | {
      status: "available";
      used: number;
      limit: number;
      percentage: number;
      label?: string;
      reason?: string;
    }
  | {
      status: "unavailable";
      label: string;
      reason: string;
      used?: never;
      limit?: never;
      percentage?: never;
    };

export type MetricKey = "inputs" | "completed" | "review" | "published";

export type BroadcastingRecord = {
  id: string;
  scope: string;
  title: string;
  generatedAt: string;
  inputType: string;
  sourceSummary: string;
  targetPersona: string;
  qualityScore: number | null;
  qualityPassed: boolean;
  revisionCount: number;
  channelProcessingStatus: Record<string, string>;
  channelPublishStatus: Record<string, string>;
  publishedUrls: Record<string, string>;
  visualAssetsStatus?: string;
  visualAssets?: Record<string, { status?: string; path?: string; relative_path?: string }>;
  visualPreviewUrls?: Record<
    string,
    {
      url: string;
      status?: string;
      size?: string;
      quality?: string;
      provider?: string;
      model?: string;
    }
  >;
  visualQuality?: { score?: number; passed?: boolean };
  externalApiStatus: string;
  path: string;
  statusReason: string;
  packageStatus: string;
  previews: {
    blog: string;
    linkedin: string;
    telegram: string;
  };
  documents?: Array<{
    key: string;
    label: string;
    fileName: string;
    path: string;
    content: string;
  }>;
};

export type MetricDetail = {
  title: string;
  description: string;
  records: BroadcastingRecord[];
};

export type OfficeDataSource = {
  broadcastingRoot: string;
  liveStatusFile: string;
  liveStatusAvailable: boolean;
  codexUsageAvailable: boolean;
  codexUsageReason: string;
};

export type OfficeMetrics = {
  todayInputs: number;
  completedContents: number;
  reviewQueue: number;
  published: number;
  overallProgress: number;
  systemStatus: string;
};

export type OfficeStatus = {
  teamName: string;
  title: string;
  subtitle: string;
  tokenUsage: TokenUsage;
  metrics: OfficeMetrics;
  metricDetails: Record<MetricKey, MetricDetail>;
  dataSource: OfficeDataSource;
  pipelineStages: PipelineStage[];
  agents: Agent[];
};

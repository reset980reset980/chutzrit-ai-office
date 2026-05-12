import { CheckCircle2, Clock3, Inbox, Rocket, ShieldCheck } from "lucide-react";
import type { MetricKey, OfficeMetrics } from "../types";

type BottomStatusBarProps = {
  metrics: OfficeMetrics;
  now: Date;
  selectedMetric: MetricKey | null;
  onSelectMetric: (metric: MetricKey) => void;
};

const timeFormatter = new Intl.DateTimeFormat("ko-KR", {
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false
});

const metricItems: Array<{
  key: MetricKey;
  label: string;
  field: keyof Pick<
    OfficeMetrics,
    "todayInputs" | "completedContents" | "reviewQueue" | "published"
  >;
  Icon: typeof Inbox;
}> = [
  { key: "inputs", label: "오늘 입력", field: "todayInputs", Icon: Inbox },
  { key: "completed", label: "작성 완료", field: "completedContents", Icon: CheckCircle2 },
  { key: "review", label: "검토 대기", field: "reviewQueue", Icon: ShieldCheck },
  { key: "published", label: "배포 완료", field: "published", Icon: Rocket }
];

export function BottomStatusBar({
  metrics,
  now,
  selectedMetric,
  onSelectMetric
}: BottomStatusBarProps) {
  return (
    <footer className="bottom-status-bar">
      {metricItems.map(({ key, label, field, Icon }) => (
        <button
          className={[
            "bottom-status-bar__metric",
            selectedMetric === key ? "bottom-status-bar__metric--selected" : ""
          ].join(" ")}
          key={key}
          type="button"
          aria-pressed={selectedMetric === key}
          onClick={() => onSelectMetric(key)}
        >
          <Icon size={18} />
          <span>{label}</span>
          <strong>{metrics[field]}</strong>
        </button>
      ))}
      <div className="bottom-status-bar__progress">
        <span>전체 진행률</span>
        <strong>{metrics.overallProgress}%</strong>
        <i style={{ width: `${metrics.overallProgress}%` }} />
      </div>
      <div className="bottom-status-bar__system">
        <ShieldCheck size={18} />
        <span>{metrics.systemStatus}</span>
      </div>
      <div className="bottom-status-bar__time">
        <Clock3 size={18} />
        <span>{timeFormatter.format(now)}</span>
      </div>
    </footer>
  );
}

import { ExternalLink, FileText, FolderOpen, X } from "lucide-react";
import type { MetricDetail, MetricKey, OfficeDataSource } from "../types";

type MetricDetailPanelProps = {
  metricKey: MetricKey;
  detail: MetricDetail;
  dataSource: OfficeDataSource;
  onClose: () => void;
};

const metricLabels: Record<MetricKey, string> = {
  inputs: "Input Packages",
  completed: "Final Packages",
  review: "Review Queue",
  published: "Published"
};

function formatGeneratedAt(value: string) {
  if (!value) return "시간 기록 없음";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("ko-KR", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  }).format(date);
}

function getChannelSummary(statuses: Record<string, string>) {
  const entries = Object.entries(statuses);
  if (entries.length === 0) return "채널 상태 기록 없음";
  return entries.map(([channel, status]) => `${channel}: ${status}`).join(" · ");
}

export function MetricDetailPanel({
  metricKey,
  detail,
  dataSource,
  onClose
}: MetricDetailPanelProps) {
  return (
    <aside className="metric-detail-panel" aria-label={`${detail.title} 상세 데이터`}>
      <div className="metric-detail-panel__header">
        <div>
          <span className="agent-detail-panel__eyebrow">{metricLabels[metricKey]}</span>
          <h2>{detail.title}</h2>
          <p>{detail.description}</p>
        </div>
        <button
          className="icon-button"
          type="button"
          aria-label="상세 패널 닫기"
          onClick={onClose}
        >
          <X size={18} />
        </button>
      </div>

      <div className="metric-detail-panel__source">
        <FolderOpen size={16} />
        <span>{dataSource.broadcastingRoot}</span>
      </div>

      <div className="metric-detail-panel__count">
        <strong>{detail.records.length}</strong>
        <span>건</span>
      </div>

      <div className="metric-detail-panel__records">
        {detail.records.length === 0 ? (
          <div className="metric-record metric-record--empty">
            <FileText size={18} />
            <span>표시할 실제 산출물이 없다.</span>
          </div>
        ) : (
          detail.records.map((record) => (
            <article className="metric-record" key={`${record.scope}-${record.id}`}>
              <div className="metric-record__topline">
                <strong>{record.title}</strong>
                <span>{formatGeneratedAt(record.generatedAt)}</span>
              </div>
              <p>{record.sourceSummary || record.statusReason || "요약 기록 없음"}</p>
              <div className="metric-record__meta">
                <span>{record.packageStatus}</span>
                <span>{record.inputType}</span>
                <span>
                  점수 {record.qualityScore == null ? "없음" : `${record.qualityScore}점`}
                </span>
                <span>수정 {record.revisionCount}회</span>
              </div>
              <div className="metric-record__status">
                {getChannelSummary(record.channelPublishStatus)}
              </div>
              <code>{record.path}</code>
              {Object.entries(record.publishedUrls).some(([, url]) => Boolean(url)) ? (
                <div className="metric-record__links">
                  {Object.entries(record.publishedUrls)
                    .filter(([, url]) => Boolean(url))
                    .map(([channel, url]) => (
                      <a href={url} key={channel} rel="noreferrer" target="_blank">
                        {channel}
                        <ExternalLink size={12} />
                      </a>
                    ))}
                </div>
              ) : null}
            </article>
          ))
        )}
      </div>
    </aside>
  );
}

import { ExternalLink, Eye, FileText, FolderOpen, Image, X } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { BroadcastingRecord, MetricDetail, MetricKey, OfficeDataSource } from "../types";

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

const previewChannels = [
  { key: "blog", label: "Blog" },
  { key: "linkedin", label: "LinkedIn" },
  { key: "telegram", label: "Telegram" }
] as const;

type PreviewChannel = (typeof previewChannels)[number]["key"];
type PreviewMode = "draft" | "visual" | "document";

const integratedDocumentKey = "__integrated";

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

function getPreviewText(record: BroadcastingRecord, channel: PreviewChannel) {
  return record.previews?.[channel]?.trim() || "아직 이 채널의 원고 파일이 생성되지 않았다.";
}

function getVisualSummary(record: BroadcastingRecord) {
  const status = record.visualAssetsStatus || "기록 없음";
  const count = Object.keys(record.visualAssets || {}).length;
  const score = record.visualQuality?.score == null ? "없음" : `${record.visualQuality.score}점`;
  return `이미지 ${status} · ${count}개 · 품질 ${score}`;
}

function getVisualEntries(record: BroadcastingRecord) {
  return Object.entries(record.visualPreviewUrls || {});
}

function getDocuments(record: BroadcastingRecord) {
  return record.documents || [];
}

function getChannelLabel(channel: PreviewChannel) {
  return previewChannels.find((item) => item.key === channel)?.label ?? channel;
}

function getVisualForChannel(record: BroadcastingRecord, channel: PreviewChannel) {
  return record.visualPreviewUrls?.[channel];
}

function getStatusEntries(record: BroadcastingRecord) {
  return Object.entries(record.channelPublishStatus || {});
}

function getReportScore(record: BroadcastingRecord) {
  return record.qualityScore == null ? "기록 없음" : `${record.qualityScore}점`;
}

function PublicationDocumentViewer({
  record,
  documentKey,
  onDocumentKeyChange
}: {
  record: BroadcastingRecord;
  documentKey: string;
  onDocumentKeyChange: (key: string) => void;
}) {
  const activeDocuments = getDocuments(record);
  const viewerRef = useRef<HTMLDivElement | null>(null);
  const activeDocument =
    documentKey === integratedDocumentKey
      ? null
      : activeDocuments.find((document) => document.key === documentKey) ?? activeDocuments[0];
  const isIntegratedDocument = documentKey === integratedDocumentKey || !documentKey;

  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer) return;

    const revealItems = Array.from(viewer.querySelectorAll<HTMLElement>("[data-reveal]"));
    revealItems.forEach((item) => item.classList.remove("is-visible"));

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      revealItems.forEach((item) => item.classList.add("is-visible"));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
          }
        });
      },
      {
        root: viewer.querySelector(".publication-preview") ?? null,
        rootMargin: "0px 0px -18% 0px",
        threshold: 0.08,
      },
    );

    revealItems.forEach((item) => observer.observe(item));
    return () => observer.disconnect();
  }, [documentKey, record.id]);

  return (
    <div className="publication-document-viewer" ref={viewerRef}>
      <div className="content-preview-panel__document-tabs" role="tablist" aria-label="배포 문서">
        <button
          className={
            isIntegratedDocument
              ? "content-preview-panel__subtab content-preview-panel__subtab--active"
              : "content-preview-panel__subtab"
          }
          type="button"
          role="tab"
          aria-selected={isIntegratedDocument}
          onClick={() => onDocumentKeyChange(integratedDocumentKey)}
        >
          통합 문서
        </button>
        {activeDocuments.map((document) => (
          <button
            key={document.key}
            className={
              !isIntegratedDocument && activeDocument?.key === document.key
                ? "content-preview-panel__subtab content-preview-panel__subtab--active"
                : "content-preview-panel__subtab"
            }
            type="button"
            role="tab"
            aria-selected={!isIntegratedDocument && activeDocument?.key === document.key}
            onClick={() => onDocumentKeyChange(document.key)}
          >
            {document.label}
          </button>
        ))}
      </div>
      <div className="publication-document-viewer__content">
        {isIntegratedDocument ? (
          <article className="publication-preview" aria-label="이미지 포함 통합 배포 문서">
            <header className="publication-preview__cover scroll-reveal" data-reveal>
              <div className="publication-preview__seal" aria-hidden="true">
                AI
              </div>
              <span className="publication-preview__kicker">통합 배포 문서</span>
              <h4>{record.title}</h4>
              <p>{record.sourceSummary || "원본 입력과 채널별 원고를 통합한 배포 미리보기입니다."}</p>
              <div className="publication-preview__status-grid" aria-label="보고서 상태">
                <div>
                  <span>품질</span>
                  <strong>{getReportScore(record)}</strong>
                </div>
                <div>
                  <span>이미지</span>
                  <strong>{record.visualAssetsStatus || "기록 없음"}</strong>
                </div>
                <div>
                  <span>수정</span>
                  <strong>{record.revisionCount}회</strong>
                </div>
              </div>
              <div className="publication-preview__chips" aria-label="채널 배포 상태">
                {getStatusEntries(record).length === 0 ? (
                  <span>채널 상태 기록 없음</span>
                ) : (
                  getStatusEntries(record).map(([channel, status]) => (
                    <span key={channel}>
                      {channel} · {status}
                    </span>
                  ))
                )}
              </div>
            </header>
            {previewChannels.map((channel, index) => {
              const visual = getVisualForChannel(record, channel.key);
              const draft = getPreviewText(record, channel.key);
              return (
                <section
                  className="publication-section scroll-reveal"
                  data-reveal
                  key={channel.key}
                  style={{ transitionDelay: `${Math.min(index * 80, 180)}ms` }}
                >
                  <div className="publication-section__heading">
                    <div>
                      <span>{channel.key.toUpperCase()}</span>
                      <strong>{getChannelLabel(channel.key)}</strong>
                    </div>
                    <mark>{record.channelPublishStatus[channel.key] || "draft"}</mark>
                  </div>
                  {visual ? (
                    <figure className="publication-section__visual">
                      <a href={visual.url} rel="noreferrer" target="_blank">
                        <img alt={`${getChannelLabel(channel.key)} 대표 이미지`} src={visual.url} />
                      </a>
                      <figcaption>
                        <span>{visual.size || "size unknown"}</span>
                        <span>{visual.quality || "quality unknown"}</span>
                      </figcaption>
                    </figure>
                  ) : (
                    <div className="content-preview-panel__empty">
                      {getChannelLabel(channel.key)} 대표 이미지가 아직 없다.
                    </div>
                  )}
                  <div className="publication-section__body">
                    <span className="publication-section__body-label">작성 원고</span>
                    {draft}
                  </div>
                </section>
              );
            })}
          </article>
        ) : activeDocument ? (
          <div className="publication-document-viewer__raw">
            <div className="content-preview-panel__document-path">{activeDocument.path}</div>
            <article className="content-preview-panel__body">{activeDocument.content}</article>
          </div>
        ) : (
          <div className="content-preview-panel__empty">표시할 배포 문서가 없다.</div>
        )}
      </div>
    </div>
  );
}

export function MetricDetailPanel({
  metricKey,
  detail,
  dataSource,
  onClose
}: MetricDetailPanelProps) {
  const firstPreviewRecord = detail.records.find((record) =>
    previewChannels.some((channel) => getPreviewText(record, channel.key).trim())
  );
  const [previewRecordId, setPreviewRecordId] = useState(firstPreviewRecord?.id ?? "");
  const [previewChannel, setPreviewChannel] = useState<PreviewChannel>("blog");
  const [previewMode, setPreviewMode] = useState<PreviewMode>("draft");
  const [documentKey, setDocumentKey] = useState("");
  const [isDocumentModalOpen, setIsDocumentModalOpen] = useState(false);

  const previewRecord = useMemo(
    () =>
      detail.records.find((record) => record.id === previewRecordId) ??
      firstPreviewRecord ??
      detail.records[0],
    [detail.records, firstPreviewRecord, previewRecordId]
  );
  function selectPreview(record: BroadcastingRecord, mode: PreviewMode) {
    setPreviewRecordId(record.id);
    setPreviewMode(mode);
  }

  function openDocumentModal(record: BroadcastingRecord) {
    setPreviewRecordId(record.id);
    setPreviewMode("document");
    setDocumentKey(integratedDocumentKey);
    setIsDocumentModalOpen(true);
  }

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
              <div className="metric-record__status">{getVisualSummary(record)}</div>
              <div className="metric-record__actions">
                <button
                  className="metric-record__preview-button"
                  type="button"
                  onClick={() => selectPreview(record, "draft")}
                >
                  <Eye size={14} />
                  원고
                </button>
                <button
                  className="metric-record__preview-button"
                  type="button"
                  onClick={() => selectPreview(record, "visual")}
                >
                  <Image size={14} />
                  이미지
                </button>
                <button
                  className="metric-record__preview-button"
                  type="button"
                  onClick={() => openDocumentModal(record)}
                >
                  <FileText size={14} />
                  문서
                </button>
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

      {previewRecord ? (
        <section className="content-preview-panel" aria-label="작성된 산출물 미리보기">
          <div className="content-preview-panel__header">
            <div>
              <span className="agent-detail-panel__eyebrow">Package Preview</span>
              <h3>{previewRecord.title}</h3>
            </div>
            <span>{formatGeneratedAt(previewRecord.generatedAt)}</span>
          </div>
          <div className="content-preview-panel__tabs" role="tablist" aria-label="미리보기 유형">
            {[
              { key: "draft", label: "원고" },
              { key: "visual", label: "이미지" },
              { key: "document", label: "배포 문서" }
            ].map((mode) => (
              <button
                key={mode.key}
                className={
                  previewMode === mode.key
                    ? "content-preview-panel__tab content-preview-panel__tab--active"
                    : "content-preview-panel__tab"
                }
                type="button"
                role="tab"
                aria-selected={previewMode === mode.key}
                onClick={() => {
                  setPreviewMode(mode.key as PreviewMode);
                  if (mode.key === "document" && previewRecord) {
                    setDocumentKey(integratedDocumentKey);
                    setIsDocumentModalOpen(true);
                  }
                }}
              >
                {mode.label}
              </button>
            ))}
          </div>
          {previewMode === "draft" ? (
            <>
              <div className="content-preview-panel__subtabs" role="tablist" aria-label="원고 채널">
                {previewChannels.map((channel) => (
                  <button
                    key={channel.key}
                    className={
                      previewChannel === channel.key
                        ? "content-preview-panel__subtab content-preview-panel__subtab--active"
                        : "content-preview-panel__subtab"
                    }
                    type="button"
                    role="tab"
                    aria-selected={previewChannel === channel.key}
                    onClick={() => setPreviewChannel(channel.key)}
                  >
                    {channel.label}
                  </button>
                ))}
              </div>
              <article className="content-preview-panel__body">
                {getPreviewText(previewRecord, previewChannel)}
              </article>
            </>
          ) : null}
          {previewMode === "visual" ? (
            <div className="content-preview-panel__visual-grid">
              {getVisualEntries(previewRecord).length === 0 ? (
                <div className="content-preview-panel__empty">
                  생성된 이미지 미리보기 파일이 없다.
                </div>
              ) : (
                getVisualEntries(previewRecord).map(([channel, visual]) => (
                  <figure className="visual-preview-card" key={channel}>
                    <span className="visual-preview-card__badge">{channel}</span>
                    <a href={visual.url} rel="noreferrer" target="_blank">
                      <img alt={`${channel} 대표 이미지`} src={visual.url} />
                    </a>
                    <figcaption>
                      <strong>{channel}</strong>
                      <span>
                        {visual.status || "generated"} · {visual.size || "size unknown"} ·{" "}
                        {visual.quality || "quality unknown"}
                      </span>
                    </figcaption>
                  </figure>
                ))
              )}
            </div>
          ) : null}
          {previewMode === "document" ? (
            <div className="content-preview-panel__empty">
              배포 문서는 팝업으로 확인합니다.
              <button
                className="publication-open-button"
                type="button"
                onClick={() => openDocumentModal(previewRecord)}
              >
                통합 문서 열기
              </button>
            </div>
          ) : null}
        </section>
      ) : null}
      {isDocumentModalOpen && previewRecord ? (
        <div className="publication-modal" role="dialog" aria-modal="true" aria-label="배포 문서 팝업">
          <button
            className="publication-modal__backdrop"
            type="button"
            aria-label="배포 문서 팝업 닫기"
            onClick={() => setIsDocumentModalOpen(false)}
          />
          <section className="publication-modal__panel">
            <div className="publication-modal__header">
              <div>
                <span className="agent-detail-panel__eyebrow">Publication Document</span>
                <h3>{previewRecord.title}</h3>
              </div>
              <button
                className="icon-button"
                type="button"
                aria-label="배포 문서 팝업 닫기"
                onClick={() => setIsDocumentModalOpen(false)}
              >
                <X size={18} />
              </button>
            </div>
            <div className="publication-modal__content">
              <PublicationDocumentViewer
                documentKey={documentKey}
                onDocumentKeyChange={setDocumentKey}
                record={previewRecord}
              />
            </div>
          </section>
        </div>
      ) : null}
    </aside>
  );
}

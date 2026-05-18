import { useState } from "react";
import type { MetricKey } from "../types";
import { officeStatus } from "../data/officeStatus";
import { AgentDetailPanel } from "./AgentDetailPanel";
import { MetricDetailPanel } from "./MetricDetailPanel";
import { OfficeHeader } from "./OfficeHeader";

export function OfficeDashboard() {
  const [selectedAgentId, setSelectedAgentId] = useState(
    officeStatus.agents[0]?.id ?? ""
  );
  const [selectedMetric, setSelectedMetric] = useState<MetricKey | null>("completed");
  const selectedAgent =
    officeStatus.agents.find((agent) => agent.id === selectedAgentId) ??
    officeStatus.agents[0];
  const selectedMetricDetail = selectedMetric
    ? officeStatus.metricDetails[selectedMetric]
    : null;

  const handleSelectAgent = (agentId: string) => {
    setSelectedMetric(null);
    setSelectedAgentId(agentId);
  };

  const handleSelectMetric = (metric: MetricKey) => {
    setSelectedMetric(metric);
    setSelectedAgentId("");
  };

  return (
    <main className="dashboard-shell">
      <OfficeHeader
        title={officeStatus.title}
        subtitle={officeStatus.subtitle}
        teamName={officeStatus.teamName}
        tokenUsage={officeStatus.tokenUsage}
        liveStatusAvailable={officeStatus.dataSource.liveStatusAvailable}
      />

      <section className="overview-strip" aria-label="오늘 콘텐츠 상태">
        <button
          className={["overview-card", selectedMetric === "inputs" ? "overview-card--active" : ""].join(" ")}
          type="button"
          onClick={() => handleSelectMetric("inputs")}
        >
          <span>들어온 요청</span>
          <strong>{officeStatus.metrics.todayInputs}</strong>
          <small>Telegram 입력</small>
        </button>
        <button
          className={["overview-card", selectedMetric === "completed" ? "overview-card--active" : ""].join(" ")}
          type="button"
          onClick={() => handleSelectMetric("completed")}
        >
          <span>볼 수 있는 글</span>
          <strong>{officeStatus.metrics.completedContents}</strong>
          <small>원고·이미지·문서</small>
        </button>
        <button
          className={["overview-card", selectedMetric === "review" ? "overview-card--active" : ""].join(" ")}
          type="button"
          onClick={() => handleSelectMetric("review")}
        >
          <span>확인 필요</span>
          <strong>{officeStatus.metrics.reviewQueue}</strong>
          <small>품질 또는 배포 대기</small>
        </button>
        <button
          className={["overview-card", selectedMetric === "published" ? "overview-card--active" : ""].join(" ")}
          type="button"
          onClick={() => handleSelectMetric("published")}
        >
          <span>배포 완료</span>
          <strong>{officeStatus.metrics.published}</strong>
          <small>공개/발송 기록</small>
        </button>
      </section>

      <div className="dashboard-layout">
        <section className="workbench-panel" aria-label="콘텐츠 산출물 확인">
          {selectedMetric && selectedMetricDetail ? (
          <MetricDetailPanel
            dataSource={officeStatus.dataSource}
            detail={selectedMetricDetail}
            metricKey={selectedMetric}
            onClose={() => setSelectedMetric("completed")}
          />
          ) : selectedAgent ? (
          <AgentDetailPanel
            agent={selectedAgent}
            onClose={() => setSelectedMetric("completed")}
          />
          ) : null}
        </section>
        <section className="automation-panel" aria-label="자동화 진행 상태">
          <div className="automation-panel__heading">
            <div>
              <span className="agent-detail-panel__eyebrow">Automation Flow</span>
              <h2>처리 순서와 직원 상태</h2>
            </div>
            <button
              className="automation-panel__reset"
              type="button"
              onClick={() => handleSelectAgent(officeStatus.agents[0]?.id ?? "")}
            >
              직원 보기
            </button>
          </div>
          <div className="pipeline-checklist" aria-label="콘텐츠 처리 순서">
            {officeStatus.pipelineStages.map((stage, index) => (
              <div className={`pipeline-checklist__item pipeline-checklist__item--${stage.status.toLowerCase()}`} key={stage.id}>
                <span>{index + 1}</span>
                <div>
                  <strong>{stage.label}</strong>
                  <small>{stage.detail}</small>
                </div>
              </div>
            ))}
          </div>
          <div className="agent-compact-list" aria-label="직원별 상태">
            {officeStatus.agents.map((agent) => (
              <button
                className={[
                  "agent-compact-card",
                  `agent-compact-card--${agent.status.toLowerCase()}`,
                  selectedAgent?.id === agent.id ? "agent-compact-card--active" : ""
                ].join(" ")}
                key={agent.id}
                type="button"
                onClick={() => handleSelectAgent(agent.id)}
              >
                <img alt="" src={agent.avatar} />
                <span>
                  <strong>{agent.name}</strong>
                  <small>{agent.role}</small>
                </span>
                <em>{agent.status === "IDLE" ? "휴식" : agent.status}</em>
              </button>
            ))}
          </div>
        </section>
      </div>

    </main>
  );
}

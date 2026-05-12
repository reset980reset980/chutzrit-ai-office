import { useEffect, useState } from "react";
import type { MetricKey } from "../types";
import { officeStatus } from "../data/officeStatus";
import { AgentDetailPanel } from "./AgentDetailPanel";
import { BottomStatusBar } from "./BottomStatusBar";
import { MetricDetailPanel } from "./MetricDetailPanel";
import { OfficeHeader } from "./OfficeHeader";
import { OfficeMap } from "./OfficeMap";

export function OfficeDashboard() {
  const [selectedAgentId, setSelectedAgentId] = useState(
    officeStatus.agents[0]?.id ?? ""
  );
  const [selectedMetric, setSelectedMetric] = useState<MetricKey | null>(null);
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const interval = window.setInterval(() => {
      setNow(new Date());
    }, 1000);

    return () => window.clearInterval(interval);
  }, []);

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

      <div className="dashboard-layout">
        <OfficeMap
          agents={officeStatus.agents}
          pipelineStages={officeStatus.pipelineStages}
          selectedAgentId={selectedAgent?.id ?? ""}
          onSelectAgent={handleSelectAgent}
        />
        {selectedMetric && selectedMetricDetail ? (
          <MetricDetailPanel
            dataSource={officeStatus.dataSource}
            detail={selectedMetricDetail}
            metricKey={selectedMetric}
            onClose={() => setSelectedMetric(null)}
          />
        ) : selectedAgent ? (
          <AgentDetailPanel
            agent={selectedAgent}
            onClose={() => setSelectedAgentId("")}
          />
        ) : null}
      </div>

      <BottomStatusBar
        metrics={officeStatus.metrics}
        now={now}
        selectedMetric={selectedMetric}
        onSelectMetric={handleSelectMetric}
      />
    </main>
  );
}

import type { Agent, PipelineStage } from "../types";
import { AgentAvatar } from "./AgentAvatar";
import { PipelineFlow } from "./PipelineFlow";

type OfficeMapProps = {
  agents: Agent[];
  pipelineStages: PipelineStage[];
  selectedAgentId: string;
  onSelectAgent: (agentId: string) => void;
};

export function OfficeMap({
  agents,
  pipelineStages,
  selectedAgentId,
  onSelectAgent
}: OfficeMapProps) {
  return (
    <section className="office-map-shell" aria-label="콘텐츠배포팀 오피스 맵">
      <div className="office-stage">
        <div className="office-stage__ambient office-stage__ambient--one" />
        <div className="office-stage__ambient office-stage__ambient--two" />
        <div className="office-stage__back-wall" />
        <div className="office-stage__floor" />
        <div className="office-zone office-zone--input" />
        <div className="office-zone office-zone--strategy" />
        <div className="office-zone office-zone--writing" />
        <div className="office-zone office-zone--review" />
        <div className="office-zone office-zone--revision" />
        <div className="office-zone office-zone--publish" />

        <div className="office-furniture office-furniture--reception" />
        <div className="office-furniture office-furniture--table" />
        <div className="office-furniture office-furniture--writer-a" />
        <div className="office-furniture office-furniture--writer-b" />
        <div className="office-furniture office-furniture--review" />
        <div className="office-furniture office-furniture--revision" />
        <div className="office-furniture office-furniture--publish" />

        <div className="office-monitor office-monitor--discord" />
        <div className="office-monitor office-monitor--board" />
        <div className="office-conveyor" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>

        <PipelineFlow stages={pipelineStages} />

        {agents.map((agent) => (
          <AgentAvatar
            agent={agent}
            key={agent.id}
            selected={agent.id === selectedAgentId}
            onSelect={onSelectAgent}
          />
        ))}
      </div>
    </section>
  );
}

import { ArrowRight, CheckCircle2, Clock3, Loader2, TriangleAlert } from "lucide-react";
import type { PipelineStage } from "../types";

type PipelineFlowProps = {
  stages: PipelineStage[];
};

function getStageIcon(status: PipelineStage["status"]) {
  if (status === "ERROR") return <TriangleAlert size={15} />;
  if (status === "IDLE") return <Clock3 size={15} />;
  if (status === "REVIEW") return <CheckCircle2 size={15} />;
  return <Loader2 size={15} />;
}

export function PipelineFlow({ stages }: PipelineFlowProps) {
  return (
    <div className="pipeline-flow" aria-label="콘텐츠 제작 파이프라인">
      {stages.map((stage, index) => (
        <div className="pipeline-flow__segment" key={stage.id}>
          <div
            className={`pipeline-stage pipeline-stage--${stage.status.toLowerCase()}`}
            style={{ left: `${stage.position.x}%`, top: `${stage.position.y}%` }}
          >
            <span className="pipeline-stage__icon" aria-hidden="true">
              {getStageIcon(stage.status)}
            </span>
            <span className="pipeline-stage__text">
              <strong>{stage.label}</strong>
              <small>{stage.detail}</small>
            </span>
          </div>
          {index < stages.length - 1 ? (
            <span
              className="pipeline-arrow"
              style={{
                left: `${stage.position.x + 7.5}%`,
                top: `${stage.position.y + 1.4}%`,
                width: `${Math.max(
                  stages[index + 1].position.x - stage.position.x - 11,
                  4
                )}%`
              }}
              aria-hidden="true"
            >
              <ArrowRight size={17} />
            </span>
          ) : null}
        </div>
      ))}
    </div>
  );
}

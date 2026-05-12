import {
  BatteryCharging,
  ClipboardCheck,
  Clock4,
  Database,
  ListChecks,
  Target,
  X,
  Zap
} from "lucide-react";
import type { Agent } from "../types";
import { StatusBadge } from "./StatusBadge";

type AgentDetailPanelProps = {
  agent: Agent;
  onClose: () => void;
};

export function AgentDetailPanel({ agent, onClose }: AgentDetailPanelProps) {
  return (
    <aside className="agent-detail-panel" aria-label="에이전트 상세 상태">
      <div className="agent-detail-panel__header">
        <div>
          <span className="agent-detail-panel__eyebrow">직원 상세</span>
          <h2>{agent.name}</h2>
          <p>{agent.role}</p>
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

      <div className="agent-detail-panel__status">
        <StatusBadge status={agent.status} />
        <span className="agent-detail-panel__motion">
          <Zap size={15} />
          {agent.motion}
        </span>
      </div>

      <div className="agent-detail-panel__source">
        <Database size={16} />
        <div>
          <span>상태 기준</span>
          <strong>{agent.statusSource ?? "상태 소스 없음"}</strong>
        </div>
      </div>

      <div className="agent-detail-panel__energy">
        <BatteryCharging size={16} />
        <div>
          <span>에너지 잔량</span>
          <strong>{agent.energyLevel}%</strong>
          <i style={{ width: `${agent.energyLevel}%` }} />
        </div>
      </div>

      <div className="agent-detail-panel__section">
        <h3>
          <Target size={16} />
          현재 작업
        </h3>
        <p>{agent.currentTask}</p>
      </div>
      <div className="agent-detail-panel__section">
        <h3>
          <ClipboardCheck size={16} />
          최근 완료
        </h3>
        <p>{agent.recentOutput}</p>
      </div>
      <div className="agent-detail-panel__section">
        <h3>
          <ListChecks size={16} />
          다음 작업
        </h3>
        <p>{agent.nextTask}</p>
      </div>
      <div className="agent-detail-panel__updated">
        <Clock4 size={15} />
        <span>업데이트 {agent.updatedAt}</span>
      </div>
    </aside>
  );
}

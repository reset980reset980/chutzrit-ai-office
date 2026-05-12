import type { AgentStatus } from "../types";

const statusLabels: Record<AgentStatus, string> = {
  WORKING: "WORKING",
  IDLE: "휴식",
  REVIEW: "REVIEW",
  ERROR: "ERROR"
};

export function StatusBadge({ status }: { status: AgentStatus }) {
  return (
    <span className={`status-badge status-badge--${status.toLowerCase()}`}>
      {statusLabels[status]}
    </span>
  );
}

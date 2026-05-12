import { useState, type CSSProperties } from "react";
import { RadioTower } from "lucide-react";
import type { Agent } from "../types";
import { StatusBadge } from "./StatusBadge";

type AgentAvatarProps = {
  agent: Agent;
  selected: boolean;
  onSelect: (agentId: string) => void;
};

function getInitials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();
}

export function AgentAvatar({ agent, selected, onSelect }: AgentAvatarProps) {
  const [avatarFailed, setAvatarFailed] = useState(false);
  const hasAvatar = Boolean(agent.avatar && !avatarFailed);

  const nodeStyle = {
    left: `${agent.position.x}%`,
    top: `${agent.position.y}%`
  } as CSSProperties;

  return (
    <button
      className={[
        "agent-node",
        `agent-node--${agent.status.toLowerCase()}`,
        `agent-node--${agent.motion}`,
        selected ? "agent-node--selected" : ""
      ].join(" ")}
      style={nodeStyle}
      type="button"
      aria-label={`${agent.name} 상세 보기`}
      aria-pressed={selected}
      onClick={() => onSelect(agent.id)}
    >
      <StatusBadge status={agent.status} />
      <span className="agent-node__portrait">
        {hasAvatar ? (
          <img
            alt=""
            className="agent-node__image"
            src={agent.avatar}
            onError={() => setAvatarFailed(true)}
          />
        ) : (
          <span className="agent-node__fallback">
            {agent.id === "publish" ? <RadioTower size={30} /> : getInitials(agent.name)}
          </span>
        )}
        <span className="agent-node__motion-dot" aria-hidden="true" />
      </span>
      <span className="agent-node__plate">
        <strong>{agent.name}</strong>
      </span>
    </button>
  );
}

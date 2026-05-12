import type { CSSProperties } from "react";
import { Cpu } from "lucide-react";
import type { TokenUsage } from "../types";

type TokenUsageWidgetProps = {
  tokenUsage: TokenUsage;
};

const numberFormatter = new Intl.NumberFormat("ko-KR");

export function TokenUsageWidget({ tokenUsage }: TokenUsageWidgetProps) {
  if (tokenUsage.status === "unavailable") {
    return (
      <section
        className="token-widget token-widget--unavailable"
        aria-label="Codex token usage unavailable"
      >
        <div className="token-widget__icon" aria-hidden="true">
          <Cpu size={18} />
        </div>
        <div className="token-widget__content">
          <div className="token-widget__label">{tokenUsage.label}</div>
          <div className="token-widget__numbers">
            <strong>연동 안 됨</strong>
          </div>
          <p>{tokenUsage.reason}</p>
        </div>
      </section>
    );
  }

  const usageStyle = {
    "--usage": `${tokenUsage.percentage}%`
  } as CSSProperties;

  return (
    <section className="token-widget" aria-label="Codex token usage">
      <div className="token-widget__icon" aria-hidden="true">
        <Cpu size={18} />
      </div>
      <div className="token-widget__content">
        <div className="token-widget__label">{tokenUsage.label ?? "Codex 사용량"}</div>
        <div className="token-widget__numbers">
          <strong>{numberFormatter.format(tokenUsage.used)}</strong>
          <span>/ {numberFormatter.format(tokenUsage.limit)}</span>
        </div>
        <div className="token-widget__bar" style={usageStyle}>
          <span />
        </div>
        {tokenUsage.reason ? <p>{tokenUsage.reason}</p> : null}
      </div>
      <div className="token-widget__percent">{tokenUsage.percentage}%</div>
    </section>
  );
}

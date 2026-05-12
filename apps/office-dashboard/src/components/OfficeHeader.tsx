import { Activity, Radio } from "lucide-react";
import type { TokenUsage } from "../types";
import { TokenUsageWidget } from "./TokenUsageWidget";

type OfficeHeaderProps = {
  title: string;
  subtitle: string;
  teamName: string;
  tokenUsage: TokenUsage;
  liveStatusAvailable: boolean;
};

export function OfficeHeader({
  title,
  subtitle,
  teamName,
  tokenUsage,
  liveStatusAvailable
}: OfficeHeaderProps) {
  return (
    <header className="office-header">
      <div className="office-header__brand">
        <div className="office-header__kicker">
          <Radio size={16} />
          <span>{teamName} 운영 화면</span>
        </div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <div className="office-header__ops">
        <div
          className={["live-chip", liveStatusAvailable ? "" : "live-chip--snapshot"].join(" ")}
          aria-label="현재 자동화 상태"
        >
          <Activity size={16} />
          <span>{liveStatusAvailable ? "실시간 운영 중" : "오늘 운영 스냅샷"}</span>
        </div>
        <TokenUsageWidget tokenUsage={tokenUsage} />
      </div>
    </header>
  );
}

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { execFile } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)));
const repoRoot = path.resolve(appDir, "../..");
const statusScript = path.join(appDir, "scripts/generate-office-status.mjs");
const outputsDir = path.join(repoRoot, "outputs/broadcasting");

function officeStatusDataPlugin() {
  let timer: ReturnType<typeof setTimeout> | null = null;
  let running = false;
  let pending = false;

  const generate = (reason: string, notify?: () => void) => {
    if (running) {
      pending = true;
      return;
    }

    running = true;
    execFile("node", [statusScript], { cwd: appDir }, (error, stdout, stderr) => {
      running = false;
      if (stdout.trim()) console.log(stdout.trim());
      if (stderr.trim()) console.warn(stderr.trim());
      if (error) {
        console.warn(`[office-status] failed to generate data after ${reason}: ${error.message}`);
      } else {
        notify?.();
      }

      if (pending) {
        pending = false;
        generate("queued output change", notify);
      }
    });
  };

  const schedule = (reason: string, notify?: () => void) => {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => generate(reason, notify), 500);
  };

  return {
    name: "chutzrit-office-status-data",
    buildStart() {
      generate("build start");
    },
    configureServer(server) {
      server.watcher.add(outputsDir);
      server.watcher.on("all", (_event, changedPath) => {
        if (!changedPath.startsWith(outputsDir)) return;
        schedule("outputs/broadcasting change", () => {
          server.ws.send({ type: "full-reload" });
        });
      });
    }
  };
}

export default defineConfig({
  plugins: [officeStatusDataPlugin(), react()],
  server: {
    host: "127.0.0.1",
    port: 5173
  },
  preview: {
    host: "127.0.0.1",
    port: 4173
  }
});

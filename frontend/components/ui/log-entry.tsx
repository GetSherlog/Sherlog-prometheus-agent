import * as React from "react";
import { cn } from "@/lib/utils";

export interface LogEntryProps {
  timestamp: string;
  severity: "info" | "warning" | "error";
  message: string;
  source?: string;
  metadata?: Record<string, any>;
  className?: string;
}

const severityColors = {
  info: "text-blue-500 dark:text-blue-400 bg-blue-50 dark:bg-blue-950",
  warning: "text-yellow-500 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-950",
  error: "text-red-500 dark:text-red-400 bg-red-50 dark:bg-red-950",
};

const LogEntry = React.forwardRef<HTMLDivElement, LogEntryProps>(
  ({ timestamp, severity, message, source, metadata, className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "flex flex-col gap-1 rounded-lg p-3 text-sm border",
          severityColors[severity],
          className
        )}
        {...props}
      >
        <div className="flex items-center justify-between">
          <span className="font-medium">{timestamp}</span>
          <span className="capitalize px-2 py-0.5 rounded text-xs font-semibold">
            {severity}
          </span>
        </div>
        <p className="font-mono">{message}</p>
        {source && (
          <span className="text-xs opacity-70">Source: {source}</span>
        )}
        {metadata && Object.keys(metadata).length > 0 && (
          <div className="mt-2 text-xs">
            <div className="font-semibold mb-1">Metadata:</div>
            <pre className="overflow-x-auto">
              {JSON.stringify(metadata, null, 2)}
            </pre>
          </div>
        )}
      </div>
    );
  }
);
LogEntry.displayName = "LogEntry";

export { LogEntry }; 
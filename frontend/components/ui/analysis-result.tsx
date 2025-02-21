import * as React from "react";
import { cn } from "@/lib/utils";

export interface Insight {
  title: string;
  description: string;
  severity: "info" | "warning" | "error";
  relatedLogs?: string[];
  recommendation?: string;
}

export interface AnalysisResultProps {
  query: string;
  timestamp: string;
  insights: Insight[];
  className?: string;
}

const severityIcons = {
  info: "ℹ️",
  warning: "⚠️",
  error: "🚨",
};

const severityColors = {
  info: "border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950",
  warning: "border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-950",
  error: "border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950",
};

const AnalysisResult = React.forwardRef<HTMLDivElement, AnalysisResultProps>(
  ({ query, timestamp, insights, className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "rounded-xl border bg-card p-6 text-card-foreground shadow",
          className
        )}
        {...props}
      >
        <div className="flex flex-col gap-4">
          <div className="space-y-1">
            <h3 className="font-semibold text-lg">Analysis Results</h3>
            <p className="text-sm text-muted-foreground">
              Query: "{query}"
            </p>
            <p className="text-xs text-muted-foreground">
              Analyzed at: {timestamp}
            </p>
          </div>

          <div className="space-y-4">
            {insights.map((insight, index) => (
              <div
                key={index}
                className={cn(
                  "rounded-lg border p-4",
                  severityColors[insight.severity]
                )}
              >
                <div className="flex items-start gap-2">
                  <span className="text-lg">{severityIcons[insight.severity]}</span>
                  <div className="flex-1 space-y-2">
                    <h4 className="font-medium">{insight.title}</h4>
                    <p className="text-sm">{insight.description}</p>
                    
                    {insight.relatedLogs && insight.relatedLogs.length > 0 && (
                      <div className="mt-2">
                        <h5 className="text-sm font-medium mb-1">Related Logs:</h5>
                        <ul className="text-sm space-y-1">
                          {insight.relatedLogs.map((log, logIndex) => (
                            <li key={logIndex} className="font-mono text-xs">
                              {log}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {insight.recommendation && (
                      <div className="mt-2">
                        <h5 className="text-sm font-medium">Recommendation:</h5>
                        <p className="text-sm italic">
                          {insight.recommendation}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }
);
AnalysisResult.displayName = "AnalysisResult";

export { AnalysisResult }; 
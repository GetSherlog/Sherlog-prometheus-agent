import * as React from "react";
import { cn } from "@/lib/utils";

export interface MetricsCardProps {
  title: string;
  value: number;
  unit?: string;
  trend?: {
    direction: "up" | "down";
    percentage: number;
  };
  threshold?: {
    warning: number;
    critical: number;
  };
  className?: string;
}

const MetricsCard = React.forwardRef<HTMLDivElement, MetricsCardProps>(
  ({ title, value, unit, trend, threshold, className, ...props }, ref) => {
    const isWarning = threshold && value >= threshold.warning && value < threshold.critical;
    const isCritical = threshold && value >= threshold.critical;

    return (
      <div
        ref={ref}
        className={cn(
          "rounded-xl border bg-card p-4 text-card-foreground shadow",
          {
            "border-yellow-500 dark:border-yellow-400": isWarning,
            "border-red-500 dark:border-red-400": isCritical,
          },
          className
        )}
        {...props}
      >
        <div className="flex flex-col gap-1">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold">
              {value}
              {unit && <span className="ml-1 text-lg">{unit}</span>}
            </span>
            {trend && (
              <div
                className={cn(
                  "flex items-center text-sm",
                  trend.direction === "up"
                    ? "text-red-500 dark:text-red-400"
                    : "text-green-500 dark:text-green-400"
                )}
              >
                {trend.direction === "up" ? "↑" : "↓"} {trend.percentage}%
              </div>
            )}
          </div>
          {threshold && (
            <div className="mt-2 flex gap-2 text-xs">
              <span
                className={cn("rounded px-1.5 py-0.5", {
                  "bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300":
                    isWarning,
                  "bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300":
                    isCritical,
                })}
              >
                {isCritical
                  ? "Critical"
                  : isWarning
                  ? "Warning"
                  : "Normal"}
              </span>
              <span className="text-muted-foreground">
                Threshold: {threshold.warning} / {threshold.critical}
              </span>
            </div>
          )}
        </div>
      </div>
    );
  }
);
MetricsCard.displayName = "MetricsCard";

export { MetricsCard }; 
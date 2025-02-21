"use client";

import { useState } from "react";
import { Button } from "./ui/button";
import { toast } from "sonner";
import { UploadIcon, BoxIcon } from "./icons";

export function DataSourceSelector() {
  const [isConnecting, setIsConnecting] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Upload failed");
      
      toast.success("Log file uploaded successfully");
    } catch (error) {
      toast.error("Failed to upload log file");
      console.error(error);
    }
  };

  const connectToPrometheus = async () => {
    setIsConnecting(true);
    try {
      const response = await fetch("/api/connect/prometheus", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          // Add connection details here
          url: "http://localhost:9090",
        }),
      });

      if (!response.ok) throw new Error("Connection failed");
      
      toast.success("Connected to Prometheus successfully");
    } catch (error) {
      toast.error("Failed to connect to Prometheus");
      console.error(error);
    } finally {
      setIsConnecting(false);
    }
  };

  return (
    <div className="border-b border-border">
      <div className="max-w-3xl mx-auto p-4 flex items-center gap-4">
        <div className="flex-1">
          <h2 className="text-lg font-semibold">Data Sources</h2>
          <p className="text-sm text-muted-foreground">
            Upload log files or connect to your metrics stack
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => document.getElementById("file-upload")?.click()}
          >
            <UploadIcon className="mr-2" />
            Upload Logs
            <input
              id="file-upload"
              type="file"
              className="hidden"
              accept=".log,.txt"
              onChange={handleFileUpload}
            />
          </Button>
          <Button
            variant="outline"
            onClick={connectToPrometheus}
            disabled={isConnecting}
          >
            <BoxIcon size={16} className="mr-2" />
            {isConnecting ? "Connecting..." : "Connect Prometheus"}
          </Button>
        </div>
      </div>
    </div>
  );
} 
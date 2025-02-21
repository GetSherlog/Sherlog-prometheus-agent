import { Chat } from "@/components/Chat";
import { DataSourceSelector } from "@/components/data-source-selector";

export default function Page() {
  return (
    <div className="flex flex-col min-h-screen">
      <div className="flex-1 flex flex-col">
        <DataSourceSelector />
        <Chat />
      </div>
    </div>
  );
} 
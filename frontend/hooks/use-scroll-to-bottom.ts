import { useEffect, useRef } from "react";

export function useScrollToBottom<T extends HTMLElement>(): [
  React.RefObject<T>,
  React.RefObject<T>,
] {
  const containerRef = useRef<T>(null);
  const bottomRef = useRef<T>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  return [containerRef, bottomRef];
} 
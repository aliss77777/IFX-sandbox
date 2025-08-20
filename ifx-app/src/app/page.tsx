'use client';

import AssetDisplay from "@/components/asset-display";
import ChatHistory from "@/components/chat-history";
import ChatInput from "@/components/chat-input";
import { useEffect, useState } from "react";

export default function Page() {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [asset, setAsset] = useState<any>(null);
  const [history, setHistory] = useState<any[]>(["Hello! How can I help you today?"]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");
    setSocket(ws);

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'asset') {
        setAsset(message);
      } else if (message.type === 'text_chunk') {
        setHistory((prevHistory) => [...prevHistory, message.chunk]);
      } else if (message.type === 'stream_end') {
        // Handle stream end
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  const sendMessage = (message: string) => {
    if (socket) {
      socket.send(message);
    }
  };

  return (
    <div className="flex h-screen">
      <div className="w-1/2 hidden lg:flex items-center justify-center fixed h-full">
        <AssetDisplay asset={asset} />
      </div>
      <div className="flex flex-col flex-1 lg:ml-[50%]">
        <ChatHistory history={history} />
        <ChatInput sendMessage={sendMessage} />
      </div>
    </div>
  );
}

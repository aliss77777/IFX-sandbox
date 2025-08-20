'use client';

import AssetDisplay from "@/components/asset-display";
import ChatHistory, { Message } from "@/components/chat-history";
import ChatInput from "@/components/chat-input";
import { useEffect, useState } from "react";

export default function Page() {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [asset, setAsset] = useState<any>(null);
  const [history, setHistory] = useState<Message[]>([{ text: 'Hello! How can I help you today?', sender: 'assistant', timestamp: new Date() }]);
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");
    setSocket(ws);

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'asset') {
        setAsset(message);
        setIsStreaming(true);
        setHistory((prev) => [...prev, { text: '', sender: 'assistant', timestamp: new Date() }]);
      } else if (message.type === 'text_chunk') {
        setHistory((prevHistory) => {
          const newHistory = [...prevHistory];
          const lastMessageIndex = newHistory.length - 1;
          const lastMessage = newHistory[lastMessageIndex];

          if (lastMessage && lastMessage.sender === 'assistant') {
            const updatedMessage = {
              ...lastMessage,
              text: lastMessage.text + message.chunk,
            };
            newHistory[lastMessageIndex] = updatedMessage;
          }
          return newHistory;
        });
      } else if (message.type === 'stream_end') {
        setIsStreaming(false);
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  const sendMessage = (message: string) => {
    if (socket && !isStreaming) {
      setHistory(prev => [...prev, { text: message, sender: 'user', timestamp: new Date() }]);
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

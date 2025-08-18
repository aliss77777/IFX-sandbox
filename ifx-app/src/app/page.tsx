import AssetDisplay from "@/components/asset-display";
import ChatHistory from "@/components/chat-history";
import ChatInput from "@/components/chat-input";
import DevPanel from "@/components/dev-panel";

export default function Page() {
  return (
    <div className="flex h-screen">
      <div className="w-1/2 hidden lg:block fixed h-full">
        <AssetDisplay />
      </div>
      <div className="flex flex-col flex-1 lg:ml-[50%]">
        <ChatHistory />
        <ChatInput />
      </div>
      <DevPanel />
    </div>
  );
}
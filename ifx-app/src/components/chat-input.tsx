import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";
import { useState } from "react";

export default function ChatInput({ sendMessage }: { sendMessage: (message: string) => void }) {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (message.trim()) {
      sendMessage(message);
      setMessage("");
    }
  };

  return (
    <div className="p-4">
      <Card className="bg-card/80 backdrop-blur-sm border-accent/20 shadow-xl">
        <CardContent className="p-6">
          <div className="flex gap-3">
            <Input
              placeholder="Type your message..."
              className="flex-1 bg-input/80 border-accent/30 focus:border-accent/60 focus:ring-accent/30 h-12 text-base"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <Button
              size="lg"
              className="bg-accent hover:bg-accent/90 text-accent-foreground shadow-lg hover:shadow-accent/30 transition-all duration-300 px-6"
              onClick={handleSend}
            >
              <Send className="h-5 w-5 mr-2" />
              Send
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
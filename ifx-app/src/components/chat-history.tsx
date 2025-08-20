import { Card, CardContent } from "@/components/ui/card";

interface Message {
  id: number;
  text: string;
  sender: "user" | "assistant";
  timestamp: Date;
}

export default function ChatHistory({ history }: { history: any[] }) {
  const messages: Message[] = history.map((chunk, index) => ({
    id: index,
    text: chunk,
    sender: "assistant",
    timestamp: new Date(),
  }));

  return (
    <div className="flex-1 overflow-auto p-4 space-y-6">
      {messages.map((message) => (
        <div key={message.id}>
          <Card
            className={`transition-all duration-300 hover:shadow-lg ${
              message.sender === "user"
                ? "ml-auto max-w-md bg-accent text-accent-foreground shadow-accent/20"
                : "mr-auto max-w-2xl bg-card border-accent/20 hover:border-accent/40"
            }`}
          >
            <CardContent className="p-4">
              <div className={`flex items-start gap-3 ${message.sender === "user" ? "flex-row-reverse" : ""}`}>
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                    message.sender === "user"
                      ? "bg-accent-foreground text-accent"
                      : "bg-accent text-accent-foreground"
                  }`}
                >
                  {message.sender === "user" ? "U" : "AI"}
                </div>
                <div className="flex-1">
                  <p className="text-sm leading-relaxed mb-2">{message.text}</p>
                  <p
                    className={`text-xs ${
                      message.sender === "user" ? "text-accent-foreground/70" : "text-muted-foreground"
                    }`}
                  >
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ))}
    </div>
  );
}
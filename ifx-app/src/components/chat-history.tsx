import { Card } from "@/components/ui/card"

export default function ChatHistory() {
  return (
    <Card className="flex-1 overflow-auto">
      <div className="p-4 space-y-4">
        <div className="flex items-start gap-4">
          <div className="rounded-full bg-gray-200 dark:bg-gray-700 w-8 h-8" />
          <div className="flex-1 space-y-2">
            <div className="font-bold">AI Assistant</div>
            <p>Hello! How can I help you today?</p>
          </div>
        </div>
        <div className="flex items-start gap-4 justify-end">
          <div className="flex-1 space-y-2 text-right">
            <div className="font-bold">You</div>
            <p>Tell me about the best soccer player in the world.</p>
          </div>
          <div className="rounded-full bg-gray-200 dark:bg-gray-700 w-8 h-8" />
        </div>
      </div>
    </Card>
  )
}

import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export default function ChatInput() {
  return (
    <div className="p-4 border-t">
      <div className="flex items-center gap-2">
        <Input className="flex-1" placeholder="Type your message..." />
        <Button>Send</Button>
      </div>
    </div>
  )
}

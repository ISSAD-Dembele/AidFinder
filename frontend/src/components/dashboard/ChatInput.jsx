import { useState } from 'react'
import { Mic, Send } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

/** Zone de saisie du chat en bas du dashboard */
export default function ChatInput({ onSend, value, onChange }) {
  const [internalMessage, setInternalMessage] = useState('')
  const message = value ?? internalMessage
  const setMessage = onChange ?? setInternalMessage

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!message.trim()) return
    onSend?.(message.trim())
    setMessage('')
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="relative mx-auto w-full max-w-3xl"
    >
      <Input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Décrivez votre situation..."
        className="h-12 rounded-full border-border pr-24 pl-5 text-sm shadow-sm"
      />
      <div className="absolute top-1/2 right-2 flex -translate-y-1/2 items-center gap-1">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="text-[#2963E8] hover:bg-[#2963E8]/10"
          aria-label="Microphone"
        >
          <Mic className="size-4" />
        </Button>
        <Button
          type="submit"
          variant="ghost"
          size="icon"
          className="text-[#2963E8] hover:bg-[#2963E8]/10"
          aria-label="Envoyer"
        >
          <Send className="size-4" />
        </Button>
      </div>
    </form>
  )
}

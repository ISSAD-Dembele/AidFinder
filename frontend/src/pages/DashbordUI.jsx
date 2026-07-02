import { useState } from 'react'
import ChatSuggestions from '@/src/components/dashboard/ChatSuggestions'
import ChatInput from '@/src/components/dashboard/ChatInput'

/**
 * Dashboard utilisateur (Accueil_UI) — interface principale du chatbot.
 * Reproduit fidèlement la maquette avec sidebar et zone de chat.
 */
export default function DashbordUI() {
  const [message, setMessage] = useState('')

  const handleSuggestionSelect = (text) => {
    setMessage(text)
  }

  const handleSend = (text) => {
    // Le chatbot sera connecté dans une prochaine itération
    console.info('Message envoyé:', text)
  }

  return (
    <div className="flex flex-1 flex-col px-4 py-8 sm:px-8 md:py-12">
      {/* En-tête centré */}
      <div className="mx-auto mb-10 max-w-2xl text-center md:mb-16">
        <h1 className="text-2xl font-bold text-foreground sm:text-3xl">
          Comment pouvons-nous vous aider ?
        </h1>
        <p className="mt-3 text-sm text-muted-foreground sm:text-base">
          Discutez avec notre assistant pour savoir les aides qui vous correspondent
        </p>
      </div>

      {/* Suggestions rapides */}
      <div className="mx-auto flex flex-1 flex-col items-center">
        <ChatSuggestions onSelect={handleSuggestionSelect} />
      </div>

      {/* Zone de saisie en bas */}
      <div className="sticky bottom-0 mt-auto bg-white pt-6 pb-4">
        <ChatInput
          value={message}
          onChange={setMessage}
          onSend={handleSend}
        />
      </div>
    </div>
  )
}

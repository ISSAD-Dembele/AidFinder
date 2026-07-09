import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Bot, Sparkles, User, AlertTriangle, RefreshCw } from 'lucide-react'
import dashboardService from '@/src/services/dashboardService'
import ChatSuggestions from '@/src/components/dashboard/ChatSuggestions'
import ChatInput from '@/src/components/dashboard/ChatInput'
import { Button } from '@/components/ui/button'

function DiscussionSkeleton() {
  return (
    <div className="space-y-6 py-4 max-w-3xl mx-auto w-full animate-pulse">
      <div className="flex items-start gap-3">
        <div className="size-8 rounded-lg bg-muted shrink-0" />
        <div className="h-12 w-2/3 bg-muted rounded-2xl rounded-tl-none" />
      </div>
      <div className="flex items-start gap-3 justify-end">
        <div className="h-10 w-1/2 bg-muted rounded-2xl rounded-tr-none" />
        <div className="size-8 rounded-lg bg-muted shrink-0" />
      </div>
      <div className="flex items-start gap-3">
        <div className="size-8 rounded-lg bg-muted shrink-0" />
        <div className="h-20 w-3/4 bg-muted rounded-2xl rounded-tl-none" />
      </div>
    </div>
  )
}

export default function DiscussionPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [sending, setSending] = useState(false)
  const [chatInputVal, setChatInputVal] = useState('')
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Effect to scroll to bottom on message updates
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load conversation details
  const loadConversation = async () => {
    if (!id) {
      setMessages([])
      setLoading(false)
      setError(null)
      return
    }

    setLoading(true)
    setError(null)
    try {
      const data = await dashboardService.getHistoryDetail(id)
      const formattedMessages = data.messages.map((m) => ({
        id: m.discussion_id,
        sender: m.expediteur,
        text: m.contenu,
      }))
      setMessages(formattedMessages)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadConversation()
  }, [id])

  const handleSend = async (text) => {
    if (!text.trim() || sending) return

    // Pre-emptively show user message in UI for smooth experience
    const tempUserMsg = {
      id: Date.now(),
      sender: 'user',
      text: text,
    }
    setMessages((prev) => [...prev, tempUserMsg])
    setSending(true)

    try {
      const res = await dashboardService.sendChatMessage(text, id)
      
      // Add the bot reply
      const botMsg = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: res.bot_message.contenu,
      }
      setMessages((prev) => [...prev, botMsg])

      // If it was a new chat, redirect to the created ID path to maintain URL parity (like ChatGPT)
      if (!id && res.historique_id) {
        navigate(`/dashboard/discussion/${res.historique_id}`, { replace: true })
      }
    } catch {
      // Remove the user message on error to stay consistent, or show error message in chat
      const errorMsg = {
        id: Date.now() + 2,
        sender: 'assistant',
        text: "Une erreur est survenue lors de l'envoi de votre message. Veuillez réessayer.",
        isError: true,
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setSending(false)
    }
  }

  const handleSuggestionSelect = (text) => {
    setChatInputVal(text)
  }

  const handleBack = () => {
    navigate(-1)
  }

  const handleQuit = () => {
    navigate('/dashboard')
  }

  if (loading) {
    return (
      <div className="flex flex-1 flex-col px-4 py-6 sm:px-8">
        <div className="mb-6 flex items-center justify-between border-b border-border/60 pb-4">
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="icon"
              onClick={handleBack}
              className="size-9 border-border text-muted-foreground"
            >
              <ArrowLeft className="size-4" />
            </Button>
            <div>
              <div className="h-4 w-32 bg-muted animate-pulse rounded-md" />
              <div className="h-3 w-48 bg-muted animate-pulse rounded-md mt-1" />
            </div>
          </div>
        </div>
        <DiscussionSkeleton />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center p-8 text-center">
        <div className="rounded-full bg-destructive/10 p-3 text-destructive">
          <AlertTriangle className="size-6" />
        </div>
        <h3 className="mt-4 text-base font-bold text-foreground">Erreur de chargement</h3>
        <p className="mt-2 text-sm text-muted-foreground max-w-sm">
          Impossible d'ouvrir la discussion. Veuillez réessayer ou retourner au tableau de bord.
        </p>
        <div className="mt-4 flex gap-3">
          <Button onClick={loadConversation} className="bg-[#2963E8] hover:bg-[#1e52c7] text-white">
            <RefreshCw className="mr-2 size-4" /> Réessayer
          </Button>
          <Button variant="outline" onClick={handleQuit}>
            Retour au Tableau de bord
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-1 flex-col px-4 py-6 sm:px-8">
      {/* Chat header */}
      <div className="mb-6 flex items-center justify-between border-b border-border/60 pb-4 shrink-0">
        <div className="flex items-center gap-3 min-w-0">
          <Button
            variant="outline"
            size="icon"
            onClick={handleBack}
            className="size-9 border-border text-muted-foreground hover:bg-muted shrink-0"
            aria-label="Page précédente"
          >
            <ArrowLeft className="size-4" />
          </Button>
          <div className="min-w-0">
            <h2 className="flex items-center gap-1.5 text-sm font-bold text-foreground">
              <Bot className="size-4.5 text-[#2963E8]" />
              Assistant IA AidFinder
            </h2>
            <p className="truncate text-xs text-muted-foreground">
              Découvrez vos aides financières en discutant
            </p>
          </div>
        </div>
        <Button
          variant="ghost"
          onClick={handleQuit}
          className="text-xs font-semibold text-[#2963E8] hover:bg-[#2963E8]/10"
        >
          Quitter la discussion
        </Button>
      </div>

      {/* Messages list */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-4 max-w-3xl mx-auto w-full py-4 min-h-[300px]">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 text-center">
            <div className="mx-auto mb-6 max-w-2xl">
              <h1 className="text-2xl font-bold text-foreground sm:text-3xl">
                Comment pouvons-nous vous aider ?
              </h1>
              <p className="mt-3 text-sm text-muted-foreground sm:text-base">
                Discutez avec notre assistant pour savoir les aides qui vous correspondent
              </p>
            </div>
            <ChatSuggestions onSelect={handleSuggestionSelect} />
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg) => {
              const isBot = msg.sender === 'assistant'
              return (
                <div
                  key={msg.id}
                  className={`flex items-start gap-3 ${
                    isBot ? 'justify-start' : 'justify-end'
                  }`}
                >
                  {isBot && (
                    <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-[#2963E8]/10 text-[#2963E8]">
                      <Bot className="size-4" />
                    </div>
                  )}
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-2xs ${
                      isBot
                        ? msg.isError
                          ? 'bg-destructive/10 text-destructive border border-destructive/20 rounded-tl-none'
                          : 'bg-muted/40 text-foreground border border-border/40 rounded-tl-none'
                        : 'bg-[#2963E8] text-white rounded-tr-none'
                    }`}
                  >
                    {msg.text}
                  </div>
                  {!isBot && (
                    <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground font-semibold text-xs">
                      <User className="size-4" />
                    </div>
                  )}
                </div>
              )
            })}
            {sending && (
              <div className="flex items-start gap-3 justify-start animate-pulse">
                <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-[#2963E8]/10 text-[#2963E8]">
                  <Bot className="size-4" />
                </div>
                <div className="bg-muted/40 text-foreground border border-border/40 rounded-2xl rounded-tl-none px-4 py-3 text-sm">
                  L'assistant réfléchit...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input container */}
      <div className="sticky bottom-0 mt-auto bg-white pt-4 pb-4 shrink-0">
        <ChatInput
          value={chatInputVal}
          onChange={setChatInputVal}
          onSend={handleSend}
        />
      </div>
    </div>
  )
}

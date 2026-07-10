import { useEffect, useState, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft,
  Bot,
  User,
  AlertTriangle,
  RefreshCw,
  Plus,
  MessageSquare,
  Sparkles,
} from 'lucide-react'
import dashboardService from '@/src/services/dashboardService'
import ChatSuggestions from '@/src/components/dashboard/ChatSuggestions'
import ChatInput from '@/src/components/dashboard/ChatInput'
import AidCard from '@/src/components/dashboard/AidCard'
import { ChatMessageSkeleton, ChatTypingIndicator, AidCardSkeleton } from '@/src/components/dashboard/SkeletonLoader'
import { Button } from '@/components/ui/button'
import { formatLocalDateTime } from '@/src/utils/date'

/* ─────────────────────────────────────────
   Variants Framer Motion
───────────────────────────────────────── */
const messageVariants = {
  hidden: { opacity: 0, y: 12, scale: 0.97 },
  visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.28, ease: 'easeOut' } },
  exit: { opacity: 0, y: -6, transition: { duration: 0.15 } },
}

const sectionVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
}

/* ─────────────────────────────────────────
   Bulle de message individuelle
───────────────────────────────────────── */
function ChatBubble({ msg }) {
  const isBot = msg.sender === 'assistant'

  return (
    <motion.div
      layout
      variants={messageVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      className={`flex items-end gap-2.5 ${isBot ? 'justify-start' : 'justify-end'}`}
    >
      {/* Avatar Bot */}
      {isBot && (
        <div className="flex size-8 shrink-0 items-center justify-center rounded-xl bg-[#2963E8]/10 text-[#2963E8] shadow-xs mb-5">
          <Bot className="size-4" />
        </div>
      )}

      <div className={`flex flex-col gap-1 max-w-[82%] ${isBot ? 'items-start' : 'items-end'}`}>
        {/* Bulle texte */}
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-xs ${
            isBot
              ? msg.isError
                ? 'bg-destructive/10 text-destructive border border-destructive/20 rounded-tl-none'
                : 'bg-muted/50 text-foreground border border-border/40 rounded-tl-none'
              : 'bg-[#2963E8] text-white rounded-br-none'
          }`}
        >
          {/* Pré-formater le texte pour les sauts de ligne */}
          {msg.text.split('\n').map((line, i) => (
            <span key={i}>
              {line}
              {i < msg.text.split('\n').length - 1 && <br />}
            </span>
          ))}
        </div>

        {/* Timestamp */}
        {msg.timestamp && (
          <span className="text-[10px] text-muted-foreground/60 px-1">
            {formatLocalDateTime(msg.timestamp)}
          </span>
        )}
      </div>

      {/* Avatar Utilisateur */}
      {!isBot && (
        <div className="flex size-8 shrink-0 items-center justify-center rounded-xl bg-muted text-muted-foreground shadow-xs mb-5">
          <User className="size-4" />
        </div>
      )}
    </motion.div>
  )
}

/* ─────────────────────────────────────────
   Empty State (aucune conversation)
───────────────────────────────────────── */
function EmptyChatState({ onSelect }) {
  return (
    <motion.div
      variants={sectionVariants}
      initial="hidden"
      animate="visible"
      className="flex flex-col items-center justify-center py-8 text-center"
    >
      {/* Icône */}
      <div className="mb-5 flex size-16 items-center justify-center rounded-2xl bg-[#2963E8]/10 text-[#2963E8] shadow-xs">
        <Sparkles className="size-7" />
      </div>

      <div className="mb-6 max-w-lg">
        <h1 className="text-2xl font-bold text-foreground sm:text-3xl">
          Comment pouvons-nous vous aider ?
        </h1>
        <p className="mt-3 text-sm text-muted-foreground sm:text-base leading-relaxed">
          Discutez avec notre assistant pour découvrir les aides financières qui vous correspondent.
        </p>
      </div>

      <ChatSuggestions onSelect={onSelect} />
    </motion.div>
  )
}

/* ─────────────────────────────────────────
   Section cartes d'aides recommandées
───────────────────────────────────────── */
function AidsRecommendedSection({ aids, loading }) {
  if (!loading && (!aids || aids.length === 0)) return null

  return (
    <motion.div
      variants={sectionVariants}
      initial="hidden"
      animate="visible"
      className="mt-8 border-t border-border/50 pt-6"
    >
      <div className="mb-4 flex items-center gap-2">
        <div className="flex size-7 items-center justify-center rounded-lg bg-[#2963E8]/10 text-[#2963E8]">
          <Sparkles className="size-3.5" />
        </div>
        <h2 className="text-sm font-bold text-foreground">Aides recommandées pour vous</h2>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <AidCardSkeleton key={i} />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {aids.map((aid, i) => (
            <AidCard key={aid.aide_id} aid={aid} index={i} />
          ))}
        </div>
      )}
    </motion.div>
  )
}

/* ─────────────────────────────────────────
   Page principale
───────────────────────────────────────── */
export default function DiscussionPage() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [sending, setSending] = useState(false)
  const [chatInputVal, setChatInputVal] = useState('')

  const [recommendations, setRecommendations] = useState([])
  const [recsLoading, setRecsLoading] = useState(false)

  const messagesEndRef = useRef(null)

  /* ── Auto-scroll ── */
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, sending, scrollToBottom])

  /* ── Charger les recommandations ── */
  const loadRecommendations = useCallback(async () => {
    setRecsLoading(true)
    try {
      const data = await dashboardService.getRecommendations()
      setRecommendations(Array.isArray(data) ? data : [])
    } catch {
      setRecommendations([])
    } finally {
      setRecsLoading(false)
    }
  }, [])

  /* ── Charger la conversation ── */
  const loadConversation = useCallback(async () => {
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
      const formatted = data.messages.map((m) => ({
        id: m.discussion_id,
        sender: m.expediteur,
        text: m.contenu,
        timestamp: m.date_creation || null,
      }))
      setMessages(formatted)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    loadConversation()
  }, [loadConversation])

  /* ── Charger les recommandations au montage ── */
  useEffect(() => {
    loadRecommendations()
  }, [loadRecommendations])

  /* ── Envoyer un message ── */
  const handleSend = async (text) => {
    if (!text.trim() || sending) return

    const now = new Date().toISOString()

    const tempUserMsg = {
      id: Date.now(),
      sender: 'user',
      text,
      timestamp: now,
    }
    setMessages((prev) => [...prev, tempUserMsg])
    setSending(true)

    try {
      const res = await dashboardService.sendChatMessage(text, id)

      const botMsg = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: res.bot_message.contenu,
        timestamp: res.bot_message.date_creation || new Date().toISOString(),
      }
      setMessages((prev) => [...prev, botMsg])

      // Redirect to the created conversation ID (nouveau chat → chat avec ID)
      if (!id && res.historique_id) {
        navigate(`/dashboard/discussion/${res.historique_id}`, { replace: true })
      }

      // Recharger les recommandations après chaque échange (le profil IA s'enrichit)
      loadRecommendations()
    } catch {
      const errorMsg = {
        id: Date.now() + 2,
        sender: 'assistant',
        text: "Une erreur est survenue lors de l'envoi de votre message. Veuillez réessayer.",
        isError: true,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setSending(false)
    }
  }

  const handleSuggestionSelect = (text) => {
    setChatInputVal(text)
  }

  const handleBack = () => navigate(-1)
  const handleNewChat = () => navigate('/dashboard/discussion')

  /* ══════════════════════════════════════════
     États de chargement initial
  ══════════════════════════════════════════ */
  if (loading) {
    return (
      <div className="flex flex-1 flex-col px-4 py-6 sm:px-8">
        {/* Header skeleton */}
        <div className="mb-6 flex items-center justify-between border-b border-border/60 pb-4 shrink-0">
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="icon"
              onClick={handleBack}
              className="size-9 border-border text-muted-foreground"
            >
              <ArrowLeft className="size-4" />
            </Button>
            <div className="space-y-1">
              <div className="h-4 w-32 bg-muted animate-pulse rounded-md" />
              <div className="h-3 w-48 bg-muted animate-pulse rounded-md" />
            </div>
          </div>
        </div>
        <div className="max-w-3xl mx-auto w-full">
          <ChatMessageSkeleton />
        </div>
      </div>
    )
  }

  /* ══════════════════════════════════════════
     État d'erreur
  ══════════════════════════════════════════ */
  if (error) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center p-8 text-center">
        <div className="rounded-full bg-destructive/10 p-4 text-destructive mb-4">
          <AlertTriangle className="size-7" />
        </div>
        <h3 className="text-base font-bold text-foreground">Erreur de chargement</h3>
        <p className="mt-2 text-sm text-muted-foreground max-w-sm leading-relaxed">
          Impossible d'ouvrir la discussion. Veuillez réessayer ou retourner au tableau de bord.
        </p>
        <div className="mt-5 flex flex-wrap justify-center gap-3">
          <Button
            onClick={loadConversation}
            className="bg-[#2963E8] hover:bg-[#1e52c7] text-white"
            id="retry-load-btn"
          >
            <RefreshCw className="mr-2 size-4" />
            Réessayer
          </Button>
          <Button variant="outline" onClick={() => navigate('/dashboard')}>
            Retour au tableau de bord
          </Button>
        </div>
      </div>
    )
  }

  /* ══════════════════════════════════════════
     Interface principale
  ══════════════════════════════════════════ */
  return (
    <div className="flex flex-1 flex-col px-4 py-6 sm:px-8">

      {/* ── En-tête ── */}
      <div className="mb-5 flex items-center justify-between border-b border-border/60 pb-4 shrink-0">
        <div className="flex items-center gap-3 min-w-0">
          <Button
            variant="outline"
            size="icon"
            onClick={handleBack}
            className="size-9 border-border text-muted-foreground hover:bg-muted shrink-0"
            aria-label="Page précédente"
            id="back-btn"
          >
            <ArrowLeft className="size-4" />
          </Button>
          <div className="min-w-0">
            <h2 className="flex items-center gap-1.5 text-sm font-bold text-foreground">
              <Bot className="size-4 text-[#2963E8]" />
              Assistant IA AidFinder
            </h2>
            <p className="truncate text-xs text-muted-foreground">
              Découvrez vos aides financières en discutant
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Bouton Nouveau Chat */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleNewChat}
            className="hidden sm:flex items-center gap-1.5 text-xs border-border text-muted-foreground hover:text-[#2963E8] hover:border-[#2963E8]/40"
            id="new-chat-header-btn"
          >
            <Plus className="size-3.5" />
            Nouveau chat
          </Button>

          <Button
            variant="ghost"
            onClick={() => navigate('/dashboard')}
            className="text-xs font-semibold text-[#2963E8] hover:bg-[#2963E8]/10"
            id="quit-discussion-btn"
          >
            Quitter
          </Button>
        </div>
      </div>

      {/* ── Zone de messages ── */}
      <div className="flex-1 overflow-y-auto pr-1 max-w-3xl mx-auto w-full">
        {messages.length === 0 ? (
          /* Empty state + suggestions */
          <EmptyChatState onSelect={handleSuggestionSelect} />
        ) : (
          <div className="space-y-3 py-2">
            <AnimatePresence initial={false}>
              {messages.map((msg) => (
                <ChatBubble key={msg.id} msg={msg} />
              ))}
            </AnimatePresence>

            {/* Indicateur "IA en train d'écrire..." */}
            <AnimatePresence>
              {sending && (
                <motion.div
                  key="typing-indicator"
                  variants={messageVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                >
                  <ChatTypingIndicator />
                </motion.div>
              )}
            </AnimatePresence>

            <div ref={messagesEndRef} />
          </div>
        )}

        {/* ── Cartes d'aides recommandées (visibles si conversation active) ── */}
        {messages.length > 0 && (
          <div className="max-w-3xl mx-auto">
            <AidsRecommendedSection aids={recommendations} loading={recsLoading} />
          </div>
        )}
      </div>

      {/* ── Zone de saisie ── */}
      <div className="sticky bottom-0 mt-4 bg-background pt-3 pb-4 shrink-0">
        <ChatInput
          value={chatInputVal}
          onChange={setChatInputVal}
          onSend={handleSend}
          disabled={sending}
        />
      </div>
    </div>
  )
}

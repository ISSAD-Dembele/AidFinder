import { useEffect, useState, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useProfile } from '@/src/contexts/ProfileContext'
import useDashboard from '@/src/hooks/useDashboard'

// Composants Dashboard
import DashboardHeader from '@/src/components/dashboard/DashboardHeader'
import ProfileCard from '@/src/components/dashboard/ProfileCard'
import StatsCards from '@/src/components/dashboard/StatsCards'
import RecommendationSection from '@/src/components/dashboard/RecommendationSection'
import HistorySection from '@/src/components/dashboard/HistorySection'
import RecentAidsSection from '@/src/components/dashboard/RecentAidsSection'
import QuickActions from '@/src/components/dashboard/QuickActions'
import SkeletonLoader from '@/src/components/dashboard/SkeletonLoader'

// Composants Chatbot
import ChatSuggestions from '@/src/components/dashboard/ChatSuggestions'
import ChatInput from '@/src/components/dashboard/ChatInput'

// UI & Icons
import { Button } from '@/components/ui/button'
import { ArrowLeft, Bot, Sparkles, User } from 'lucide-react'

export default function DashbordUI() {
  const { profile } = useProfile()
  const { data, loading, error, refresh } = useDashboard()
  const [searchParams, setSearchParams] = useSearchParams()
  
  // Lecture de la vue depuis l'URL (?view=chat ou ?view=dashboard)
  const view = searchParams.get('view') || 'dashboard'
  const selectedConvId = searchParams.get('id')

  // Gestion des messages de discussion interactifs
  const [messages, setMessages] = useState([])
  const [chatInputVal, setChatInputVal] = useState('')
  const messagesEndRef = useRef(null)

  // Scroll automatique vers le bas des messages du chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    if (view === 'chat') {
      scrollToBottom()
    }
  }, [messages, view])

  // Charger ou initialiser la discussion lors d'un changement de vue ou de conversation
  useEffect(() => {
    if (view !== 'chat') return

    let active = true
    const initChat = async () => {
      await Promise.resolve()
      if (!active) return

      if (selectedConvId && data?.dernieres_conversations) {
        const conv = data.dernieres_conversations.find(
          (c) => String(c.historique_id) === String(selectedConvId)
        )
        if (conv) {
          setMessages([
            {
              id: 'init-user',
              sender: 'user',
              text: conv.titre_resume || 'Reprendre la discussion',
            },
            {
              id: 'init-bot',
              sender: 'assistant',
              text: `Bonjour ! Content de vous retrouver pour continuer notre discussion à propos de : "${conv.titre_resume}". Comment puis-je vous aider aujourd'hui ?`,
            },
          ])
          return
        }
      }

      // Discussion vierge
      setMessages([])
    }

    initChat()

    return () => {
      active = false
    }
  }, [view, selectedConvId, data])

  // Scroll fluide vers une section ciblée
  useEffect(() => {
    const scrollTarget = searchParams.get('scroll')
    if (scrollTarget && view === 'dashboard') {
      // Un léger délai pour s'assurer que le rendu est terminé
      const timer = setTimeout(() => {
        const element = document.getElementById(scrollTarget)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }, 100)
      return () => clearTimeout(timer)
    }
  }, [searchParams, view])

  // Handlers pour les actions du chat
  const handleStartChat = () => {
    setSearchParams({ view: 'chat' })
  }

  const handleContinueChat = (conv) => {
    setSearchParams({ view: 'chat', id: String(conv.historique_id) })
  }

  const handleCloseChat = () => {
    setSearchParams({ view: 'dashboard' })
  }

  const handleSuggestionSelect = (text) => {
    setChatInputVal(text)
  }

  const handleSend = (text) => {
    const userMsg = { id: Date.now(), sender: 'user', text }
    setMessages((prev) => [...prev, userMsg])
    
    // Simulation d'une réponse de l'assistant IA
    setTimeout(() => {
      const assistantMsg = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: `Merci pour votre demande : "${text}". Notre assistant analyse actuellement votre profil (${profile?.region || 'non renseignée'}, ${profile?.niveau_etude || 'sans diplôme'}) afin de vous proposer les meilleures aides d'État éligibles. Cette fonctionnalité sera entièrement connectée au modèle IA dans la prochaine version.`,
      }
      setMessages((prev) => [...prev, assistantMsg])
      // Rafraîchir les stats du dashboard en tâche de fond (simulé)
      refresh()
    }, 850)
  }

  const handleExportPDF = () => {
    window.print()
  }

  if (loading) {
    return (
      <div className="flex-1 px-4 py-8 sm:px-8 md:py-10">
        <SkeletonLoader />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center p-8 text-center">
        <div className="rounded-full bg-destructive/10 p-3 text-destructive">
          <Bot className="size-6" />
        </div>
        <h3 className="mt-4 text-base font-bold text-foreground">Erreur de chargement</h3>
        <p className="mt-2 text-sm text-muted-foreground max-w-sm">
          Impossible de se connecter au serveur backend. Veuillez vérifier que le serveur est démarré.
        </p>
        <Button onClick={refresh} className="mt-4 bg-[#2963E8] hover:bg-[#1e52c7] text-white">
          Réessayer
        </Button>
      </div>
    )
  }

  // --- VUE CHATBOT AI ---
  if (view === 'chat') {
    return (
      <div className="flex flex-1 flex-col px-4 py-6 sm:px-8">
        {/* En-tête du chat */}
        <div className="mb-6 flex items-center justify-between border-b border-border/60 pb-4">
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="icon"
              onClick={handleCloseChat}
              className="size-9 border-border text-muted-foreground hover:bg-muted"
              aria-label="Retour au tableau de bord"
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
            onClick={handleCloseChat}
            className="text-xs font-semibold text-[#2963E8] hover:bg-[#2963E8]/10"
          >
            Quitter la discussion
          </Button>
        </div>

        {/* Zone des messages */}
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
                          ? 'bg-muted/40 text-foreground border border-border/40 rounded-tl-none'
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
                );
              })}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Formulaire de saisie fixe en bas */}
        <div className="sticky bottom-0 mt-auto bg-white pt-4 pb-4">
          <ChatInput
            value={chatInputVal}
            onChange={setChatInputVal}
            onSend={handleSend}
          />
        </div>
      </div>
    )
  }

  // --- VUE TABLEAU DE BORD SAAS ---
  return (
    <div className="flex-1 px-4 py-6 sm:px-8 sm:py-8 space-y-8">
      {/* Header */}
      <DashboardHeader nom={data?.nom_utilisateur || profile?.nom} />

      {/* Grid Principal */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Colonne Gauche : Stats & Recommandations (2/3 de l'écran) */}
        <div className="lg:col-span-2 space-y-8">
          {/* Cartes Statistiques */}
          <StatsCards
            recherches={data?.nombre_recherches}
            conversations={data?.nombre_conversations}
            recommandations={data?.nombre_recommandations}
            pdfExportes={data?.nombre_pdf_exportes}
          />

          {/* Section Recommandations */}
          <div id="recommendations" className="space-y-4 pt-2">
            <div className="flex items-center justify-between">
              <h2 className="flex items-center gap-2 text-base font-bold text-foreground">
                <Sparkles className="size-5 text-amber-500 fill-amber-500" />
                Recommandations IA pour vous
              </h2>
            </div>
            <RecommendationSection recommendations={data?.dernieres_recommandations_ia} />
          </div>
        </div>

        {/* Colonne Droite : Infos Profil & Actions & Historique (1/3 de l'écran) */}
        <div className="space-y-6">
          {/* Carte Profil */}
          <ProfileCard />

          {/* Actions Rapides */}
          <QuickActions
            onStartChat={handleStartChat}
            onExportPDF={handleExportPDF}
          />

          {/* Historique Récent */}
          <div id="history" className="space-y-3 pt-2">
            <h3 className="text-sm font-semibold text-foreground">Historique des conversations</h3>
            <HistorySection
              conversations={data?.dernieres_conversations}
              onContinueChat={handleContinueChat}
            />
          </div>

          {/* Dernières Aides Consultées */}
          <div className="space-y-3 pt-2">
            <h3 className="text-sm font-semibold text-foreground">Dernières aides consultées</h3>
            <RecentAidsSection recentAids={data?.dernieres_aides_consultees} />
          </div>
        </div>
      </div>
    </div>
  )
}

import { useCallback, useRef, useState } from 'react'
import dashboardService from '@/src/services/dashboardService'

/**
 * Hook custom pour le streaming SSE du chatbot AidFinder.
 *
 * Cycle de vie d'un message :
 *  1. isThinking = true  → TypingIndicator visible ("AidFinder IA est en train d'écrire...")
 *  2. Premier chunk reçu → isThinking = false, isStreaming = true
 *     La bulle IA apparaît et grandit progressivement
 *  3. Événement "done" → isStreaming = false
 *     La bulle est finalisée, suggestions + recommendations sont mises à jour
 *
 * @returns {{
 *   streamingText: string,
 *   isThinking: boolean,
 *   isStreaming: boolean,
 *   streamError: Error|null,
 *   startStream: (message: string, historiqueId: number|null, callbacks: object) => void,
 *   cancelStream: () => void,
 * }}
 */
export default function useStreamingChat() {
  // Texte accumulé pendant le streaming (mis à jour chunk par chunk)
  const [streamingText, setStreamingText] = useState('')
  // true = en attente du 1er chunk (TypingIndicator visible)
  const [isThinking, setIsThinking] = useState(false)
  // true = chunks en cours de réception (bulle IA visible et croissante)
  const [isStreaming, setIsStreaming] = useState(false)
  // Erreur éventuelle du stream
  const [streamError, setStreamError] = useState(null)

  // Référence vers le contrôleur d'annulation (AbortController)
  const abortRef = useRef(null)

  /**
   * Démarre un stream SSE pour le message donné.
   *
   * @param {string} message - Texte envoyé par l'utilisateur
   * @param {number|null} historiqueId - ID de la conversation (null = nouvelle)
   * @param {object} opts
   * @param {function} opts.onDone    - (metadata) => void — appelé quand le stream est terminé
   * @param {function} opts.onError   - (err) => void — appelé en cas d'erreur
   */
  const startStream = useCallback((message, historiqueId, { onDone, onError } = {}) => {
    // Annuler un éventuel stream précédent
    if (abortRef.current) {
      abortRef.current.abort()
    }

    // Réinitialiser l'état
    setStreamingText('')
    setStreamError(null)
    setIsThinking(true)
    setIsStreaming(false)

    let firstChunkReceived = false

    abortRef.current = dashboardService.streamChatMessage(
      message,
      historiqueId,
      {
        onChunk: (chunk) => {
          if (!firstChunkReceived) {
            firstChunkReceived = true
            // Premier chunk : on passe de "thinking" à "streaming"
            setIsThinking(false)
            setIsStreaming(true)
          }
          // Accumuler le texte sans reconstruire tout le DOM
          setStreamingText((prev) => prev + chunk)
        },

        onDone: (metadata) => {
          setIsStreaming(false)
          setIsThinking(false)
          onDone?.(metadata)
        },

        onError: (err) => {
          setIsStreaming(false)
          setIsThinking(false)
          setStreamError(err)
          onError?.(err)
        },
      }
    )
  }, [])

  /** Annule le stream en cours (ex: composant démonté) */
  const cancelStream = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort()
      abortRef.current = null
    }
    setIsStreaming(false)
    setIsThinking(false)
  }, [])

  return {
    streamingText,
    isThinking,
    isStreaming,
    streamError,
    startStream,
    cancelStream,
  }
}

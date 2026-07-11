import { useState } from 'react'
import { AnimatePresence } from 'framer-motion'
import { Sparkles } from 'lucide-react'
import EmptyState from './EmptyState'
import AidCard from './AidCard'
import AidDetailModal from './AidDetailModal'
import dashboardService from '@/src/services/dashboardService'

export default function RecommendationSection({ recommendations = [] }) {
  const [selectedAid, setSelectedAid] = useState(null)

  if (!recommendations || recommendations.length === 0) {
    return (
      <EmptyState
        title="Aucune recommandation pour le moment"
        description="Complétez votre profil ou démarrez une conversation avec le chatbot pour obtenir des recommandations d'aides adaptées."
        icon={Sparkles}
      />
    )
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {recommendations.map((aid, idx) => (
          <AidCard
            key={aid.aide_id}
            aid={aid}
            index={idx}
            onShowDetail={(a) => setSelectedAid(a)}
          />
        ))}
      </div>

      {/* Modal de détail d'aide pour les recommandations */}
      <AnimatePresence>
        {selectedAid && (
          <AidDetailModal
            aid={selectedAid}
            onClose={() => setSelectedAid(null)}
            onConsult={async () => {
              try {
                await dashboardService.recordAidConsultation(selectedAid.aide_id)
              } catch (err) {
                console.error("Erreur enregistrement consultation:", err)
              } finally {
                if (selectedAid.url_officielle) {
                  window.open(selectedAid.url_officielle, '_blank', 'noopener,noreferrer')
                }
                setSelectedAid(null)
              }
            }}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

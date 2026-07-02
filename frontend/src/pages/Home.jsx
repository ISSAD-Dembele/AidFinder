import { Link } from 'react-router-dom'
import { ArrowRight, Search, MessageSquare, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import heroImage from '@/src/assets/images/image_finder.png'

const FEATURES = [
  {
    icon: Search,
    title: 'Recherche intelligente',
    description: 'Trouvez les aides financières adaptées à votre profil en quelques clics.',
  },
  {
    icon: MessageSquare,
    title: 'Chatbot IA',
    description: 'Discutez avec notre assistant pour obtenir des recommandations personnalisées.',
  },
  {
    icon: FileText,
    title: 'Export PDF',
    description: 'Exportez vos résultats et conservez un historique de vos recherches.',
  },
]

/** Page d'accueil visiteur — point d'entrée de l'application */
export default function Home() {
  return (
    <div className="overflow-hidden">
      {/* Hero */}
      <section className="relative bg-gradient-to-b from-[#2963E8]/5 to-background">
        <div className="mx-auto grid max-w-6xl items-center gap-10 px-4 py-16 sm:px-6 md:py-24 lg:grid-cols-2 lg:gap-16 lg:px-8">
          <div className="order-2 lg:order-1">
            <span className="mb-4 inline-block rounded-full bg-[#2963E8]/10 px-4 py-1.5 text-xs font-medium text-[#2963E8]">
              Plateforme intelligente d&apos;aides financières
            </span>
            <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl lg:text-5xl">
              Trouvez les aides qui{' '}
              <span className="text-[#2963E8]">vous correspondent</span>
            </h1>
            <p className="mt-5 max-w-lg text-base leading-relaxed text-muted-foreground sm:text-lg">
              AidFinder vous accompagne dans la recherche de subventions et aides
              financières grâce à un chatbot intelligent adapté à votre situation.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Button
                size="lg"
                className="bg-[#2963E8] hover:bg-[#1e52c7]"
                asChild
              >
                <Link to="/register">
                  Commencer maintenant
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link to="/login">Se connecter</Link>
              </Button>
            </div>
          </div>

          <div className="order-1 flex justify-center lg:order-2">
            <img
              src={heroImage}
              alt="Utilisateur consultant AidFinder sur son ordinateur"
              className="w-full max-w-md rounded-2xl object-contain drop-shadow-lg lg:max-w-lg"
            />
          </div>
        </div>
      </section>

      {/* Texte introductif avant les fonctionnalités */}
      <section className="border-y border-border/60 bg-muted/30 py-16 md:py-20">
        <div className="mx-auto max-w-6xl px-4 text-center sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-foreground sm:text-3xl">
            Simplifiez votre recherche d&apos;aides
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
            Fini les recherches interminables. Notre IA analyse votre profil et
            vous propose les aides les plus pertinentes.
          </p>
        </div>
      </section>

      {/* Fonctionnalités */}
      <section className="py-16 md:py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="mb-12 text-center">
            <h2 className="text-2xl font-bold text-foreground sm:text-3xl">
              Fonctionnalités clés
            </h2>
            <p className="mt-3 text-muted-foreground">
              Tout ce dont vous avez besoin pour trouver vos aides
            </p>
          </div>

          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map(({ icon: Icon, title, description }) => (
              <div
                key={title}
                className="rounded-xl border border-border bg-card p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="mb-4 flex size-10 items-center justify-center rounded-lg bg-[#2963E8]/10">
                  <Icon className="size-5 text-[#2963E8]" />
                </div>
                <h3 className="font-semibold text-foreground">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  {description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA final */}
      <section className="bg-[#1a2332] py-16 text-white md:py-20">
        <div className="mx-auto max-w-6xl px-4 text-center sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold sm:text-3xl">
            Prêt à découvrir vos aides ?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-white/70">
            Créez votre compte en quelques secondes et commencez à discuter avec
            notre assistant intelligent.
          </p>
          <Button
            size="lg"
            className="mt-8 bg-[#2963E8] hover:bg-[#1e52c7]"
            asChild
          >
            <Link to="/register">
              Créer un compte
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        </div>
      </section>
    </div>
  )
}

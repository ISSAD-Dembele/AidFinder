import { motion } from 'framer-motion'
import { Bot, User } from 'lucide-react'
import { formatLocalDateTime } from '@/src/utils/date'

const bubbleVariants = {
  hidden: { opacity: 0, y: 12, scale: 0.97 },
  visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.28, ease: 'easeOut' } },
  exit: { opacity: 0, y: -6, transition: { duration: 0.15 } },
}

export default function ConversationBubble({ msg }) {
  const isBot = msg.sender === 'assistant'

  return (
    <motion.div
      layout
      variants={bubbleVariants}
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

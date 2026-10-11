// Callout banner used for alerts, environment notes, or disclaimer notifications
import { Activity } from 'lucide-react'

export default function NoticeBanner({
  icon: Icon = Activity,
  title = 'Prototype preview',
  message = 'Zone scores, temperatures and impact estimates shown here are illustrative, not live safety alerts or verified forecasts.'
}) {
  return (
    <section className="notice" role="status">
      <span className="notice-icon" aria-hidden="true">
        <Icon size={17} />
      </span>
      <p>
        <strong>{title}</strong> — {message}
      </p>
    </section>
  )
}

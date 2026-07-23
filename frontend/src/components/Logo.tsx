export const BRAND_NAME = 'Zapture'

type LogoProps = {
  size?: number
  withWordmark?: boolean
  badge?: boolean
  className?: string
}

export function Logo({ size = 28, withWordmark = true, badge = false, className }: LogoProps) {
  const mark = (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <defs>
        <linearGradient id="zapture-mark-gradient" x1="4" y1="2" x2="20" y2="22" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="var(--brand-navy-700)" />
          <stop offset="1" stopColor="var(--brand-navy)" />
        </linearGradient>
      </defs>
      <path
        d="M13.2 2.2c.35-.44 1.05-.19 1.05.36v5.53c0 .64.51 1.16 1.14 1.16h4.9c.48 0 .76.55.46.93l-6.9 8.66c-.35.44-1.05.2-1.05-.35v-5.53c0-.64-.5-1.16-1.13-1.16H6.75c-.48 0-.76-.54-.46-.93z"
        fill="url(#zapture-mark-gradient)"
      />
    </svg>
  )

  return (
    <span className={['logo', className].filter(Boolean).join(' ')}>
      {badge ? <span className="logo-badge">{mark}</span> : mark}
      {withWordmark && <span className="logo-wordmark">{BRAND_NAME}</span>}
    </span>
  )
}

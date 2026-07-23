export const BRAND_NAME = 'Zapture'

type LogoProps = {
  size?: number
  withWordmark?: boolean
  badge?: boolean
  className?: string
}

export function Logo({ size = 28, withWordmark = true, badge = false, className }: LogoProps) {
  const barWidth = Math.max(2, Math.round(size * 0.095))
  const gap = Math.max(1, Math.round(size * 0.08))
  const barHeights = [0.21, 0.34, 0.46].map((factor) => Math.round(size * factor))
  const outerRadius = Math.round(size * 0.31)
  const cornerRadius = Math.max(2, Math.round(size * 0.09))

  const mark = (
    <span
      aria-hidden="true"
      className="logo-mark"
      style={{
        width: size,
        height: size,
        borderRadius: `${outerRadius}px ${outerRadius}px ${outerRadius}px ${cornerRadius}px`,
        background: 'var(--zapture-gradient)',
        paddingBottom: Math.round(size * 0.18),
        gap,
      }}
    >
      {barHeights.map((height, index) => (
        <span key={index} className="logo-mark-bar" style={{ width: barWidth, height }} />
      ))}
    </span>
  )

  return (
    <span className={['logo', className].filter(Boolean).join(' ')}>
      {badge ? <span className="logo-badge">{mark}</span> : mark}
      {withWordmark && <span className="logo-wordmark">{BRAND_NAME}</span>}
    </span>
  )
}

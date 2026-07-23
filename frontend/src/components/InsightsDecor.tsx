export function PageInsightsBackdrop() {
  return (
    <div className="decor-backdrop" aria-hidden="true">
      <svg
        className="decor-backdrop-svg decor-parallax-slow"
        viewBox="0 0 1600 1000"
        preserveAspectRatio="xMidYMin slice"
      >
        <defs>
          <linearGradient id="decor-wave-fill" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="var(--zapture-green)" stopOpacity="0.22" />
            <stop offset="1" stopColor="var(--zapture-blue)" stopOpacity="0.16" />
          </linearGradient>
          <linearGradient id="decor-wave-stroke" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stopColor="var(--zapture-green)" stopOpacity="0.55" />
            <stop offset="1" stopColor="var(--zapture-blue)" stopOpacity="0.55" />
          </linearGradient>
        </defs>
        <path
          d="M0,420 C 220,340 380,520 560,460 C 760,394 900,220 1100,260 C 1300,300 1420,180 1600,140 L1600,0 L0,0 Z"
          fill="url(#decor-wave-fill)"
        />
        <path
          d="M0,420 C 220,340 380,520 560,460 C 760,394 900,220 1100,260 C 1300,300 1420,180 1600,140"
          fill="none"
          stroke="url(#decor-wave-stroke)"
          strokeWidth="4"
          strokeLinecap="round"
        />
      </svg>

      <svg
        className="decor-backdrop-svg decor-backdrop-bars decor-parallax-fast"
        viewBox="0 0 1600 1000"
        preserveAspectRatio="xMidYMax slice"
      >
        <g fill="var(--zapture-blue)" opacity="0.09">
          <rect x="120" y="640" width="90" height="360" rx="18" />
          <rect x="260" y="520" width="90" height="480" rx="18" />
          <rect x="400" y="700" width="90" height="300" rx="18" />
        </g>
        <g fill="var(--zapture-green)" opacity="0.1">
          <rect x="1180" y="560" width="100" height="440" rx="20" />
          <rect x="1330" y="460" width="100" height="540" rx="20" />
          <rect x="1480" y="640" width="100" height="360" rx="20" />
        </g>
      </svg>

      <div className="decor-backdrop-grid" />
    </div>
  )
}

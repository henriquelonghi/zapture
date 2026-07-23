import { Link, NavLink } from 'react-router-dom'
import { Logo } from './Logo'

const NAV_ITEMS = [
  { to: '/relatorio', label: 'Relatório' },
  { to: '/conectar', label: 'Conectar' },
  { to: '/configuracoes', label: 'Configurações' },
  { to: '/plano', label: 'Plano' },
]

type AppHeaderProps = {
  showNav?: boolean
}

export function AppHeader({ showNav = true }: AppHeaderProps) {
  return (
    <header className="app-header">
      <Link to="/" className="app-header-logo">
        <Logo />
      </Link>
      {showNav && (
        <nav className="app-header-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => 'app-header-link' + (isActive ? ' active' : '')}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      )}
    </header>
  )
}

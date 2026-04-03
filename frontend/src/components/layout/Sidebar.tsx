import { NavLink } from 'react-router-dom';
import { cn } from '@/utils/cn';
import { useTranslation } from '@/i18n/useTranslation';

const navItemDefs = [
  {
    translationKey: 'nav.dashboard',
    path: '/dashboard',
    icon: 'M4 5a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm10 0a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zm10-1a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1h-4a1 1 0 01-1-1v-5z',
  },
  {
    translationKey: 'nav.statements',
    path: '/statements',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  },
  {
    translationKey: 'nav.accounts',
    path: '/chart-of-accounts',
    icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
  },
  {
    translationKey: 'nav.targets',
    path: '/targets',
    icon: 'M13 10V3L4 14h7v7l9-11h-7z',
  },
  {
    translationKey: 'nav.upload',
    path: '/upload',
    icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12',
  },
  {
    translationKey: 'nav.budget',
    path: '/budget',
    icon: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z',
  },
  {
    translationKey: 'nav.settings',
    path: '/settings',
    icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z',
  },
];

export function Sidebar() {
  const { t } = useTranslation();
  return (
    <aside className="flex w-[220px] flex-col h-screen sticky top-0 bg-[#0f1629] text-white">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 pt-6 pb-8">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-400 via-blue-500 to-indigo-600 text-sm font-extrabold shadow-[0_0_20px_rgba(59,130,246,0.4)]">
          IF
        </div>
        <div>
          <div className="text-[15px] font-bold tracking-tight font-display">InterFinOps</div>
          <div className="text-[10px] font-medium text-blue-300/60 uppercase tracking-widest">Finance</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 space-y-0.5">
        {navItemDefs.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] font-medium transition-all duration-200',
                isActive
                  ? 'bg-gradient-to-r from-blue-500/20 to-blue-400/5 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
              )
            }
          >
            {({ isActive }) => (
              <>
                <div className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-lg transition-all duration-200',
                  isActive
                    ? 'bg-blue-500 shadow-[0_0_12px_rgba(59,130,246,0.5)]'
                    : 'bg-white/[0.05] group-hover:bg-white/[0.08]'
                )}>
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
                  </svg>
                </div>
                <span>{t(item.translationKey)}</span>
                {isActive && (
                  <div className="ml-auto h-1.5 w-1.5 rounded-full bg-blue-400 shadow-[0_0_6px_rgba(96,165,250,0.8)]" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom: version/branding */}
      <div className="px-5 py-4 border-t border-white/[0.04]">
        <div className="text-[10px] text-slate-500">InterFinOps {t('common.version')} 1.0</div>
        <div className="text-[10px] text-slate-600">{t('common.gdprCompliant')}</div>
      </div>
    </aside>
  );
}

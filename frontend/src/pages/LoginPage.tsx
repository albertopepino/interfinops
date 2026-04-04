import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useLogin } from '@/api/hooks';
import { useAuthStore } from '@/store/authStore';
import { useDashboardStore } from '@/store/dashboardStore';
import { useTranslation } from '@/i18n/useTranslation';
import { LANGUAGES } from '@/i18n/translations';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const loginMutation = useLogin();
  const { t } = useTranslation();
  const setLanguage = useDashboardStore((s) => s.setLanguage);
  const currentLang = useDashboardStore((s) => s.language);

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/dashboard';

  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      await loginMutation.mutateAsync(data);
      navigate(from, { replace: true });
    } catch {
      // handled by mutation state
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4">
      {/* Background - clean gradient, no orbs or grid */}
      <div
        className="absolute inset-0 -z-10"
        style={{
          background: 'linear-gradient(140deg, #062033 0%, #0c3a5f 30%, #1a6fb5 55%, #3a9d6a 80%, #2d8a4e 100%)',
        }}
      />

      {/* Card */}
      <div className="w-full max-w-[440px] animate-scale-in" style={{ animationFillMode: 'backwards' }}>
        {/* Logo */}
        <div className="mb-10 flex justify-center">
          <img
            src="/logo.png"
            alt="ConsolidaSuite"
            className="h-20 w-auto"
          />
        </div>

        {/* Form card - clean white with shadow */}
        <div className="rounded-2xl bg-white p-8 shadow-lg dark:bg-slate-900 dark:border dark:border-slate-800">
          <div className="mb-7">
            <h1 className="text-xl font-semibold text-slate-900 dark:text-white">
              {t('login.welcome')}
            </h1>
            <p className="mt-1.5 text-sm text-slate-500 dark:text-slate-400">
              {t('login.subtitle')}
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label htmlFor="email" className="input-label">
                {t('login.email')}
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                className="input w-full"
                placeholder="name@company.com"
                {...register('email')}
              />
              {errors.email && (
                <p className="mt-1.5 text-xs text-red-500">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="input-label">
                {t('login.password')}
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                className="input w-full"
                placeholder="Enter your password"
                {...register('password')}
              />
              {errors.password && (
                <p className="mt-1.5 text-xs text-red-500">{errors.password.message}</p>
              )}
            </div>

            {loginMutation.isError && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 dark:border-red-800 dark:bg-red-900/20">
                <p className="text-sm text-red-600 dark:text-red-400">
                  {loginMutation.error instanceof Error
                    ? loginMutation.error.message
                    : t('login.invalidCredentials')}
                </p>
              </div>
            )}

            <button
              type="submit"
              disabled={loginMutation.isPending}
              className="btn-primary w-full justify-center py-3"
            >
              {loginMutation.isPending ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  ...
                </span>
              ) : (
                t('login.signIn')
              )}
            </button>
          </form>
        </div>

        {/* Language switcher */}
        <div className="mt-8 flex items-center justify-center gap-1">
          {LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              onClick={() => setLanguage(lang.code)}
              className={`rounded-lg px-3 py-2 text-[13px] font-medium transition-colors ${
                currentLang === lang.code
                  ? 'bg-white/15 text-white'
                  : 'text-white/30 hover:text-white/60 hover:bg-white/5'
              }`}
            >
              {lang.label}
            </button>
          ))}
        </div>

        {/* Footer */}
        <p className="mt-6 text-center text-[11px] text-white/20">
          {t('login.footerNote')}
        </p>
      </div>
    </div>
  );
}

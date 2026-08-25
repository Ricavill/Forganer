import { forwardRef, type ReactNode } from 'react';

export function PhoneShell({ children }: { children: ReactNode }) {
  return (
    <div
      style={{
        width: 390,
        height: 844,
        background: 'var(--bg)',
        color: 'var(--text)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        position: 'relative',
        borderRadius: 28,
        boxShadow: '0 20px 60px rgba(0,0,0,0.25)',
      }}
    >
      <div style={{ height: 50, flexShrink: 0 }} />
      {children}
    </div>
  );
}

export function ScreenHeader({ title, subtitle, action }: { title: string; subtitle: string; action?: ReactNode }) {
  return (
    <div style={{ padding: '0 22px 18px 22px', flexShrink: 0, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
      <div>
        <h1 style={{ fontWeight: 700, fontSize: 28, lineHeight: 1.1, letterSpacing: '-0.01em' }}>{title}</h1>
        <div style={{ fontSize: 14, color: 'var(--muted)', marginTop: 5 }}>{subtitle}</div>
      </div>
      {action && <div style={{ flexShrink: 0, marginTop: 2 }}>{action}</div>}
    </div>
  );
}

export const ScreenContent = forwardRef<HTMLDivElement, { children: ReactNode }>(function ScreenContent({ children }, ref) {
  return (
    <div ref={ref} style={{ flex: 1, overflowY: 'auto', padding: '2px 22px 24px 22px', display: 'flex', flexDirection: 'column', gap: 22 }}>
      {children}
    </div>
  );
});

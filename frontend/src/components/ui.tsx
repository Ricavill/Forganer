import type { CSSProperties, ReactNode } from 'react';

export function Card({ children, style, onClick }: { children: ReactNode; style?: CSSProperties; onClick?: () => void }) {
  return (
    <div
      onClick={onClick}
      style={{
        background: 'white',
        border: '1px solid var(--border)',
        borderRadius: 14,
        padding: '13px 16px',
        cursor: onClick ? 'pointer' : 'default',
        ...style,
      }}
    >
      {children}
    </div>
  );
}

export function SectionLabel({ children }: { children: ReactNode }) {
  return (
    <div
      style={{
        fontSize: 12,
        fontWeight: 700,
        letterSpacing: '0.06em',
        color: 'var(--muted)',
        textTransform: 'uppercase',
      }}
    >
      {children}
    </div>
  );
}

export function Badge({ children, tone = 'positive' }: { children: ReactNode; tone?: 'positive' | 'negative' }) {
  const bg = tone === 'positive' ? 'var(--accent-tint)' : 'var(--negative-tint)';
  const color = tone === 'positive' ? 'var(--accent-tint-text)' : 'var(--negative-tint-text)';
  return (
    <span style={{ background: bg, color, fontSize: 11, fontWeight: 700, padding: '4px 10px', borderRadius: 100 }}>
      {children}
    </span>
  );
}

export function Avatar({
  initial,
  size = 40,
  bg = 'var(--accent-tint)',
  color = 'var(--accent-tint-text)',
  border,
}: {
  initial: string;
  size?: number;
  bg?: string;
  color?: string;
  border?: string;
}) {
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: '50%',
        background: bg,
        color,
        border,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 700,
        fontSize: size * 0.35,
        flexShrink: 0,
      }}
    >
      {initial}
    </div>
  );
}

export function PrimaryButton({ children, onClick, disabled }: { children: ReactNode; onClick?: () => void; disabled?: boolean }) {
  return (
    <div
      onClick={disabled ? undefined : onClick}
      style={{
        cursor: disabled ? 'default' : 'pointer',
        opacity: disabled ? 0.6 : 1,
        background: 'var(--accent)',
        color: 'white',
        textAlign: 'center',
        padding: 15,
        borderRadius: 14,
        fontWeight: 700,
        fontSize: 15,
      }}
    >
      {children}
    </div>
  );
}

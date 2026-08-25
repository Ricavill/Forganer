import { CalendarIcon, FriendsIcon, MessageIcon, PlusIcon, UserIcon } from './Icons';

export type Tab = 'assistant' | 'calendar' | 'create' | 'friends' | 'profile';

const TABS: { key: Tab; label: string }[] = [
  { key: 'assistant', label: 'Assistant' },
  { key: 'calendar', label: 'Calendar' },
  { key: 'create', label: '' },
  { key: 'friends', label: 'Friends' },
  { key: 'profile', label: 'You' },
];

function tabIcon(key: Tab, active: boolean) {
  const color = active ? 'var(--accent)' : 'var(--muted-light)';
  switch (key) {
    case 'assistant':
      return <MessageIcon color={color} />;
    case 'calendar':
      return <CalendarIcon color={color} />;
    case 'friends':
      return <FriendsIcon color={color} />;
    case 'profile':
      return <UserIcon color={color} />;
    default:
      return null;
  }
}

export function TabBar({ active, onChange }: { active: Tab; onChange: (tab: Tab) => void }) {
  return (
    <div
      style={{
        flexShrink: 0,
        height: 82,
        borderTop: '1px solid var(--border)',
        background: 'white',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-around',
        paddingTop: 11,
      }}
    >
      {TABS.map((tab) =>
        tab.key === 'create' ? (
          <div
            key={tab.key}
            onClick={() => onChange(tab.key)}
            style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 5, width: 52, marginTop: -22 }}
          >
            <div
              style={{
                width: 50,
                height: 50,
                borderRadius: '50%',
                background: 'var(--accent)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 10px oklch(0.6 0.135 40 / 35%)',
              }}
            >
              <PlusIcon />
            </div>
          </div>
        ) : (
          <div
            key={tab.key}
            onClick={() => onChange(tab.key)}
            style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 5, width: 52 }}
          >
            {tabIcon(tab.key, active === tab.key)}
            <span style={{ fontSize: 11, fontWeight: active === tab.key ? 700 : 500, color: active === tab.key ? 'var(--accent)' : 'var(--muted-light)' }}>
              {tab.label}
            </span>
          </div>
        ),
      )}
    </div>
  );
}

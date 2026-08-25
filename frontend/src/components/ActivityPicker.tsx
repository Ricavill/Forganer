import { useState } from 'react';
import { activitiesApi } from '../api/endpoints';
import type { ActivityOut } from '../api/types';
import { ApiError } from '../api/client';
import { Card, SectionLabel } from './ui';
import { SearchIcon } from './Icons';

const inputStyle: React.CSSProperties = {
  width: '100%',
  background: 'white',
  border: '1px solid var(--border)',
  borderRadius: 14,
  padding: '13px 16px',
  fontSize: 14,
  fontFamily: 'inherit',
  color: 'var(--text)',
};

const DUPLICATE_PATTERN = /already exists: '(.+)' \(id=(\d+)\)/;

export function ActivityPicker({ onPick }: { onPick: (activity: ActivityOut) => void }) {
  const [mode, setMode] = useState<'search' | 'create'>('search');
  const [query, setQuery] = useState('');
  const [matches, setMatches] = useState<ActivityOut[]>([]);
  const [searched, setSearched] = useState(false);

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestion, setSuggestion] = useState<{ name: string; id: number } | null>(null);

  async function search() {
    const q = query.trim();
    if (!q) return;
    try {
      setMatches(await activitiesApi.search(q));
    } catch {
      setMatches([]);
    } finally {
      setSearched(true);
    }
  }

  function openCreate() {
    setName(query.trim());
    setDescription('');
    setError(null);
    setSuggestion(null);
    setMode('create');
  }

  async function submitCreate() {
    const trimmedName = name.trim();
    if (!trimmedName) return;
    setCreating(true);
    setError(null);
    setSuggestion(null);
    try {
      const activity = await activitiesApi.create(trimmedName, description.trim() || undefined);
      onPick(activity);
    } catch (err) {
      if (err instanceof ApiError) {
        const match = err.message.match(DUPLICATE_PATTERN);
        if (match) {
          setSuggestion({ name: match[1], id: Number(match[2]) });
          setError(`An activity like this already exists.`);
        } else {
          setError(err.message);
        }
      } else {
        setError('Could not create that activity');
      }
    } finally {
      setCreating(false);
    }
  }

  async function useSuggested() {
    if (!suggestion) return;
    try {
      const activity = await activitiesApi.get(suggestion.id);
      onPick(activity);
    } catch {
      setError('Could not load that activity');
    }
  }

  if (mode === 'create') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <SectionLabel>Create a new activity</SectionLabel>
        <input style={inputStyle} placeholder="Activity name" value={name} onChange={(e) => setName(e.target.value)} autoFocus />
        <textarea
          style={{ ...inputStyle, resize: 'vertical', minHeight: 64, fontFamily: 'inherit' }}
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />

        {error && <div style={{ color: 'var(--negative-tint-text)', fontSize: 13 }}>{error}</div>}

        {suggestion && (
          <Card onClick={useSuggested} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 12, color: 'var(--muted)' }}>Use existing instead</div>
              <div style={{ fontWeight: 600, fontSize: 14, marginTop: 2 }}>{suggestion.name}</div>
            </div>
            <span style={{ fontSize: 13, color: 'var(--accent)', fontWeight: 700 }}>Use this</span>
          </Card>
        )}

        <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
          <div
            onClick={creating ? undefined : submitCreate}
            style={{
              cursor: creating ? 'default' : 'pointer',
              opacity: creating || !name.trim() ? 0.6 : 1,
              background: 'var(--accent)',
              color: 'white',
              fontWeight: 700,
              fontSize: 14,
              padding: '12px 20px',
              borderRadius: 14,
              textAlign: 'center',
            }}
          >
            {creating ? 'Creating…' : 'Create activity'}
          </div>
          <span style={{ fontSize: 13, color: 'var(--muted)', fontWeight: 600, cursor: 'pointer' }} onClick={() => setMode('search')}>
            Back to search
          </span>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <Card style={{ padding: '11px 16px', display: 'flex', alignItems: 'center', gap: 10 }}>
        <SearchIcon color="var(--muted-light)" />
        <input
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setSearched(false);
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter') search();
          }}
          placeholder="Board games, hiking, movie night…"
          style={{ border: 'none', outline: 'none', flex: 1, fontSize: 14, fontFamily: 'inherit', color: 'var(--text)', background: 'transparent' }}
        />
      </Card>
      <div style={{ display: 'flex', gap: 8 }}>
        <div style={{ fontSize: 13, color: 'var(--accent)', fontWeight: 700, cursor: 'pointer' }} onClick={search}>
          Search
        </div>
        <div style={{ fontSize: 13, color: 'var(--accent)', fontWeight: 700, cursor: 'pointer' }} onClick={openCreate}>
          Create new
        </div>
      </div>

      {matches.map((a) => (
        <Card key={a.id} onClick={() => onPick(a)} style={{ fontSize: 14, fontWeight: 600 }}>
          {a.name}
        </Card>
      ))}

      {searched && matches.length === 0 && (
        <div style={{ fontSize: 13, color: 'var(--muted)' }}>
          No matches. <span style={{ color: 'var(--accent)', fontWeight: 700, cursor: 'pointer' }} onClick={openCreate}>Create "{query.trim()}"</span>
        </div>
      )}
    </div>
  );
}

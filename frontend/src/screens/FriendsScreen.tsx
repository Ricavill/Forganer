import { useEffect, useState } from 'react';
import { friendsApi, usersApi } from '../api/endpoints';
import type { FriendInvitationOut, FriendOut, UserOut } from '../api/types';
import { ScreenContent, ScreenHeader } from '../components/PhoneShell';
import { Avatar, Card, SectionLabel } from '../components/ui';
import { PlusIcon, SearchIcon } from '../components/Icons';
import { ApiError } from '../api/client';

const searchBarStyle = {
  borderRadius: 24,
  padding: '11px 18px',
  display: 'flex',
  alignItems: 'center' as const,
  gap: 10,
};

const searchInputStyle = {
  border: 'none',
  outline: 'none',
  flex: 1,
  fontSize: 14,
  fontFamily: 'inherit',
  color: 'var(--text)',
  background: 'transparent',
};

function PlusButton({ onClick, title }: { onClick: () => void; title: string }) {
  return (
    <div
      onClick={onClick}
      title={title}
      style={{
        cursor: 'pointer',
        width: 38,
        height: 38,
        borderRadius: '50%',
        background: 'var(--accent)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 4px 10px oklch(0.6 0.135 40 / 35%)',
      }}
    >
      <PlusIcon size={18} strokeWidth={2.4} />
    </div>
  );
}

function AddFriendsView({ onDone, existingFriendIds }: { onDone: () => void; existingFriendIds: Set<number> }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<UserOut[]>([]);
  const [sentIds, setSentIds] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string | null>(null);

  async function search() {
    const q = query.trim();
    if (!q) {
      setResults([]);
      return;
    }
    try {
      const users = await usersApi.search(q);
      setResults(users.filter((u) => !existingFriendIds.has(u.id)));
    } catch {
      setResults([]);
    }
  }

  async function sendRequest(user: UserOut) {
    try {
      await friendsApi.send(user.id);
      setSentIds((prev) => new Set(prev).add(user.id));
      onDone();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not send that request');
    }
  }

  return (
    <>
      <ScreenHeader
        title="Add friends"
        subtitle="Search for people to add"
        action={
          <div style={{ fontSize: 13, color: 'var(--accent)', fontWeight: 700, cursor: 'pointer', padding: '8px 0' }} onClick={onDone}>
            Cancel
          </div>
        }
      />
      <ScreenContent>
        <Card style={searchBarStyle}>
          <SearchIcon color="var(--muted-light)" />
          <input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') search();
            }}
            placeholder="Search by name or email"
            style={searchInputStyle}
          />
        </Card>
        <div style={{ marginTop: -12, fontSize: 13, color: 'var(--accent)', fontWeight: 700, cursor: 'pointer' }} onClick={search}>
          Search
        </div>

        {error && <div style={{ color: 'var(--negative-tint-text)', fontSize: 13 }}>{error}</div>}

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {results.map((u) => (
            <Card key={u.id} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <Avatar initial={u.name[0]?.toUpperCase() ?? '?'} />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>
                  {u.name} {u.last_name}
                </div>
                <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 1 }}>{u.email}</div>
              </div>
              {sentIds.has(u.id) ? (
                <span style={{ fontSize: 12, color: 'var(--muted)', fontWeight: 600 }}>Sent</span>
              ) : (
                <PlusButton onClick={() => sendRequest(u)} title="Send friend request" />
              )}
            </Card>
          ))}
          {query.trim() && results.length === 0 && <div style={{ color: 'var(--muted)', fontSize: 13 }}>No matches.</div>}
        </div>
      </ScreenContent>
    </>
  );
}

export function FriendsScreen() {
  const [view, setView] = useState<'friends' | 'add'>('friends');
  const [friends, setFriends] = useState<FriendOut[]>([]);
  const [incoming, setIncoming] = useState<FriendInvitationOut[]>([]);
  const [sent, setSent] = useState<FriendInvitationOut[]>([]);
  const [query, setQuery] = useState('');
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const [friendList, incomingList, sentList] = await Promise.all([
        friendsApi.list(),
        friendsApi.listIncomingRequests(),
        friendsApi.listSentRequests(),
      ]);
      setFriends(friendList);
      setIncoming(incomingList.filter((i) => i.status === 1));
      setSent(sentList.filter((i) => i.status === 1));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load friends');
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function cancelSent(invitationId: number) {
    try {
      await friendsApi.cancel(invitationId);
      setSent((prev) => prev.filter((s) => s.id !== invitationId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not cancel that request');
    }
  }

  async function accept(invitationId: number) {
    await friendsApi.accept(invitationId);
    refresh();
  }

  async function reject(invitationId: number) {
    await friendsApi.reject(invitationId);
    refresh();
  }

  if (view === 'add') {
    return (
      <AddFriendsView
        existingFriendIds={new Set(friends.map((f) => f.id))}
        onDone={() => {
          setView('friends');
          refresh();
        }}
      />
    );
  }

  const q = query.trim().toLowerCase();
  const filteredFriends = q
    ? friends.filter((f) => `${f.name} ${f.last_name}`.toLowerCase().includes(q) || f.email.toLowerCase().includes(q))
    : friends;

  return (
    <>
      <ScreenHeader title="Friends" subtitle="Manage your circle" action={<PlusButton onClick={() => setView('add')} title="Add a friend" />} />
      <ScreenContent>
        <Card style={searchBarStyle}>
          <SearchIcon color="var(--muted-light)" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search your friends"
            style={searchInputStyle}
          />
        </Card>

        {incoming.length > 0 && (
          <div>
            <SectionLabel>Requests</SectionLabel>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 10 }}>
              {incoming.map((inv) => (
                <Card key={inv.id} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <Avatar initial={inv.from_user.name[0]?.toUpperCase() ?? '?'} bg="var(--card-avatar-bg)" color="var(--card-avatar-text)" />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 14 }}>
                      {inv.from_user.name} {inv.from_user.last_name}
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 1 }}>wants to be friends</div>
                  </div>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <div
                      onClick={() => accept(inv.id)}
                      style={{ cursor: 'pointer', background: 'var(--accent)', color: 'white', fontSize: 13, fontWeight: 700, padding: '8px 13px', borderRadius: 100 }}
                    >
                      Accept
                    </div>
                    <div
                      onClick={() => reject(inv.id)}
                      style={{ cursor: 'pointer', background: 'var(--border)', color: 'var(--text)', fontSize: 13, fontWeight: 700, padding: '8px 13px', borderRadius: 100 }}
                    >
                      Reject
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {sent.length > 0 && (
          <div>
            <SectionLabel>Sent &middot; {sent.length}</SectionLabel>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 10 }}>
              {sent.map((inv) => (
                <Card key={inv.id} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <Avatar initial={inv.to_user.name[0]?.toUpperCase() ?? '?'} bg="var(--card-avatar-bg)" color="var(--card-avatar-text)" />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 14 }}>
                      {inv.to_user.name} {inv.to_user.last_name}
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 1 }}>Pending</div>
                  </div>
                  <div
                    onClick={() => cancelSent(inv.id)}
                    style={{ cursor: 'pointer', background: 'var(--border)', color: 'var(--text)', fontSize: 13, fontWeight: 700, padding: '8px 13px', borderRadius: 100 }}
                  >
                    Cancel
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {error && <div style={{ color: 'var(--negative-tint-text)', fontSize: 13 }}>{error}</div>}

        <div>
          <SectionLabel>Your friends &middot; {friends.length}</SectionLabel>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 10 }}>
            {friends.length === 0 && (
              <div style={{ color: 'var(--muted)', fontSize: 13 }}>No friends yet — tap + above to add some.</div>
            )}
            {friends.length > 0 && filteredFriends.length === 0 && <div style={{ color: 'var(--muted)', fontSize: 13 }}>No matches.</div>}
            {filteredFriends.map((f) => (
              <Card key={f.id} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <Avatar initial={f.name[0]?.toUpperCase() ?? '?'} />
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>
                    {f.name} {f.last_name}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 1 }}>{f.email}</div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </ScreenContent>
    </>
  );
}

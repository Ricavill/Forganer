import { useEffect, useState } from 'react';
import { friendsApi, groupsApi, meetingsApi, schedulesApi } from '../api/endpoints';
import { SENTIMENT_LABELS, Sentiment } from '../api/types';
import type { ActivityOut, FriendOut } from '../api/types';
import { ScreenContent, ScreenHeader } from '../components/PhoneShell';
import { Avatar, Card, PrimaryButton, SectionLabel } from '../components/ui';
import { ActivityPicker } from '../components/ActivityPicker';
import { CheckIcon } from '../components/Icons';
import { ApiError } from '../api/client';
import { useAuth } from '../context/AuthContext';

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

export function CreateMeetupScreen() {
  const { user } = useAuth();
  const [friends, setFriends] = useState<FriendOut[]>([]);
  const [selectedActivity, setSelectedActivity] = useState<ActivityOut | null>(null);
  const [opinionByFriend, setOpinionByFriend] = useState<Record<number, Sentiment>>({});
  const [selectedFriendIds, setSelectedFriendIds] = useState<Set<number>>(new Set());
  const [date, setDate] = useState('');
  const [time, setTime] = useState('18:00');
  const [creating, setCreating] = useState(false);
  const [created, setCreated] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    friendsApi.list().then(setFriends).catch(() => setFriends([]));
  }, []);

  async function pickActivity(activity: ActivityOut) {
    setSelectedActivity(activity);
    try {
      const opinions = await friendsApi.opinionsFor(activity.id);
      const byFriend = Object.fromEntries(opinions.map((o) => [o.user_id, o.sentiment]));
      setOpinionByFriend(byFriend);
      const interestedIds = opinions.filter((o) => o.sentiment >= Sentiment.Like).map((o) => o.user_id);
      setSelectedFriendIds(new Set(interestedIds));
    } catch {
      setOpinionByFriend({});
      setSelectedFriendIds(new Set());
    }
  }

  function toggleFriend(id: number) {
    setSelectedFriendIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function createMeetup() {
    if (!selectedActivity || !date || !user) return;

    const start = new Date(`${date}T${time}`);
    if (start.getTime() < Date.now()) {
      setError('That date and time has already passed — pick a time in the future.');
      return;
    }

    setCreating(true);
    setError(null);
    try {
      const end = new Date(start.getTime() + 2 * 60 * 60 * 1000);

      const group = await groupsApi.create(selectedActivity.name);
      const memberIds = new Set(selectedFriendIds);
      memberIds.add(user.id);
      await Promise.all([...memberIds].map((id) => groupsApi.addMember(group.id, id)));

      const schedule = await schedulesApi.create(start.toISOString(), end.toISOString());
      const meet = await meetingsApi.create(schedule.id, group.id);

      try {
        await meetingsApi.sendInvites(meet.id);
      } catch {
        // email invites are optional / may not be configured — ignore failures here
      }

      setCreated(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not create the meetup');
    } finally {
      setCreating(false);
    }
  }

  if (created) {
    return (
      <>
        <ScreenHeader title="New meetup" subtitle="Plan something with your friends" />
        <ScreenContent>
          <div
            style={{
              background: 'var(--accent-tint)',
              color: 'var(--accent-tint-dark)',
              textAlign: 'center',
              padding: 15,
              borderRadius: 14,
              fontWeight: 700,
              fontSize: 15,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
            }}
          >
            <CheckIcon color="var(--accent-tint-dark)" />
            Meetup created
          </div>
          <div
            style={{ color: 'var(--accent)', fontWeight: 700, fontSize: 14, cursor: 'pointer', textAlign: 'center' }}
            onClick={() => {
              setCreated(false);
              setSelectedActivity(null);
              setSelectedFriendIds(new Set());
              setDate('');
            }}
          >
            Plan another
          </div>
        </ScreenContent>
      </>
    );
  }

  return (
    <>
      <ScreenHeader title="New meetup" subtitle="Plan something with your friends" />
      <ScreenContent>
        <div>
          <SectionLabel>Activity</SectionLabel>
          {selectedActivity ? (
            <Card style={{ marginTop: 10, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontWeight: 600, fontSize: 15 }}>{selectedActivity.name}</span>
              <span style={{ fontSize: 13, color: 'var(--accent)', fontWeight: 700, cursor: 'pointer' }} onClick={() => setSelectedActivity(null)}>
                Change
              </span>
            </Card>
          ) : (
            <div style={{ marginTop: 10 }}>
              <ActivityPicker onPick={pickActivity} />
            </div>
          )}
        </div>

        {selectedActivity && (
          <div>
            <SectionLabel>Friends</SectionLabel>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 10 }}>
              {friends.length === 0 && <div style={{ color: 'var(--muted)', fontSize: 13 }}>No friends yet — add some from the Friends tab.</div>}
              {friends.map((f) => {
                const selected = selectedFriendIds.has(f.id);
                const sentiment = opinionByFriend[f.id];
                return (
                  <Card key={f.id} onClick={() => toggleFriend(f.id)} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <Avatar initial={f.name[0]?.toUpperCase() ?? '?'} />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: 14 }}>
                        {f.name} {f.last_name}
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 1 }}>
                        {sentiment !== undefined ? SENTIMENT_LABELS[sentiment] : 'No opinion yet'}
                      </div>
                    </div>
                    <div
                      style={{
                        width: 24,
                        height: 24,
                        borderRadius: '50%',
                        border: '2px solid var(--accent)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        background: selected ? 'var(--accent)' : 'transparent',
                      }}
                    >
                      {selected && <CheckIcon />}
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        {selectedActivity && (
          <div>
            <SectionLabel>When</SectionLabel>
            <div style={{ display: 'flex', gap: 10, marginTop: 10 }}>
              <input
                style={inputStyle}
                type="date"
                value={date}
                min={new Date().toISOString().slice(0, 10)}
                onChange={(e) => setDate(e.target.value)}
              />
              <input style={inputStyle} type="time" value={time} onChange={(e) => setTime(e.target.value)} />
            </div>
          </div>
        )}

        {error && <div style={{ color: 'var(--negative-tint-text)', fontSize: 13 }}>{error}</div>}

        {selectedActivity && (
          <PrimaryButton onClick={createMeetup} disabled={!date || creating}>
            {creating ? 'Creating…' : 'Create meetup'}
          </PrimaryButton>
        )}
      </ScreenContent>
    </>
  );
}

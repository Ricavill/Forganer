import { useEffect, useState } from 'react';
import { activitiesApi, opinionsApi } from '../api/endpoints';
import { SENTIMENT_LABELS, Sentiment } from '../api/types';
import type { ActivityOut, OpinionOut } from '../api/types';
import { ScreenContent } from '../components/PhoneShell';
import { Avatar, Badge, Card, SectionLabel } from '../components/ui';
import { ActivityPicker } from '../components/ActivityPicker';
import { useAuth } from '../context/AuthContext';
import { ApiError } from '../api/client';

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

export function ProfileScreen() {
  const { user, logout } = useAuth();
  const [opinions, setOpinions] = useState<OpinionOut[]>([]);
  const [activities, setActivities] = useState<Record<number, ActivityOut>>({});
  const [pickedActivity, setPickedActivity] = useState<ActivityOut | null>(null);
  const [sentiment, setSentiment] = useState<Sentiment>(Sentiment.Like);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const [opinionList, activityList] = await Promise.all([opinionsApi.list(), activitiesApi.list()]);
      setOpinions(opinionList);
      setActivities(Object.fromEntries(activityList.map((a) => [a.id, a])));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load your opinions');
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  const existingOpinion = pickedActivity ? opinions.find((o) => o.activity_id === pickedActivity.id) : undefined;

  function pickActivity(activity: ActivityOut) {
    setPickedActivity(activity);
    const existing = opinions.find((o) => o.activity_id === activity.id);
    setSentiment(existing ? existing.sentiment : Sentiment.Like);
  }

  async function saveOpinion() {
    if (!pickedActivity) return;
    setError(null);
    try {
      if (existingOpinion) {
        await opinionsApi.update(existingOpinion.id, { sentiment });
      } else {
        await opinionsApi.create(pickedActivity.name, pickedActivity.id, sentiment);
      }
      setPickedActivity(null);
      setSentiment(Sentiment.Like);
      refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not save that opinion');
    }
  }

  return (
    <ScreenContent>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <Avatar initial={user?.name[0]?.toUpperCase() ?? '?'} size={56} bg="var(--accent)" color="white" />
        <div>
          <div style={{ fontFamily: "'Source Serif 4', serif", fontWeight: 700, fontSize: 19 }}>
            {user?.name} {user?.last_name}
          </div>
          <div style={{ fontSize: 13, color: 'var(--muted)', marginTop: 2 }}>{user?.email}</div>
        </div>
      </div>

      <div>
        <SectionLabel>Your opinions</SectionLabel>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 10 }}>
          {opinions.length === 0 && <div style={{ color: 'var(--muted)', fontSize: 13 }}>No opinions yet — add one below.</div>}
          {opinions.map((o) => (
            <Card key={o.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontWeight: 600, fontSize: 14 }}>{activities[o.activity_id]?.name ?? o.name}</span>
              <Badge tone={o.sentiment >= Sentiment.Indifferent ? 'positive' : 'negative'}>{SENTIMENT_LABELS[o.sentiment]}</Badge>
            </Card>
          ))}
        </div>
      </div>

      <div>
        <SectionLabel>Add an opinion</SectionLabel>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 10 }}>
          {pickedActivity ? (
            <Card style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontWeight: 600, fontSize: 14 }}>{pickedActivity.name}</span>
              <span style={{ fontSize: 13, color: 'var(--accent)', fontWeight: 700, cursor: 'pointer' }} onClick={() => setPickedActivity(null)}>
                Change
              </span>
            </Card>
          ) : (
            <ActivityPicker onPick={pickActivity} />
          )}

          {pickedActivity && (
            <>
              {existingOpinion && (
                <div style={{ fontSize: 12, color: 'var(--muted)' }}>You already reviewed this — saving will update your existing opinion.</div>
              )}
              <select
                value={sentiment}
                onChange={(e) => setSentiment(Number(e.target.value) as Sentiment)}
                style={inputStyle}
              >
                {Object.entries(SENTIMENT_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
              <div
                onClick={saveOpinion}
                style={{ cursor: 'pointer', background: 'var(--accent)', color: 'white', textAlign: 'center', padding: 13, borderRadius: 14, fontWeight: 700, fontSize: 14 }}
              >
                {existingOpinion ? 'Update opinion' : 'Save opinion'}
              </div>
            </>
          )}
        </div>
      </div>

      {error && <div style={{ color: 'var(--negative-tint-text)', fontSize: 13 }}>{error}</div>}

      <div style={{ borderTop: '1px solid var(--border)', paddingTop: 16 }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--accent)', cursor: 'pointer' }} onClick={logout}>
          Sign out
        </div>
      </div>
    </ScreenContent>
  );
}

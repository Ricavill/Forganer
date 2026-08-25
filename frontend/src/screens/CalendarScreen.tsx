import { useEffect, useState } from 'react';
import { groupsApi, meetingsApi, schedulesApi, usersApi } from '../api/endpoints';
import type { GroupMemberOut, MeetGroupOut, MeetOut, ScheduleOut, UserOut } from '../api/types';
import { ScreenContent, ScreenHeader } from '../components/PhoneShell';
import { Avatar, Badge, Card } from '../components/ui';
import { ApiError } from '../api/client';

function formatDateTime(iso: string): string {
  const d = new Date(iso);
  return (
    d.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' }) +
    ' · ' +
    d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
  );
}

export function CalendarScreen() {
  const [meets, setMeets] = useState<MeetOut[]>([]);
  const [schedules, setSchedules] = useState<Record<number, ScheduleOut>>({});
  const [groups, setGroups] = useState<Record<number, MeetGroupOut>>({});
  const [memberIds, setMemberIds] = useState<Record<number, number[]>>({});
  const [attendees, setAttendees] = useState<Record<number, UserOut[]>>({});
  const [expandedMeetId, setExpandedMeetId] = useState<number | null>(null);
  const [loadingAttendees, setLoadingAttendees] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [meetList, scheduleList, groupList] = await Promise.all([meetingsApi.list(), schedulesApi.list(), groupsApi.list()]);
        if (cancelled) return;
        setMeets(meetList);
        setSchedules(Object.fromEntries(scheduleList.map((s) => [s.id, s])));
        setGroups(Object.fromEntries(groupList.map((g) => [g.id, g])));

        const ids: Record<number, number[]> = {};
        await Promise.all(
          meetList.map(async (m) => {
            try {
              const members: GroupMemberOut[] = await groupsApi.listMembers(m.meet_group_id);
              ids[m.meet_group_id] = members.map((mem) => mem.user_id);
            } catch {
              ids[m.meet_group_id] = [];
            }
          }),
        );
        if (!cancelled) setMemberIds(ids);
      } catch (err) {
        if (!cancelled) setError(err instanceof ApiError ? err.message : 'Could not load your meetups');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  async function toggleExpand(meet: MeetOut) {
    if (expandedMeetId === meet.id) {
      setExpandedMeetId(null);
      return;
    }
    setExpandedMeetId(meet.id);
    if (!attendees[meet.meet_group_id]) {
      setLoadingAttendees(meet.id);
      try {
        const users = await usersApi.byIds(memberIds[meet.meet_group_id] ?? []);
        setAttendees((prev) => ({ ...prev, [meet.meet_group_id]: users }));
      } catch {
        setAttendees((prev) => ({ ...prev, [meet.meet_group_id]: [] }));
      } finally {
        setLoadingAttendees(null);
      }
    }
  }

  const upcoming = meets
    .filter((m) => schedules[m.schedule_id])
    .sort((a, b) => new Date(schedules[a.schedule_id].start_date).getTime() - new Date(schedules[b.schedule_id].start_date).getTime());

  return (
    <>
      <ScreenHeader title="Calendar" subtitle="Your upcoming meetups" />
      <ScreenContent>
        {loading && <div style={{ color: 'var(--muted)', fontSize: 14 }}>Loading…</div>}
        {error && <div style={{ color: 'var(--negative-tint-text)', fontSize: 13 }}>{error}</div>}
        {!loading && !error && upcoming.length === 0 && (
          <div style={{ color: 'var(--muted)', fontSize: 14, textAlign: 'center', marginTop: 40 }}>
            No meetups scheduled yet. Create one from the assistant or the + tab.
          </div>
        )}
        {upcoming.map((meet) => {
          const schedule = schedules[meet.schedule_id];
          const group = groups[meet.meet_group_id];
          const count = memberIds[meet.meet_group_id]?.length ?? 0;
          const expanded = expandedMeetId === meet.id;
          return (
            <Card key={meet.id} onClick={() => toggleExpand(meet)} style={{ borderRadius: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 16 }}>{group ? group.name : `Group #${meet.meet_group_id}`}</div>
                  <div style={{ fontSize: 13, color: 'var(--muted)', marginTop: 3 }}>{formatDateTime(schedule.start_date)}</div>
                </div>
                <Badge tone="positive">{count} going</Badge>
              </div>

              {expanded && (
                <div style={{ marginTop: 14, paddingTop: 14, borderTop: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {loadingAttendees === meet.id && <div style={{ fontSize: 13, color: 'var(--muted)' }}>Loading attendees…</div>}
                  {loadingAttendees !== meet.id &&
                    (attendees[meet.meet_group_id] ?? []).map((u) => (
                      <div key={u.id} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <Avatar initial={u.name[0]?.toUpperCase() ?? '?'} size={30} />
                        <span style={{ fontSize: 14, fontWeight: 600 }}>
                          {u.name} {u.last_name}
                        </span>
                      </div>
                    ))}
                  {loadingAttendees !== meet.id && (attendees[meet.meet_group_id] ?? []).length === 0 && (
                    <div style={{ fontSize: 13, color: 'var(--muted)' }}>No attendees found.</div>
                  )}
                </div>
              )}
            </Card>
          );
        })}
      </ScreenContent>
    </>
  );
}

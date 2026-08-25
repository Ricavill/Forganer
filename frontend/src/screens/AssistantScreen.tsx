import { useEffect, useRef, useState } from 'react';
import { botAgentApi } from '../api/endpoints';
import { MessageDirection } from '../api/types';
import { ScreenContent, ScreenHeader } from '../components/PhoneShell';
import { SendIcon } from '../components/Icons';
import { ApiError } from '../api/client';

interface Message {
  id: number;
  direction: 'in' | 'out';
  text: string;
}

export function AssistantScreen() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState('');
  const [sending, setSending] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, sending]);

  useEffect(() => {
    let cancelled = false;
    botAgentApi
      .todaysMessages()
      .then((history) => {
        if (cancelled) return;
        setMessages(
          history.map((m) => ({
            id: m.id,
            direction: m.direction === MessageDirection.In ? 'out' : 'in',
            text: m.text,
          })),
        );
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoadingHistory(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function send() {
    const text = draft.trim();
    if (!text || sending) return;
    setDraft('');
    const userMessage: Message = { id: Date.now(), direction: 'out', text };
    setMessages((prev) => [...prev, userMessage]);
    setSending(true);
    try {
      const res = await botAgentApi.chat(text);
      setMessages((prev) => [...prev, { id: Date.now() + 1, direction: 'in', text: res.reply }]);
    } catch (err) {
      const detail = err instanceof ApiError ? err.message : 'Something went wrong reaching the assistant';
      setMessages((prev) => [...prev, { id: Date.now() + 1, direction: 'in', text: detail }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <>
      <ScreenHeader title="Assistant" subtitle="Your meetup organizer" />
      <ScreenContent ref={scrollRef}>
        {!loadingHistory && messages.length === 0 && (
          <div style={{ color: 'var(--muted)', fontSize: 14, textAlign: 'center', marginTop: 40 }}>
            Tell your organizer what you'd like to plan.
          </div>
        )}
        {messages.map((m) => (
          <div
            key={m.id}
            style={{
              alignSelf: m.direction === 'out' ? 'flex-end' : 'flex-start',
              maxWidth: '85%',
              background: m.direction === 'out' ? 'var(--accent)' : 'white',
              color: m.direction === 'out' ? 'white' : 'var(--text)',
              border: m.direction === 'out' ? 'none' : '1px solid var(--border)',
              padding: '13px 17px',
              borderRadius: m.direction === 'out' ? '20px 20px 5px 20px' : '20px 20px 20px 5px',
              fontSize: 15,
              lineHeight: 1.5,
              whiteSpace: 'pre-wrap',
            }}
          >
            {m.text}
          </div>
        ))}
        {sending && <div style={{ color: 'var(--muted)', fontSize: 13, alignSelf: 'flex-start' }}>Thinking&hellip;</div>}
      </ScreenContent>

      <div
        style={{
          flexShrink: 0,
          padding: '12px 16px',
          display: 'flex',
          gap: 10,
          alignItems: 'center',
          borderTop: '1px solid var(--border)',
          background: 'var(--bg)',
        }}
      >
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') send();
          }}
          placeholder="Message your organizer…"
          style={{
            flex: 1,
            background: 'white',
            border: '1px solid var(--border)',
            borderRadius: 24,
            padding: '12px 18px',
            fontSize: 14,
            fontFamily: 'inherit',
            color: 'var(--text)',
          }}
        />
        <div
          onClick={send}
          style={{
            cursor: 'pointer',
            width: 42,
            height: 42,
            borderRadius: '50%',
            background: 'var(--accent)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <SendIcon />
        </div>
      </div>
    </>
  );
}

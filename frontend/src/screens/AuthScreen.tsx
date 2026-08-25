import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { ApiError } from '../api/client';

export function AuthScreen() {
  const { login, signup } = useAuth();
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [name, setName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

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

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await signup(name, lastName, email, password);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div
      style={{
        width: 390,
        height: 844,
        background: 'var(--bg)',
        color: 'var(--text)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: '0 28px',
        borderRadius: 28,
        boxShadow: '0 20px 60px rgba(0,0,0,0.25)',
      }}
    >
      <h1 style={{ fontWeight: 700, fontSize: 30, marginBottom: 6 }}>Friends Planner</h1>
      <div style={{ fontSize: 14, color: 'var(--muted)', marginBottom: 32 }}>
        {mode === 'login' ? 'Log in to keep planning' : 'Create your account'}
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {mode === 'signup' && (
          <>
            <input style={inputStyle} placeholder="First name" value={name} onChange={(e) => setName(e.target.value)} required />
            <input style={inputStyle} placeholder="Last name" value={lastName} onChange={(e) => setLastName(e.target.value)} required />
          </>
        )}
        <input style={inputStyle} type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input style={inputStyle} type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />

        {error && <div style={{ color: 'var(--negative-tint-text)', fontSize: 13 }}>{error}</div>}

        <button
          type="submit"
          disabled={busy}
          style={{
            marginTop: 8,
            cursor: busy ? 'default' : 'pointer',
            opacity: busy ? 0.6 : 1,
            background: 'var(--accent)',
            color: 'white',
            border: 'none',
            textAlign: 'center',
            padding: 15,
            borderRadius: 14,
            fontWeight: 700,
            fontSize: 15,
          }}
        >
          {mode === 'login' ? 'Log in' : 'Sign up'}
        </button>
      </form>

      <div style={{ marginTop: 20, fontSize: 13, color: 'var(--muted)', textAlign: 'center' }}>
        {mode === 'login' ? (
          <>
            No account?{' '}
            <span style={{ color: 'var(--accent)', fontWeight: 700, cursor: 'pointer' }} onClick={() => setMode('signup')}>
              Sign up
            </span>
          </>
        ) : (
          <>
            Already have an account?{' '}
            <span style={{ color: 'var(--accent)', fontWeight: 700, cursor: 'pointer' }} onClick={() => setMode('login')}>
              Log in
            </span>
          </>
        )}
      </div>
    </div>
  );
}

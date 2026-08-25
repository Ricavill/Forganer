import { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AuthScreen } from './screens/AuthScreen';
import { AssistantScreen } from './screens/AssistantScreen';
import { CalendarScreen } from './screens/CalendarScreen';
import { CreateMeetupScreen } from './screens/CreateMeetupScreen';
import { FriendsScreen } from './screens/FriendsScreen';
import { ProfileScreen } from './screens/ProfileScreen';
import { PhoneShell } from './components/PhoneShell';
import { TabBar, type Tab } from './components/TabBar';

function AppShell() {
  const { user, loading } = useAuth();
  const [tab, setTab] = useState<Tab>('assistant');

  if (loading) {
    return null;
  }

  if (!user) {
    return <AuthScreen />;
  }

  return (
    <PhoneShell>
      {tab === 'assistant' && <AssistantScreen />}
      {tab === 'calendar' && <CalendarScreen />}
      {tab === 'create' && <CreateMeetupScreen />}
      {tab === 'friends' && <FriendsScreen />}
      {tab === 'profile' && <ProfileScreen />}
      <TabBar active={tab} onChange={setTab} />
    </PhoneShell>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  );
}

export default App;

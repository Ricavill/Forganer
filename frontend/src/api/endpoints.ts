import { api } from './client';
import type {
  ActivityOut,
  ChatMessageOut,
  ChatResponse,
  FriendInvitationOut,
  FriendOut,
  GroupMemberOut,
  InterestedFriendOut,
  MeetGroupOut,
  MeetInviteResult,
  MeetOut,
  OpinionOut,
  ScheduleOut,
  Sentiment,
  Token,
  UserOut,
} from './types';

export const authApi = {
  login: (email: string, password: string) => api.post<Token>('/auth/login', { email, password }),
  me: () => api.get<UserOut>('/auth/me'),
};

export const usersApi = {
  signup: (name: string, last_name: string, email: string, password: string) =>
    api.post<Token>('/users/signup', { name, last_name, email, password }),
  search: (q: string) => api.get<UserOut[]>(`/users/search?q=${encodeURIComponent(q)}`),
  lookup: (email: string) => api.get<UserOut>(`/users/lookup?email=${encodeURIComponent(email)}`),
  byIds: (ids: number[]) =>
    ids.length === 0 ? Promise.resolve<UserOut[]>([]) : api.get<UserOut[]>(`/users/by-ids?ids=${ids.join(',')}`),
};

export const activitiesApi = {
  list: () => api.get<ActivityOut[]>('/activities'),
  search: (q: string) => api.get<ActivityOut[]>(`/activities/search?q=${encodeURIComponent(q)}`),
  get: (id: number) => api.get<ActivityOut>(`/activities/${id}`),
  create: (name: string, description?: string) => api.post<ActivityOut>('/activities', { name, description }),
};

export const opinionsApi = {
  list: () => api.get<OpinionOut[]>('/opinions'),
  create: (name: string, activity_id: number, sentiment: Sentiment, description?: string) =>
    api.post<OpinionOut>('/opinions', { name, activity_id, sentiment, description }),
  update: (id: number, payload: Partial<{ name: string; description: string; sentiment: Sentiment }>) =>
    api.patch<OpinionOut>(`/opinions/${id}`, payload),
  remove: (id: number) => api.delete<void>(`/opinions/${id}`),
};

export const schedulesApi = {
  list: () => api.get<ScheduleOut[]>('/schedules'),
  create: (start_date: string, end_date: string) => api.post<ScheduleOut>('/schedules', { start_date, end_date }),
};

export const groupsApi = {
  list: () => api.get<MeetGroupOut[]>('/groups'),
  create: (name: string) => api.post<MeetGroupOut>('/groups', { name }),
  get: (id: number) => api.get<MeetGroupOut>(`/groups/${id}`),
  listMembers: (id: number) => api.get<GroupMemberOut[]>(`/groups/${id}/members`),
  addMember: (id: number, user_id: number) => api.post<GroupMemberOut>(`/groups/${id}/members`, { user_id }),
};

export const meetingsApi = {
  list: () => api.get<MeetOut[]>('/meets'),
  create: (schedule_id: number, meet_group_id: number) => api.post<MeetOut>('/meets', { schedule_id, meet_group_id }),
  sendInvites: (id: number) => api.post<MeetInviteResult>(`/meets/${id}/invite`),
};

export const friendsApi = {
  list: () => api.get<FriendOut[]>('/friends'),
  listIncomingRequests: () => api.get<FriendInvitationOut[]>('/friends/requests'),
  listSentRequests: () => api.get<FriendInvitationOut[]>('/friends/requests/sent'),
  send: (to_user_id: number) => api.post<FriendInvitationOut>('/friends/requests', { to_user_id }),
  accept: (invitationId: number) => api.post<FriendInvitationOut>(`/friends/requests/${invitationId}/accept`),
  reject: (invitationId: number) => api.post<FriendInvitationOut>(`/friends/requests/${invitationId}/reject`),
  cancel: (invitationId: number) => api.delete<void>(`/friends/requests/${invitationId}`),
  interested: (activityId: number) => api.get<InterestedFriendOut[]>(`/friends/interested?activity_id=${activityId}`),
  opinionsFor: (activityId: number) => api.get<InterestedFriendOut[]>(`/friends/opinions?activity_id=${activityId}`),
};

export const botAgentApi = {
  chat: (message: string) => api.post<ChatResponse>('/bot-agent/chat', { message }),
  todaysMessages: () => api.get<ChatMessageOut[]>('/bot-agent/messages'),
};

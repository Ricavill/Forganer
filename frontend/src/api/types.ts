export const Sentiment = {
  StronglyDislike: 1,
  Dislike: 2,
  Indifferent: 3,
  Like: 4,
  StronglyLike: 5,
} as const;

export type Sentiment = (typeof Sentiment)[keyof typeof Sentiment];

export const SENTIMENT_LABELS: Record<Sentiment, string> = {
  [Sentiment.StronglyDislike]: 'Strongly dislike',
  [Sentiment.Dislike]: 'Dislike',
  [Sentiment.Indifferent]: 'Indifferent',
  [Sentiment.Like]: 'Like',
  [Sentiment.StronglyLike]: 'Strongly like',
};

export const InvitationStatus = {
  Pending: 1,
  Accepted: 2,
  Rejected: 3,
} as const;

export type InvitationStatus = (typeof InvitationStatus)[keyof typeof InvitationStatus];

export interface Token {
  access_token: string;
  token_type: string;
}

export interface UserOut {
  id: number;
  name: string;
  last_name: string;
  email: string;
}

export interface ActivityOut {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface OpinionOut {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  activity_id: number;
  sentiment: Sentiment;
  created_at: string;
  updated_at: string;
}

export interface ScheduleOut {
  id: number;
  start_date: string;
  end_date: string;
  created_at: string;
  updated_at: string;
}

export interface MeetGroupOut {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface GroupMemberOut {
  id: number;
  user_id: number;
  meet_group_id: number;
}

export interface MeetOut {
  id: number;
  schedule_id: number;
  meet_group_id: number;
  created_at: string;
  updated_at: string;
}

export interface MeetInviteResult {
  sent_to: string[];
}

export interface FriendOut {
  id: number;
  name: string;
  last_name: string;
  email: string;
}

export interface FriendInvitationOut {
  id: number;
  from_user: FriendOut;
  to_user: FriendOut;
  status: InvitationStatus;
  created_at: string;
}

export interface InterestedFriendOut {
  user_id: number;
  name: string;
  last_name: string;
  sentiment: Sentiment;
}

export interface ChatResponse {
  session_id: number;
  reply: string;
}

export const MessageDirection = {
  In: 1,
  Out: 2,
  ToolLog: 3,
} as const;

export type MessageDirection = (typeof MessageDirection)[keyof typeof MessageDirection];

export interface ChatMessageOut {
  id: number;
  direction: MessageDirection;
  text: string;
  created_at: string;
}

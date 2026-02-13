export type Role = 'moderator' | 'voter' | 'spectator';

export interface Participant {
	id: string;
	name: string;
	role: Role;
	connected: boolean;
}

export interface Vote {
	participant_id: string;
	value?: string;
	has_voted?: boolean;
}

export interface RoundState {
	story: string;
	story_link: string | null;
	votes: Record<string, Vote>;
	revealed: boolean;
	round_number: number;
}

export interface CardDef {
	value: string;
	label: string;
	description: string;
}

export interface Stats {
	average?: number;
	median?: number;
	min?: number;
	max?: number;
	consensus?: boolean;
}

export interface RoomState {
	id: string;
	deck_type: string;
	description_flavor: string;
	participants: Record<string, Participant>;
	current_round: RoundState | null;
	deck_cards: CardDef[];
	stats?: Stats;
}

export interface WsMessage {
	type: string;
	payload: Record<string, unknown>;
}

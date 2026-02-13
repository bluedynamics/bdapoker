const en = {
	// Home page
	'app.title': 'Planning Poker',
	'home.deck': 'Deck',
	'home.descriptions': 'Descriptions',
	'home.createRoom': 'Create Room',
	'home.creating': 'Creating...',
	'home.error.failed': 'Failed to create room',
	'home.error.network': 'Network error',

	// Deck types
	'deck.fibonacci': 'Fibonacci (0, ½, 1, 2, 3, 5, 8, 13, 20, 40, 100)',
	'deck.tshirt': 'T-Shirt (XS, S, M, L, XL, XXL)',
	'deck.powers2': 'Powers of 2 (1, 2, 4, 8, 16, 32, 64)',

	// Flavors
	'flavor.technical': 'Technical — straightforward complexity',
	'flavor.idioms': 'Idioms — sayings & metaphors',
	'flavor.animals': 'Animals — complexity by creature size',
	'flavor.software': 'Software — developer analogies',

	// Room page
	'room.loading': 'Loading...',
	'room.notFound': 'Room not found',
	'room.networkError': 'Network error',
	'room.label': 'Room:',
	'room.copyLink': 'Copy link',

	// Join form
	'join.title': 'Join Room',
	'join.yourName': 'Your name',
	'join.placeholder': 'Enter your name',
	'join.role': 'Role',
	'join.voter': 'Voter',
	'join.spectator': 'Spectator',
	'join.button': 'Join',

	// Story field
	'story.label': 'Story:',
	'story.noStory': '(no story set)',
	'story.round': 'Round',
	'story.waiting': 'Waiting for moderator to start a round...',
	'story.link': '[link]',

	// Participants list
	'participants.title': 'Participants',
	'participants.name': 'Name',
	'participants.role': 'Role',
	'participants.vote': 'Vote',

	// Vote results
	'results.title': 'Results',
	'results.average': 'Average',
	'results.median': 'Median',
	'results.range': 'Range',
	'results.consensus': 'Consensus',
	'results.yes': 'Yes',
	'results.no': 'No',

	// Moderator controls
	'mod.reveal': 'Reveal',
	'mod.revote': 'Re-vote',
	'mod.newStory': 'New Story',
	'mod.cancel': 'Cancel',
	'mod.timer60': 'Timer 60s',
	'mod.timer120': 'Timer 120s',
	'mod.stopTimer': 'Stop Timer',
	'mod.storyPlaceholder': 'Story description',
	'mod.linkPlaceholder': 'Link (optional)',
	'mod.startRound': 'Start Round',

	// Roles (displayed in participant list)
	'role.moderator': 'moderator',
	'role.voter': 'voter',
	'role.spectator': 'spectator',

	// Backend error messages (mapped from English originals)
	'error.Name is required': 'Name is required',
	'error.No active round': 'No active round',
	'error.Round already revealed': 'Round already revealed',
	'error.Not in room': 'Not in room',
	'error.Spectators cannot vote': 'Spectators cannot vote',
	'error.Only moderator can reveal': 'Only moderator can reveal',
	'error.Only moderator can start new round': 'Only moderator can start new round',
	'error.Only moderator can reset round': 'Only moderator can reset round',
	'error.Only moderator can kick': 'Only moderator can kick',
	'error.Cannot kick yourself': 'Cannot kick yourself',
	'error.Only moderator can change deck': 'Only moderator can change deck',
	'error.Only moderator can start timer': 'Only moderator can start timer',
	'error.Only moderator can stop timer': 'Only moderator can stop timer',
} as const;

export type TranslationKey = keyof typeof en;
export default en;

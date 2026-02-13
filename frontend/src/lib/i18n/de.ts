import type { TranslationKey } from './en';

const de: Record<TranslationKey, string> = {
	// Home page
	'app.title': 'Planning Poker',
	'home.deck': 'Kartendeck',
	'home.descriptions': 'Beschreibungen',
	'home.createRoom': 'Raum erstellen',
	'home.creating': 'Erstelle...',
	'home.error.failed': 'Raum konnte nicht erstellt werden',
	'home.error.network': 'Netzwerkfehler',

	// Deck types
	'deck.fibonacci': 'Fibonacci (0, ½, 1, 2, 3, 5, 8, 13, 20, 40, 100)',
	'deck.tshirt': 'T-Shirt (XS, S, M, L, XL, XXL)',
	'deck.powers2': 'Zweierpotenzen (1, 2, 4, 8, 16, 32, 64)',

	// Flavors
	'flavor.technical': 'Technisch — sachliche Komplexität',
	'flavor.idioms': 'Redewendungen — Sprichwörter & Metaphern',
	'flavor.animals': 'Tiere — Komplexität nach Tiergröße',
	'flavor.software': 'Software — Entwickler-Analogien',

	// Room page
	'room.loading': 'Lade...',
	'room.notFound': 'Raum nicht gefunden',
	'room.networkError': 'Netzwerkfehler',
	'room.label': 'Raum:',
	'room.copyLink': 'Link kopieren',

	// Join form
	'join.title': 'Raum beitreten',
	'join.yourName': 'Dein Name',
	'join.placeholder': 'Namen eingeben',
	'join.role': 'Rolle',
	'join.voter': 'Abstimmender',
	'join.spectator': 'Zuschauer',
	'join.button': 'Beitreten',

	// Story field
	'story.label': 'Story:',
	'story.noStory': '(keine Story festgelegt)',
	'story.round': 'Runde',
	'story.waiting': 'Warte auf den Moderator...',
	'story.link': '[Link]',

	// Participants list
	'participants.title': 'Teilnehmer',
	'participants.name': 'Name',
	'participants.role': 'Rolle',
	'participants.vote': 'Stimme',

	// Vote results
	'results.title': 'Ergebnisse',
	'results.average': 'Durchschnitt',
	'results.median': 'Median',
	'results.range': 'Bereich',
	'results.consensus': 'Konsens',
	'results.yes': 'Ja',
	'results.no': 'Nein',

	// Moderator controls
	'mod.reveal': 'Aufdecken',
	'mod.revote': 'Neu abstimmen',
	'mod.newStory': 'Neue Story',
	'mod.cancel': 'Abbrechen',
	'mod.timer60': 'Timer 60s',
	'mod.timer120': 'Timer 120s',
	'mod.stopTimer': 'Timer stoppen',
	'mod.storyPlaceholder': 'Story-Beschreibung',
	'mod.linkPlaceholder': 'Link (optional)',
	'mod.startRound': 'Runde starten',

	// Roles
	'role.moderator': 'Moderator',
	'role.voter': 'Abstimmender',
	'role.spectator': 'Zuschauer',

	// Backend error messages
	'error.Name is required': 'Name ist erforderlich',
	'error.No active round': 'Keine aktive Runde',
	'error.Round already revealed': 'Runde bereits aufgedeckt',
	'error.Not in room': 'Nicht im Raum',
	'error.Spectators cannot vote': 'Zuschauer können nicht abstimmen',
	'error.Only moderator can reveal': 'Nur der Moderator kann aufdecken',
	'error.Only moderator can start new round': 'Nur der Moderator kann eine neue Runde starten',
	'error.Only moderator can reset round': 'Nur der Moderator kann die Runde zurücksetzen',
	'error.Only moderator can kick': 'Nur der Moderator kann Teilnehmer entfernen',
	'error.Cannot kick yourself': 'Du kannst dich nicht selbst entfernen',
	'error.Only moderator can change deck': 'Nur der Moderator kann das Deck ändern',
	'error.Only moderator can start timer': 'Nur der Moderator kann den Timer starten',
	'error.Only moderator can stop timer': 'Nur der Moderator kann den Timer stoppen',
};

export default de;

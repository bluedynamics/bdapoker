import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import en from './en';
import de from './de';
import type { TranslationKey } from './en';

export type Locale = 'en' | 'de';
export type { TranslationKey };

const translations: Record<Locale, Record<TranslationKey, string>> = { en, de };

function detectLocale(): Locale {
	if (!browser) return 'en';
	const stored = localStorage.getItem('locale');
	if (stored === 'en' || stored === 'de') return stored;
	const browserLang = navigator.language.split('-')[0];
	return browserLang === 'de' ? 'de' : 'en';
}

export const locale = writable<Locale>(detectLocale());

if (browser) {
	locale.subscribe((value) => {
		localStorage.setItem('locale', value);
	});
}

export const t = derived(locale, ($locale) => {
	const dict = translations[$locale];
	return (key: TranslationKey): string => dict[key] ?? key;
});

export function translateError(message: string): string {
	const loc = get(locale);
	const key = `error.${message}` as TranslationKey;
	return translations[loc][key] ?? message;
}

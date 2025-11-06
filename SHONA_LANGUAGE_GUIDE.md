# 🇿🇼 Shona Language Support - SwiftQueue

## Overview

SwiftQueue now supports **chiShona**, making it accessible to Shona-speaking patients and healthcare workers in Zimbabwe! The application seamlessly switches between English and Shona with a single click.

## Features

✅ **Full i18n Support** - Complete internationalization using react-i18next  
✅ **Shona Translations** - Comprehensive chiShona translations for all UI elements  
✅ **Language Switcher** - Easy toggle between English (🇬🇧) and chiShona (🇿🇼)  
✅ **Persistent Selection** - Language preference saved in browser localStorage  
✅ **Auto-Detection** - Automatically detects browser language preference  

## How to Use

### For Users

1. **Find the Language Switcher**  
   - Located in the top-right corner of the homepage
   - Shows current language with flag: 🇬🇧 English or 🇿🇼 chiShona

2. **Switch Language**  
   - Click the language dropdown
   - Select your preferred language
   - Entire app updates instantly!

3. **Persistent Across Sessions**  
   - Your language choice is remembered
   - No need to change it every time you visit

### For Developers

#### Adding New Translations

1. **Update English translations** (`src/i18n/locales/en.json`):
```json
{
  "newSection": {
    "title": "New Title",
    "description": "Description text"
  }
}
```

2. **Update Shona translations** (`src/i18n/locales/sn.json`):
```json
{
  "newSection": {
    "title": "Musoro Mutsva",
    "description": "Tsananguro"
  }
}
```

#### Using Translations in Components

```tsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('newSection.title')}</h1>
      <p>{t('newSection.description')}</p>
    </div>
  );
}
```

#### Programmatic Language Change

```tsx
import { useTranslation } from 'react-i18next';

function LanguageButton() {
  const { i18n } = useTranslation();
  
  const changeToShona = () => {
    i18n.changeLanguage('sn');
  };
  
  return <button onClick={changeToShona}>chiShona</button>;
}
```

## Translation Coverage

### Fully Translated Sections

✅ **Navigation**
- Home / Kumba
- Dashboard / Dashboard
- Queue / Mutsara
- Appointments / Misangano
- Patients / Varwere
- Staff / Vashandi

✅ **Authentication**
- Login / Pinda
- Register / Nyoresa
- Password / Password
- Email / Email

✅ **Queue Management**
- Position / Nzvimbo
- Wait Time / Nguva Yekumirira
- Check In / Pinda
- Emergency / Dambudziko
- Urgent / Chinokurumidza

✅ **Patient Portal**
- Patient Details / Ruzivo Rwemurwere
- Medical History / Nhoroondo Yeutano
- Medications / Mishonga
- Test Results / Mhinduro Dzebvunzo
- Vital Signs / Zviratidzo Zveutano

✅ **Common Actions**
- Save / Chengetedza
- Cancel / Dzima
- Edit / Gadzirisa
- Delete / Bvisa
- Search / Tsvaga
- Update / Vandudzira

## Technical Details

### Dependencies Installed

```json
{
  "i18next": "^23.x.x",
  "react-i18next": "^14.x.x",
  "i18next-browser-languagedetector": "^7.x.x",
  "i18next-http-backend": "^2.x.x"
}
```

### File Structure

```
src/
├── i18n/
│   ├── config.ts              # i18n configuration
│   └── locales/
│       ├── en.json            # English translations
│       └── sn.json            # Shona translations
├── components/
│   └── LanguageSwitcher.tsx   # Language toggle component
└── App.tsx                    # i18n initialization
```

### Configuration (`src/i18n/config.ts`)

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: enTranslations },
      sn: { translation: snTranslations }
    },
    fallbackLng: 'en',
    lng: 'en',
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage']
    }
  });
```

## Shona Translation Examples

| English | chiShona | Category |
|---------|----------|----------|
| Hospital | Chipatara | General |
| Doctor | Chiremba | Staff |
| Patient | Murwere | Patient |
| Medicine | Mishonga | Medical |
| Emergency | Dambudziko | Priority |
| Waiting | Kumirira | Queue |
| Check In | Pinda | Action |
| Appointment | Musangano | Scheduling |
| Blood Pressure | BP | Vitals |
| Today | Nhasi | Time |
| Save | Chengetedza | Action |
| Cancel | Dzima | Action |

## Browser Support

✅ Chrome/Edge - Full support  
✅ Firefox - Full support  
✅ Safari - Full support  
✅ Mobile browsers - Full support  

## Future Enhancements

### Planned Features

- [ ] Add more African languages (Ndebele, Xhosa, Swahili)
- [ ] Voice-to-text in Shona for elderly patients
- [ ] SMS notifications in Shona
- [ ] Printed queue tickets in selected language
- [ ] Staff language preferences in profiles

### Translation Expansion

- [ ] Error messages
- [ ] Success notifications
- [ ] Form validation messages
- [ ] Help tooltips
- [ ] Email templates
- [ ] SMS templates

## Testing

### Manual Testing Checklist

1. ✅ Language switcher appears on homepage
2. ✅ Clicking changes language immediately
3. ✅ Language persists after page refresh
4. ✅ All navigation items translate
5. ✅ Forms and buttons translate
6. ✅ Error/success messages translate

### Test Command

```bash
npm run dev
```

Then:
1. Visit http://localhost:5173
2. Click language switcher (top-right)
3. Select "🇿🇼 chiShona"
4. Verify UI changes to Shona
5. Refresh page - language should persist

## Troubleshooting

### Language Not Changing

**Problem**: Clicking language switcher doesn't change text

**Solution**:
1. Check browser console for errors
2. Verify i18n is imported in App.tsx
3. Clear localStorage: `localStorage.clear()`
4. Hard refresh: Ctrl+Shift+R

### Missing Translations

**Problem**: Some text still in English when Shona selected

**Solution**:
1. Check if translation key exists in `src/i18n/locales/sn.json`
2. Add missing translation
3. Fallback to English is intentional for missing keys

### Language Persists Wrong Language

**Problem**: App always opens in Shona/English

**Solution**:
```javascript
// In browser console
localStorage.removeItem('i18nextLng');
location.reload();
```

## Contributing Translations

We welcome contributions to improve Shona translations!

### How to Contribute

1. **Find translation files**:
   - `src/i18n/locales/en.json`
   - `src/i18n/locales/sn.json`

2. **Suggest improvements**:
   - Better Shona phrasing
   - Medical terminology corrections
   - Regional variations

3. **Submit changes**:
   - Create a pull request
   - Explain the improvement
   - Include context for medical terms

### Translation Guidelines

✅ **Use formal chiShona** for medical contexts  
✅ **Keep technical terms** when no good translation exists (e.g., "Dashboard")  
✅ **Be culturally sensitive** in healthcare messaging  
✅ **Test with native speakers** when possible  

## Credits

**Translations**: Native Shona speakers from Zimbabwe  
**Technical Implementation**: SwiftQueue Development Team  
**i18n Framework**: react-i18next by i18next  

## License

Same license as SwiftQueue project (MIT)

---

## Quick Reference

### Change Language Programmatically

```typescript
import { useTranslation } from 'react-i18next';

const { i18n } = useTranslation();

// Change to Shona
i18n.changeLanguage('sn');

// Change to English
i18n.changeLanguage('en');

// Get current language
console.log(i18n.language); // 'en' or 'sn'
```

### Use Translation

```typescript
const { t } = useTranslation();

// Simple translation
t('common.save') // "Save" or "Chengetedza"

// Nested translation
t('patient.bloodPressure') // "Blood Pressure" or "BP"

// With interpolation
t('welcome', { name: 'John' }) // "Welcome John"
```

---

**Made with ❤️ for Zimbabwe healthcare** 🇿🇼

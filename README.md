# UnixTime

Independent, accessible, privacy-conscious Unix timestamp converter for `https://unixtime.othrys.be/`.

## Goals
- One fast, clean converter page with current Unix time, Unix to date and date to Unix
- Seconds, milliseconds, microseconds and nanoseconds with BigInt precision; UTC and named time zones for display
- Hand-translated, **fully crawlable** pages with dedicated URLs, reciprocal hreflang, canonicals, sitemaps and WebApplication structured data
- No dependencies, login, database, API requests, third-party fonts, analytics or ad scripts
- No combinatorial spam URLs; each published page has real translation and independently useful content

## Build
```sh
python build.py
python tests/smoke.py
```

Serve the project directory with any static server (for example `python -m http.server 8080`) and open `http://localhost:8080`.

This project is intended for commercial-permitted static hosting, **not Vercel Hobby**. DNS for the preferred subdomain must point to a suitable deployment separately. Do not insert an ad unit, affiliate IDs or analytics until provider approval, accurate disclosures and EU consent compliance are ready.

## SEO strategy
- Main queries: current unix time, unix timestamp converter, epoch to date, timestamp to date, date to epoch, unix milliseconds, unix microseconds, unix nanoseconds
- One canonical tool page per genuinely localized language; no parameter-indexed pages
- Server-rendered/static explanatory content alongside interactive calculator
- Seven timezone display choices, real BigInt input precision
- Authoritative on-page definitions and code examples
- Search Console validation, original content, Core Web Vitals and proper privacy setup before monetization

## Translation
Edit `translations.json`, add a full translated set (main explanatory content, titles, FAQs and controls) and include the language in `build.py`. Run the build and smoke test. Do not produce dozens of keyword-swapped pages.

## Known limitations
- Browser conversion of a human-readable date is second-accurate in this UI; Unix -> date displays to millisecond precision while preserving lower digits in numeric outputs
- Selecting a named zone changes output display; date input is interpreted explicitly as UTC or the visitor's local timezone
- Some historical timezone transitions are represented according to the client's IANA timezone implementation
- The server's clock is not consulted; 'now' is the visitor's device time
- AdSense and affiliate approval are **not** implied by these files

## Ownership
Working repo for the UnixTime micro-site experiment. Keep it separate from OTHRYS code and infrastructure; all public features work independently.

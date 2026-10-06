# Orange Instagram Saver

An original Manifest V3 Chrome extension and popup app, with orange **↓** single-download and **↓↓↓** bulk-download controls. It saves HTTPS photos and videos already loaded on Instagram pages in your browser session. Open a post, carousel item, reel or story to load its media, confirm permission in the extension popup, then use a button. Batch size is capped at 200; cancellation affects only this extension's downloads.

## Installation

Download `releases/instagram-orange.zip`, extract it, open Chrome's Extensions page, enable Developer mode, choose **Load unpacked**, and select the extracted directory containing `manifest.json`. Open Instagram and click the extension icon. This repository release is not a Chrome Web Store listing.

## Access and coverage

The follower checkbox is your assertion, not verified follower status. Instagram controls access through your existing signed-in session. No passwords, cookies, private API requests, access-control bypass, analytics or external service are used. Only Instagram content scripts and CDN media downloads are permitted.

Bulk means currently loaded media, not a guaranteed whole-account archive. Scroll or open additional items and repeat. Profile images can be thumbnails rather than full-resolution originals. Lazy carousel items, expired stories, inaccessible content, blob/MSE streams and unloaded videos cannot be saved by this version. Single download selects the first qualifying loaded media in a post, or on the current page for the popup/floating button; review the page first. All batches use original browser `currentSrc` URLs, which may expire. Save only media you own or have permission to copy.

Queue progress and permissions are in memory. Browser/service-worker restart clears permission and progress; already accepted browser downloads continue. Reconfirm permission after a restart. Filenames use predictable numbering and Chrome's conflict handling. No persistent download inventory is collected. Chrome itself maintains its usual download history and files. A failed CDN request is reported by the browser; supported URL shape does not guarantee availability or file encoding. File suffixes are image `.jpg` or video `.mp4`, while the supplied media bytes remain unchanged.

## Validation and design references

Run `node tests/instagram-orange/core.cjs` from the repository root. Tests cover URL boundaries, deduplication, cap, authorization, download request, completion and cancellation using a mocked Chrome API. Live Instagram compatibility and Chrome Web Store approval have not been verified.

Design references supplied by the user: Mass Downloader (`ijcemfcomjlamigapfebkgdgehbmjpjj`), Turbo Downloader (`cpgaheeihidjmolbakklolchdplenjai`), Ulti Downloader (`ecocgofdjmiomgmgnchijbghkikolkkl`), Bulk Saver (`gkfioconmfepeapbgohmhdgccfkeddkb`), Reels Extractor (`ngfjkjdigiloiocgjehabfdiopknacmo`) and ToolMaster Downloader (`epocgljljclegljpgjdefgeejhiobnda`). Listing titles were checked where available; the Ulti listing returned only the generic store title. No third-party extension code or assets were copied.

## Automatic standard renditions and upkeep

Install and run the desktop companion described in `docs/MEDIA-STANDARDISATION-AND-UPDATES.md` to watch this extension’s download folder and create verified TIFF/FFV1/FLAC renditions while preserving originals. The extension downloads source bytes; conversion is performed by the companion. The checked repository updater tests candidates before fast-forwarding. An unpacked extension still requires Chrome reload; automatic Web Store distribution is not configured.

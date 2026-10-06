# Media standardisation and checked maintenance

The Orange Instagram Saver supplies orange single-down-arrow and triple-down-arrow bulk controls, a follower/permission assertion, a 200-item loaded-media cap and cancellation. The Chrome popup is its app interface. It uses session-accessible loaded media rather than claiming an entire account archive. Source is in `extensions/instagram-orange`; the installable unpacked bundle is `releases/instagram-orange.zip`. No third-party extension code is used. See the included extension README for installation, access, queue and listing-reference details.

## Original and standard rendition

Quality means preserving the available source and testing the conversion, rather than inventing missing detail. The companion `tools/media_standardize.py` retains originals and SHA-256 receipts. Static RGB/RGBA/grayscale images become losslessly compressed TIFF after orientation normalisation; embedded ICC profiles are carried over. It verifies pixel equality. It refuses animation and unsupported colour modes instead of flattening them. It does not manufacture camera RAW, increase source bit depth, upscale images, repair Instagram compression or promise every metadata tag survives. Original files remain the metadata authority.

Video becomes Matroska with FFV1 video and FLAC integer audio or PCM floating-point audio. Integer audio alone becomes FLAC; floating-point audio becomes WAV with its decoded sample precision preserved. FFmpeg compares decoded frame/sample hashes before a result is marked verified. Unsupported stream types and conversion failures leave the original intact. These archive formats can be much larger than Instagram MP4/JPEG files and require compatible players. A 512 MiB input cap and ten-minute subprocess timeouts bound individual conversions; output disk space is still required. This is decoded-media preservation, not lossless recovery of an earlier camera source.

On a Linux desktop install Python 3.10+, Pillow and FFmpeg (for example `sudo apt install python3-pil ffmpeg`). From this repository run:

```
python3 tools/media_standardize.py "$HOME/Downloads/RasnikiInstagram" --watch
```

Use the actual Chrome download directory if customised. The process waits for stable filenames/sizes, ignores temporary browser downloads and writes a `standardized` subdirectory. Keep it running for automatic conversion upon download. On other platforms install equivalent tools and supply the appropriate directory. This cloud instance cannot install or start software on your personal computer. The companion needs explicit desktop installation; no passwords, native-message bridge or background remote-code loader is installed by the extension.

One file can also be converted using `python3 tools/media_standardize.py /path/to/file --output /path/to/archive`. Receipts include source and output hashes, finite verification status and an explicit statement that detail was not recovered. Failures are reported and originals remain available.

For automatic startup and daily checked updates on a Linux desktop with systemd user services, use a dedicated clean repository checkout and run:

```
python3 tools/install_media_maintenance.py --downloads "$HOME/Downloads/RasnikiInstagram"
```

This installs and starts `rasniki-media.service` and `rasniki-update.timer` for the current user. A successful checked update restarts the watcher so it uses new code. It does not restart other apps or overwrite existing service files. The user service manager must be available; startup before login requires the desktop administrator's normal user-service configuration. Inspect logs with `journalctl --user -u rasniki-media -u rasniki-update`; stop automation with `systemctl --user disable --now rasniki-update.timer rasniki-media.service`. This installer has not been run on your desktop or enabled in the cloud instance.

## Updating through input/output

`python3 tools/checked_update.py --check-only` checks the configured Git origin/main. `python3 tools/checked_update.py` tests a fetched candidate in a disposable clone using the complete bootstrap, then permits only a fast-forward of a clean checkout. It refuses local edits, divergent histories, failed tests and changes during validation. Preserve `.lab-state`; restart running app/companion processes after an update. This workflow trusts maintainers of the configured origin; passing tests is not a proof that arbitrary code is safe. It never imports code from media files or changes the immutable historical snapshots.

To automate desktop repository updates, schedule that command with your OS scheduler from a dedicated clean checkout. For example a user crontab can invoke `/usr/bin/python3 /absolute/repository/path/tools/checked_update.py` daily and append output to a local maintenance log. Scheduling is an installation choice on the user's machine; no cron service has been installed by this publication. Review failure logs. Test candidates may need the same optional codec dependencies as the existing checkout. Weekly GitHub Actions also runs bootstrap and verifies reproducible publication and extension outputs, alongside push and pull-request checks. Repository maintainers must repair newly discovered failures; scheduling tests cannot guarantee future Instagram layouts or platform compatibility.

Chrome does not automatically refresh a developer-mode unpacked extension from GitHub. After a repository update, reload it on Chrome's Extensions page and reload Instagram pages. Automatic browser-managed extension updates require a Chrome Web Store release or a properly configured enterprise distribution/update service. Neither is established here. No remote scripts are fetched into the extension, and no silent self-installation is attempted. Browser-managed updates must be configured before they can be claimed operational.

## Acceptance and requested quality labels

The requested “ostar”, “lair”, “max”, “greatest” and “surasuch” labels remain editorial names, not recognised media measurements or a compatibility warranty. Operational acceptance consists of pixel/hash comparisons, input limits, permission checks, queue tests, pinned-source integrity, deterministic packaging, publication checks and scheduled regression tests. Live Instagram layout tests, personal-desktop watcher startup and Web Store automatic updates are distinct checks which have not been performed by this cloud publication. Original-source preservation and explicit failures take priority over presenting an unverified conversion as improved quality.

# Image downloader v2

The earlier script requested nine hard-coded Library of Congress image paths. Many returned 403 or 404. The revised script FIRST looks up each image in the Library of Congress record and attempts the record's current JPEG derivatives, rather than relying entirely on old paths. If the institution denies programmatic access, it **reports a failure instead of pretending the photo was downloaded**.

For Windows: double-click `DOWNLOAD_IMAGES_WINDOWS.bat` with an internet connection. No third-party Python libraries are required. The script keeps any genuine images already downloaded (copy your existing `archive_02.jpg` into this ZIP's `assets/images` folder to avoid re-downloading).

Check `assets/images` for each file. If a given archival record has no publicly downloadable JPEG or blocks automatic access, open the Library of Congress catalog link and download that image through the browser; save it with the filename from `assets/image_manifest.json`.

Important: Other page styling (Bootstrap + fonts) still depends on internet access. This ZIP does not claim to contain all nine photos.

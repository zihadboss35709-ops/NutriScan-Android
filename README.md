# NutriScan AI — Android App

> AI-powered food calorie scanner wrapped in a native Android shell using **Capacitor**.  
> The app loads the live web application at **https://nutri-scan-mate--aaaaaa35709.replit.app** and adds native Android capabilities on top.

---

## Table of Contents

1. [Project structure](#project-structure)
2. [How it works](#how-it-works)
3. [Upload to GitHub](#upload-to-github)
4. [GitHub Actions builds the APK / AAB automatically](#github-actions-builds-the-apk--aab-automatically)
5. [Download the APK](#download-the-apk)
6. [Set up Release Signing](#set-up-release-signing)
7. [Publish on Google Play](#publish-on-google-play)
8. [Update the app later](#update-the-app-later)
9. [Local development](#local-development)
10. [Native features enabled](#native-features-enabled)

---

## Project structure

```
NutriScan-Android/
├── .github/workflows/
│   └── android-build.yml       ← GitHub Actions CI/CD
├── android/                    ← Android Studio project
│   ├── app/
│   │   ├── build.gradle
│   │   ├── capacitor.build.gradle
│   │   ├── proguard-rules.pro
│   │   └── src/main/
│   │       ├── AndroidManifest.xml
│   │       ├── assets/capacitor.config.json
│   │       ├── java/com/nutriscan/ai/
│   │       │   └── MainActivity.java
│   │       └── res/            ← icons, splash, styles
│   ├── build.gradle
│   ├── settings.gradle
│   ├── variables.gradle
│   ├── gradle.properties
│   └── gradlew
├── www/                        ← Minimal web fallback (overridden by server.url)
├── capacitor.config.ts         ← Capacitor configuration (source of truth)
├── capacitor.config.json       ← JSON copy (used at runtime by Android)
└── package.json
```

---

## How it works

Capacitor wraps your **existing Flask web app** in a native Android WebView.

```
Android App
  └── Capacitor WebView
        └── https://nutri-scan-mate--aaaaaa35709.replit.app
              └── Your Flask + AI scanning logic (unchanged)
```

The web app keeps running on Replit. The Android app just renders it natively and adds:
- Camera & gallery access
- Splash screen
- Adaptive app icon
- Back-button navigation
- Pull-to-refresh
- Dark mode
- Full HTTPS security

---

## Upload to GitHub

**Step 1 — Create a new GitHub repository**

1. Go to [github.com/new](https://github.com/new)
2. Name it `nutriscan-ai-android` (or anything you like)
3. Set it to **Private** (recommended) or Public
4. **Do NOT** initialise with README — the repo must be empty
5. Click **Create repository**

**Step 2 — Upload the project**

Option A — via the GitHub web UI (easiest, no Git required):
1. On the empty repository page, click **uploading an existing file**
2. Drag and drop the entire `NutriScan-Android` folder contents
3. Commit to `main`

Option B — via Git on your PC:
```bash
cd NutriScan-Android
git init
git add .
git commit -m "Initial commit — NutriScan AI Android project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/nutriscan-ai-android.git
git push -u origin main
```

---

## GitHub Actions builds the APK / AAB automatically

Every time you push code to `main` or `master`:

1. GitHub spins up an Ubuntu runner
2. Installs Node.js 20, Java 17, Android SDK 35
3. Runs `npm install` + `npx cap sync android`
4. Builds a **Release APK** (`assembleRelease`)
5. Builds a **Release AAB** (`bundleRelease`)
6. Uploads both as downloadable artifacts

You can also trigger a build manually: go to **Actions → Android Build → Run workflow**.

---

## Download the APK

1. Open your repository on GitHub
2. Click **Actions** in the top navigation bar
3. Click the latest successful workflow run
4. Scroll to the **Artifacts** section at the bottom
5. Download **NutriScan-AI-Release-APK** (contains the `.apk` file)
6. Install it on any Android phone by transferring and opening the file  
   *(enable "Install from unknown sources" in Android settings first)*

---

## Set up Release Signing

> Without signing secrets the workflow produces a **debug-signed APK** — fine for
> testing but **not accepted by Google Play**.  To produce a Play-ready AAB, add
> these four secrets to your GitHub repository.

**Step 1 — Generate a release keystore (do this once)**

```bash
keytool -genkey -v \
  -keystore nutriscan-release.jks \
  -alias nutriscan \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -dname "CN=Your Name, O=Your Company, C=US"
```

Keep `nutriscan-release.jks` in a very safe place — you need it for every future update.

**Step 2 — Base64-encode the keystore**

```bash
# Linux / macOS
base64 -w 0 nutriscan-release.jks > release.b64
cat release.b64   # copy this entire string
```

**Step 3 — Add GitHub repository secrets**

Go to **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name        | Value                                      |
|--------------------|--------------------------------------------|
| `KEYSTORE_BASE64`  | The base64 string from the previous step   |
| `KEYSTORE_PASSWORD`| Your keystore password                     |
| `KEY_ALIAS`        | `nutriscan` (or whatever alias you chose)  |
| `KEY_PASSWORD`     | Your key password                          |

Push any change to trigger a new build. This time the APK/AAB will be **release-signed**.

---

## Publish on Google Play

1. **Create a Google Play developer account** at [play.google.com/console](https://play.google.com/console)  
   (one-time $25 USD fee)

2. **Create a new app** → fill in the store listing (title, description, screenshots)

3. **Set up release signing**  
   Use the AAB artifact downloaded from GitHub Actions.  
   Google Play requires an AAB (`.aab`), not an APK, for new apps.

4. **Upload the AAB**  
   Go to **Production → Create new release → Upload → select your .aab file**

5. **Complete the content rating questionnaire**

6. **Submit for review** — Google typically reviews in 1–3 days for new apps

---

## Update the app later

### Option A — Web-only update (no app store submission needed!)

Because the Android app loads your **live Replit URL**, any change you make to the
Flask web app is instantly live for all users — no APK update required.

Just update your Flask app on Replit and users see the changes immediately.

### Option B — Native / config update (requires new APK / AAB)

If you change `capacitor.config.ts`, `AndroidManifest.xml`, icons, splash screen,
or any native Android code:

1. Make your changes in this project
2. Push to GitHub (`git push`)
3. GitHub Actions builds a new APK + AAB automatically
4. Download the new AAB from the Artifacts section
5. Go to Google Play Console → Production → Create new release
6. Upload the new AAB (bump `versionCode` in `app/build.gradle` first)
7. Submit for review

> **Always increment `versionCode`** in `android/app/build.gradle` for each Play Store release.

---

## Local development

If you want to build locally (requires Android Studio installed):

```bash
# 1. Install dependencies
npm install

# 2. Sync Capacitor
npx cap sync android

# 3. Open in Android Studio
npx cap open android

# 4. Or build from terminal
cd android
./gradlew assembleRelease
```

---

## Native features enabled

| Feature | Status |
|---|---|
| Camera (take photo) | ✅ |
| Gallery / file picker | ✅ |
| Internet (HTTPS only) | ✅ |
| Back button navigation | ✅ |
| Pull to refresh | ✅ |
| Splash screen | ✅ |
| Adaptive app icon | ✅ |
| Dark mode support | ✅ |
| Full screen mode | ✅ |
| Network security config | ✅ |
| Hardware acceleration | ✅ |
| Android 8–15 support | ✅ |

---

## Package details

| Key | Value |
|---|---|
| Application ID | `com.nutriscan.ai` |
| App Name | `NutriScan AI` |
| Version | `1.0.0` (versionCode 1) |
| Min Android | Android 6.0 (API 23) |
| Target Android | Android 15 (API 35) |
| Capacitor | 6.x |
| Build Tool | Gradle 8.9 + AGP 8.7 |

---

*Generated for the NutriScan AI project — Capacitor + Flask hybrid Android app.*

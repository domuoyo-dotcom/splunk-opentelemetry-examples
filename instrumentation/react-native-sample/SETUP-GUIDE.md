# Astronomy Shop — Setup Guide

How to install dependencies and run the **Astronomy Shop** React Native app (`react-native-sample/`) on iOS and Android.

This is an **Expo SDK 54** app. Development uses **Expo Go**. Splunk RUM instrumentation requires a **development build** — see [MRUM-Splunk-Instrumentation-Guide.md](./MRUM-Splunk-Instrumentation-Guide.md).

---

## App overview

| Item | Value |
|---|---|
| App name | Astronomy Shop |
| Directory | `react-native-sample/` |
| Expo SDK | 54 |
| React Native | 0.81.5 |
| Backend | None — products from [DummyJSON](https://dummyjson.com); cart/orders are in-memory |

**Screens:** Home, Products, Product Detail, Cart, Checkout, Order Confirmation, Order History, Profile.

---

## Prerequisites

| Platform | Required |
|---|---|
| All | Node.js 18+, npm |
| iOS (macOS only) | Xcode 15+ with iOS Simulator runtime |
| Android | Android Studio with an emulator, **or** a physical device with Expo Go from the Play Store |

Install project dependencies once:

```bash
cd react-native-sample
npm install
```

---

## Run on iOS Simulator

### 1. Install Xcode and a simulator

1. Install **Xcode** from the App Store.
2. Open **Xcode → Settings → Platforms** and install an **iOS Simulator** runtime.
3. Accept the license if prompted:

```bash
sudo xcodebuild -license accept
```

Verify simulators are available:

```bash
xcrun simctl list devices available | grep iPhone
```

### 2. Start the app

```bash
cd react-native-sample
npm run ios
```

This script:

- Opens the iOS Simulator (boots an iPhone if none is running)
- Installs **Expo Go** on the simulator if missing
- Starts Metro at `http://127.0.0.1:8081` with `--localhost`
- Opens `exp://127.0.0.1:8081` in Expo Go

**Do not use** `npm run ios:expo` unless Terminal/Cursor has macOS **Automation** permission for System Events. Prefer `npm run ios`.

### iOS troubleshooting

| Error | Cause | Fix |
|---|---|---|
| OSStatus **-10814** when opening `exp://…` | Expo Go not installed on the simulator | `npm run ios:install-expo-go`, then `npm run ios` |
| **osascript … not allowed** | macOS blocked Automation | Use `npm run ios` instead of `npm run ios:expo`, or grant Automation in **System Settings → Privacy & Security → Automation** |
| Metro port in use | Stale dev server on 8081 | The start script kills port 8081 automatically; if needed: `lsof -ti :8081 \| xargs kill -9` |
| No simulators listed | iOS runtime not downloaded | Xcode → Settings → Platforms → download iOS |

---

## Run on Android

### Emulator (recommended)

1. Create an AVD in **Android Studio → Device Manager** (API 24+).
2. Start the emulator, then run:

```bash
cd react-native-sample
npm run android
```

This script:

- Kills stale Metro on port 8081
- Runs `adb reverse tcp:8081 tcp:8081` so the emulator reaches Metro at `127.0.0.1`
- Starts Expo with `--localhost` (LAN URLs fail on emulators)

**Use Play Store Expo Go** on the emulator. The app targets **SDK 54**; an older Expo Go will show a compatibility error.

### Physical Android device

Same Wi‑Fi as your computer:

```bash
npm run android:device
```

If the device cannot reach your machine over LAN:

```bash
npm run android:tunnel
```

### Android troubleshooting

| Symptom | Fix |
|---|---|
| Expo Go “Something went wrong”, no Metro error | Ensure Play Store Expo Go supports SDK 54; run `npm run android` (not plain `expo start`) |
| Cannot connect to Metro | Emulator: use `npm run android`. Device: same Wi‑Fi or `npm run android:tunnel` |
| `adb reverse` fails | Start the emulator first; confirm `adb devices` lists it |

---

## npm scripts

| Script | Purpose |
|---|---|
| `npm start` | Metro only (`expo start --clear`) |
| `npm run ios` | iOS Simulator + Expo Go + Metro (recommended) |
| `npm run ios:install-expo-go` | Install Expo Go on booted simulator only |
| `npm run android` | Android emulator + Metro with localhost/adb reverse |
| `npm run android:device` | Physical Android on same Wi‑Fi |
| `npm run android:tunnel` | Physical Android via Expo tunnel |

---

## Project layout

```
react-native-sample/
├── App.tsx                 # Root: providers, NavigationContainer, ErrorBoundary
├── src/
│   ├── api/productsApi.ts  # DummyJSON fetch + local fallback
│   ├── navigation/         # Bottom tabs + product/cart stacks
│   ├── screens/            # 8 screens
│   └── store/ShopContext.tsx  # Cart, orders, product state
└── scripts/
    ├── start-ios.sh
    ├── start-android.sh
    └── install-expo-go-ios.sh
```

---

## Next steps

- **Splunk RUM:** [MRUM-Splunk-Instrumentation-Guide.md](./MRUM-Splunk-Instrumentation-Guide.md) — requires `expo prebuild` and a native development build; does not run in Expo Go.

---

*Updated July 2026 — Astronomy Shop React Native (Expo SDK 54)*

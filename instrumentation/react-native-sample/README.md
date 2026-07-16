# Astronomy Shop — React Native

Cross-platform (iOS & Android) React Native port of the [base-android-jetpack-astronomy-shop](../base-android-jetpack-astronomy-shop) app.

An e-commerce demo for astronomy gear: browse telescopes, eyepieces, and accessories, add items to cart, checkout, and view order history.

## Features

- **8 screens**: Home, Products, Product Detail, Cart, Checkout, Order Confirmation, Order History, Profile
- **Bottom tab navigation** with cart badge
- **Product catalog** from DummyJSON API with astronomy-themed overlay and local fallback data
- **In-memory cart & orders** with tax (8.5%), shipping ($9.99 or free over $50), and bulk savings display
- **Material Design 3** styling via React Native Paper (indigo primary `#3F51B5`)

## Tech Stack

| Layer | Library |
|---|---|
| Framework | Expo SDK 54 + React Native 0.81 |
| Language | TypeScript |
| Navigation | React Navigation (bottom tabs + native stack) |
| UI | React Native Paper |
| State | React Context (mirrors Android `MainViewModel`) |
| API | DummyJSON (`https://dummyjson.com`) |

## Project Structure

```
src/
├── api/              # DummyJSON product fetching & mapping
├── components/       # ProductCard, CartItemCard, OrderCard, etc.
├── constants/        # Astronomy product templates & sample data
├── models/           # TypeScript interfaces
├── navigation/       # AppNavigator, route types
├── screens/          # 8 screen components
├── store/            # ShopContext (cart, orders, products)
├── theme/            # Colors & Paper theme
└── utils/            # Formatters & pricing logic
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- For iOS: Xcode + iOS Simulator (macOS only)
- For Android: Android Studio + emulator, or a physical device with Expo Go

### Install & Run

**Android emulator (recommended for development):**

```bash
cd react-native-sample
npm install
npm run android
```

This script automatically:
- Kills any stale Metro server on port 8081
- Runs `adb reverse` so the emulator can reach Metro at `127.0.0.1`
- Starts Expo with `--localhost` (required for emulators)

**Physical Android device:**

```bash
npm run android:device   # same Wi‑Fi as your computer
# or, if Wi‑Fi is unreliable:
npm run android:tunnel
```

**iOS simulator:**

```bash
npm run ios
```

## License
Sample project for demonstration purposes.

@domuoyo-dotcom - July 2026

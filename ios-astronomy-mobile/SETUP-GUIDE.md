# How to Run AstronomyShop iOS on Your Mac

A step-by-step guide to launch and run the AstronomyShop iOS app on your local Mac.

---

## Prerequisites

Before starting, ensure you have:

- **macOS Sonoma 14.0** or later (recommended)
- **Xcode 15.0** or later
- At least **10GB free disk space** (for Xcode and simulators)
- Apple ID (free account works for simulator testing)

---

## Step 1: Install Xcode

### Option A: From App Store (Recommended)

1. Open the **App Store** on your Mac
2. Search for **"Xcode"**
3. Click **Get** / **Install**
4. Wait for download to complete (~7GB)

### Option B: From Developer Portal

1. Go to: https://developer.apple.com/download/
2. Sign in with your Apple ID
3. Download Xcode 15 or later
4. Open the downloaded `.xip` file
5. Drag Xcode to your Applications folder

### Verify Installation

Open Terminal and run:
```bash
xcode-select --version
```

You should see output like: `xcode-select version 2397`

---

## Step 2: Install Command Line Tools

Open Terminal and run:

```bash
xcode-select --install
```

A dialog will appear - click **Install** and wait for completion.

---

## Step 3: Accept Xcode License

Open Terminal and run:

```bash
sudo xcodebuild -license accept
```

Enter your Mac password when prompted.

---

## Step 4: Install iOS Simulator

1. Open **Xcode**
2. Go to **Xcode > Settings** (or press `Cmd + ,`)
3. Click the **Platforms** tab
4. Click the **+** button at bottom left
5. Select **iOS 17** (or latest available)
6. Click **Download & Install**
7. Wait for download (~5GB)

### Verify Simulators

```bash
xcrun simctl list devices available
```

You should see devices like "iPhone 15 Pro", "iPhone 15", etc.

---

## Step 5: Navigate to Project Directory

Open Terminal and run:

```bash
cd /Users/domuoyo/ios-astronomy-mobile
```

Verify project files exist:

```bash
ls -la
```

You should see:
```
AstronomyShop.xcodeproj/
AstronomyShop/
Package.swift
README.md
...
```

---

## Step 6: Open Project in Xcode

### Option A: From Terminal

```bash
open AstronomyShop.xcodeproj
```

### Option B: From Finder

1. Open Finder
2. Navigate to `/Users/domuoyo/ios-astronomy-mobile`
3. Double-click `AstronomyShop.xcodeproj`

---

## Step 7: Configure Signing (First Time Only)

When Xcode opens:

1. Click on **AstronomyShop** in the Project Navigator (left sidebar)
2. Select the **AstronomyShop** target
3. Click the **Signing & Capabilities** tab
4. Check **Automatically manage signing**
5. Select your **Team**:
   - If you have an Apple Developer account, select it
   - If not, click **Add Account** and sign in with your Apple ID
   - Select **Personal Team** (free option)

### For Simulator Only (No Signing Required)

If you're only running on the Simulator, you can skip signing configuration. The app will build and run without a team selected.

---

## Step 8: Select Target Device

### In the Xcode Toolbar:

1. Look for the device selector (shows something like "Any iOS Device")
2. Click on it to open the dropdown
3. Under **iOS Simulators**, select a device:
   - **iPhone 15 Pro** (recommended)
   - **iPhone 15**
   - **iPhone SE** (for smaller screen testing)

![Device Selector Location: Top center of Xcode window, next to the Play button]

---

## Step 9: Build and Run

### Option A: Using Xcode UI

1. Click the **Play button** (▶) in the top-left corner
   - Or press `Cmd + R`

2. Wait for:
   - Build process (first build takes 1-2 minutes)
   - Simulator to launch
   - App to install and open

### Option B: Using Terminal

```bash
# Build the app
xcodebuild -project AstronomyShop.xcodeproj \
  -scheme AstronomyShop \
  -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
  build

# Build and run
xcodebuild -project AstronomyShop.xcodeproj \
  -scheme AstronomyShop \
  -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
  build

# Then open simulator and run
open -a Simulator
xcrun simctl boot "iPhone 15 Pro"
xcrun simctl install "iPhone 15 Pro" \
  ~/Library/Developer/Xcode/DerivedData/AstronomyShop-*/Build/Products/Debug-iphonesimulator/AstronomyShop.app
xcrun simctl launch "iPhone 15 Pro" com.astronomyshop.app
```

---

## Step 10: Using the App

Once the app launches in the Simulator:

### Home Tab
- Browse product categories
- View featured products
- Tap a category or product to explore

### Products Tab
- Search for products
- Filter by category
- Tap a product for details

### Cart Tab
- View items in your cart
- Adjust quantities
- Proceed to checkout

### Orders Tab
- View order history
- Tap an order for details

### Profile Tab
- Access developer tools
- Test error simulations

---

## Simulator Tips

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd + Shift + H` | Go to Home screen |
| `Cmd + Right Arrow` | Rotate right |
| `Cmd + Left Arrow` | Rotate left |
| `Cmd + S` | Take screenshot |
| `Cmd + K` | Toggle software keyboard |
| `Cmd + Shift + K` | Toggle keyboard connect |

### Simulator Menu Options

- **Device > Shake** - Trigger shake gesture
- **Device > Rotate** - Change orientation
- **Features > Toggle Appearance** - Switch light/dark mode
- **Debug > Slow Animations** - Debug UI animations

### Reset Simulator

If the app behaves unexpectedly:

1. In Simulator: **Device > Erase All Content and Settings**
2. Or in Terminal:
   ```bash
   xcrun simctl erase all
   ```

---

## Troubleshooting

### Issue: "No devices registered"

**Solution:**
1. Xcode > Settings > Platforms
2. Download iOS Simulator

### Issue: Build fails with signing error

**Solution:**
1. Select project in Navigator
2. Target > Signing & Capabilities
3. Check "Automatically manage signing"
4. Select a Team (or Personal Team)

### Issue: "Module not found"

**Solution:**
```bash
# Clean build folder
rm -rf ~/Library/Developer/Xcode/DerivedData/AstronomyShop-*

# Rebuild
xcodebuild clean build -project AstronomyShop.xcodeproj -scheme AstronomyShop
```

### Issue: Simulator won't launch

**Solution:**
```bash
# Kill all simulators
killall Simulator

# Reset simulators
xcrun simctl shutdown all

# Try again
open -a Simulator
```

### Issue: App crashes on launch

**Solution:**
1. In Xcode, go to **Product > Clean Build Folder** (`Cmd + Shift + K`)
2. Then **Product > Build** (`Cmd + B`)
3. Run again (`Cmd + R`)

### Issue: "Unable to boot device in current state"

**Solution:**
```bash
xcrun simctl shutdown all
xcrun simctl erase all
```

---

## Running on Physical iPhone (Optional)

To run on a real device:

### Requirements
- iPhone with iOS 17.0+
- USB cable (Lightning or USB-C)
- Apple Developer account (free works for 7 days)

### Steps

1. Connect iPhone to Mac via USB
2. On iPhone: **Trust This Computer** when prompted
3. In Xcode, select your iPhone from device dropdown
4. Click **Run** (▶)
5. On first run:
   - iPhone: Go to **Settings > General > Device Management**
   - Trust the developer certificate
6. Run again

---

## Quick Reference Commands

```bash
# Navigate to project
cd /Users/domuoyo/ios-astronomy-mobile

# Open in Xcode
open AstronomyShop.xcodeproj

# List available simulators
xcrun simctl list devices available

# Boot a specific simulator
xcrun simctl boot "iPhone 15 Pro"

# Open Simulator app
open -a Simulator

# Build from command line
xcodebuild -project AstronomyShop.xcodeproj \
  -scheme AstronomyShop \
  -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
  build

# Clean build
xcodebuild clean -project AstronomyShop.xcodeproj -scheme AstronomyShop

# View build logs
xcodebuild -project AstronomyShop.xcodeproj -scheme AstronomyShop 2>&1 | tee build.log
```

---

## Summary Checklist

- [ ] Xcode installed
- [ ] Command line tools installed
- [ ] License accepted
- [ ] iOS Simulator downloaded
- [ ] Project opened in Xcode
- [ ] Simulator device selected
- [ ] App built and running

---

*Guide Version: 1.0 | February 2026*

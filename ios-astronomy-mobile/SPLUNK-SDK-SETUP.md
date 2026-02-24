# Splunk RUM SDK 2.x — Full Instrumentation Guide

Step-by-step setup for the AstronomyShop iOS app covering SDK installation, utility file creation, and instrumentation for Session Replay, Workflow Tracking, Error Tracking, Crash Reporting, and Event Tracking.

---

## Prerequisites

- Xcode 15.0 or later
- iOS 16.0+ deployment target
- Splunk Observability Cloud account
- RUM Access Tokens (one per realm you intend to use)

---

## Part 1 — SDK Installation

### Step 1.1: Add the Package

1. Open `AstronomyShop.xcodeproj` in Xcode
2. Go to **File > Add Package Dependencies...**
3. Enter:
   ```
   https://github.com/signalfx/splunk-otel-ios
   ```
4. Set **Dependency Rule** → **Exact Version** → `2.0.6`
5. Click **Add Package**
6. In the product selection dialog, check **SplunkAgent**
7. Click **Add Package**

### Step 1.2: Verify the Package Is Linked

1. In the Xcode project navigator, select the **AstronomyShop** target
2. Go to **Build Phases > Link Binary With Libraries**
3. Confirm **SplunkAgent** appears in the list
4. If missing, click **+**, search for `SplunkAgent`, and add it

---

## Part 2 — Creating the Utility Files

Two files form the instrumentation foundation. Create both before instrumenting any views.

---

### Step 2.1: Create `SplunkConfiguration.swift`

**File path:** `AstronomyShop/Utils/SplunkConfiguration.swift`

This file holds all configuration constants and computed properties. No SDK import is needed here.

```swift
import Foundation

enum SplunkConfiguration {

    // MARK: - Realm (dynamic, set by user in Profile tab)

    static var realm: String {
        SplunkManager.shared.selectedRealm
    }

    // MARK: - RUM Access Tokens
    // Replace with your actual tokens from Splunk Observability Cloud

    static let rumAccessTokenUS1 = "YOUR_US1_TOKEN_HERE"
    static let rumAccessTokenEU0 = "YOUR_EU0_TOKEN_HERE"

    // Selects token based on active realm
    static var rumAccessToken: String {
        switch SplunkManager.shared.selectedRealm {
        case "eu0": return rumAccessTokenEU0
        default:    return rumAccessTokenUS1
        }
    }

    // MARK: - App Identity

    // App name appears in the Splunk RUM dashboard — includes realm for easy filtering
    static var appName: String {
        "AstronomyShop-iOS-\(SplunkManager.shared.selectedRealm.lowercased())"
    }

    static let environment = "development"

    static var appVersion: String {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.0"
    }

    static var buildNumber: String {
        Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "1"
    }

    // MARK: - Endpoint

    static var endpointUrl: String {
        "https://rum-ingest.\(realm).signalfx.com/v1/rum"
    }

    // MARK: - Feature Flags

    static let sessionReplayEnabled          = true
    static let debugLoggingEnabled           = true
    static let samplingRate: Double          = 1.0
    static let enableNavigationTracking      = true
    static let enableCrashReporting         = true
    static let enableNetworkInstrumentation  = true
    static let enableInteractionTracking     = true
    static let enableSlowRenderingDetection  = true

    // MARK: - Validation

    // Guards against un-replaced placeholder tokens
    static var isValid: Bool {
        let token = rumAccessToken
        return !token.isEmpty
            && !token.contains("YOUR_")
            && !token.contains("_HERE")
            && !realm.isEmpty
    }

    static var isUS1Configured: Bool {
        !rumAccessTokenUS1.isEmpty
            && !rumAccessTokenUS1.contains("YOUR_")
            && !rumAccessTokenUS1.contains("_HERE")
    }

    static var isEU0Configured: Bool {
        !rumAccessTokenEU0.isEmpty
            && !rumAccessTokenEU0.contains("YOUR_")
            && !rumAccessTokenEU0.contains("_HERE")
    }

    // MARK: - Global Attributes

    static var globalAttributes: [String: String] {
        [
            "app.version": appVersion,
            "app.build":   buildNumber,
            "app.platform": "iOS"
        ]
    }
}
```

**Getting your tokens:**

1. Log in to [Splunk Observability Cloud](https://app.signalfx.com)
2. Go to **Settings > Access Tokens**
3. Create a token with **RUM** permissions for each realm (US1, EU0)
4. Replace `YOUR_US1_TOKEN_HERE` and `YOUR_EU0_TOKEN_HERE` with your actual values

---

### Step 2.2: Create `SplunkManager.swift`

**File path:** `AstronomyShop/Utils/SplunkManager.swift`

This is the central instrumentation hub. All views and view models call methods on `SplunkManager.shared`. The entire SDK surface is wrapped in `#if canImport(SplunkAgent)` so the app compiles and runs without the SDK installed (useful for the uninstrumented baseline build).

```swift
import Foundation
import Combine
import SwiftUI

#if canImport(SplunkAgent)
import SplunkAgent
import OpenTelemetryApi
import OpenTelemetrySdk
#endif

final class SplunkManager: ObservableObject {

    // MARK: - Singleton
    static let shared = SplunkManager()

    // MARK: - SDK Reference
    #if canImport(SplunkAgent)
    private var agent: SplunkRum?
    #endif

    // MARK: - Published State
    @Published var isInitialized: Bool = false
    @Published var isSessionReplayActive: Bool = false
    @Published var currentScreenName: String = "unknown"
    @Published var lastError: String?
    @Published var spanCount: Int = 0
    @Published var errorCount: Int = 0
    @Published var needsRestart: Bool = false

    // Realm persisted in UserDefaults
    @Published var selectedRealm: String = {
        UserDefaults.standard.string(forKey: "splunk_realm") ?? "us1"
    }() {
        didSet {
            UserDefaults.standard.set(selectedRealm, forKey: "splunk_realm")
            UserDefaults.standard.synchronize()
            if isInitialized && selectedRealm != initializedRealm {
                needsRestart = true
            }
        }
    }

    private var initializedRealm: String = "us1"

    enum Realm: String, CaseIterable {
        case us1 = "us1"
        case eu0 = "eu0"
    }

    var appName: String {
        "AstronomyShop-iOS-\(selectedRealm.lowercased())"
    }

    private init() {}

    // MARK: - Initialization

    func initialize() {
        guard SplunkConfiguration.isValid else {
            lastError = "Configuration invalid - update token in SplunkConfiguration.swift"
            print("[SplunkManager] ERROR: Token not configured")
            return
        }
        guard !isInitialized else { return }

        #if canImport(SplunkAgent)
        do {
            let endpoint = EndpointConfiguration(
                realm: SplunkConfiguration.realm,
                rumAccessToken: SplunkConfiguration.rumAccessToken
            )

            var config = AgentConfiguration(
                endpoint: endpoint,
                appName: SplunkConfiguration.appName,
                deploymentEnvironment: SplunkConfiguration.environment
            )

            config = config.enableDebugLogging(SplunkConfiguration.debugLoggingEnabled)
            config = config.sessionConfiguration(
                SessionConfiguration(samplingRate: SplunkConfiguration.samplingRate)
            )

            agent = try SplunkRum.install(with: config)

            // Attach global attributes to every span
            SplunkRum.shared.globalAttributes[string: "app.version"] = SplunkConfiguration.appVersion
            SplunkRum.shared.globalAttributes[string: "app.build"]   = SplunkConfiguration.buildNumber
            SplunkRum.shared.globalAttributes[string: "app.platform"] = "iOS"

            // Enable auto-navigation tracking
            agent?.navigation.preferences.enableAutomatedTracking = true

            isInitialized = true
            initializedRealm = selectedRealm
            print("[SplunkManager] Initialized for realm: \(selectedRealm)")

        } catch {
            lastError = error.localizedDescription
            print("[SplunkManager] ERROR: \(error.localizedDescription)")
        }
        #endif
    }
}
```

> The `WorkflowSpan` class, screen tracking, workflow tracking, error tracking, event tracking, and crash methods are added to this file in the sections below.

---

### Step 2.3: Wire Up the App Entry Point

Open `AstronomyShop/AstronomyShopApp.swift` and call `initialize()` before the first view renders. Also inject `SplunkManager.shared` as an environment object so views can access it:

```swift
import SwiftUI

@main
struct AstronomyShopApp: App {
    @StateObject private var cartViewModel    = CartViewModel()
    @StateObject private var productViewModel = ProductViewModel()
    @StateObject private var orderViewModel   = OrderViewModel()

    init() {
        SplunkManager.shared.initialize()
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(cartViewModel)
                .environmentObject(productViewModel)
                .environmentObject(orderViewModel)
                .environmentObject(SplunkManager.shared)
        }
    }
}
```

`initialize()` is called in `init()` so the SDK is started before any view's `onAppear` fires.

---

## Part 3 — Session Replay

Session Replay records the full visual state of the app so you can replay exactly what the user saw during a session.

### Step 3.1: Start Session Replay

Add this to `SplunkManager.initialize()` immediately after `isInitialized = true`:

```swift
#if canImport(SplunkAgent)
if SplunkConfiguration.sessionReplayEnabled {
    agent?.sessionReplay.start()
    isSessionReplayActive = true
    print("[SplunkManager] Session Replay started")
}
#endif
```

With `sessionReplayEnabled = true` in `SplunkConfiguration.swift`, replay starts on every launch automatically.

### Step 3.2: Add the Privacy Masking Modifier

Add this extension and `ViewModifier` to `SplunkManager.swift` (after the main class):

```swift
// MARK: - Session Replay Privacy Modifier

extension SwiftUI.View {
    /// Marks a view as sensitive — excluded from Session Replay recordings.
    func sessionReplaySensitive() -> some SwiftUI.View {
        self.modifier(SessionReplaySensitiveModifier())
    }
}

struct SessionReplaySensitiveModifier: SwiftUI.ViewModifier {
    func body(content: Content) -> some SwiftUI.View {
        content
        // When the SDK supports it, apply srSensitive here:
        // content.srSensitive()
    }
}
```

### Step 3.3: Mark Sensitive Views

Apply `.sessionReplaySensitive()` to any view containing personal or payment data. In `CheckoutView.swift`:

```swift
// Card number — mask in replay
CustomTextField(placeholder: "Card Number", text: $orderViewModel.cardNumber, icon: "creditcard")
    .sessionReplaySensitive()

// CVV — mask in replay
CustomTextField(placeholder: "CVV", text: $orderViewModel.cvv, icon: "lock.fill")
    .sessionReplaySensitive()
```

### Step 3.4: Viewing Replays in Splunk

1. Go to [Splunk Observability Cloud](https://app.signalfx.com)
2. Navigate to **RUM > Session Replay**
3. Select your app (`AstronomyShop-iOS-us1` or `AstronomyShop-iOS-eu0`)
4. Filter by session, user, or time range
5. Click any session to play it back

---

## Part 4 — Workflow Tracking

Workflows track multi-step user journeys (browsing → product detail → add to cart → checkout). Each workflow is an OpenTelemetry span that stays open until the action completes.

### Step 4.1: Add the WorkflowSpan Class

Add this class to `SplunkManager.swift` after the main `SplunkManager` class:

```swift
// MARK: - WorkflowSpan

class WorkflowSpan {
    let name: String
    private var isEnded = false

    #if canImport(SplunkAgent)
    private var span: (any OpenTelemetryApi.Span)?

    init(name: String, span: (any OpenTelemetryApi.Span)?) {
        self.name = name
        self.span = span
    }
    #else
    init(name: String) { self.name = name }
    #endif

    func setAttribute(key: String, value: String) {
        guard !isEnded else { return }
        #if canImport(SplunkAgent)
        span?.setAttribute(key: key, value: .string(value))
        #endif
    }

    func setAttribute(key: String, value: Int) {
        guard !isEnded else { return }
        #if canImport(SplunkAgent)
        span?.setAttribute(key: key, value: .int(value))
        #endif
    }

    func setAttribute(key: String, value: Double) {
        guard !isEnded else { return }
        #if canImport(SplunkAgent)
        span?.setAttribute(key: key, value: .double(value))
        #endif
    }

    func setAttribute(key: String, value: Bool) {
        guard !isEnded else { return }
        #if canImport(SplunkAgent)
        span?.setAttribute(key: key, value: .bool(value))
        #endif
    }

    func addEvent(name: String) {
        guard !isEnded else { return }
        #if canImport(SplunkAgent)
        span?.addEvent(name: name, attributes: [:])
        #endif
    }

    func end() {
        guard !isEnded else { return }
        isEnded = true
        #if canImport(SplunkAgent)
        span?.end()
        #endif
    }
}
```

### Step 4.2: Add the Core `startWorkflow` Method to SplunkManager

Add inside the `SplunkManager` class:

```swift
// MARK: - Workflow Tracking

func startWorkflow(_ name: String, attributes: [String: String] = [:]) -> WorkflowSpan {
    spanCount += 1
    #if canImport(SplunkAgent)
    let tracer = OpenTelemetry.instance.tracerProvider.get(
        instrumentationName: "AstronomyShop",
        instrumentationVersion: "1.0.0"
    )
    let span = tracer.spanBuilder(spanName: name).startSpan()
    span.setAttribute(key: "workflow.name", value: .string(name))
    span.setAttribute(key: "view.name",     value: .string(currentScreenName))
    for (key, value) in attributes {
        span.setAttribute(key: key, value: .string(value))
    }
    return WorkflowSpan(name: name, span: span)
    #else
    return WorkflowSpan(name: name)
    #endif
}
```

> **Important:** `workflow.name` is required for spans to appear in the Splunk RUM UI. Always set it.

### Step 4.3: Add Pre-built Workflow Helpers

Add these convenience methods inside `SplunkManager`:

```swift
func trackProductBrowsing() -> WorkflowSpan {
    startWorkflow("ProductListLoaded")
}

func trackProductDetail(productId: Int, productName: String) -> WorkflowSpan {
    startWorkflow("ProductDetail", attributes: [
        "product.id":   String(productId),
        "product.name": productName
    ])
}

func trackAddToCart(productId: Int, productName: String, price: Double) -> WorkflowSpan {
    startWorkflow("AddToCart", attributes: [
        "product.id":    String(productId),
        "product.name":  productName,
        "product.price": String(format: "%.2f", price)
    ])
}

func trackCheckout(cartTotal: Double, itemCount: Int) -> WorkflowSpan {
    startWorkflow("PlaceOrder", attributes: [
        "cart.total":     String(format: "%.2f", cartTotal),
        "cart.itemCount": String(itemCount)
    ])
}

func trackSearch(query: String, resultCount: Int) -> WorkflowSpan {
    startWorkflow("ProductSearch", attributes: [
        "search.query":       query,
        "search.resultCount": String(resultCount)
    ])
}
```

### Step 4.4: Add Screen Tracking

Screen tracking records each view transition as a named span and updates the global `view.name` attribute:

```swift
// MARK: - Screen Tracking

func setScreenName(_ screenName: String) {
    currentScreenName = screenName
    let workflowName = screenName == "Home" ? "HomePage" : screenName
    guard isInitialized else { return }
    #if canImport(SplunkAgent)
    SplunkRum.shared.globalAttributes[string: "view.name"] = screenName
    let tracer = OpenTelemetry.instance.tracerProvider.get(
        instrumentationName: "AstronomyShop",
        instrumentationVersion: "1.0.0"
    )
    let span = tracer.spanBuilder(spanName: workflowName).startSpan()
    span.setAttribute(key: "workflow.name", value: .string(workflowName))
    span.setAttribute(key: "component",     value: .string("ui"))
    span.setAttribute(key: "view.name",     value: .string(screenName))
    span.end()
    #endif
    spanCount += 1
}
```

### Step 4.5: Instrument Each View

Call `setScreenName` in every view's `.onAppear`. For views with trackable user journeys, also start and end a workflow span.

**HomeView.swift**
```swift
.onAppear {
    SplunkManager.shared.setScreenName("Home")
    let span = SplunkManager.shared.trackProductBrowsing()
    span.end()
}
```

**ProductsView.swift**
```swift
.onAppear {
    SplunkManager.shared.setScreenName("Products")
}

// Track search queries as the user types
.onChange(of: productViewModel.searchText) { newValue in
    if !newValue.isEmpty {
        let span = SplunkManager.shared.trackSearch(
            query: newValue,
            resultCount: productViewModel.filteredProducts.count
        )
        span.end()
    }
}
```

**ProductDetailView.swift**
```swift
.onAppear {
    SplunkManager.shared.setScreenName("ProductDetail")
    let span = SplunkManager.shared.trackProductDetail(
        productId: product.id,
        productName: product.name
    )
    span.end()
}
```

**ProductDetailView — Add to Cart action:**
```swift
private func addToCart() {
    let span = SplunkManager.shared.trackAddToCart(
        productId: product.id,
        productName: product.name,
        price: product.price * Double(quantity)
    )
    span.setAttribute(key: "quantity", value: quantity)
    cartViewModel.addToCart(product, quantity: quantity)
    span.addEvent(name: "product_added_to_cart")
    span.end()
}
```

**ProductDetailView — Buy Now action:**
```swift
private func buyNow() {
    let span = SplunkManager.shared.trackAddToCart(
        productId: product.id,
        productName: product.name,
        price: product.price * Double(quantity)
    )
    span.setAttribute(key: "quantity", value: quantity)
    span.setAttribute(key: "action",   value: "buy_now")
    cartViewModel.addToCart(product, quantity: quantity)
    span.addEvent(name: "buy_now_clicked")
    span.end()
    navigateToCheckout = true
}
```

**CheckoutView.swift — long-lived span across the full checkout journey:**
```swift
@State private var checkoutSpan: WorkflowSpan?

// Start on appear
.onAppear {
    SplunkManager.shared.setScreenName("Checkout")
    checkoutSpan = SplunkManager.shared.trackCheckout(
        cartTotal: cartViewModel.total,
        itemCount: cartViewModel.itemCount
    )
}

// End on abandon
.onDisappear {
    if !showConfirmation {
        checkoutSpan?.addEvent(name: "checkout_abandoned")
        checkoutSpan?.end()
    }
}

// End on success
.onChange(of: orderViewModel.orderPlaced) { placed in
    if placed {
        checkoutSpan?.addEvent(name: "order_placed_successfully")
        checkoutSpan?.end()
        cartViewModel.clearCart()
        showConfirmation = true
        orderViewModel.resetOrderPlaced()
    }
}
```

**Other views** (Cart, OrderHistory, OrderDetails, OrderConfirmation, Profile):
```swift
.onAppear {
    SplunkManager.shared.setScreenName("Cart")           // CartView
    SplunkManager.shared.setScreenName("OrderHistory")   // OrderHistoryView
    SplunkManager.shared.setScreenName("OrderDetails")   // OrderDetailsView
    SplunkManager.shared.setScreenName("OrderConfirmation") // OrderConfirmationView
    SplunkManager.shared.setScreenName("Profile")        // ProfileView
}
```

---

## Part 5 — Error Tracking

Error tracking records structured error spans to Splunk with type, message, and custom attributes.

### Step 5.1: Add Error Tracking Methods to SplunkManager

```swift
// MARK: - Error Tracking

func recordError(type: String, message: String, attributes: [String: String] = [:]) {
    guard isInitialized else { return }
    errorCount += 1
    spanCount  += 1
    lastError   = "\(type): \(message)"

    var attrs = attributes
    attrs["error"]         = "true"
    attrs["error.type"]    = type
    attrs["error.message"] = message
    attrs["screen.name"]   = currentScreenName

    #if canImport(SplunkAgent)
    let error = NSError(domain: type, code: -1, userInfo: [
        NSLocalizedDescriptionKey: message,
        "attributes": attrs
    ])
    SplunkRum.shared.customTracking.trackError(error)
    #endif
}

// Convenience overload for Swift Error types
func recordError(_ error: Error, context: String? = nil) {
    var attrs: [String: String] = [:]
    if let ctx = context { attrs["context"] = ctx }
    recordError(
        type: String(describing: Swift.type(of: error)),
        message: error.localizedDescription,
        attributes: attrs
    )
}
```

### Step 5.2: Add Error Simulation Methods

These are called from the Profile tab's **Error Simulation** section:

```swift
// MARK: - Error Simulations

func simulateNetworkError() {
    recordError(
        type: "NetworkError",
        message: "Connection timeout - unable to reach server",
        attributes: [
            "endpoint":    "/api/products",
            "http.method": "GET",
            "timeout":     "30000"
        ]
    )
}

func simulatePaymentError() {
    recordError(
        type: "PaymentError",
        message: "Card declined - insufficient funds",
        attributes: [
            "payment.method": "credit_card",
            "error.code":     "CARD_DECLINED"
        ]
    )
}

func simulateSlowLoading() {
    addEvent("SlowLoadingStarted", attributes: [
        "delay": "5000ms",
        "type":  "network_simulation"
    ])
}
```

### Step 5.3: Record Payment Errors at Checkout

In `CheckoutView.swift`, when `placeOrder()` detects a simulated error, record it before showing the alert:

```swift
private func placeOrder() {
    checkoutSpan?.addEvent(name: "place_order_clicked")

    if cartViewModel.hasSimulatedPaymentError {
        checkoutSpan?.addEvent(name: "payment_failed_simulated")
        SplunkManager.shared.recordError(
            type: "PaymentError",
            message: "Card declined - simulated payment failure",
            attributes: [
                "error.code":      "CARD_DECLINED",
                "payment.method":  "credit_card",
                "simulated":       "true"
            ]
        )
        showPaymentErrorAlert = true
        return
    }

    orderViewModel.placeOrder(cartItems: cartViewModel.items, total: cartViewModel.total)
}
```

### Step 5.4: Wire the Payment Error Flow in ProfileView

The payment error simulation in the Profile tab uses a two-step flow — confirmation first, then the error is armed for checkout:

```swift
// ProfileView.swift — button triggers confirmation
Button(action: { showPaymentErrorAlert = true }) {
    HStack {
        Image(systemName: "creditcard.trianglebadge.exclamationmark")
        Text("Simulate Payment Error")
    }
}

// Confirmation alert
.alert("Payment Error Test", isPresented: $showPaymentErrorAlert) {
    Button("Simulate Error") {
        cartViewModel.simulatePaymentError()   // arms the error flag
        SplunkManager.shared.simulatePaymentError()  // records to Splunk
    }
    Button("Cancel", role: .cancel) {}
} message: {
    Text("This will simulate a payment failure when you tap Place Order at checkout.")
}
```

The "Credit Card Declined" alert then appears at checkout when the user taps Place Order:

```swift
// CheckoutView.swift — shown when hasSimulatedPaymentError is true
.alert("Credit Card Declined", isPresented: $showPaymentErrorAlert) {
    Button("Try Again") {
        showPaymentErrorAlert = true  // re-shows the alert
    }
    Button("Clear Error") {
        cartViewModel.clearError()    // resets hasSimulatedPaymentError
    }
} message: {
    Text("Your payment could not be processed. The card was declined by the issuing bank.")
}
```

---

## Part 6 — Crash Reporting

Crash reporting sends a structured error span to Splunk immediately before the app terminates. A 3-second countdown overlay gives time to observe the pre-crash state in Session Replay.

### Step 6.1: Add Crash Simulation Methods to SplunkManager

```swift
// MARK: - Crash Simulations

func triggerRuntimeExceptionCrash() {
    recordError(type: "CrashSimulation", message: "Triggering RuntimeException crash",
                attributes: ["crash.type": "RuntimeException"])
    abort()
}

func triggerNullPointerCrash() {
    recordError(type: "CrashSimulation", message: "Triggering Null Pointer crash",
                attributes: ["crash.type": "NullPointer"])
    abort()
}

func triggerIndexOutOfBoundsCrash() {
    recordError(type: "CrashSimulation", message: "Triggering Index Out of Bounds crash",
                attributes: ["crash.type": "IndexOutOfBounds"])
    abort()
}

func triggerTypeCastCrash() {
    recordError(type: "CrashSimulation", message: "Triggering Type Cast crash",
                attributes: ["crash.type": "TypeCast"])
    abort()
}
```

### Step 6.2: Add the Crash Simulation UI to ProfileView

The Profile tab **Crash Simulation** section displays a 3-second countdown before calling the relevant crash method:

```swift
// ProfileView.swift

enum CrashType: String, CaseIterable {
    case runtime         = "Runtime Exception"
    case nullPointer     = "Null Pointer"
    case indexOutOfBounds = "Index Out of Bounds"
    case typeCast        = "Type Cast"
}

@State private var selectedCrashType: CrashType = .runtime
@State private var showCrashAlert     = false
@State private var showCrashCountdown = false
@State private var crashCountdown     = 3

// Confirmation alert
.alert("\(selectedCrashType.rawValue) Crash", isPresented: $showCrashAlert) {
    Button("Crash App", role: .destructive) { startCrashCountdown() }
    Button("Cancel",    role: .cancel) {}
} message: {
    Text("WARNING: This will crash the app. You will need to restart it.")
}

// Countdown overlay
private func startCrashCountdown() {
    crashCountdown = 3
    showCrashCountdown = true
    Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { timer in
        if crashCountdown > 1 {
            crashCountdown -= 1
        } else {
            timer.invalidate()
            triggerCrash(type: selectedCrashType)
        }
    }
}

private func triggerCrash(type: CrashType) {
    switch type {
    case .runtime:          SplunkManager.shared.triggerRuntimeExceptionCrash()
    case .nullPointer:      SplunkManager.shared.triggerNullPointerCrash()
    case .indexOutOfBounds: SplunkManager.shared.triggerIndexOutOfBoundsCrash()
    case .typeCast:         SplunkManager.shared.triggerTypeCastCrash()
    }
}
```

### Step 6.3: Crash Types Reference

| Crash Type | `crash.type` Attribute | Termination |
|------------|----------------------|-------------|
| Runtime Exception | `RuntimeException` | `abort()` |
| Null Pointer | `NullPointer` | `abort()` |
| Index Out of Bounds | `IndexOutOfBounds` | `abort()` |
| Type Cast | `TypeCast` | `abort()` |

Each crash sends a `CrashSimulation` error span to Splunk before calling `abort()`, so the crash appears in both **RUM > Errors** and the **Session Replay** recording.

---

## Part 7 — Event Tracking

Event tracking records discrete user actions and app state changes as named spans. Unlike workflow spans, events are fire-and-forget.

### Step 7.1: Add the `addEvent` Method to SplunkManager

```swift
// MARK: - Custom Event Tracking

func addEvent(_ name: String, attributes: [String: String] = [:], workflow: String? = nil) {
    guard isInitialized else { return }
    spanCount += 1
    #if canImport(SplunkAgent)
    let tracer = OpenTelemetry.instance.tracerProvider.get(
        instrumentationName: "AstronomyShop",
        instrumentationVersion: "1.0.0"
    )
    let span = tracer.spanBuilder(spanName: name).startSpan()
    // workflow.name is required for the event to appear in Splunk UI
    span.setAttribute(key: "workflow.name", value: .string(workflow ?? name))
    span.setAttribute(key: "view.name",     value: .string(currentScreenName))
    for (key, value) in attributes {
        span.setAttribute(key: key, value: .string(value))
    }
    span.end()
    #endif
}
```

### Step 7.2: Add User Identity Helpers

```swift
// MARK: - User Identity

func setUserId(_ userId: String) {
    guard isInitialized else { return }
    #if canImport(SplunkAgent)
    SplunkRum.shared.globalAttributes[string: "enduser.id"] = userId
    #endif
    addEvent("UserIdentified", attributes: ["user.id": userId])
}

func clearUserId() {
    guard isInitialized else { return }
    #if canImport(SplunkAgent)
    SplunkRum.shared.globalAttributes[string: "enduser.id"] = nil
    #endif
    addEvent("UserCleared")
}
```

### Step 7.3: Usage Examples Throughout the App

**CartView — when user clears the entire cart:**
```swift
Button(action: { showClearCartAlert = true }) { ... }

// On confirm:
SplunkManager.shared.addEvent("CartCleared", attributes: [
    "itemCount": String(cartViewModel.itemCount)
])
cartViewModel.clearCart()
```

**CartView — when a specific item is removed:**
```swift
private func removeItem() {
    SplunkManager.shared.addEvent("CartItemRemoved", attributes: [
        "product.id":   String(item.product.id),
        "product.name": item.product.name
    ])
    cartViewModel.removeFromCart(item)
}
```

**Slow network simulation:**
```swift
SplunkManager.shared.addEvent("SlowLoadingStarted", attributes: [
    "delay": "5000ms",
    "type":  "network_simulation"
])
```

**Associating an event with a named workflow:**
```swift
SplunkManager.shared.addEvent("FilterApplied",
    attributes: ["category": "Telescopes"],
    workflow: "ProductSearch"   // groups this event under the ProductSearch workflow
)
```

### Step 7.4: Clear Tracking Data

Add this utility to `SplunkManager` for the Profile tab's **Reset All** button:

```swift
func clearTrackingData() {
    spanCount  = 0
    errorCount = 0
    lastError  = nil
}
```

Used in `ProfileView`:
```swift
private func clearAllData() {
    productViewModel.clearError()
    cartViewModel.clearError()
    SplunkManager.shared.clearTrackingData()
    productViewModel.loadProducts()
}
```

---

## Configuration Reference

All flags are in `AstronomyShop/Utils/SplunkConfiguration.swift`:

| Property | Current Value | Description |
|----------|---------------|-------------|
| `rumAccessTokenUS1` | *(your token)* | RUM token for US1 realm |
| `rumAccessTokenEU0` | *(your token)* | RUM token for EU0 realm |
| `environment` | `"development"` | Deployment environment tag |
| `sessionReplayEnabled` | `true` | Start Session Replay on launch |
| `debugLoggingEnabled` | `true` | Verbose SDK console output |
| `samplingRate` | `1.0` | Session sampling rate (0.0–1.0) |
| `enableNavigationTracking` | `true` | Auto-track navigation events |
| `enableCrashReporting` | `true` | Capture crash reports |
| `enableNetworkInstrumentation` | `true` | Auto-instrument network calls |
| `enableInteractionTracking` | `true` | Track user taps |
| `enableSlowRenderingDetection` | `true` | Detect slow frame renders |

---

## Viewing Data in Splunk

1. Go to [Splunk Observability Cloud](https://app.signalfx.com)
2. Navigate to **RUM** in the left sidebar
3. Select your app (`AstronomyShop-iOS-us1` or `AstronomyShop-iOS-eu0`)

| Section | What You'll See |
|---------|----------------|
| **Sessions** | Full user session timelines with all spans |
| **Session Replay** | Visual playback of user sessions |
| **Errors** | All `recordError` calls with type, message, and attributes |
| **Tag Spotlight** | Filter by `workflow.name`, `view.name`, `app.version` |
| **Workflows** | Funnel analysis for AddToCart, PlaceOrder, ProductSearch |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `"Configuration invalid"` in console | Token still contains `YOUR_` — update `SplunkConfiguration.swift` |
| SDK not initialising | Verify SplunkAgent is linked to the target under **Build Phases > Link Binary With Libraries** |
| Data not in Splunk | Allow 2 min for first data; verify realm selection matches the token's organisation |
| Replay not recording | Confirm `sessionReplayEnabled = true` and `isInitialized = true` (check console) |
| Realm switch not applying | Tap **Restart Now** in the prompt — the SDK cannot reinitialise mid-session |
| Spans missing `workflow.name` | Always pass `workflow.name` attribute — it is required for Splunk UI visibility |

---

## SDK Version

| Version | Notes |
|---------|-------|
| **2.0.6** | Current — stable release with Session Replay |
| 2.0.0 | Initial 2.x release; renamed to `SplunkAgent`, added Session Replay |
| 0.x | Legacy `SplunkOtel` package — deprecated, do not use |

---

## Resources

- [Splunk RUM iOS Documentation](https://help.splunk.com/en/splunk-observability-cloud/manage-data/instrument-front-end-applications/instrument-mobile-and-web-applications-for-splunk-rum/instrument-ios-applications-for-splunk-rum)
- [GitHub: signalfx/splunk-otel-ios](https://github.com/signalfx/splunk-otel-ios)
- [Session Replay Documentation](https://help.splunk.com/en/splunk-observability-cloud/monitor-end-user-experience/real-user-monitoring/replay-user-sessions)
- [OpenTelemetry Swift](https://github.com/open-telemetry/opentelemetry-swift)

---

*Updated February 2026 — Full step-by-step instrumentation guide based on AstronomyShop implementation.*

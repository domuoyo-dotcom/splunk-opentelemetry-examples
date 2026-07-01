export function extractTraceCorrelation(serverTiming, span) {
    if (!serverTiming) return;

    const traceParentMatch = serverTiming.match(/traceparent;desc="([^"]+)"/);
    if (traceParentMatch) {
        const traceParent = traceParentMatch[1];
        const parts = traceParent.split('-');
        if (parts.length >= 3) {
            span.setAttribute('link.traceId', parts[1]);
            span.setAttribute('link.spanId', parts[2]);
        }
    }
}

export const serverTimingPlugin = {
    async requestDidStart(requestContext) {
        return {
            async willSendResponse({ contextValue }) {
                const currentSpan = contextValue.otelSpan;

                if (currentSpan) {
                    currentSpan.setAttribute(
                        'graphql.operationName',
                        requestContext.request.operationName || 'anonymous'
                    );

                    const spanContext = currentSpan.spanContext();
                    const { traceId, spanId, traceFlags } = spanContext;

                    if (traceId && spanId) {
                        const flags = (traceFlags & 1) === 1 ? '01' : '00';
                        const serverTimingValue = `traceparent;desc="00-${traceId}-${spanId}-${flags}"`;

                        if (contextValue.res && typeof contextValue.res.setHeader === 'function') {
                            contextValue.res.setHeader('Server-Timing', serverTimingValue);
                            contextValue.res.setHeader(
                                'Access-Control-Expose-Headers',
                                'Server-Timing'
                            );
                        }
                    }

                    currentSpan.end();
                }
            },
        };
    },
};

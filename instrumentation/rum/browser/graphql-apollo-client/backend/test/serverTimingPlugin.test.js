import test from 'node:test';
import assert from 'node:assert/strict';
import { serverTimingPlugin } from '../serverTimingPlugin.js';

test('willSendResponse sets Server-Timing header from active span', async () => {
    const headers = {};
    const res = {
        setHeader(name, value) {
            headers[name] = value;
        },
    };
    const span = {
        attributes: {},
        setAttribute(name, value) {
            this.attributes[name] = value;
        },
        spanContext() {
            return {
                traceId: '4bf92f3577b34da6a3ce929d0e0e4736',
                spanId: '00f067aa0ba902b7',
                traceFlags: 1,
            };
        },
        end() {},
    };

    const requestContext = { request: { operationName: 'GetBooks' } };
    const listener = await serverTimingPlugin.requestDidStart(requestContext);

    await listener.willSendResponse({
        response: {},
        contextValue: { res, otelSpan: span },
    });

    assert.equal(span.attributes['graphql.operationName'], 'GetBooks');
    assert.equal(
        headers['Server-Timing'],
        'traceparent;desc="00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"'
    );
    assert.equal(headers['Access-Control-Expose-Headers'], 'Server-Timing');
});

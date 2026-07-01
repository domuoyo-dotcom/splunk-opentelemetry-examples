import { describe, expect, it, vi } from "vitest";
import { extractTraceCorrelation } from "../graphqlTracing";

describe("extractTraceCorrelation", () => {
    it("sets trace link attributes from Server-Timing header", () => {
        const span = {
            setAttribute: vi.fn(),
        };

        extractTraceCorrelation(
            'traceparent;desc="00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"',
            span
        );

        expect(span.setAttribute).toHaveBeenCalledWith(
            "link.traceId",
            "4bf92f3577b34da6a3ce929d0e0e4736"
        );
        expect(span.setAttribute).toHaveBeenCalledWith("link.spanId", "00f067aa0ba902b7");
    });

    it("ignores missing Server-Timing header", () => {
        const span = {
            setAttribute: vi.fn(),
        };

        extractTraceCorrelation(undefined, span);

        expect(span.setAttribute).not.toHaveBeenCalled();
    });
});

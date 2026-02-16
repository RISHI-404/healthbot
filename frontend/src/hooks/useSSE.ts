import { useCallback, useRef, useState } from 'react';

interface SSEOptions {
    onToken: (token: string) => void;
    onDone: () => void;
    onError?: (error: string) => void;
    onHeaders?: (headers: Headers) => void;
}

export function useSSE() {
    const [isStreaming, setIsStreaming] = useState(false);
    const abortControllerRef = useRef<AbortController | null>(null);

    const startStream = useCallback(async (
        url: string,
        body: object,
        options: SSEOptions,
    ) => {
        setIsStreaming(true);
        abortControllerRef.current = new AbortController();

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body),
                signal: abortControllerRef.current.signal,
                credentials: 'include',
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `HTTP ${response.status}`);
            }

            // Pass headers to caller
            if (options.onHeaders && response.headers) {
                options.onHeaders(response.headers);
            }

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();

            if (!reader) throw new Error('No response body');

            let buffer = '';
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.done) {
                                options.onDone();
                            } else if (data.token) {
                                options.onToken(data.token);
                            }
                        } catch {
                            // Skip malformed JSON
                        }
                    }
                }
            }
        } catch (err: any) {
            if (err.name !== 'AbortError') {
                options.onError?.(err.message || 'Streaming failed');
            }
        } finally {
            setIsStreaming(false);
            abortControllerRef.current = null;
        }
    }, []);

    const abort = useCallback(() => {
        abortControllerRef.current?.abort();
        setIsStreaming(false);
    }, []);

    return { isStreaming, startStream, abort };
}

import React, { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';

interface Props {
    onSend: (message: string) => void;
    onAbort: () => void;
    isStreaming: boolean;
    disabled: boolean;
}

export default function ChatInput({ onSend, onAbort, isStreaming, disabled }: Props) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const autoResize = () => {
        const el = textareaRef.current;
        if (el) { el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 150) + 'px'; }
    };

    useEffect(() => { textareaRef.current?.focus(); }, []);

    const handleSubmit = () => {
        const val = textareaRef.current?.value.trim();
        if (!val || disabled || isStreaming) return;
        onSend(val);
        if (textareaRef.current) { textareaRef.current.value = ''; textareaRef.current.style.height = 'auto'; }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
    };

    return (
        <div className="p-4 max-w-3xl mx-auto w-full">
            <div className="flex items-end gap-3 bg-white dark:bg-[#1e293b] rounded-2xl border border-slate-200 dark:border-slate-700/60 px-4 py-2 focus-within:border-indigo-400/60 focus-within:ring-1 focus-within:ring-indigo-400/20 transition-all duration-200 shadow-sm">
                <textarea
                    ref={textareaRef}
                    rows={1}
                    placeholder="Ask me anything about health..."
                    onInput={autoResize}
                    onKeyDown={handleKeyDown}
                    disabled={disabled}
                    className="flex-1 bg-transparent text-[15px] text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 resize-none focus:outline-none py-2 max-h-[150px]"
                />

                {isStreaming ? (
                    <motion.button
                        whileTap={{ scale: 0.85 }}
                        onClick={onAbort}
                        className="flex-shrink-0 w-10 h-10 rounded-xl bg-red-50 dark:bg-red-500/20 text-red-500 dark:text-red-400 flex items-center justify-center hover:bg-red-100 dark:hover:bg-red-500/30 transition-colors"
                    >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </motion.button>
                ) : (
                    <motion.button
                        whileTap={{ scale: 0.85 }}
                        onClick={handleSubmit}
                        className="flex-shrink-0 w-10 h-10 rounded-xl bg-indigo-500 text-white flex items-center justify-center hover:bg-indigo-600 hover:shadow-lg transition-all duration-200"
                    >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M12 5l7 7-7 7" />
                        </svg>
                    </motion.button>
                )}
            </div>
        </div>
    );
}

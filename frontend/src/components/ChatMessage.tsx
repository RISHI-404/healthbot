import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { ChatMessage as ChatMessageType } from '../types';
import ReactMarkdown from 'react-markdown';

interface Props {
    message: ChatMessageType;
}

function StaggeredMarkdown({ content }: { content: string }) {
    const paragraphs = useMemo(() => content.split(/\n{2,}/).filter(p => p.trim()), [content]);
    return (
        <>
            {paragraphs.map((p, i) => (
                <motion.div key={i} initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.25, delay: i * 0.05, ease: [0.16, 1, 0.3, 1] }}>
                    <ReactMarkdown>{p}</ReactMarkdown>
                </motion.div>
            ))}
        </>
    );
}

export default function ChatMessage({ message }: Props) {
    const isUser = message.role === 'user';
    const time = new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className={`flex gap-3 mb-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
        >
            {/* Avatar */}
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${isUser
                ? 'bg-indigo-500 text-white'
                : 'bg-slate-100 dark:bg-slate-800 text-indigo-500 ring-1 ring-slate-200 dark:ring-slate-700'
                }`}>
                {isUser ? 'U' : 'AI'}
            </div>

            {/* Bubble */}
            <div className={`max-w-[65%] flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
                <div className={`text-[15px] leading-relaxed ${isUser
                    ? 'bubble-user'
                    : message.is_emergency
                        ? 'bubble-ai emergency-bubble'
                        : 'bubble-ai prose-custom'
                    }`}>
                    {isUser ? (
                        <div className="whitespace-pre-wrap">{message.content}</div>
                    ) : (
                        <StaggeredMarkdown content={message.content} />
                    )}
                </div>
                <span className="text-[10px] text-slate-400 dark:text-slate-600 mt-1 px-1">{time}</span>
            </div>
        </motion.div>
    );
}

export function TypingIndicator() {
    return (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex gap-3 mb-4">
            <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-xs font-bold text-indigo-500 ring-1 ring-slate-200 dark:ring-slate-700">
                AI
            </div>
            <div className="bubble-ai">
                <div className="flex items-center gap-1.5 h-5">
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                </div>
            </div>
        </motion.div>
    );
}

export function StreamingMessage({ content }: { content: string }) {
    return (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex gap-3 mb-4">
            <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-xs font-bold text-indigo-500 ring-1 ring-slate-200 dark:ring-slate-700">
                AI
            </div>
            <div className="max-w-[65%]">
                <div className="bubble-ai prose-custom">
                    <ReactMarkdown>{content}</ReactMarkdown>
                    <span className="streaming-caret"></span>
                </div>
            </div>
        </motion.div>
    );
}

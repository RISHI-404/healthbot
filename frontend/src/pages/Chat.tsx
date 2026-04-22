import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSSE } from '../hooks/useSSE';
import api from '../api/client';
import { Conversation, ChatMessage as ChatMessageType } from '../types';
import ChatMessage, { TypingIndicator, StreamingMessage } from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';

interface Props {
    conversations: Conversation[];
    activeConvId: number | null;
    setActiveConvId: (id: number | null) => void;
    onConversationsChange: () => void;
}

export default function Chat({ conversations, activeConvId, setActiveConvId, onConversationsChange }: Props) {
    const { isStreaming, startStream, abort } = useSSE();

    const [messages, setMessages] = useState<ChatMessageType[]>([]);
    const [streamingContent, setStreamingContent] = useState('');

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });

    useEffect(() => { scrollToBottom(); }, [messages, streamingContent]);

    useEffect(() => {
        if (activeConvId) { loadMessages(activeConvId); }
        else { setMessages([]); }
    }, [activeConvId]);

    const loadMessages = async (convId: number) => {
        try {
            const res = await api.get(`/chat/conversations/${convId}`);
            setMessages(res.data.messages || []);
        } catch { }
    };

    const handleSend = async (message: string) => {
        const userMsg: ChatMessageType = {
            id: Date.now(), role: 'user', content: message,
            is_emergency: false, created_at: new Date().toISOString(),
        };
        setMessages(prev => [...prev, userMsg]);
        setStreamingContent('');

        const apiBase = import.meta.env.VITE_API_URL || '';
        await startStream(`${apiBase}/api/chat/send`, { message, conversation_id: activeConvId }, {
            onToken: (token) => setStreamingContent(prev => prev + token),
            onDone: () => {
                setStreamingContent(prev => {
                    const assistantMsg: ChatMessageType = {
                        id: Date.now() + 1, role: 'assistant', content: prev,
                        is_emergency: false, created_at: new Date().toISOString(),
                    };
                    setMessages(msgs => [...msgs, assistantMsg]);
                    return '';
                });
                onConversationsChange();
            },
            onHeaders: (headers) => {
                const convId = headers.get('X-Conversation-Id');
                if (convId && !activeConvId) setActiveConvId(parseInt(convId));
            },
            onError: (err) => {
                setMessages(prev => [...prev, {
                    id: Date.now() + 1, role: 'assistant',
                    content: `Sorry, something went wrong: ${err}`,
                    is_emergency: false, created_at: new Date().toISOString(),
                }]);
            },
        });
    };

    const hasMessages = messages.length > 0 || isStreaming;

    const suggestions = [
        { emoji: '🦠', text: 'Flu vs COVID symptoms?', query: "What are standard flu symptoms vs COVID-19?" },
        { emoji: '🥗', text: 'Heart-healthy meal plan', query: "Give me a 3-day heart-healthy meal plan." },
        { emoji: '🧘', text: 'Natural stress relief', query: "How can I reduce stress and anxiety naturally?" },
        { emoji: '❤️', text: 'Explain high blood pressure', query: "Explain high blood pressure like I'm 5." },
    ];

    return (
        <div className="flex-1 flex flex-col min-w-0 h-full bg-white dark:bg-gradient-to-b dark:from-[#0a0f1a] dark:to-[#0f172a]">
            <div className="flex-1 overflow-y-auto">
                {!hasMessages ? (
                    /* ===== WELCOME ===== */
                    <div className="flex flex-col items-center justify-center h-full text-center px-4">
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ type: 'spring', stiffness: 200, delay: 0.05 }}
                            className="mb-6"
                        >
                            <div className="w-16 h-16 rounded-2xl gradient-icon-bg flex items-center justify-center shadow-lg shadow-teal-500/20">
                                <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                                    <path strokeLinecap="round" strokeLinejoin="round"
                                        d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                                </svg>
                            </div>
                        </motion.div>

                        <motion.h1
                            initial={{ opacity: 0, y: 12 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.15 }}
                            className="text-2xl md:text-3xl font-bold text-slate-800 dark:text-white mb-3"
                        >
                            How can I help you today?
                        </motion.h1>

                        <motion.p
                            initial={{ opacity: 0, y: 8 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.25 }}
                            className="text-slate-500 dark:text-slate-400 mb-10 max-w-md"
                        >
                            Ask about symptoms, wellness tips, or medical terms.
                        </motion.p>

                        {/* Suggestion grid */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full">
                            {suggestions.map((s, i) => (
                                <motion.button
                                    key={i}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.3 + i * 0.05 }}
                                    whileHover={{ y: -2 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={() => handleSend(s.query)}
                                    className="suggestion-card"
                                >
                                    <span className="text-lg">{s.emoji}</span>
                                    {s.text}
                                </motion.button>
                            ))}
                        </div>
                    </div>
                ) : (
                    /* ===== MESSAGES ===== */
                    <div className="max-w-3xl mx-auto w-full p-4">
                        <AnimatePresence>
                            {messages.map((msg) => (
                                <ChatMessage key={msg.id} message={msg} />
                            ))}
                        </AnimatePresence>
                        {isStreaming && streamingContent && <StreamingMessage content={streamingContent} />}
                        {isStreaming && !streamingContent && <TypingIndicator />}
                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            <ChatInput onSend={handleSend} onAbort={abort} isStreaming={isStreaming} disabled={false} />
        </div>
    );
}

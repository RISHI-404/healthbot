import React, { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useLocation } from 'react-router-dom';
import { Conversation } from '../types';

interface Props {
    conversations: Conversation[];
    activeId: number | null;
    onSelect: (id: number) => void;
    onDelete: (id: number) => void;
    isOpen: boolean;
    onToggle: () => void;
}

interface GroupedConversations { label: string; conversations: Conversation[]; }

function groupByDate(convs: Conversation[]): GroupedConversations[] {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today); yesterday.setDate(yesterday.getDate() - 1);
    const week = new Date(today); week.setDate(week.getDate() - 7);
    const month = new Date(today); month.setDate(month.getDate() - 30);

    const g: Record<string, Conversation[]> = { 'Today': [], 'Yesterday': [], 'Previous 7 Days': [], 'Previous 30 Days': [], 'Older': [] };
    for (const c of convs) {
        const d = new Date(c.updated_at || c.created_at);
        if (d >= today) g['Today'].push(c);
        else if (d >= yesterday) g['Yesterday'].push(c);
        else if (d >= week) g['Previous 7 Days'].push(c);
        else if (d >= month) g['Previous 30 Days'].push(c);
        else g['Older'].push(c);
    }
    return Object.entries(g).filter(([, v]) => v.length > 0).map(([label, conversations]) => ({ label, conversations }));
}

/* HealthBot SVG Logo */
function Logo() {
    return (
        <svg width="36" height="36" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="40" height="40" rx="12" fill="url(#lg)" />
            <path d="M10 14C10 11.79 11.79 10 14 10H26C28.21 10 30 11.79 30 14V22C30 24.21 28.21 26 26 26H18L13 30V26H14C11.79 26 10 24.21 10 22V14Z"
                fill="white" fillOpacity="0.95" />
            <rect x="18" y="13" width="4" height="12" rx="1.5" fill="#4f46e5" />
            <rect x="14" y="17" width="12" height="4" rx="1.5" fill="#4f46e5" />
            <defs>
                <linearGradient id="lg" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
                    <stop stopColor="#6366f1" />
                    <stop offset="1" stopColor="#4f46e5" />
                </linearGradient>
            </defs>
        </svg>
    );
}

export default function Sidebar({ conversations, activeId, onSelect, onDelete, isOpen, onToggle }: Props) {
    const grouped = useMemo(() => groupByDate(conversations), [conversations]);
    const location = useLocation();

    const navItems = [
        {
            to: '/', label: 'Chat', icon: (
                <svg className="w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                    <path strokeLinecap="round" strokeLinejoin="round"
                        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
            )
        },
        {
            to: '/symptoms', label: 'Symptoms', icon: (
                <svg className="w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                    <path strokeLinecap="round" strokeLinejoin="round"
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
            )
        },
    ];

    const content = (
        <div className="flex flex-col h-full">
            {/* Logo + brand */}
            <div className="px-4 pt-5 pb-4 flex items-center gap-3 border-b border-slate-200 dark:border-slate-800/60">
                <Logo />
                <div>
                    <h1 className="font-bold text-[15px] text-slate-800 dark:text-white leading-tight">HealthBot</h1>
                    <p className="text-[10px] text-slate-400 dark:text-slate-500 font-semibold uppercase tracking-widest">AI Assistant</p>
                </div>
            </div>

            {/* Navigation */}
            <div className="px-3 pt-4 space-y-0.5">
                {navItems.map((item) => {
                    const active = location.pathname === item.to;
                    return (
                        <Link key={item.to} to={item.to} onClick={() => { if (window.innerWidth < 768) onToggle(); }}
                            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] font-medium transition-all duration-200 ${active
                                ? 'bg-indigo-50 dark:bg-indigo-500/15 text-indigo-600 dark:text-indigo-400'
                                : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-700 dark:hover:text-slate-200'
                                }`}>
                            {item.icon}
                            {item.label}
                        </Link>
                    );
                })}
            </div>

            {/* Divider + History label */}
            <div className="px-4 pt-5 pb-1">
                <p className="text-[10px] font-semibold text-slate-400 dark:text-slate-600 uppercase tracking-widest">History</p>
            </div>

            {/* History list */}
            <div className="flex-1 overflow-y-auto px-2 pb-4">
                {conversations.length === 0 ? (
                    <p className="text-center text-[12px] text-slate-400 dark:text-slate-600 py-8">No conversations yet</p>
                ) : (
                    grouped.map((group) => (
                        <div key={group.label} className="mb-1">
                            <p className="px-3 pt-3 pb-1 text-[10px] font-semibold text-slate-300 dark:text-slate-600 uppercase tracking-wider">
                                {group.label}
                            </p>
                            {group.conversations.map((conv) => (
                                <div key={conv.id}
                                    className={`group flex items-center gap-2 px-3 py-1.5 rounded-lg cursor-pointer transition-all duration-150 ${activeId === conv.id
                                        ? 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-white'
                                        : 'text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60 hover:text-slate-700 dark:hover:text-slate-300'
                                        }`}
                                    onClick={() => { onSelect(conv.id); if (window.innerWidth < 768) onToggle(); }}>
                                    <span className="flex-1 text-[13px] truncate">{conv.title}</span>
                                    <button
                                        onClick={(e) => { e.stopPropagation(); onDelete(conv.id); }}
                                        className="opacity-0 group-hover:opacity-100 p-0.5 rounded text-slate-400 hover:text-red-500 transition-all">
                                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                            <path strokeLinecap="round" strokeLinejoin="round"
                                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                        </svg>
                                    </button>
                                </div>
                            ))}
                        </div>
                    ))
                )}
            </div>
        </div>
    );

    return (
        <>
            {/* Overlay */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/30 backdrop-blur-sm z-30 md:hidden" onClick={onToggle} />
                )}
            </AnimatePresence>

            {/* Sidebar panel */}
            <AnimatePresence>
                {isOpen && (
                    <motion.aside
                        initial={{ x: -280 }} animate={{ x: 0 }} exit={{ x: -280 }}
                        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                        className="fixed z-40 top-0 left-0 bottom-0 w-[260px] bg-white dark:bg-[#0f172a] border-r border-slate-200 dark:border-slate-800/60 flex flex-col shadow-xl">
                        {content}
                    </motion.aside>
                )}
            </AnimatePresence>
        </>
    );
}

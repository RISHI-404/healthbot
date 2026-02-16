import React from 'react';
import { useTheme } from '../context/ThemeContext';
import { motion, AnimatePresence } from 'framer-motion';

interface Props {
    onToggleSidebar: () => void;
    onNewChat: () => void;
}

export default function Navbar({ onToggleSidebar, onNewChat }: Props) {
    const { isDark, toggle } = useTheme();

    return (
        <nav className="h-14 flex items-center justify-between px-4 border-b bg-white dark:bg-[#0f172a] border-slate-200 dark:border-slate-800/60 flex-shrink-0">
            {/* Left: sidebar toggle */}
            <button
                onClick={onToggleSidebar}
                className="p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
            </button>

            {/* Right: New Chat + Dark Mode */}
            <div className="flex items-center gap-2">
                {/* New Chat */}
                <button onClick={onNewChat} className="btn-new-chat text-[13px] py-1.5 px-3.5 rounded-lg">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                    </svg>
                    New Chat
                </button>

                {/* Dark Mode Toggle */}
                <motion.button
                    whileTap={{ scale: 0.85 }}
                    onClick={toggle}
                    className="p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                    aria-label="Toggle dark mode"
                >
                    <AnimatePresence mode="wait" initial={false}>
                        {isDark ? (
                            <motion.svg key="sun" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }} transition={{ duration: 0.15 }}
                                className="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round"
                                    d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                            </motion.svg>
                        ) : (
                            <motion.svg key="moon" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }} transition={{ duration: 0.15 }}
                                className="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round"
                                    d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                            </motion.svg>
                        )}
                    </AnimatePresence>
                </motion.button>
            </div>
        </nav>
    );
}

import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import api from './api/client';
import { Conversation } from './types';

import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Chat from './pages/Chat';
import SymptomChecker from './pages/SymptomChecker';
import Dashboard from './pages/Dashboard';

function AppContent() {
    const navigate = useNavigate();
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [activeConvId, setActiveConvId] = useState<number | null>(null);
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const loadConversations = useCallback(async () => {
        try {
            const res = await api.get('/chat/conversations');
            setConversations(res.data);
        } catch { }
    }, []);

    useEffect(() => { loadConversations(); }, [loadConversations]);

    const handleNewChat = () => {
        setActiveConvId(null);
        setSidebarOpen(false);
        navigate('/');
    };

    const handleSelectConv = (id: number) => {
        setActiveConvId(id);
        setSidebarOpen(false);
        navigate('/');
    };

    const handleDeleteConv = async (id: number) => {
        try {
            await api.delete(`/chat/conversations/${id}`);
            setConversations(prev => prev.filter(c => c.id !== id));
            if (activeConvId === id) setActiveConvId(null);
        } catch { }
    };

    return (
        <div className="h-screen flex flex-col bg-slate-50 dark:bg-[#0b1120]">
            {/* Top bar */}
            <Navbar
                onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
                onNewChat={handleNewChat}
            />

            {/* Body */}
            <div className="flex flex-1 overflow-hidden relative">
                <Sidebar
                    conversations={conversations}
                    activeId={activeConvId}
                    onSelect={handleSelectConv}
                    onDelete={handleDeleteConv}
                    isOpen={sidebarOpen}
                    onToggle={() => setSidebarOpen(false)}
                />

                <div className="flex-1 flex flex-col min-w-0">
                    <Routes>
                        <Route path="/" element={
                            <Chat
                                conversations={conversations}
                                activeConvId={activeConvId}
                                setActiveConvId={setActiveConvId}
                                onConversationsChange={loadConversations}
                            />
                        } />
                        <Route path="/symptoms" element={<SymptomChecker />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="*" element={<Navigate to="/" />} />
                    </Routes>
                </div>
            </div>
        </div>
    );
}

export default function App() {
    return (
        <BrowserRouter>
            <ThemeProvider>
                <AppContent />
            </ThemeProvider>
        </BrowserRouter>
    );
}

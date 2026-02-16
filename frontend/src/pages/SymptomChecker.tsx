import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../api/client';
import { SymptomQuestion, SymptomResult } from '../types';

export default function SymptomChecker() {
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [currentQuestion, setCurrentQuestion] = useState<SymptomQuestion | null>(null);
    const [result, setResult] = useState<SymptomResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [step, setStep] = useState(0);

    const startCheck = async () => {
        setLoading(true); setResult(null); setStep(0);
        try {
            const res = await api.post('/symptoms/start');
            setSessionId(res.data.session_id);
            setCurrentQuestion(res.data);
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Failed to start symptom check');
        } finally { setLoading(false); }
    };

    const handleAnswer = async (optIdx: number) => {
        if (!sessionId) return;
        setLoading(true);
        try {
            const res = await api.post('/symptoms/answer', { session_id: sessionId, option_index: optIdx });
            if (res.data.is_final) { setResult(res.data); setCurrentQuestion(null); setSessionId(null); }
            else { setCurrentQuestion(res.data); setStep(s => s + 1); }
        } catch (err: any) { alert(err.response?.data?.detail || 'Error'); }
        finally { setLoading(false); }
    };

    const reset = () => { setSessionId(null); setCurrentQuestion(null); setResult(null); setStep(0); };

    return (
        <div className="flex-1 overflow-y-auto bg-gradient-to-b from-navy-950 to-navy-900">
            <div className="max-w-2xl mx-auto px-4 py-8">
                <h1 className="text-2xl font-bold text-white mb-2">Symptom Checker</h1>
                <p className="text-navy-400 mb-8">Answer a few questions to get preliminary health guidance.</p>

                {!currentQuestion && !result && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card text-center py-12">
                        <div className="w-20 h-20 mx-auto bg-navy-800 border border-navy-700/50 rounded-3xl flex items-center justify-center mb-6">
                            <svg className="w-10 h-10 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                                <path strokeLinecap="round" strokeLinejoin="round"
                                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                        </div>
                        <h2 className="text-xl font-semibold text-navy-200 mb-3">Start Health Assessment</h2>
                        <p className="text-navy-500 text-sm max-w-sm mx-auto mb-6">
                            I'll ask you a series of questions about your symptoms to provide preliminary guidance.
                        </p>
                        <button onClick={startCheck} disabled={loading} className="btn-primary">
                            {loading ? 'Starting...' : 'Begin Assessment'}
                        </button>
                    </motion.div>
                )}

                <AnimatePresence mode="wait">
                    {currentQuestion && (
                        <motion.div key={step} initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}
                            transition={{ duration: 0.25 }} className="card">
                            <div className="flex items-center gap-2 mb-4">
                                <span className="text-xs font-medium text-brand-500 bg-brand-500/10 px-2.5 py-1 rounded-full">Step {step + 1}</span>
                                <span className="text-xs text-navy-500 capitalize">{currentQuestion.category}</span>
                            </div>
                            <h3 className="text-lg font-semibold text-white mb-6">{currentQuestion.question}</h3>
                            <div className="space-y-3">
                                {currentQuestion.options.map((opt, i) => (
                                    <motion.button key={i} whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}
                                        onClick={() => handleAnswer(i)} disabled={loading}
                                        className="w-full text-left px-4 py-3.5 rounded-xl border border-navy-700 bg-navy-800/50
                                            hover:border-brand-500/40 hover:bg-navy-800
                                            text-sm font-medium text-navy-300 transition-all disabled:opacity-50">
                                        {opt.text}
                                    </motion.button>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {result && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                        <div className="card">
                            <h3 className="text-lg font-semibold text-white mb-4">Assessment Results</h3>
                            {result.result.conditions.length > 0 && (
                                <div className="space-y-3 mb-6">
                                    {result.result.conditions.map((cond, i) => (
                                        <div key={i} className={`p-4 rounded-xl border ${i === 0
                                            ? 'bg-brand-500/10 border-brand-500/30'
                                            : 'bg-navy-800/50 border-navy-700/50'}`}>
                                            <div className="flex items-center justify-between mb-2">
                                                <h4 className="font-semibold text-white capitalize">{cond.name.replace(/_/g, ' ')}</h4>
                                                <span className={`text-sm font-medium px-2 py-0.5 rounded-full ${cond.probability > 50
                                                    ? 'bg-red-500/20 text-red-400'
                                                    : cond.probability > 30
                                                        ? 'bg-yellow-500/20 text-yellow-400'
                                                        : 'bg-green-500/20 text-green-400'}`}>
                                                    {cond.probability}%
                                                </span>
                                            </div>
                                            <p className="text-sm text-navy-400">{cond.description}</p>
                                            <p className="text-sm text-brand-500 mt-2">💡 {cond.recommendation}</p>
                                        </div>
                                    ))}
                                </div>
                            )}
                            <div className={`p-4 rounded-xl ${result.result.urgency === 'high'
                                ? 'bg-red-500/10 border border-red-500/30'
                                : result.result.urgency === 'medium'
                                    ? 'bg-yellow-500/10 border border-yellow-500/30'
                                    : 'bg-green-500/10 border border-green-500/30'}`}>
                                <p className="text-sm font-medium text-white mb-1">Recommendation</p>
                                <p className="text-sm text-navy-400">{result.result.recommendation}</p>
                            </div>
                            <p className="text-xs text-navy-600 mt-4">{result.result.disclaimer}</p>
                        </div>
                        <button onClick={reset} className="btn-secondary w-full">Start New Assessment</button>
                    </motion.div>
                )}
            </div>
        </div>
    );
}

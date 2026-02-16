import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../api/client';
import { Appointment, Medication } from '../types';

export default function Dashboard() {
    const [appointments, setAppointments] = useState<Appointment[]>([]);
    const [medications, setMedications] = useState<Medication[]>([]);
    const [activeTab, setActiveTab] = useState<'appointments' | 'medications'>('appointments');

    // Appointment form
    const [apptTitle, setApptTitle] = useState('');
    const [apptDoctor, setApptDoctor] = useState('');
    const [apptLocation, setApptLocation] = useState('');
    const [apptDate, setApptDate] = useState('');
    const [apptNotes, setApptNotes] = useState('');

    // Medication form
    const [medName, setMedName] = useState('');
    const [medDosage, setMedDosage] = useState('');
    const [medFrequency, setMedFrequency] = useState('');
    const [medTime, setMedTime] = useState('');
    const [medStart, setMedStart] = useState('');
    const [medNotes, setMedNotes] = useState('');

    const [showApptForm, setShowApptForm] = useState(false);
    const [showMedForm, setShowMedForm] = useState(false);

    useEffect(() => {
        loadAppointments();
        loadMedications();
    }, []);

    const loadAppointments = async () => {
        const res = await api.get('/appointments/');
        setAppointments(res.data);
    };

    const loadMedications = async () => {
        const res = await api.get('/medications/');
        setMedications(res.data);
    };

    const handleCreateAppt = async (e: React.FormEvent) => {
        e.preventDefault();
        await api.post('/appointments/', {
            title: apptTitle,
            doctor_name: apptDoctor || null,
            location: apptLocation || null,
            notes: apptNotes || null,
            scheduled_at: new Date(apptDate).toISOString(),
        });
        setApptTitle(''); setApptDoctor(''); setApptLocation(''); setApptDate(''); setApptNotes('');
        setShowApptForm(false);
        loadAppointments();
    };

    const handleDeleteAppt = async (id: number) => {
        await api.delete(`/appointments/${id}`);
        loadAppointments();
    };

    const handleCreateMed = async (e: React.FormEvent) => {
        e.preventDefault();
        await api.post('/medications/', {
            medication_name: medName,
            dosage: medDosage,
            frequency: medFrequency,
            time_of_day: medTime || null,
            notes: medNotes || null,
            start_date: new Date(medStart).toISOString(),
        });
        setMedName(''); setMedDosage(''); setMedFrequency(''); setMedTime(''); setMedStart(''); setMedNotes('');
        setShowMedForm(false);
        loadMedications();
    };

    const handleDeleteMed = async (id: number) => {
        await api.delete(`/medications/${id}`);
        loadMedications();
    };

    return (
        <div className="flex-1 overflow-y-auto">
            <div className="max-w-4xl mx-auto px-4 py-8">
                <h1 className="text-2xl font-bold text-surface-800 dark:text-white mb-6">Dashboard</h1>

                {/* Tabs */}
                <div className="flex gap-2 mb-6">
                    {(['appointments', 'medications'] as const).map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-5 py-2.5 rounded-xl text-sm font-medium transition-colors ${activeTab === tab
                                ? 'bg-primary-600 text-white'
                                : 'bg-surface-100 text-surface-600 hover:bg-surface-200 dark:bg-surface-700 dark:text-surface-400'
                                }`}
                        >
                            {tab === 'appointments' ? '📅 Appointments' : '💊 Medications'}
                        </button>
                    ))}
                </div>

                {/* Appointments Tab */}
                {activeTab === 'appointments' && (
                    <div>
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-semibold text-surface-700 dark:text-surface-300">Your Appointments</h2>
                            <button onClick={() => setShowApptForm(!showApptForm)} className="btn-primary text-sm">
                                + New Appointment
                            </button>
                        </div>

                        <AnimatePresence>
                            {showApptForm && (
                                <motion.form
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    onSubmit={handleCreateAppt}
                                    className="card mb-4 space-y-3"
                                >
                                    <input value={apptTitle} onChange={e => setApptTitle(e.target.value)} className="input-field" placeholder="Appointment Title *" required />
                                    <div className="grid grid-cols-2 gap-3">
                                        <input value={apptDoctor} onChange={e => setApptDoctor(e.target.value)} className="input-field" placeholder="Doctor Name" />
                                        <input value={apptLocation} onChange={e => setApptLocation(e.target.value)} className="input-field" placeholder="Location" />
                                    </div>
                                    <input type="datetime-local" value={apptDate} onChange={e => setApptDate(e.target.value)} className="input-field" required />
                                    <textarea value={apptNotes} onChange={e => setApptNotes(e.target.value)} className="input-field" placeholder="Notes" rows={2} />
                                    <div className="flex gap-2">
                                        <button type="submit" className="btn-primary text-sm">Save</button>
                                        <button type="button" onClick={() => setShowApptForm(false)} className="btn-secondary text-sm">Cancel</button>
                                    </div>
                                </motion.form>
                            )}
                        </AnimatePresence>

                        <div className="space-y-3">
                            {appointments.length === 0 ? (
                                <p className="text-center text-surface-400 py-8">No appointments scheduled</p>
                            ) : (
                                appointments.map((appt) => (
                                    <motion.div key={appt.id} layout initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card flex items-start justify-between">
                                        <div>
                                            <h3 className="font-medium text-surface-800 dark:text-white">{appt.title}</h3>
                                            <p className="text-sm text-surface-500 mt-1">
                                                📅 {new Date(appt.scheduled_at).toLocaleDateString()} at {new Date(appt.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </p>
                                            {appt.doctor_name && <p className="text-sm text-surface-500">👨‍⚕️ {appt.doctor_name}</p>}
                                            {appt.location && <p className="text-sm text-surface-500">📍 {appt.location}</p>}
                                        </div>
                                        <button onClick={() => handleDeleteAppt(appt.id)} className="text-surface-400 hover:text-red-500 transition-colors p-1">
                                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </motion.div>
                                ))
                            )}
                        </div>
                    </div>
                )}

                {/* Medications Tab */}
                {activeTab === 'medications' && (
                    <div>
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-semibold text-surface-700 dark:text-surface-300">Your Medications</h2>
                            <button onClick={() => setShowMedForm(!showMedForm)} className="btn-primary text-sm">
                                + New Medication
                            </button>
                        </div>

                        <AnimatePresence>
                            {showMedForm && (
                                <motion.form
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    onSubmit={handleCreateMed}
                                    className="card mb-4 space-y-3"
                                >
                                    <input value={medName} onChange={e => setMedName(e.target.value)} className="input-field" placeholder="Medication Name *" required />
                                    <div className="grid grid-cols-2 gap-3">
                                        <input value={medDosage} onChange={e => setMedDosage(e.target.value)} className="input-field" placeholder="Dosage (e.g. 500mg) *" required />
                                        <input value={medFrequency} onChange={e => setMedFrequency(e.target.value)} className="input-field" placeholder="Frequency (e.g. twice daily) *" required />
                                    </div>
                                    <div className="grid grid-cols-2 gap-3">
                                        <input value={medTime} onChange={e => setMedTime(e.target.value)} className="input-field" placeholder="Time (e.g. 08:00, 20:00)" />
                                        <input type="date" value={medStart} onChange={e => setMedStart(e.target.value)} className="input-field" required />
                                    </div>
                                    <textarea value={medNotes} onChange={e => setMedNotes(e.target.value)} className="input-field" placeholder="Notes" rows={2} />
                                    <div className="flex gap-2">
                                        <button type="submit" className="btn-primary text-sm">Save</button>
                                        <button type="button" onClick={() => setShowMedForm(false)} className="btn-secondary text-sm">Cancel</button>
                                    </div>
                                </motion.form>
                            )}
                        </AnimatePresence>

                        <div className="space-y-3">
                            {medications.length === 0 ? (
                                <p className="text-center text-surface-400 py-8">No medications added</p>
                            ) : (
                                medications.map((med) => (
                                    <motion.div key={med.id} layout initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card flex items-start justify-between">
                                        <div>
                                            <h3 className="font-medium text-surface-800 dark:text-white">{med.medication_name}</h3>
                                            <p className="text-sm text-surface-500 mt-1">💊 {med.dosage} — {med.frequency}</p>
                                            {med.time_of_day && <p className="text-sm text-surface-500">⏰ {med.time_of_day}</p>}
                                            <p className="text-sm text-surface-500">📅 From {new Date(med.start_date).toLocaleDateString()}</p>
                                        </div>
                                        <button onClick={() => handleDeleteMed(med.id)} className="text-surface-400 hover:text-red-500 transition-colors p-1">
                                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </motion.div>
                                ))
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

/** @type {import('tailwindcss').Config} */
export default {
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                navy: {
                    950: '#0b1120',
                    900: '#0f172a',
                    800: '#1e293b',
                    700: '#334155',
                    600: '#475569',
                    500: '#64748b',
                    400: '#94a3b8',
                    300: '#cbd5e1',
                    200: '#e2e8f0',
                },
                brand: {
                    500: '#6366f1',
                    600: '#4f46e5',
                    700: '#4338ca',
                    glow: 'rgba(99, 102, 241, 0.35)',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            boxShadow: {
                'glow-brand': '0 0 20px rgba(99, 102, 241, 0.3)',
                'glow-brand-lg': '0 0 30px rgba(99, 102, 241, 0.4)',
                'card': '0 2px 8px rgba(0,0,0,0.2)',
            },
            keyframes: {
                'float': {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-6px)' },
                },
            },
            animation: {
                'float': 'float 4s ease-in-out infinite',
            },
        },
    },
    plugins: [],
};

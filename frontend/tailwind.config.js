/** @type {import('tailwindcss').Config} */
export default {
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                navy: {
                    950: '#0a0f1a',
                    900: '#0f172a',
                    800: '#1a2332',
                    700: '#283548',
                    600: '#3a4d63',
                    500: '#64748b',
                    400: '#94a3b8',
                    300: '#cbd5e1',
                    200: '#e2e8f0',
                },
                brand: {
                    400: '#2dd4bf',
                    500: '#14b8a6',
                    600: '#0d9488',
                    700: '#0f766e',
                    glow: 'rgba(20, 184, 166, 0.35)',
                },
                accent: {
                    400: '#34d399',
                    500: '#10b981',
                    600: '#059669',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            boxShadow: {
                'glow-brand': '0 0 20px rgba(20, 184, 166, 0.3)',
                'glow-brand-lg': '0 0 30px rgba(20, 184, 166, 0.4)',
                'glow-accent': '0 0 20px rgba(16, 185, 129, 0.3)',
                'card': '0 2px 8px rgba(0,0,0,0.08)',
                'card-dark': '0 2px 16px rgba(0,0,0,0.4)',
            },
            keyframes: {
                'float': {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-6px)' },
                },
                'shimmer': {
                    '0%': { backgroundPosition: '-200% 0' },
                    '100%': { backgroundPosition: '200% 0' },
                },
                'pulse-ring': {
                    '0%': { transform: 'scale(1)', opacity: '1' },
                    '100%': { transform: 'scale(1.5)', opacity: '0' },
                },
                'gradient-shift': {
                    '0%, 100%': { backgroundPosition: '0% 50%' },
                    '50%': { backgroundPosition: '100% 50%' },
                },
            },
            animation: {
                'float': 'float 4s ease-in-out infinite',
                'shimmer': 'shimmer 2s linear infinite',
                'pulse-ring': 'pulse-ring 1.5s ease-out infinite',
                'gradient-shift': 'gradient-shift 3s ease-in-out infinite',
            },
        },
    },
    plugins: [],
};

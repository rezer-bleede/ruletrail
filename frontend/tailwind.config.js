/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        presight: {
          primary: '#0F3D5E',
          secondary: '#1F6F8B',
          accent: '#99D5C9',
          surface: '#F5F7FA',
          danger: '#E53E3E',
          warning: '#F6AD55',
          success: '#38A169'
        }
      }
    }
  },
  plugins: []
}

# Sherlog Frontend

A modern chat interface for interacting with Sherlog, built with Next.js and TypeScript.

## Features

- 🎨 Modern UI with dark mode support
- 📤 File upload for log analysis
- 📊 Prometheus/Loki/Grafana integration
- 💬 Real-time streaming responses
- 📱 Responsive design
- ⚡ Fast and efficient

## Quick Start

1. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

2. Create a `.env.local` file:
```bash
# Backend API URL (default for local development)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Start the development server:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

The application will be available at [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── app/                 # Next.js app directory
├── components/          # React components
├── lib/                 # Utility functions
├── public/             # Static assets
└── styles/             # Global styles
```

## Development

- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run start`: Start production server
- `npm run lint`: Run ESLint

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Sherlog backend API URL
- `NEXT_PUBLIC_ENABLE_ANALYTICS`: Enable/disable analytics (optional)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 
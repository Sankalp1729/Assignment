# AI DDR Generator Frontend

Modern React/Next.js frontend for the AI DDR Generator application.

## Features

- 📄 Document upload (PDF, JSON)
- 🔍 Real-time extraction preview
- 📊 Interactive analytics dashboard
- 📥 Report downloads
- 🎨 Responsive design with Tailwind CSS
- ⚡ Fast with Next.js 14

## Tech Stack

- **Framework:** Next.js 14
- **UI:** React 18 + Tailwind CSS
- **State Management:** Zustand
- **HTTP Client:** Axios
- **Charts:** Recharts
- **Icons:** React Icons

## Getting Started

### Prerequisites

- Node.js 18+ (or use `.nvmrc` for automatic version)
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Update .env.local with your API URL
# NEXT_PUBLIC_API_URL=http://localhost:8000  (for local dev)
# NEXT_PUBLIC_API_URL=https://api.render.com  (for production)
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

The app will hot-reload as you make changes.

### Building

```bash
# Create optimized production build
npm run build

# Start production server
npm run start
```

## Project Structure

```
frontend/
├── public/              # Static files
├── src/
│   ├── pages/          # Next.js pages (routes)
│   ├── components/     # Reusable components
│   ├── lib/            # Utilities, hooks, services
│   ├── styles/         # Global styles
│   └── types/          # TypeScript types
├── .env.example        # Environment template
├── next.config.js      # Next.js configuration
├── tailwind.config.js  # Tailwind CSS config
├── tsconfig.json       # TypeScript config
└── package.json        # Dependencies
```

## Deployment

### Deploy to Vercel (Recommended)

```bash
# 1. Push to GitHub
git push origin main

# 2. Import project in Vercel dashboard
# https://vercel.com/new

# 3. Set environment variables in Vercel
# - NEXT_PUBLIC_API_URL=https://your-backend-api.render.com

# 4. Deploy!
```

### Deploy to Other Platforms

```bash
# Build static export
npm run export

# Deploy `out` folder to any static hosting
```

## Environment Variables

Create `.env.local` from `.env.example`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Integration

The frontend communicates with the FastAPI backend:

- **Health Check:** `GET /health`
- **Extract Observations:** `POST /api/extract`
- **Run Pipeline:** `POST /api/pipeline`
- **Get Status:** `GET /api/status/{document_id}`

See backend documentation for API details.

## Troubleshooting

### CORS Issues
- Ensure `NEXT_PUBLIC_API_URL` matches backend CORS configuration
- Backend must have frontend URL in CORS allowed origins

### Build Errors
- Clear `.next` folder: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`

### Port Conflicts
- Default dev port is 3000
- Change with: `npm run dev -- -p 3001`

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and test locally
3. Commit: `git commit -am "Add feature"`
4. Push: `git push origin feature/my-feature`
5. Create Pull Request

## License

MIT License

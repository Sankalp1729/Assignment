# UrbanRoof DDR Generator - Deployment Guide

This project is structured as a unified Node.js application, where a single Express server hosts both the backend REST API and serves the compiled React (Vite) frontend. This structure makes deployment extremely simple.

---

## 1. Local Production Build & Run

To build and run the application locally in production mode:

1. **Install Dependencies**:
   ```bash
   pnpm install
   ```
2. **Build the Application**:
   ```bash
   pnpm build
   ```
   This will:
   * Build the React frontend into `dist/public`.
   * Bundle the TypeScript backend server into `dist/index.js`.
3. **Start the Production Server**:
   ```bash
   pnpm start
   ```
   The application will run on the port specified by the `PORT` environment variable (defaults to `5000`). Access it at `http://localhost:5000/`.

---

## 2. Cloud Deployment (Render / Railway / Heroku)

You can deploy the unified application to platforms like **Render**, **Railway**, or **Heroku** directly from a GitHub repository:

* **Repository Structure**: Unified root folder.
* **Environment Variable**: `NODE_ENV=production`
* **Build Command**: `pnpm install && pnpm build` (or `npm install && npm run build`)
* **Start Command**: `node dist/index.js` (or `npm start`)
* **Port**: The platform will automatically inject a `PORT` environment variable (e.g. `8080`), and the server is configured to bind to it.

---

## 3. VPS Deployment (Ubuntu / AWS EC2)

To deploy on a Linux server:

1. Clone your repository:
   ```bash
   git clone <your-repo-url>
   cd Urbanroof
   ```
2. Install Node.js (v18+) and pnpm:
   ```bash
   npm install -g pnpm
   pnpm install
   ```
3. Build the project:
   ```bash
   pnpm build
   ```
4. Install **PM2** to run the app in the background:
   ```bash
   npm install -g pm2
   pm2 start dist/index.js --name "ddr-generator"
   ```
5. Configure Nginx as a reverse proxy to route domain traffic to `http://localhost:5000`.

---

## 4. Production Storage Considerations

* **Local Uploads Directory**: By default, the application writes uploaded/generated files to `./uploads`. On ephemeral hosting platforms (like Render or Heroku without persistent disks), these files will be lost when the instance restarts.
* **Production Recommendation**:
  * **Render**: Attach a persistent disk mount at `/uploads`.
  * **AWS/S3**: For scaling, swap out the `fs` write operations in `pdfParser.ts` and `reportGenerator.ts` to push files directly to an AWS S3 bucket.


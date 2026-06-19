# Tessen Invoice Editor

A full-stack invoice operations workspace built with Next.js, Prisma/PostgreSQL, pdf.js, Nodemailer, and a FastAPI/PyMuPDF editing service. It is ready to run as one Vercel project.

## Setup

1. Copy `.env.example` to `.env` and add a PostgreSQL connection string.
2. Install dependencies: `npm install`
3. Set up the database: `npx prisma generate && npx prisma migrate deploy`
4. Start the PDF sidecar in a separate terminal: `bash sidecar/start.sh`
5. Start the web app: `npm run dev`
6. Open [http://localhost:3000](http://localhost:3000)

## Deploy to Vercel

1. Push this repository to GitHub.
2. In Vercel, choose **Add New → Project**, import the GitHub repository, and keep the detected Next.js settings.
3. From the project dashboard, open **Storage → Create Database** and add a PostgreSQL provider such as Neon.
4. Confirm that the integration created a `DATABASE_URL` environment variable for Production, Preview, and Development.
5. Deploy again. The build runs the checked-in Prisma migration automatically.

The Python function at `/api/pdf_edit` is deployed with the same project. The Next.js invoice route uses it automatically on Vercel and continues to use `sidecar/start.sh` during local development.

## First-time configuration

1. Open **Settings**. Enter your Gmail address, Gmail App Password, and sender name, save, then send a test email. Create an App Password under Google Account → Security → 2-Step Verification → App Passwords.
2. Create a company profile and optionally make it the default.
3. Add clients, contacts, and work locations in **Clients**.
4. Upload PDFs in **Editor**, complete the form, and click **Apply Changes**. You can then preview, download, email, or bundle ready invoices into a ZIP.

Email credentials are stored in PostgreSQL and never sent to the browser. Restrict database access and use a dedicated Gmail App Password.

# Tessen Invoice Editor

A full-stack invoice operations workspace built with Next.js, Prisma/SQLite, pdf.js, Nodemailer, and a FastAPI/PyMuPDF editing service.

## Setup

1. Install dependencies: `npm install`
2. Set up the database: `npx prisma generate && npx prisma db push`
3. Start the PDF sidecar in a separate terminal: `bash sidecar/start.sh`
4. Start the web app: `npm run dev`
5. Open [http://localhost:3000](http://localhost:3000)

## First-time configuration

1. Open **Settings**. Enter your Gmail address, Gmail App Password, and sender name, save, then send a test email. Create an App Password under Google Account → Security → 2-Step Verification → App Passwords.
2. Create a company profile and optionally make it the default.
3. Add clients, contacts, and work locations in **Clients**.
4. Upload PDFs in **Editor**, complete the form, and click **Apply Changes**. You can then preview, download, email, or bundle ready invoices into a ZIP.

Email credentials are stored only in the SQLite database. Keep the database file private.

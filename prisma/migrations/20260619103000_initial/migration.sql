CREATE TABLE "CompanyProfile" (
  "id" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "website" TEXT,
  "phone" TEXT,
  "email" TEXT,
  "remitEmail" TEXT,
  "addr1" TEXT,
  "city" TEXT,
  "state" TEXT,
  "zip" TEXT,
  "isDefault" BOOLEAN NOT NULL DEFAULT false,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "CompanyProfile_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "Client" (
  "id" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "type" TEXT,
  "poNumber" TEXT,
  "c1Name" TEXT,
  "c1Title" TEXT,
  "c1Email" TEXT,
  "c1Phone" TEXT,
  "c2Name" TEXT,
  "c2Title" TEXT,
  "c2Email" TEXT,
  "c2Phone" TEXT,
  "bcName" TEXT,
  "bcTitle" TEXT,
  "bcEmail" TEXT,
  "bcPhone" TEXT,
  "notes" TEXT,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "Client_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "Location" (
  "id" TEXT NOT NULL,
  "label" TEXT NOT NULL,
  "line1" TEXT NOT NULL,
  "line2" TEXT,
  "clientId" TEXT NOT NULL,
  CONSTRAINT "Location_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "EmailSettings" (
  "id" TEXT NOT NULL DEFAULT 'singleton',
  "gmailUser" TEXT,
  "gmailAppPwd" TEXT,
  "senderName" TEXT,
  CONSTRAINT "EmailSettings_pkey" PRIMARY KEY ("id")
);

ALTER TABLE "Location" ADD CONSTRAINT "Location_clientId_fkey" FOREIGN KEY ("clientId") REFERENCES "Client"("id") ON DELETE CASCADE ON UPDATE CASCADE;

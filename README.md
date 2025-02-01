# Create T3 App

This is a [T3 Stack](https://create.t3.gg/) project bootstrapped with `create-t3-app`.

## What's next? How do I make an app with this?

We try to keep this project as simple as possible, so you can start with just the scaffolding we set up for you, and add additional things later when they become necessary.

If you are not familiar with the different technologies used in this project, please refer to the respective docs. If you still are in the wind, please join our [Discord](https://t3.gg/discord) and ask for help.

- [Next.js](https://nextjs.org)
- [NextAuth.js](https://next-auth.js.org)
- [Prisma](https://prisma.io)
- [Drizzle](https://orm.drizzle.team)
- [Tailwind CSS](https://tailwindcss.com)
- [tRPC](https://trpc.io)

## Learn More

To learn more about the [T3 Stack](https://create.t3.gg/), take a look at the following resources:

- [Documentation](https://create.t3.gg/)
- [Learn the T3 Stack](https://create.t3.gg/en/faq#what-learning-resources-are-currently-available) — Check out these awesome tutorials

You can check out the [create-t3-app GitHub repository](https://github.com/t3-oss/create-t3-app) — your feedback and contributions are welcome!

## How do I deploy this?

Follow our deployment guides for [Vercel](https://create.t3.gg/en/deployment/vercel), [Netlify](https://create.t3.gg/en/deployment/netlify) and [Docker](https://create.t3.gg/en/deployment/docker) for more information.




# Caregiver App

A simple caregiver application that allows caregivers to log in, create patient profiles, manage medications with dosage and schedules, and integrates with Twilio to call patients and confirm that medications have been taken.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [License](#license)

## Overview

The Caregiver App is designed to streamline medication management. Caregivers can register or log in, create patient profiles, add medications, set dosage instructions, and schedule medication times. The app uses Twilio for automated call integration to confirm if the patient has taken their medication. The backend is built with FastAPI and Python, and uses SQLite as the database, managed with SQLAlchemy and Alembic for migrations.

## Features

- **User Authentication:** Caregivers can securely log in and manage their accounts.
- **Patient Management:** Create and manage patient profiles.
- **Medication Management:** Add medications with dosage and instructions.
- **Scheduling:** Schedule medication times.
- **Automated Calls:** Integrated with Twilio to call patients and verify medication intake.
- **Clean & Simple Design:** Focus on essential features with the option to add more later.

## Tech Stack

- **Frontend:** React, Next.js, ShadcnUI (Figma)
- **Backend:** Python, FastAPI
- **Database:** SQLite with SQLAlchemy ORM
- **Migrations:** Alembic
- **APIs:** OpenAI API, Twilio API, Azure for Students API




### Prerequisites

- **Python 3.x** installed on your system.
- **Node.js** (if working on or testing the frontend).
- (Optional) A virtual environment tool like `venv` or `virtualenv`.




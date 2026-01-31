FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY app ./app
COPY components ./components
COPY lib ./lib
COPY styles ./styles
COPY next.config.mjs ./
COPY tsconfig.json ./
COPY postcss.config.js ./
COPY tailwind.config.ts ./
COPY next-env.d.ts ./

ENV NEXT_TELEMETRY_DISABLED=1

CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3000"]

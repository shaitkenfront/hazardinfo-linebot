/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: true,
  },
  env: {
    HAZARD_API_URL: process.env.HAZARD_API_URL || 'http://localhost:3001/api',
  },
}

module.exports = nextConfig
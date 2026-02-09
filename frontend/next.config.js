/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  env: {
    NEXT_PUBLIC_GRPC_WEB_URL: process.env.NEXT_PUBLIC_GRPC_WEB_URL || 'http://localhost:8080',
  },
}

module.exports = nextConfig

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {
    serverComponentsExternalPackages: ["better-auth", "pg"],
  },
};

module.exports = nextConfig;
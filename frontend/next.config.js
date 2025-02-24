/** @type {import('next').NextConfig} */
/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
      remotePatterns: [
        {
          protocol: 'http',
          hostname: '127.0.0.1',
          port: '5000',
          pathname: '/static/**',
        },
      ],
    },
  };
  

module.exports = nextConfig

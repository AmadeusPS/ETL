/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone", // Optimised Docker image
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
    NEXT_PUBLIC_B2C_TENANT_NAME: process.env.NEXT_PUBLIC_B2C_TENANT_NAME || "",
    NEXT_PUBLIC_B2C_CLIENT_ID: process.env.NEXT_PUBLIC_B2C_CLIENT_ID || "",
    NEXT_PUBLIC_B2C_POLICY_NAME: process.env.NEXT_PUBLIC_B2C_POLICY_NAME || "B2C_1_signupsignin",
  },
};

module.exports = nextConfig;

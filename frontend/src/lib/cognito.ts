/**
 * Azure AD B2C authentication via MSAL (replaces AWS Amplify/Cognito).
 *
 * Auth flow:
 *  1. User clicks "Entrar" → loginRedirect() → browser redirected to B2C hosted UI
 *  2. B2C handles credentials + MFA
 *  3. Browser redirected back to /dashboard with auth code
 *  4. handleRedirectPromise() exchanges code for tokens (called in layout.tsx)
 *  5. getIdToken() returns the ID token to attach to API requests
 */
import {
  PublicClientApplication,
  Configuration,
  AccountInfo,
  RedirectRequest,
} from "@azure/msal-browser";

const tenantName = process.env.NEXT_PUBLIC_B2C_TENANT_NAME!;
const clientId = process.env.NEXT_PUBLIC_B2C_CLIENT_ID!;
const policyName = process.env.NEXT_PUBLIC_B2C_POLICY_NAME || "B2C_1_signupsignin";

const authority = `https://${tenantName}.b2clogin.com/${tenantName}.onmicrosoft.com/${policyName}`;

const msalConfig: Configuration = {
  auth: {
    clientId,
    authority,
    knownAuthorities: [`${tenantName}.b2clogin.com`],
    redirectUri: typeof window !== "undefined"
      ? `${window.location.origin}/dashboard`
      : "http://localhost:3000/dashboard",
    postLogoutRedirectUri: typeof window !== "undefined"
      ? `${window.location.origin}/login`
      : "http://localhost:3000/login",
  },
  cache: {
    cacheLocation: "localStorage",
    storeAuthStateInCookie: false,
  },
};

const loginRequest: RedirectRequest = {
  scopes: ["openid", "profile", "offline_access"],
};

let _msal: PublicClientApplication | null = null;

async function getMsal(): Promise<PublicClientApplication> {
  if (!_msal) {
    _msal = new PublicClientApplication(msalConfig);
    await _msal.initialize();
  }
  return _msal;
}

/** Call once on app load to complete any pending redirect. */
export async function handleRedirectPromise(): Promise<void> {
  const msal = await getMsal();
  await msal.handleRedirectPromise();
  const accounts = msal.getAllAccounts();
  if (accounts.length > 0) {
    msal.setActiveAccount(accounts[0]);
  }
}

/** Redirect to B2C sign-in / sign-up hosted UI. */
export async function signIn(): Promise<void> {
  const msal = await getMsal();
  await msal.loginRedirect(loginRequest);
}

/** Sign out and redirect to /login. */
export async function signOut(): Promise<void> {
  const msal = await getMsal();
  const account = msal.getActiveAccount();
  await msal.logoutRedirect({ account: account ?? undefined });
}

/** Returns the current ID token string for API authorization headers. */
export async function getIdToken(): Promise<string | null> {
  const msal = await getMsal();
  const accounts = msal.getAllAccounts();
  if (accounts.length === 0) return null;
  msal.setActiveAccount(accounts[0]);
  try {
    const result = await msal.acquireTokenSilent({ ...loginRequest, account: accounts[0] });
    return result.idToken;
  } catch {
    return null;
  }
}

/** Returns the signed-in AccountInfo or null if not authenticated. */
export async function getCurrentAccount(): Promise<AccountInfo | null> {
  const msal = await getMsal();
  return msal.getActiveAccount();
}

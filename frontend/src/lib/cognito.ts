import { Amplify } from "aws-amplify";
import {
  signIn,
  signUp,
  signOut,
  confirmSignUp,
  fetchAuthSession,
  getCurrentUser,
  resetPassword,
  confirmResetPassword,
} from "aws-amplify/auth";

export function configureAmplify() {
  Amplify.configure({
    Auth: {
      Cognito: {
        userPoolId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID!,
        userPoolClientId: process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID!,
        loginWith: { email: true },
      },
    },
  });
}

export async function getIdToken(): Promise<string | null> {
  try {
    const session = await fetchAuthSession();
    return session.tokens?.idToken?.toString() ?? null;
  } catch {
    return null;
  }
}

export { signIn, signUp, signOut, confirmSignUp, getCurrentUser, resetPassword, confirmResetPassword };

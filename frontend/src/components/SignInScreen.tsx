import { startGoogleSignIn } from "../services/auth";

export function SignInScreen() {
  return (
    <div className="auth-screen">
      <section className="auth-card" aria-label="Sign in to SANE">
        <span className="auth-kicker">Stage 1 ALPHA</span>
        <h1>Sign in to SANE</h1>
        <p>
          Google sign-in authenticates you to SANE. Gmail mailbox access stays a
          separate step in Connections, and scans only run when you trigger
          them.
        </p>
        <button
          className="btn-primary"
          type="button"
          onClick={startGoogleSignIn}
        >
          Sign in with Google
        </button>
      </section>
    </div>
  );
}

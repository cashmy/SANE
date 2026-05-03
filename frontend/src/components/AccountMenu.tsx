import type { UserMe } from "../types/auth";

interface AccountMenuProps {
  user: UserMe;
  isSigningOut: boolean;
  onSignOut: () => void | Promise<void>;
}

export function AccountMenu({
  user,
  isSigningOut,
  onSignOut,
}: AccountMenuProps) {
  return (
    <div className="account-menu" aria-label="Signed-in user account">
      <div className="account-menu__identity">
        <span className="account-menu__name">{user.display_name}</span>
        {!user.is_local_alpha && user.email ? (
          <span className="account-menu__email">{user.email}</span>
        ) : null}
      </div>
      <div className="account-menu__actions">
        {user.is_local_alpha ? (
          <span className="chip chip--neutral">Local dev</span>
        ) : null}
        <button
          className="btn-secondary"
          type="button"
          onClick={() => {
            void onSignOut();
          }}
          disabled={isSigningOut}
        >
          {isSigningOut ? "Signing out..." : "Sign out"}
        </button>
      </div>
    </div>
  );
}

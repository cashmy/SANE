from dataclasses import dataclass


@dataclass(frozen=True)
class DemoCandidateSeed:
    source_key: str
    source_name: str
    sender_emails: tuple[str, ...]
    email_count: int
    representative_subject: str
    mailbox_category: str


DEMO_CANDIDATES: tuple[DemoCandidateSeed, ...] = (
    DemoCandidateSeed(
        source_key="daily-deals-dispatch",
        source_name="Daily Deals Dispatch",
        sender_emails=(
            "offers@dailydeals.example",
            "member-perks@dailydeals.example",
        ),
        email_count=74,
        representative_subject="Weekend flash sale and member-only discount roundup",
        mailbox_category="Promotions",
    ),
    DemoCandidateSeed(
        source_key="workspace-vendor-update",
        source_name="Workspace Vendor Update",
        sender_emails=(
            "newsletter@workspacevendor.example",
            "events@workspacevendor.example",
        ),
        email_count=28,
        representative_subject="April feature digest and customer webinar recap",
        mailbox_category="Updates",
    ),
    DemoCandidateSeed(
        source_key="local-events-weekly",
        source_name="Local Events Weekly",
        sender_emails=("weekly@localevents.example",),
        email_count=13,
        representative_subject="Neighborhood events newsletter for this week",
        mailbox_category="Social",
    ),
    DemoCandidateSeed(
        source_key="tooling-community-notes",
        source_name="Tooling Community Notes",
        sender_emails=(
            "notes@tooling-community.example",
            "events@tooling-community.example",
        ),
        email_count=18,
        representative_subject="Community office hours and release notes",
        mailbox_category="Updates",
    ),
    DemoCandidateSeed(
        source_key="routine-platform-bulletin",
        source_name="Routine Platform Bulletin",
        sender_emails=(
            "bulletin@routine-platform.example",
            "status@routine-platform.example",
            "ops@routine-platform.example",
        ),
        email_count=41,
        representative_subject="Monthly status summary for your workspace",
        mailbox_category="Updates",
    ),
    DemoCandidateSeed(
        source_key="cloud-billing-notices",
        source_name="Cloud Billing Notices",
        sender_emails=("alerts@cloudbilling.example",),
        email_count=9,
        representative_subject="Usage threshold reminder and invoice preview",
        mailbox_category="Updates",
    ),
    DemoCandidateSeed(
        source_key="founder-network-roundup",
        source_name="Founder Network Roundup",
        sender_emails=(
            "digest@foundernetwork.example",
            "newsletter@foundernetwork.example",
        ),
        email_count=22,
        representative_subject="This week in founder communities and partner offers",
        mailbox_category="Promotions",
    ),
    DemoCandidateSeed(
        source_key="product-research-invitations",
        source_name="Product Research Invitations",
        sender_emails=("research@productlab.example",),
        email_count=6,
        representative_subject="Invitation to join a short feedback panel",
        mailbox_category="Updates",
    ),
)

from dataclasses import dataclass


@dataclass(frozen=True)
class DemoCandidateSeed:
    sender_name: str
    sender_email: str
    subject: str
    mailbox_category: str


DEMO_CANDIDATES: tuple[DemoCandidateSeed, ...] = (
    DemoCandidateSeed(
        sender_name="Daily Deals Dispatch",
        sender_email="offers@dailydeals.example",
        subject="Weekend flash sale and member-only discount roundup",
        mailbox_category="Promotions",
    ),
    DemoCandidateSeed(
        sender_name="Workspace Vendor Update",
        sender_email="newsletter@workspacevendor.example",
        subject="April feature digest and customer webinar recap",
        mailbox_category="Updates",
    ),
    DemoCandidateSeed(
        sender_name="Local Events Weekly",
        sender_email="weekly@localevents.example",
        subject="Neighborhood events newsletter for this week",
        mailbox_category="Social",
    ),
    DemoCandidateSeed(
        sender_name="Tooling Community Notes",
        sender_email="notes@tooling-community.example",
        subject="Community office hours and release notes",
        mailbox_category="Updates",
    ),
    DemoCandidateSeed(
        sender_name="Routine Platform Bulletin",
        sender_email="bulletin@routine-platform.example",
        subject="Monthly status summary for your workspace",
        mailbox_category="Updates",
    ),
)

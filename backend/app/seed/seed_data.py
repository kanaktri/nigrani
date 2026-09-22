"""
Populates the database with demo accounts and sample data so a judge or a
teammate can log in and see a working system in under a minute - never an
empty dashboard.

Run with:  ./venv/bin/python -m app.seed.seed_data
"""
import sys
from datetime import datetime, timedelta

from app.core.security import hash_password
from app.core.time import utcnow
from app.db.base import Base, SessionLocal, engine
from app.db.models.alert import Alert
from app.db.models.assignment import Assignment
from app.db.models.camera_feed import CameraFeed
from app.db.models.grievance import Grievance
from app.db.models.institute import Institute
from app.db.models.institute_document import InstituteDocument
from app.db.models.user import User
from app.services.anomaly import (generate_synthetic_history, score_day,
                                  train_model)

DEMO_PASSWORD = "Password123!"


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).count() > 0:
        print("Database already has data - skipping seed. Delete dosje_nigrani.db to reseed.")
        db.close()
        return

    # --- Institutes (spread across a district, realistic-looking coordinates) ---
    institutes = [
        Institute(name="Asha Girls Shelter", type="shelter", latitude=26.8467, longitude=80.9462, district="Lucknow", state="Uttar Pradesh"),
        Institute(name="Nirmaan Skill Centre", type="skill_center", latitude=26.8500, longitude=80.9200, district="Lucknow", state="Uttar Pradesh"),
        Institute(name="Sahara Rehab Home", type="rehab", latitude=26.7606, longitude=83.3732, district="Gorakhpur", state="Uttar Pradesh"),
        Institute(name="Umang NGO Centre", type="ngo", latitude=25.3176, longitude=82.9739, district="Varanasi", state="Uttar Pradesh"),
    ]
    db.add_all(institutes)
    db.commit()
    for i in institutes:
        db.refresh(i)

    # --- Demo accounts, one per role ---
    demo_users = [
        User(name="Admin User", email="admin@dosje.gov.in", password_hash=hash_password(DEMO_PASSWORD), role="admin"),
        User(name="Rakesh Kumar (Inspector)", email="inspector1@dosje.gov.in", password_hash=hash_password(DEMO_PASSWORD), role="inspector"),
        User(name="Sunita Verma (Inspector)", email="inspector2@dosje.gov.in", password_hash=hash_password(DEMO_PASSWORD), role="inspector"),
        User(name="District Official", email="official@dosje.gov.in", password_hash=hash_password(DEMO_PASSWORD), role="official"),
        User(name="Institute Staff", email="staff@dosje.gov.in", password_hash=hash_password(DEMO_PASSWORD), role="institute_staff", institute_id=institutes[0].id),
        User(name="Test Beneficiary", email="beneficiary@dosje.gov.in", password_hash=hash_password(DEMO_PASSWORD), role="beneficiary", phone_number="+919999999999", institute_id=institutes[0].id),
    ]
    db.add_all(demo_users)
    db.commit()
    for u in demo_users:
        db.refresh(u)

    inspectors = [u for u in demo_users if u.role == "inspector"]

    # --- A handful of past assignments so the fairness constraint has history to work with ---
    for idx, inst in enumerate(institutes):
        assignment = Assignment(
            institute_id=inst.id,
            inspector_id=inspectors[idx % len(inspectors)].id,
            random_seed_ref=f"seed-{idx}",
            created_at=utcnow() - timedelta(days=10 - idx),
            geofence_triggered_at=utcnow() - timedelta(days=10 - idx, hours=-1),
            notified_institute_at=utcnow() - timedelta(days=10 - idx, hours=-1),
        )
        db.add(assignment)
    db.commit()

    # --- Real anomaly detection run: generate synthetic history for one
    #     institute with an injected "prepared for inspection" pattern,
    #     train Isolation Forest, and write a GENUINE computed alert - not
    #     a hardcoded one. This is what proves USP4 isn't just a slide.
    target_institute = institutes[0]
    history_df = generate_synthetic_history(days=60, inject_anomaly_on_last_n=5)
    model = train_model(history_df.iloc[:-5])  # train on the clean history only
    last_day = history_df.iloc[-1].to_dict()
    result = score_day(model, last_day)

    if result["is_anomaly"]:
        alert = Alert(
            institute_id=target_institute.id,
            type="attendance_spike",
            severity="red",
            status="open",
            detail=(
                f"Isolation Forest anomaly score {result['anomaly_score']:.3f}: attendance and CCTV uptime "
                f"spiked to near-perfect while VC pickup rate collapsed - pattern consistent with "
                f"'prepared for inspection' behavior, not normal operation."
            ),
        )
        db.add(alert)
        db.commit()
        print(f"Anomaly alert generated for '{target_institute.name}' (score={result['anomaly_score']:.3f})")
    else:
        print("No anomaly detected in synthetic run (unexpected - check anomaly.py injection logic)")

    # --- Camera feeds per institute, mixed health states - what Sentinel's
    #     CCTV wall actually renders (this is connection-health monitoring,
    #     a real signal, not a live video stream - see the README on what's
    #     genuinely wired up vs. a documented integration point).
    camera_names = ["Main Gate", "Dormitory Hall", "Kitchen", "Common Room"]
    camera_statuses_cycle = ["online", "online", "stale", "offline"]
    for inst in institutes:
        for i, name in enumerate(camera_names):
            status = camera_statuses_cycle[i % len(camera_statuses_cycle)]
            db.add(CameraFeed(
                institute_id=inst.id,
                name=f"{name} - {inst.name}",
                status=status,
                last_ping_at=utcnow() - timedelta(minutes=2 if status == "online" else 240),
            ))
    db.commit()

    # --- One institute's renewal is still pending review, the rest approved -
    #     gives Sentinel's renewal-approval screen something real to act on.
    institutes[0].renewal_status = "pending"
    for inst in institutes[1:]:
        inst.renewal_status = "approved"
    db.commit()

    # --- A sample grievance and a document response, from the institute
    #     staff account - what Setu's own screens read back.
    staff_user = next(u for u in demo_users if u.role == "institute_staff")
    db.add(Grievance(
        institute_id=institutes[0].id,
        submitted_by_id=staff_user.id,
        subject="CCTV maintenance request",
        description="The Kitchen camera has been offline for 3 days - requesting a technician visit.",
        status="open",
    ))
    db.add(InstituteDocument(
        institute_id=institutes[0].id,
        uploaded_by_id=staff_user.id,
        file_url="local:///institute-documents/demo/fire-safety-certificate.pdf",
        description="Updated fire safety certificate, submitted in response to the compliance review.",
    ))
    db.commit()

    # session - accessing ORM attributes after close() raises
    # DetachedInstanceError, since the session is what lazy-loads them.
    account_lines = [(u.role, u.email) for u in demo_users]
    db.close()

    print("\nSeed complete. Demo accounts (all use password: {}):".format(DEMO_PASSWORD))
    for role, email in account_lines:
        print(f"  {role:<16} {email}")


if __name__ == "__main__":
    sys.exit(run() or 0)

from app.core.models.profile import Profile


def gen_profiles():
    return [
        Profile(firstname="Mathéo", lastname="Gomes", skills="Développeur")
    ]

def gen_job_applications():
    return []
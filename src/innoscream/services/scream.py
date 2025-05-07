"""
Bot‑facing service that just delegates to the DB repo.
"""
from ..db import scream_repo as repo

EMOJI_TO_COLUMN = repo.EMOJI_TO_COLUMN

save_scream = repo.create_post
add_reaction = repo.switch_reaction
delete_post = repo.soft_delete
get_user_stats = repo.user_post_count
get_top_daily = repo.top_daily
weekly_labels_counts = repo.weekly_labels_counts

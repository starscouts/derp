# Derp configuration file

# ---------------------------
# Paths to the data files for this configuration file
sent_list_path = "list-raindrops.txt"
token_path = "token-raindrops.txt"

# ---------------------------
# The tags to show in the notification, considered high-importance tags

triggers = {"explicit", "suggestive", "grimdark", "semi-grimdark", "grotesque", "questionable", "foalcon", "male", "intersex", "bondage", "close-up", "tentacles"}

# ---------------------------
# The query to send to Derpibooru when looking for new images

query = "my:watched"

# ---------------------------
# If you want to use a Derpibooru filter when fetching images, enter its ID here

filter_id = 206751 # 56027 is the "Everything" filter, meaning nothing is filtered

# ---------------------------
# The size the images should be cropped at when they are attached to the notification.

resolution = (1000, 500)  # Recommended for Android 12+
#resolution = (1300, 400) # Recommended for Android 9-11

# ---------------------------
# The user name associated with the Derpibooru account
# Notifications are sent to the 'derpibooru-<username>' channel

user_name = "RaindropsSys"
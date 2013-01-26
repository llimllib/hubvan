rsync -az --delete -e ssh --safe-links --exclude '.git' --exclude '*.pyc' \
    hubvan llimllib@hubvan.com:/srv/hubvan.com/
rsync requirements.txt llimllib@hubvan.com:/srv/hubvan.com/
